"""Sintetizadores sustractivos: la escalera Moog y la voz que la usa.

Esta parte del framework NO es de oido: sale de los papers que modelaron el circuito
real del Moog. Las constantes de abajo son las de esos papers, no valores elegidos
porque sonaban bien.

FUENTES

- Antti Huovilainen, "Non-Linear Digital Implementation of the Moog Ladder Filter",
  DAFx-04, Napoli, 2004. https://dafx.de/paper-archive/2004/P_061.PDF
  Es el modelo que usamos: mete la no linealidad ADENTRO de cada una de las cuatro
  celdas de un polo, que es donde estan los transistores en el circuito.
- Tim Stilson y Julius Smith, "Analyzing the Moog VCF with Considerations for
  Digital Implementation", ICMC 1996.
  https://ccrma.stanford.edu/~stilti/papers/moogvcf.pdf
  De aca sale el analisis del lazo: con realimentacion inversora la ganancia en el
  corte tiende a infinito cuando k tiende a 4, que es la auto-oscilacion.
- Implementacion de referencia contrastada:
  https://github.com/ddiakopoulos/MoogLadders (HuovilainenModel.h)
- Moog VCF en musicdsp (variante Stilson/Smith):
  https://www.musicdsp.org/en/latest/Filters/24-moog-vcf.html

QUE HACE QUE UN MOOG SUENE A MOOG, EN ORDEN DE IMPORTANCIA

1. **Cuatro polos en cascada con realimentacion negativa.** 24 dB por octava. La
   realimentacion es la resonancia: `k` tendiendo a 4 es auto-oscilacion.
2. **La no linealidad esta DENTRO de cada celda**, no a la salida. Por eso cuando se
   lo satura no distorsiona como un fuzz: se comprime y la resonancia se dobla sola.
   Esto es lo que ningun pasa-bajos con un peak encima puede imitar.
3. **Perdida de ganancia en la banda pasante al subir resonancia.** No es un defecto,
   es parte del sonido: al abrir la resonancia el Moog se adelgaza.
4. **Envolvente de filtro separada de la de amplitud.**
5. **Sub-oscilador y osciladores desafinados entre si.**

SOBRE LOS OSCILADORES

Aca se generan por SUMA DE ARMONICOS hasta Nyquist. Eso es band-limited exacto: no
hay aliasing, cero. Las tecnicas tipo polyBLEP existen porque en tiempo real no se
puede pagar una suma de cincuenta senos por muestra; nosotros rendimos offline, asi
que usamos la version exacta y no la aproximacion.
"""
import numpy as np

from .core import SR

# Tension termica de los transistores del circuito, en voltios. Es la que fija en que
# nivel empieza a saturar cada celda: la no linealidad recien muerde cuando la senal
# se acerca a 1/THERMAL. Por eso `drive` abajo escala hacia esa zona.
THERMAL = 0.000025

# Cada cuanto se recalculan los coeficientes cuando el corte se mueve. El barrido de
# un filtro es lento comparado con el audio, asi que 64 muestras es transparente y
# evita un exp() por muestra.
BLOQUE_COEF = 64


# --------------------------------------------------------------- osciladores
def _fase(freq, sr=SR):
    """Fase acumulada. Se acumula y no se multiplica por t porque la frecuencia
    cambia (glide): multiplicar daria un barrido en vez de la nota."""
    return 2 * np.pi * np.cumsum(np.atleast_1d(freq)) / sr


def sierra(freq, sr=SR, armonicos=64):
    """Diente de sierra band-limited exacta. `freq` puede ser escalar o array."""
    f = np.atleast_1d(freq).astype(np.float64)
    fase = _fase(f, sr)
    y = np.zeros(len(f))
    for k in range(1, armonicos + 1):
        y += np.sin(k * fase) / k * ((f * k) < sr / 2 * 0.92)
    return y * (2 / np.pi)


def cuadrada(freq, sr=SR, armonicos=64):
    """Cuadrada band-limited exacta. Solo armonicos impares."""
    f = np.atleast_1d(freq).astype(np.float64)
    fase = _fase(f, sr)
    y = np.zeros(len(f))
    for k in range(1, armonicos + 1, 2):
        y += np.sin(k * fase) / k * ((f * k) < sr / 2 * 0.92)
    return y * (4 / np.pi)


def pulso(freq, ancho=0.5, sr=SR, armonicos=64):
    """Pulso con ancho variable, band-limited exacto. `ancho` puede ser un array.

    La serie de Fourier de un rectangulo de ciclo de trabajo d es
    (2d-1) + suma_k (4/(k*pi)) * sin(k*pi*d) * cos(k*w*t).
    En d=0,5 los armonicos pares se anulan solos y queda una cuadrada.

    El PWM (mover `ancho` con un LFO) es medio sonido analogico por si solo: el
    timbre se mueve sin que se mueva el filtro.
    """
    f = np.atleast_1d(freq).astype(np.float64)
    d = np.clip(np.broadcast_to(np.atleast_1d(ancho).astype(np.float64), f.shape), 0.02, 0.98)
    fase = _fase(f, sr)
    y = 2 * d - 1.0
    for k in range(1, armonicos + 1):
        y += (4 / (k * np.pi)) * np.sin(k * np.pi * d) * np.cos(k * fase) * ((f * k) < sr / 2 * 0.92)
    return y


def sync_duro(freq_maestro, freq_esclavo, sr=SR, oversample=16):
    """Hard sync: el esclavo reinicia su fase cada vez que el maestro cierra ciclo.

    El sync genera un salto de tension, o sea contenido infinito en frecuencia, y por
    eso en tiempo real hace falta BLEP para que no aliasee. Offline se resuelve por
    fuerza bruta y sin aproximar: se genera a 16x y se decima con filtro anti-alias.
    Es exactamente el tipo de cosa que un plugin no puede pagar y nosotros si.
    """
    fm = np.atleast_1d(freq_maestro).astype(np.float64)
    fe = np.atleast_1d(freq_esclavo).astype(np.float64)
    n = len(fm)
    fm = np.repeat(fm, oversample)
    fe = np.repeat(np.broadcast_to(fe, (n,)), oversample)
    sr_alto = sr * oversample

    fase_m = np.cumsum(fm) / sr_alto
    ciclo = np.floor(fase_m)
    # fase del esclavo, reiniciada en cada ciclo del maestro
    fase_e = np.cumsum(fe) / sr_alto
    inicio = np.zeros_like(fase_e)
    cambios = np.flatnonzero(np.diff(ciclo, prepend=ciclo[0]))
    if len(cambios):
        inicio[cambios] = fase_e[cambios]
        inicio = np.maximum.accumulate(inicio)
    y = 2.0 * ((fase_e - inicio) % 1.0) - 1.0

    from scipy.signal import resample_poly
    return resample_poly(y, 1, oversample)


def deriva(n, cents=4.0, periodo_s=11.0, semilla=0, sr=SR):
    """Deriva de afinacion, como la de un oscilador analogico.

    Es lo que mas se nota de todo lo que hay en este modulo. Un oscilador digital
    perfecto delata que es digital porque NO se mueve: dos osciladores desafinados
    con valores fijos mantienen su relacion de fase para siempre y el oido los funde.
    Uno analogico deriva, y por eso el batido entre los dos nunca es igual.

    Tres osciladores lentos incoherentes, no un LFO: un LFO se escucha como un LFO.
    """
    rng = np.random.RandomState(semilla)
    t = np.arange(n) / sr
    d = sum(rng.uniform(0.5, 1.0) * np.sin(2 * np.pi * t / (periodo_s * f) + rng.uniform(0, 6.28))
            for f in (1.0, 1.73, 2.91))
    d /= np.abs(d).max() or 1.0        # asi `cents` es la desviacion real, no una escala
    return 2.0 ** (cents * d / 1200.0)


def cluster_microtonal(f0, voces=5, paso_semitonos=0.75, sr=SR, dur=None,
                       generador=None, deriva_cents=5.0, semilla=24):
    """El racimo microtonal: voces separadas por 0,75 de semitono.

    Es el truco de afinacion del score de Dune (Zimmer, 2021), documentado en la nota
    de Sound On Sound: en vez de apilar octavas y quintas, se separan las voces en
    incrementos de tres cuartos de semitono. Al no caer en ningun intervalo de la
    escala temperada, el oido no puede leerlo como acorde y lo escucha como TEXTURA.
    Y como los parciales quedan a pocos Hz entre si, aparece un batido lento que es
    lo que da la sensacion de amenaza.

    No es un efecto: es una decision de afinacion. Ningun reverb la reemplaza.
    """
    generador = generador or sierra
    n = int(dur * sr) if dur else int(sr)
    rng = np.random.RandomState(semilla)
    y = np.zeros(n)
    for i in range(voces):
        # centrado alrededor de f0: la mitad abajo y la mitad arriba
        semis = (i - (voces - 1) / 2.0) * paso_semitonos
        f = f0 * 2.0 ** (semis / 12.0)
        f = np.full(n, f) * deriva(n, deriva_cents, periodo_s=8.0 + 3.1 * i,
                                   semilla=semilla + i, sr=sr)
        y += generador(f, sr) * rng.uniform(0.75, 1.0)
    return y / (np.abs(y).max() or 1.0)


# ------------------------------------------------------------- escalera Moog
def ladder_moog(x, corte_hz, resonancia=0.7, sr=SR, drive=1.0, oversample=2,
                compensar=True):
    """El filtro escalera del Moog, modelo Huovilainen (DAFx-04).

    Args:
      x:          senal mono, normalizada a +-1
      corte_hz:   escalar o array por muestra. La frecuencia de corte
      resonancia: 0 a 1 el rango util. La ganancia del lazo es 4*resonancia*acr, y
                  la auto-oscilacion necesita pasar de 4: con resonancia = 1 queda
                  justo abajo (marginalmente estable) y recien arriba de ~1,02 el
                  filtro oscila solo. Se permite pasarse a proposito
      drive:      cuanto se empuja hacia la zona no lineal. En 1 apenas satura;
                  arriba de 20 la escalera empieza a comprimir y a doblar la
                  resonancia, que es el sonido de un Moog exigido
      oversample: 2 en el paper. Baja el aliasing que genera la propia no linealidad

    Los polinomios de `fcr` y `acr` son los del paper: corrigen la desafinacion y la
    caida de resonancia que mete la discretizacion, y sin ellos el filtro afina mal
    a medida que sube el corte.
    """
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    corte = np.full(n, float(corte_hz)) if np.isscalar(corte_hz) else np.asarray(corte_hz, dtype=np.float64)
    corte = np.clip(corte, 20.0, sr * 0.45)

    # el drive escala hacia la zona donde tanh() deja de ser una recta
    ganancia = drive / THERMAL * 1e-5

    y = np.zeros(n)

    d0 = d1 = d2 = d3 = d4 = d5 = 0.0
    t0 = t1 = t2 = 0.0
    tune = res_quad = 0.0
    tanh = np.tanh

    for i in range(n):
        if i % BLOQUE_COEF == 0:
            # f normalizada al SR interno (el de oversampling)
            f = corte[i] / (sr * oversample)
            fcr = 1.8730 * f ** 3 + 0.4955 * f ** 2 - 0.6490 * f + 0.9988
            acr = -3.9364 * f ** 2 + 1.8409 * f + 0.9968
            tune = (1.0 - np.exp(-2 * np.pi * f * fcr)) / THERMAL
            res_quad = 4.0 * resonancia * acr

        muestra = x[i] * ganancia
        for _ in range(oversample):
            entrada = muestra - res_quad * d5
            # celda 1: la no linealidad va DENTRO, no a la salida
            d0 = s0 = d0 + tune * (tanh(entrada * THERMAL) - t0)
            t0 = tanh(s0 * THERMAL)
            d1 = s1 = d1 + tune * (t0 - t1)
            t1 = tanh(s1 * THERMAL)
            d2 = s2 = d2 + tune * (t1 - t2)
            t2 = tanh(s2 * THERMAL)
            d3 = s3 = d3 + tune * (t2 - tanh(d3 * THERMAL))
            # medio retardo: compensa la fase que mete el oversampling
            d5 = (s3 + d4) * 0.5
            d4 = s3
        y[i] = d5

    # se deshace la escala del drive: asi el filtro tiene ganancia ~1 y el nivel de
    # salida depende de la resonancia y no de cuanto se lo empujo
    y /= ganancia or 1.0

    # Compensacion de la banda pasante. Con realimentacion k la ganancia en continua
    # del lazo cae a 1/(1+k): por eso un Moog se adelgaza al abrir la resonancia. Es
    # parte del sonido, pero sin nada de makeup el filtro queda inservible para un
    # bajo. Se compensa a medias, como el "gain makeup" de los equipos reales.
    if compensar:
        y *= 1.0 + 2.4 * resonancia

    pico = np.abs(y).max()
    return y / pico if pico > 1.0 else y


def adsr(n, ataque_s, caida_s, sostenido, soltar_s, sr=SR, curva=1.4):
    """Envolvente. `curva` > 1 hace el ataque mas lento al principio, que es como se
    comporta un circuito RC de verdad."""
    a, d, s = (max(int(v * sr), 1) for v in (ataque_s, caida_s, soltar_s))
    cuerpo = max(0, n - a - d - s)
    e = np.concatenate([
        np.linspace(0, 1, a) ** curva,
        np.linspace(1, sostenido, d),
        np.full(cuerpo, sostenido),
        np.linspace(sostenido, 0, s) ** 1.8,
    ])
    return np.pad(e, (0, max(0, n - len(e))))[:n]


def glide(notas, glide_s=0.0, sr=SR, curva=0.7):
    """Convierte [(hz, segundos), ...] en una frecuencia por muestra, con portamento.

    El glide es exponencial porque el oido percibe proporciones y no diferencias: un
    barrido lineal en Hz se escucha acelerando al principio y frenando al final.
    """
    n = int(sum(dur for _, dur in notas) * sr)
    f = np.zeros(n)
    pos, anterior = 0, None
    for hz, dur in notas:
        fin = min(n, pos + int(dur * sr))
        if fin <= pos:
            break
        if anterior is None or glide_s <= 0:
            f[pos:fin] = hz
        else:
            g = min(int(glide_s * sr), fin - pos)
            f[pos:pos + g] = anterior * (hz / anterior) ** np.linspace(0, 1, g) ** curva
            f[pos + g:fin] = hz
        anterior, pos = hz, fin
    f[pos:] = anterior or 110.0
    return f


def voz_moog(notas, glide_s=2.0, detune_cents=2.5, sub=0.6, corte_base=90.0,
             corte_barrido=2000.0, resonancia=0.75, drive=28.0, sr=SR,
             env_filtro=(3.0, 4.0, 0.55, 6.0), env_amp=(2.0, 3.0, 0.85, 7.0),
             deriva_cents=1.5, pwm=0.18, pwm_periodo_s=9.0, semilla=24):
    """Una voz monofonica completa, al modo del Subsequent 25.

    Dos sierras desafinadas entre si, un sub con ancho de pulso modulado, la escalera
    y dos envolventes independientes. La de filtro va mas rapida que la de amplitud a
    proposito: el brillo entra despues del ataque, no junto, y eso es la mitad de lo
    que se reconoce como "Moog".

    Cada oscilador lleva su PROPIA deriva de afinacion. Sin eso el desafinado es un
    numero fijo, los osciladores mantienen su relacion de fase para siempre y el
    batido queda congelado: es el tell mas claro de que algo es digital.

    OJO CON LOS VALORES. Arrancaron en 7 cents de desafinado y 4,5 de deriva, y sobre
    una nota larga y GRAVE eso deja de leerse como vida y se escucha como un latido:
    medido, la voz pulsaba a 1,27 Hz en la nota Si, contra 0,97 Hz de batido teorico
    entre las dos sierras. En un bajo sostenido un pulso asi es un defecto, no textura.
    Por eso los defaults son bajos. Para material corto o agudo se pueden subir.
    """
    f = glide(notas, glide_s, sr)
    n = len(f)

    d1 = deriva(n, deriva_cents, periodo_s=11.0, semilla=semilla, sr=sr)
    d2 = deriva(n, deriva_cents, periodo_s=7.3, semilla=semilla + 1, sr=sr)
    d3 = deriva(n, deriva_cents * 0.6, periodo_s=13.7, semilla=semilla + 2, sr=sr)

    # el ancho del pulso del sub se mueve solo: timbre en movimiento sin tocar el filtro
    t = np.arange(n) / sr
    ancho = 0.5 + pwm * np.sin(2 * np.pi * t / pwm_periodo_s)

    x = (sierra(f * 2 ** (+detune_cents / 1200) * d1, sr) * 0.5
         + sierra(f * 2 ** (-detune_cents / 1200) * d2, sr) * 0.5
         + pulso(f / 2.0 * d3, ancho, sr) * sub)
    x /= np.abs(x).max() or 1.0

    ef = adsr(n, *env_filtro, sr=sr, curva=1.6)
    x = ladder_moog(x, corte_base + corte_barrido * ef ** 1.6,
                    resonancia=resonancia, drive=drive, sr=sr)
    return x * adsr(n, *env_amp, sr=sr)
