// La voz del moog, muestra a muestra. Puerto EXACTO de `framework/aem/synths.py`.
//
// Corre en un AudioWorklet y no como cadena de nodos Web Audio a proposito: el filtro
// escalera es recursivo con una no linealidad ADENTRO de cada celda, y eso no se puede
// armar con BiquadFilter. Un pasabajos con resonancia se le parece de lejos; esto es el
// mismo algoritmo que rinde el disco.
//
// Lo unico que cambia respecto de Python son los osciladores: alla se suman 64 armonicos
// (exacto, offline), aca va polyBLEP, que es la aproximacion que corresponde en tiempo
// real. Suena igual salvo en las notas mas agudas, donde polyBLEP deja un pelo mas de
// aliasing.

const THERMAL = 0.000025;
const BLOQUE_COEF = 64;      // cada cuantas muestras se recalculan tune y res_quad

// --- polyBLEP: le saca el escalon a la discontinuidad del diente de sierra
function blep(t, dt) {
  if (t < dt) { t /= dt; return t + t - t * t - 1; }
  if (t > 1 - dt) { t = (t - 1) / dt; return t * t + t + t + 1; }
  return 0;
}

class Escalera {
  constructor() { this.reset(); }
  reset() {
    this.d0 = this.d1 = this.d2 = this.d3 = this.d4 = this.d5 = 0;
    this.t0 = this.t1 = this.t2 = 0;
    this.tune = 0; this.resQuad = 0; this.cont = 0;
  }
  // Los polinomios fcr y acr son los del paper (Huovilainen, DAFx-04): corrigen la
  // desafinacion y la caida de resonancia que mete la discretizacion.
  coefs(corteHz, res, sr, over) {
    const f = Math.min(Math.max(corteHz, 20), sr * 0.45) / (sr * over);
    const fcr = 1.8730 * f * f * f + 0.4955 * f * f - 0.6490 * f + 0.9988;
    const acr = -3.9364 * f * f + 1.8409 * f + 0.9968;
    this.tune = (1 - Math.exp(-2 * Math.PI * f * fcr)) / THERMAL;
    this.resQuad = 4.0 * res * acr;     // arriba de 4 el lazo se auto-oscila
  }
  procesar(x, corteHz, res, drive, sr, over) {
    if (this.cont-- <= 0) { this.coefs(corteHz, res, sr, over); this.cont = BLOQUE_COEF; }
    const ganancia = drive / THERMAL * 1e-5;
    let m = x * ganancia;
    for (let k = 0; k < over; k++) {
      const entrada = m - this.resQuad * this.d5;
      // la no linealidad va DENTRO de cada celda, no a la salida
      let s0 = this.d0 + this.tune * (Math.tanh(entrada * THERMAL) - this.t0);
      this.d0 = s0; this.t0 = Math.tanh(s0 * THERMAL);
      let s1 = this.d1 + this.tune * (this.t0 - this.t1);
      this.d1 = s1; this.t1 = Math.tanh(s1 * THERMAL);
      let s2 = this.d2 + this.tune * (this.t1 - this.t2);
      this.d2 = s2; this.t2 = Math.tanh(s2 * THERMAL);
      let s3 = this.d3 + this.tune * (this.t2 - Math.tanh(this.d3 * THERMAL));
      this.d3 = s3;
      this.d5 = (s3 + this.d4) * 0.5;   // medio retardo: compensa la fase del oversampling
      this.d4 = s3;
    }
    // se deshace la escala del drive, y se compensa a medias la banda pasante: con
    // realimentacion k la ganancia en continua cae a 1/(1+k), por eso un Moog se
    // adelgaza al abrir la resonancia
    return (this.d5 / (ganancia || 1)) * (1 + 2.4 * res);
  }
}

class Moog extends AudioWorkletProcessor {
  static get parameterDescriptors() {
    return [
      { name: "corte",    defaultValue: 900,  minValue: 20,   maxValue: 9000, automationRate: "k-rate" },
      { name: "res",      defaultValue: 0.72, minValue: 0,    maxValue: 1.25, automationRate: "k-rate" },
      { name: "drive",    defaultValue: 14,   minValue: 1,    maxValue: 80,   automationRate: "k-rate" },
      { name: "sub",      defaultValue: 0.35, minValue: 0,    maxValue: 1,    automationRate: "k-rate" },
      { name: "detune",   defaultValue: 2.5,  minValue: 0,    maxValue: 40,   automationRate: "k-rate" },
      { name: "glide",    defaultValue: 0.08, minValue: 0,    maxValue: 2,    automationRate: "k-rate" },
      { name: "ataque",   defaultValue: 0.02, minValue: 0.001, maxValue: 4,   automationRate: "k-rate" },
      { name: "caida",    defaultValue: 1.2,  minValue: 0.02, maxValue: 8,    automationRate: "k-rate" },
      { name: "sostiene", defaultValue: 0.85, minValue: 0,    maxValue: 1,    automationRate: "k-rate" },
      { name: "suelta",   defaultValue: 1.4,  minValue: 0.02, maxValue: 8,    automationRate: "k-rate" },
      { name: "envFiltro", defaultValue: 0.65, minValue: 0,   maxValue: 1,    automationRate: "k-rate" },
      // 0 = mono (las dos sierras en la misma nota, separadas por el detune)
      // 1 = duo  (OSC1 sigue la tecla mas grave, OSC2 la mas aguda)
      { name: "duo",      defaultValue: 0,    minValue: 0,    maxValue: 1,    automationRate: "k-rate" },
    ];
  }

  constructor() {
    super();
    this.esc = new Escalera();
    // DOS osciladores con frecuencia propia. En mono los dos siguen la misma nota y el
    // detune los separa; en duo cada uno sigue una tecla distinta. Es la arquitectura
    // del Subsequent 25: dos osciladores, UN filtro, UNA envolvente. Eso es parafonia,
    // no polifonia: no hay dos voces completas, hay dos alturas entrando al mismo filtro.
    this.f1 = 0; this.f2 = 0;
    this.f1Obj = 0; this.f2Obj = 0;
    this.fase = 0; this.fase2 = 0; this.faseSub = 0;
    this.env = 0; this.envF = 0;
    this.etapa = "off";               // off | ataque | caida | suelta
    this.notas = [];                  // pila de teclas apretadas
    this.pico = 0;
    this.port.onmessage = (e) => this.mensaje(e.data);
  }

  // Reparte las teclas apretadas entre los dos osciladores segun el modo.
  repartir(duo) {
    if (!this.notas.length) return;
    if (duo) {
      // OSC1 la mas grave, OSC2 la mas aguda. Con una sola tecla los dos van ahi, que
      // es lo que hace el hardware: duo con una nota colapsa a unisono.
      const hz = this.notas.map((n) => n.hz);
      this.f1Obj = Math.min(...hz);
      this.f2Obj = Math.max(...hz);
    } else {
      this.f1Obj = this.f2Obj = this.notas[this.notas.length - 1].hz;
    }
    if (this.f1 === 0) this.f1 = this.f1Obj;
    if (this.f2 === 0) this.f2 = this.f2Obj;
  }

  mensaje(m) {
    if (m.tipo === "on") {
      const legato = this.notas.length > 0;   // ya habia una tecla: NO se re-dispara
      this.notas = this.notas.filter((n) => n.id !== m.id);
      this.notas.push({ id: m.id, hz: m.hz });
      this.repartir(this.duo);
      if (!legato) { this.etapa = "ataque"; }
      this.port.postMessage({ tipo: "art", legato });
    } else if (m.tipo === "off") {
      this.notas = this.notas.filter((n) => n.id !== m.id);
      if (this.notas.length) this.repartir(this.duo);
      else this.etapa = "suelta";
    } else if (m.tipo === "panico") {
      this.notas = []; this.etapa = "suelta";
    }
  }

  process(_in, outputs, p) {
    const out = outputs[0][0];
    if (!out) return true;
    const sr = sampleRate;
    const v = (n) => (p[n].length > 1 ? p[n][0] : p[n][0]);
    const corte = v("corte"), res = v("res"), drive = v("drive"), sub = v("sub");
    const det = v("detune"), glide = v("glide"), envF = v("envFiltro");
    const duo = v("duo") > 0.5;
    if (duo !== this.duo) { this.duo = duo; this.repartir(duo); }
    const at = v("ataque"), ca = v("caida"), so = v("sostiene"), su = v("suelta");

    // el glide es exponencial: el oido escucha proporciones, no diferencias en Hz
    const kGlide = glide > 0.0005 ? Math.exp(-1 / (glide * sr)) : 0;
    const kAt = 1 - Math.exp(-1 / (at * sr));
    const kCa = 1 - Math.exp(-1 / (ca * sr));
    const kSu = 1 - Math.exp(-1 / (su * sr));

    const up = Math.pow(2, det / 1200), dn = Math.pow(2, -det / 1200);
    let pico = 0;

    for (let i = 0; i < out.length; i++) {
      if (this.f1Obj > 0) this.f1 = this.f1Obj + (this.f1 - this.f1Obj) * kGlide;
      if (this.f2Obj > 0) this.f2 = this.f2Obj + (this.f2 - this.f2Obj) * kGlide;

      if (this.etapa === "ataque") {
        this.env += (1 - this.env) * kAt;
        if (this.env > 0.995) { this.env = 1; this.etapa = "caida"; }
      } else if (this.etapa === "caida") {
        this.env += (so - this.env) * kCa;
      } else if (this.etapa === "suelta") {
        this.env += (0 - this.env) * kSu;
        if (this.env < 1e-4) { this.env = 0; this.etapa = "off"; }
      }
      this.envF += (this.env - this.envF) * 0.0012;   // el filtro sigue mas lento

      // --- dos sierras desafinadas y un pulso una octava abajo
      // en duo el detune casi no se aplica: las alturas ya son distintas de verdad
      const dt1 = (this.f1 * (duo ? 1 : up)) / sr;
      const dt2 = (this.f2 * (duo ? 1 : dn)) / sr;
      const dts = (this.f1 / 2) / sr;          // el sub sigue a OSC1, como en el hardware
      this.fase += dt1; if (this.fase >= 1) this.fase -= 1;
      this.fase2 += dt2; if (this.fase2 >= 1) this.fase2 -= 1;
      this.faseSub += dts; if (this.faseSub >= 1) this.faseSub -= 1;

      let s1 = 2 * this.fase - 1 - blep(this.fase, dt1);
      let s2 = 2 * this.fase2 - 1 - blep(this.fase2, dt2);
      const d = 0.42;                                  // ancho del pulso, como en el tema
      let ps = (this.faseSub < d ? 1 : -1)
             + blep(this.faseSub, dts)
             - blep((this.faseSub + 1 - d) % 1, dts);

      let x = (s1 * 0.5 + s2 * 0.5 + ps * sub) * 0.5;

      // el corte sigue a la envolvente, igual que en `melodia.py`
      const c = corte * (1 - envF + envF * this.envF);
      let y = this.esc.procesar(x, c, res, drive, sr, 2);

      y *= this.env;
      out[i] = y;
      const a = Math.abs(y); if (a > pico) pico = a;
    }

    this.pico = Math.max(pico, this.pico * 0.92);
    if (currentFrame % 2048 < out.length) {
      this.port.postMessage({ tipo: "medida", pico: this.pico, hz: this.f1, hz2: this.f2,
                              env: this.env, voces: this.notas.length });
    }
    return true;
  }
}

registerProcessor("moog", Moog);
