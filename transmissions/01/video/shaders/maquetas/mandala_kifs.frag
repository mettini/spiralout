#version 330
// =============================================================================
//  Mandala — GLSL Kaleidoscopic IFS (Iterated Function System) 2D
// =============================================================================
//  Técnica clásica de "Knighty" en fractalforums.com. KIFS = iteración de fold
//  (abs) + transformación afín (escala + rotación + traslación). Cada iteración
//  refina detalle del fractal. Distance estimate guía el color/shading.
//
//  Para mandala 2D: folding angular (kaleid de N segmentos) + KIFS radial.
//  Resultado: simetría rotacional + detalle fractal recursivo = mandala PRO.
//
//  Paleta: magenta-violeta + dorado halo + black background. NO verde phosphor.

in vec2 v_uv;
out vec4 fragColor;

uniform vec2  u_res;
uniform float u_time;
uniform float u_approach;     // 0..1 — el mandala se "abre" con el tiempo

// ---- noise (para texturizar el resultado) -----------------------------------
float hash(vec2 p) {
    p = fract(p * vec2(443.897, 441.423));
    p += dot(p, p.yx + 19.19);
    return fract(p.x * p.y);
}
float hash3(vec3 p) {
    return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453);
}
float vnoise3(vec3 p) {
    vec3 i = floor(p), f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(
        mix(mix(hash3(i + vec3(0,0,0)), hash3(i + vec3(1,0,0)), f.x),
            mix(hash3(i + vec3(0,1,0)), hash3(i + vec3(1,1,0)), f.x), f.y),
        mix(mix(hash3(i + vec3(0,0,1)), hash3(i + vec3(1,0,1)), f.x),
            mix(hash3(i + vec3(0,1,1)), hash3(i + vec3(1,1,1)), f.x), f.y),
        f.z);
}
float fbm3(vec3 p) {
    float s = 0.0, a = 0.5;
    for (int i = 0; i < 4; i++) { s += a * vnoise3(p); p *= 2.1; a *= 0.5; }
    return s;
}

// ---- KIFS 2D (Knighty's recursive folding) ----------------------------------
float kifs(vec2 p) {
    float scale = 1.45;                       // factor de escala por iteración
    float trap = 1e10;                        // orbit trap (distance acumulado)
    for (int i = 0; i < 7; i++) {             // 7 iteraciones = detalle profundo
        // 1) Fold: abs (refleja al primer cuadrante)
        p = abs(p);
        // 2) Rotate (rotación leve por iteración + tiempo)
        float a = 0.35 + u_time * 0.020 + float(i) * 0.05;
        float ca = cos(a), sa = sin(a);
        p = mat2(ca, -sa, sa, ca) * p;
        // 3) Translate (desplazar el origen — el "offset" característico del KIFS)
        p -= vec2(0.55, 0.30);
        // 4) Scale up
        p *= scale;
        // 5) Orbit trap: registrar mínima distancia a (0,0) durante la iteración
        trap = min(trap, length(p));
    }
    return trap;
}

// ---- kaleid angular wrapper -------------------------------------------------
//  Antes del KIFS, envolvemos el plano en N segmentos de simetría.
vec2 kaleid(vec2 p, float n) {
    float r = length(p);
    float a = atan(p.y, p.x);
    float seg = 6.2831853 / n;
    a = abs(mod(a + 0.5 * seg, seg) - 0.5 * seg);
    return vec2(cos(a), sin(a)) * r;
}

void main() {
    vec2 uv = v_uv;
    vec2 p = (uv * 2.0 - 1.0);
    p.x *= u_res.x / u_res.y;

    // El mandala "emerge" — al principio chico (escala alta = zoom out),
    // crece a tamaño completo con u_approach.
    float zoom = mix(2.5, 0.8, u_approach);
    p *= zoom;

    // Simetría octogonal (8 segmentos). Para mandala más cerrado: aumentar N.
    vec2 kp = kaleid(p, 8.0);

    // KIFS sobre la coordenada kaleidoscopiada
    float d = kifs(kp);

    // ---- Coloreado por distance ---------------------------------------------
    // 3 colores principales:
    //   centro (anillo bright magenta-pink)
    //   halo medio (violet)
    //   borde (gold)
    vec3 cCenter = vec3(0.92, 0.55, 0.78);    // magenta-pink
    vec3 cMid    = vec3(0.55, 0.30, 0.72);    // violet
    vec3 cEdge   = vec3(0.95, 0.78, 0.35);    // gold

    // Mapeo de la orbit-trap distance al color
    float td = clamp(d * 0.9, 0.0, 1.5);
    vec3 col = mix(cCenter, cMid, smoothstep(0.0, 0.7, td));
    col = mix(col, cEdge, smoothstep(0.7, 1.4, td));

    // Banda brillante donde d es mínimo (centro del mandala)
    float core = exp(-d * d * 3.0);
    col += vec3(1.0, 0.85, 0.55) * core * 0.45;

    // Atenuación radial — el mandala se "centra"
    float r = length(uv - 0.5);
    col *= 1.0 - smoothstep(0.35, 0.65, r) * 0.55;

    // Painterly noise overlay
    float painterly = fbm3(vec3(uv * 5.0, u_time * 0.04));
    col *= mix(0.88, 1.15, painterly);

    // Chromatic aberration sutil
    float lum = dot(col, vec3(0.299, 0.587, 0.114));
    float ca = smoothstep(0.6, 0.95, lum) * 0.025;
    col.r *= 1.0 + ca;
    col.b *= 1.0 - ca;

    // Pseudo-bloom
    col += col * smoothstep(0.55, 0.95, lum) * 0.20;

    // Vignette
    col *= 1.0 - 0.38 * r;

    // Grain
    col += (hash(uv * u_res + u_time) - 0.5) * 0.030;

    col = clamp(col, 0.0, 1.0);
    col = pow(col, vec3(0.93));

    fragColor = vec4(col, 1.0);
}
