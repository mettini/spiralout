#version 330
// Capa B — pase de ACUMULACIÓN (feedback buffer + contenido nuevo).
// frame_N = warp(frame_{N-1}) * decay  +  contenido_nuevo
// El warp (zoom+rotación) ES la recursión/espiral: f(x) = transform(f(x-1)).
// Contenido nuevo = latido/retina + humo + túnel + polvo. Salida RGB float (HDR);
// el color final lo decide post.frag.

in vec2 v_uv;
out vec4 fragColor;

uniform sampler2D prevTex;     // frame anterior (feedback)
uniform vec2  u_res;
uniform float u_time;

// feedback / dinámica base
uniform float u_decay;         // 0..0.99  cuánto sobrevive del frame anterior
uniform float u_spiralZoom;    // >1.0     zoom del warp (fuga/espiral/túnel)
uniform float u_spiralRot;     // rad      rotación del warp
uniform float u_glitch;        // desplazamiento horizontal por línea (chicharreo)
uniform float u_dropout;       // 0/1 banda de dropout tipo salto de púa
uniform float u_collapse;      // 0..1 rampa de cierre (reabsorción al centro)

// elementos de contenido (manejados por el audio vía render.py)
uniform float u_pulse;         // glow radial central (latido)
uniform float u_retina;        // presencia del iris/retina (anillos + fibras)
uniform float u_iris;          // 0..1 radio de la pupila (dilata con el bass = latido)
uniform float u_smoke;         // densidad de humo (fbm con domain warping)
uniform float u_tunnel;        // intensidad de los anillos de túnel que fugan al centro
uniform float u_dust;          // polvo/specks
uniform float u_kaleidN;       // segmentos del pliegue mandala (<2 = off)
uniform float u_lightning;     // relámpagos (flash jagged) — viaje complicado de Outbound
uniform float u_rocks;         // piedras (oclusión chunky) — tropezones
uniform float u_wave;          // señal sub-42: onda/interferencia sutil en el negro (impasse)
uniform float u_horizon;       // campanas/bells → destellos lejanos en el horizonte (Outbound)

// color: u_inject=0 → monocromo (concepto A); >0 → hue sucio (concepto B)
uniform float u_inject;
uniform float u_hueBase;
uniform float u_hueSpread;
uniform float u_sat;

float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}
float vnoise(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    float a = hash21(i), b = hash21(i + vec2(1, 0));
    float c = hash21(i + vec2(0, 1)), d = hash21(i + vec2(1, 1));
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}
float fbm(vec2 p) {
    float s = 0.0, a = 0.5;
    for (int i = 0; i < 5; i++) { s += a * vnoise(p); p *= 2.0; a *= 0.5; }
    return s;
}
vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main() {
    float aspect = u_res.x / u_res.y;
    vec2 uv = v_uv;
    vec2 c = uv - 0.5; c.x *= aspect;          // centrado, corregido por aspecto
    float r = length(c);
    float ang = atan(c.y, c.x);

    // pliegue caleidoscópico (mandala): se APAGA durante el colapso (si no, deja
    // visible la línea de espejo horizontal en y=0.5). keff = N gateado por collapse.
    // CUANTIZAMOS a entero: con N fraccionario las costuras del fold no tilan
    // y aparece una franja horizontal visible (bug del outbound python).
    // Además rotamos la fase angular con u_time → las costuras restantes derivan
    // y se promedian en el feedback en vez de quedar fijas en ang=0/π.
    float keff = floor(u_kaleidN * (1.0 - smoothstep(0.05, 0.45, u_collapse)) + 0.5);
    float kphase = u_time * 0.13;     // deriva lenta del eje del kaleidoscopio
    float af = ang;
    if (keff >= 2.0) {
        float seg = 6.2831853 / keff;
        af = abs(mod(ang - kphase, seg) - 0.5 * seg);
    }
    vec2 cf = vec2(cos(af), sin(af)) * r;

    // --- feedback: warp espiral del frame anterior ---
    // en el colapso: ESPIRAL/alcantarilla — gira fuerte y se va por el centro
    float rot = u_spiralRot + u_collapse * u_collapse * 0.13;     // acelera (cuadrático)
    float zoom = u_spiralZoom + u_collapse * 0.07;
    mat2 R = mat2(cos(rot), -sin(rot), sin(rot), cos(rot));
    vec2 cc = uv - 0.5;
    vec2 warped = (R * cc) / zoom + 0.5;
    // pliegue caleidoscópico del FEEDBACK → la imagen entera se vuelve mandala/fractal
    // Misma fase rotante kphase → coherente con el fold de coordenadas de arriba.
    if (keff >= 2.0) {
        vec2 wc = warped - 0.5;
        float wseg = 6.2831853 / keff;
        float wa = abs(mod(atan(wc.y, wc.x) - kphase, wseg) - 0.5 * wseg);
        warped = 0.5 + vec2(cos(wa), sin(wa)) * length(wc);
    }
    // glitch: desplazamiento horizontal por bandas (chicharreo) — sutil y gateado,
    // si no, smear-ea todo en franjas horizontales y tapa la estructura radial.
    float line = floor(uv.y * u_res.y * 0.5);
    float g = (hash21(vec2(line, floor(u_time * 18.0))) - 0.5) * u_glitch * 0.018;
    warped.x += g;
    vec3 prev = texture(prevTex, warped).rgb * u_decay;
    // dropout: banda oscura puntual tipo salto de púa
    float drop = step(0.5, u_dropout) * step(0.6, hash21(vec2(line, floor(u_time * 60.0))));
    prev *= (1.0 - 0.8 * drop);

    // --- contenido nuevo ---
    // 1) latido central
    float pulse = u_pulse * exp(-r * 5.0);

    // 2) RETINA / iris latiendo: anillo gaussiano en el radio u_iris (la pupila),
    //    + fibras radiales plegables (textura del iris/mandala). dilata con el sub-bass.
    float ringEdge = exp(-pow((r - u_iris) * 9.0, 2.0));            // borde de la pupila
    float fibers = 0.5 + 0.5 * cos(af * 34.0 + 6.0 * vnoise(vec2(af * 4.0, r * 6.0)));
    fibers *= smoothstep(u_iris, u_iris + 0.28, r) * exp(-r * 1.4); // solo fuera de la pupila
    float retina = u_retina * (ringEdge + 0.35 * fibers);

    // 3) HUMO: fbm con domain warping (wisps que se pliegan, no esferas)
    vec2 q = vec2(fbm(cf * 2.2 + vec2(u_time * 0.05, 0.0)),
                  fbm(cf * 2.2 + vec2(5.2, -u_time * 0.04)));
    float smoke = u_smoke * fbm(cf * 3.0 + 1.6 * q - vec2(0.0, u_time * 0.03));
    smoke *= mix(0.45, 1.0, smoothstep(1.4, 0.0, r));              // llena el cuadro (nubes)

    // 4) TÚNEL: anillos en coordenadas polares que fugan hacia el centro
    float depth = 1.0 / (r + 0.12);
    float rings = 0.5 + 0.5 * sin(depth * 7.0 - u_time * 1.8);
    float tunnel = u_tunnel * smoothstep(0.55, 1.0, rings) * (0.22 / (r + 0.14));

    // 5) polvo: specks que derivan; bajo zoom alto se estiran en streaks (slit-scan)
    vec2 dcoord = cf * (8.0 + 6.0 * u_collapse) + vec2(cos(af), sin(af)) * u_time * 0.5;
    float speck = step(0.93, vnoise(dcoord * 6.0 + vec2(0.0, -u_time)));
    float dust = u_dust * speck * exp(-r * 1.5);

    // 6) RELÁMPAGO: rama brillante jagged en una posición aleatoria por flash
    float boltX = (hash21(vec2(floor(u_time * 9.0), 3.0)) - 0.5) * 1.4;
    float jag = 0.07 * (fbm(vec2(r * 7.0, floor(u_time * 9.0))) - 0.5);
    float bolt = u_lightning * smoothstep(0.045, 0.0, abs(c.x - boltX - jag));

    // 7) SEÑAL sub-42: onda de osciloscopio fina + interferencia tenue (impasse entre temas)
    float wave = 0.0;
    if (u_wave > 0.001) {
        float yl = 0.5 + 0.05 * u_wave * sin(uv.x * 34.0 - u_time * 1.5)
                       * sin(uv.x * 6.0 + u_time * 0.7);
        wave  = (0.5 + 0.5 * u_wave) * smoothstep(0.010, 0.0, abs(uv.y - yl));   // línea
        wave += 0.12 * u_wave * (0.5 + 0.5 * sin(uv.y * u_res.y * 0.25 - u_time * 5.0)); // interferencia
        wave *= 0.6;                                                             // sutil
    }

    // 8) HORIZONTE: banda de luz baja; las campanas encienden faros/destellos lejanos
    float horizon = 0.0;
    if (u_horizon > 0.001) {
        float band = exp(-pow((v_uv.y - 0.26) * 15.0, 2.0));          // tercio inferior
        float beacons = step(0.90, hash21(vec2(floor(v_uv.x * 11.0), floor(u_time * 1.5))));
        float ripple = 0.55 + 0.45 * sin(v_uv.x * 16.0 - u_time * 1.2);
        horizon = u_horizon * band * (0.35 * ripple + 0.65 * beacons);
    }

    float newc = (pulse + retina + smoke + tunnel + dust + bolt + wave + horizon)
                 * (1.0 - 0.5 * u_collapse);

    // tinte: monocromo (A) o hue sucio cíclico (B).
    // OJO: `ang` (de atan2) salta de +π a -π en el eje horizontal izquierdo →
    // si lo usás directo en hue, aparece una franja rosa visible en ese eje
    // (bug detectado en outbound). Usamos cos(ang) que ES continuo en ±π.
    float angCyc = 0.5 + 0.5 * cos(ang);                                                  // 0..1 continuo
    float hue = u_hueBase + r * u_hueSpread + 0.10 * (angCyc - 0.5) * u_hueSpread + 0.05 * sin(u_time * 0.05);
    vec3 tint = mix(vec3(1.0), hsv2rgb(vec3(hue, u_sat, 1.0)), u_inject);

    vec3 col = prev + tint * newc;
    // ROCAS: oclusión chunky que se atraviesa (tropezones, dificultad en el andar)
    float rockMask = u_rocks * smoothstep(0.55, 0.85,
                                          vnoise(cf * 2.5 + vec2(-u_time * 0.25, u_time * 0.05)));
    col *= (1.0 - 0.65 * rockMask);
    col = clamp(col, 0.0, 3.0);
    fragColor = vec4(col, 1.0);
}
