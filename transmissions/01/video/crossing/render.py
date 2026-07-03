#!/usr/bin/env python3.10
"""Crossing — Turrell v3: verde anegrado + sombra-detrás-de-capas reactiva.

Construcción manual (no agente). Cambios sobre v2:
  - Paleta TODA en verde anegrado / negro-verdoso. CERO blanco brillante.
  - Sombra OFF-CENTER, no centrada. Posición ~(0.58, 0.40), drift sutil.
  - Dos capas de sombra (apilada) para sentir "atrás de capas".
  - Tamaño y vibración de la sombra MANEJADOS por el control track del audio:
        size  ← rms_low  (la "peludez" del medio)  → en min 3 crece, devora
        jitter ← flux    (turbulencia espectral)   → tiembla cuando se agita
        opacity ← (low + flux) suaves              → presencia
  - Evento de "distorsión de luz" cuando aparece el `rms_air` (bells/echoes
    en min ~10:30–12:10). Glow soft en una esquina superior, sin flash.
  - Grano hash con seed por frame: ruido espacialmente plano, sin patrón
    hex/IGN. Encode 10-bit yuv420p10le sin dither en shader → libre de
    banding y libre de "interferencia".
  - El campo de color hace una micro-variación durante el cruce de
    heliopausa (~6:00–7:30) — un poco más oscuro/saturado y vuelve.

Uso:
    .venv/bin/python render.py --pretest    # 3 frames de test: 0s, 210s, 660s
    .venv/bin/python render.py              # render completo 13:00 4K
    .venv/bin/python render.py --seconds 30 # corto para iterar
    .venv/bin/python render.py --no-audio   # sin mux
"""
import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

import moderngl
import numpy as np
import soundfile as sf
from PIL import Image

# ───── Paths ────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent
OUT_MP4 = HERE / "final_4k.mp4"
REPO = HERE.parents[3]
AUDIO_WAV = REPO / "transmissions/01/release/masters/02_crossing_master.wav"
CONTROL_NPZ = REPO / "transmissions/01/video/control/crossing.npz"

# ───── Targets ──────────────────────────────────────────────────────────
W, H = 3840, 2160
FPS = 24
DURATION_S = 13 * 60.0
N_FRAMES = int(round(DURATION_S * FPS))

# ───── Paleta: verde anegrado (drowned green / petroleum) ────────────────
# Mantenida TODA en negro-verdoso. La micro-variación cromática es para que
# el ojo "respire" diferente en cada zona del track, no para iluminar.
# RGB en 0..1 (linear-ish sRGB; el encoder se ocupa del resto).
# Estaciones por tiempo (minutos):
PALETTE_STATIONS = [
    # (t_min,  R,      G,      B)
    # v3.19: brillo subido en primera mitad ("se ve muy oscuro").
    # Stations 0-3 min ~+40%, 7.30+ ~+15%. Julia (4.30, 6.30) sin tocar.
    ( 0.00,   0.068,  0.160,  0.092),  # +40% brillo (era 0.048, 0.115, 0.066)
    ( 1.50,   0.077,  0.180,  0.102),  # +40%
    ( 3.00,   0.060,  0.150,  0.085),  # +43%
    ( 4.30,   0.036,  0.095,  0.054),  # Julia start — sin tocar
    ( 5.30,   0.057,  0.132,  0.076),  # mid julia — sin tocar
    ( 6.30,   0.031,  0.088,  0.050),  # Julia end — sin tocar
    ( 7.30,   0.078,  0.170,  0.098),  # +20% (transición a liso final)
    ( 9.30,   0.078,  0.165,  0.098),  # +15%
    (10.50,   0.060,  0.142,  0.082),  # +15%
    (12.00,   0.054,  0.130,  0.075),  # +12%
    (13.00,   0.033,  0.090,  0.052),  # ending — sin tocar
]

# ───── Sombra: trayectoria off-center ───────────────────────────────────
# Idea: la sombra ENTRA por arriba-izquierda, baja diagonalmente hasta una
# posición ligeramente desplazada del centro (arriba-derecha), pausa en el
# umbral, retrocede por OTRO eje. Nunca pasa por el centro exacto.
# Coordenadas en (x, y) en 0..1; y=0 es arriba (UV invertido).
SHADOW_TRAJ = [
    # (t_min, x,     y)
    # v3.19: amplitud DRAMÁTICA en primera mitad — la sombra debe verse
    # MOVIÉNDOSE en los primeros 2 minutos. Antes 0.30 → 0.46 era apenas
    # perceptible. Ahora arranca lejos en upper-left y cruza diagonalmente.
    ( 0.00, 0.15,  0.15),    # esquina arriba-izq EXTREMA
    ( 0.50, 0.20,  0.18),
    ( 1.00, 0.28,  0.22),
    ( 1.50, 0.36,  0.27),
    ( 2.00, 0.44,  0.32),
    ( 2.50, 0.50,  0.36),    # llega cerca del Julia peak
    ( 4.30, 0.56,  0.40),    # peludo peak: cerca del centro-arriba-derecha
    ( 6.30, 0.58,  0.42),    # umbral: ligeramente off-center
    ( 8.00, 0.60,  0.44),
    (10.50, 0.66,  0.50),    # entrada bells
    (13.00, 0.74,  0.58),    # sale hacia abajo-derecha
]

# Opacidad base (sin reactividad). Se MULTIPLICA por (1 + low + flux)
# para la presencia dinámica.
SHADOW_OP_KEYS = [
    # Silueta MÁS visible al inicio (compensa s2 reducida)
    ( 0.00, 0.55),
    ( 1.50, 0.60),
    ( 3.00, 0.65),
    ( 4.30, 0.72),   # PEAK peludo
    ( 5.30, 0.52),
    ( 6.30, 0.58),
    ( 8.00, 0.48),
    (10.50, 0.38),
    (13.00, 0.22),
]

# SILUETA: body + head (figura humana abstracta).
# Body = ellipse VERTICAL (más alta que ancha). Head = circle pequeño arriba.
SHADOW_R_BASE     = 0.20        # half-y del body (alto total ~40% del frame)
SHADOW_FALLOFF    = 0.50        # bordes blandos pero leíbles
SHADOW_ECC        = 0.70        # ecc alta = body taller (vertical)
SHADOW_ROT_DEG    = -3.0        # leve inclinación

# Head: encima del body. Más chica + más circular.
SHADOW_HEAD_R     = 0.085
SHADOW_HEAD_FALLOFF = 0.45
SHADOW_HEAD_OFFSET = (0.0, -0.22)   # arriba del centro del body (UV: y- = arriba en saved)

# Segunda capa (atrás): atmósfera blanda, mucho más grande
SHADOW2_R_BASE  = 0.55
SHADOW2_FALLOFF = 1.40
SHADOW2_OFFSET  = (0.04, 0.03)
SHADOW2_OP_MULT = 0.18    # reducido — elimina overlay de gradiente que creaba ondas

# ───── Evento de luz (bells / aire) ─────────────────────────────────────
# Activo durante 10:30–12:10. Es un GLOW SOFT en una esquina superior-
# izquierda. NO un flash. Intensidad guiada por rms_air suavizado.
LIGHT_POS = (0.13, 0.82)           # bells: esquina superior-izquierda
LIGHT_R = 0.50
LIGHT_FALLOFF = 1.6
LIGHT_TINT = (0.85, 1.00, 0.55)
LIGHT_PEAK = 0.18                   # bells

# Voyager light: esquina superior-derecha, MÁS sutil que bells
VOYAGER_POS = (0.87, 0.82)
VOYAGER_PEAK = 0.10
# Momentos voyager (en minutos): cada uno con ventana Gaussian ±5s
VOYAGER_MOMENTS_MIN = [
    0.27,    # 0:16 (user confirmed)
    0.917,   # 0:55 (user confirmed echo)
    1.998,   # 1:59
    2.258,   # 2:15
    3.098,   # 3:05
    4.754,   # 4:45
    7.325,   # 7:19
    7.590,   # 7:35
    8.423,   # 8:25
    9.255,   # 9:15
]

# Ventana temporal del evento (clamp adicional, además de air):
LIGHT_T_WINDOW = (10.30, 12.20)    # minutos

# ───── Shader ───────────────────────────────────────────────────────────
VERTEX = """
#version 330 core
in vec2 in_pos;
out vec2 v_uv;
void main() {
    v_uv = (in_pos + 1.0) * 0.5;
    gl_Position = vec4(in_pos, 0.0, 1.0);
}
"""

FRAGMENT = """
#version 330 core
in vec2 v_uv;
out vec4 fragColor;

uniform vec3  u_color;
uniform float u_aspect;

// shadow primaria
uniform vec2  u_s1_pos;
uniform float u_s1_op;
uniform float u_s1_r;
uniform float u_s1_falloff;
uniform float u_s1_ecc;
uniform float u_s1_rot;

// Head de la silueta
uniform vec2  u_head_pos;
uniform float u_head_r;
uniform float u_head_falloff;

// Fondo dinámico: pesos de phases (liso + nebula + fractales)
uniform float u_w_liso;
uniform float u_w_nebula;
uniform float u_w_fractals;
uniform float u_time;
uniform float u_peludo;       // 0..1, peludo intensity (rms_low smoothed)
uniform float u_jitter_freq;  // hz para jitter del shadow durante peludo

// shadow secundaria (capa atrás)
uniform vec2  u_s2_pos;
uniform float u_s2_op;
uniform float u_s2_r;
uniform float u_s2_falloff;

// light event (bells - upper-left)
uniform vec2  u_lt_pos;
uniform float u_lt_intensity;
uniform float u_lt_r;
uniform float u_lt_falloff;
uniform vec3  u_lt_tint;

// voyager light event (upper-right, otros momentos)
uniform vec2  u_lt2_pos;
uniform float u_lt2_intensity;

// fade in/out global
uniform float u_fade;

uniform float u_grain_amt;
uniform float u_seed;

float hash21(vec2 p) {
    p = fract(p * vec2(443.8975, 397.2973));
    p += dot(p, p.yx + 19.19);
    return fract((p.x + p.y) * p.x);
}

// Value noise + FBM (renombrado vNoise para no chocar con builtin noise2)
float vNoise(vec2 pp) {
    vec2 ip = floor(pp);
    vec2 fp = fract(pp);
    vec2 sf = fp * fp * (vec2(3.0) - vec2(2.0) * fp);
    float a = hash21(ip);
    float b = hash21(ip + vec2(1.0, 0.0));
    float c = hash21(ip + vec2(0.0, 1.0));
    float d = hash21(ip + vec2(1.0, 1.0));
    float ab = a + (b - a) * sf.x;
    float cd = c + (d - c) * sf.x;
    return ab + (cd - ab) * sf.y;
}

float fbm2(vec2 pp) {
    float acc = 0.0;
    float amp = 0.5;
    vec2 q = pp;
    float v = 0.0;
    for (int oct = 0; oct < 2; oct = oct + 1) {
        v = vNoise(q);
        acc = acc + amp * v;
        q = q * 2.0;
        amp = amp * 0.5;
    }
    return acc;
}

// ─── Julia FLUIDO v4 ────────────────────────────────────────────────────
// El escape-time (iter count + cutoff MAX_ITER + binario dentro/fuera) es
// CUANTIZADO: a medida que c se mueve, los level-sets barren pixeles y el
// techo de iteraciones se desplaza → POPPING (los "saltos" y el "fade-in
// pedorro" que reportó el user). Solución: campos analíticos CONTINUOS.
//   - Distance Estimation (DE): distancia al borde vía la derivada. Campo
//     real suave en TODO el plano (dentro, fuera, borde). Sin cliff.
//   - Orbit traps: distancia mínima de la órbita a una forma → estructura
//     orgánica continua, animable. Da vida al interior, no solo al borde.
// Además: exponente d animado (z^d) → muta de simetría continuo; y c en el
// INTERIOR de la cardioide → Julia siempre conexo, sin estallido topológico.
vec2 cmul(vec2 a, vec2 b) { return vec2(a.x*b.x - a.y*b.y, a.x*b.y + a.y*b.x); }
// Julia escape-time — el look "delirio cósmico" dendrítico que el user quiere
// CONSERVAR. MAX_ITER alto + smooth iteration count para bordes limpios.
float juliaIter(vec2 z, vec2 c) {
    const int MAX_ITER = 90;
    float bailout = 4.0;
    int it = 0;
    for (int i = 0; i < MAX_ITER; i = i + 1) {
        if (dot(z, z) > bailout) break;
        z = vec2(z.x*z.x - z.y*z.y, 2.0*z.x*z.y) + c;
        it = i;
    }
    float fi = float(it);
    if (it < MAX_ITER - 1) {
        float log_z = log(dot(z, z)) * 0.5;
        float nu = log(log_z / log(2.0)) / log(2.0);
        fi = fi + 1.0 - nu;
    }
    return fi / float(MAX_ITER);
}

float fbm4(vec2 pp) {
    float acc = 0.0;
    float amp = 0.5;
    vec2 q = pp;
    float v = 0.0;
    for (int oct = 0; oct < 4; oct = oct + 1) {
        v = vNoise(q);
        acc = acc + amp * v;
        q = q * 2.0;
        amp = amp * 0.5;
    }
    return acc;
}

// Sombra elíptica con falloff GAUSSIANO — curva C∞, sin puntos de inflexión.
// Reemplaza smoothstep (cuyas inflexiones se ven como "layers/olas" en
// gradientes lentos a baja amplitud). Calibrado para que a dist=r el peso
// sea ~0.95 y a dist=r*(1+falloff) sea ~0.05 (mismo footprint que smoothstep).
float ellipse_soft(vec2 uv, vec2 pos, float r, float falloff, float ecc, float rot, float aspect) {
    vec2 d = uv - pos;
    d.x *= aspect;
    if (abs(rot) > 1e-4) {
        float cs = cos(rot), sn = sin(rot);
        d = vec2(cs * d.x - sn * d.y, sn * d.x + cs * d.y);
    }
    float ey = 1.0 + ecc;
    d.y *= 1.0 / ey;
    float dist = length(d);
    // sigma calibrado: el footprint efectivo (peso > 0.05) llega a ~r*(1+falloff)
    float sigma = r * (0.5 + falloff * 0.5);
    return exp(-(dist * dist) / (2.0 * sigma * sigma));
}

void main() {
    vec2 uv = v_uv;

    // 1) campo base — combinación de 3 phases: liso, nebula, fractales
    float vgrad = mix(0.95, 1.05, uv.y);
    vec3 base_color = u_color * vgrad;

    // Nebula: FBM low-freq, advectado. Humo en movimiento.
    float neb = fbm2(uv * 4.5 + vec2(u_time * 0.18, u_time * 0.12));
    vec3 col_neb = base_color * (0.50 + 1.00 * neb);

    // Fractales: Julia v4 — look v3 (dragones+caracoles) con 2 fixes:
    //  (1) SIN CORTES: el path de v3 era la cardioide en el BORDE (|w|=1), que
    //      es la región que estalla (cuts). Ahora |w|=0.96 (apenas adentro) →
    //      mismo barrido angular (mismos dragones) pero CONEXO → sin estallidos.
    //  (2) SIN DIFUMINADO: bandas de contorno MARCADAS (las "vueltas" de la
    //      iteración) revelan el espiral natural en vez de un relleno plano.
    vec3 col_frac = base_color * 0.35;
    if (u_w_fractals > 0.001) {
        float jt = u_time * 0.05;
        float ja = jt * 1.4;
        vec2 w = 0.96 * vec2(cos(ja), sin(ja));            // cardioide APENAS adentro
        vec2 julia_c = 0.5 * w - 0.25 * cmul(w, w);
        vec2 z = (uv - vec2(0.5)) * vec2(u_aspect, 1.0) * 3.0;
        vec2 dz = vec2(1.0, 0.0);
        float m2 = dot(z, z); float tmin = 1e9; int it = 0;
        const int MAXI = 160;
        for (int k = 0; k < MAXI; k = k + 1) {
            if (m2 > 1e10) break;
            dz = 2.0 * cmul(z, dz);
            z = cmul(z, z) + julia_c;
            m2 = dot(z, z); tmin = min(tmin, m2); it = k + 1;
        }
        vec3 julia_bright = vec3(0.18, 0.42, 0.26);
        vec3 julia_dark   = base_color * 0.35;
        vec3 col;
        if (m2 > 1e10) {
            // EXTERIOR (escapó): bandas fuertes sobre la iteración suave →
            // revelan el espiral enroscándose. Borde nítido con DE.
            float sn = float(it) - log2(log2(m2)) + 4.0;
            float band = 0.5 + 0.5 * cos(6.28318 * sn * 0.55);
            float frac = clamp(sn / float(MAXI), 0.0, 1.0);
            col = mix(julia_dark, julia_bright, pow(frac, 0.55));
            col *= 0.50 + 0.50 * band;                       // bandas MARCADAS
            float de = 0.5 * sqrt(m2 / dot(dz, dz)) * log(m2);
            col = mix(julia_bright * 1.08, col, smoothstep(0.0, 0.0035, de));
        } else {
            // INTERIOR (filled): bandas por orbit-trap (min |z|) → estructura
            // interna marcada, no relleno plano.
            float band = 0.5 + 0.5 * cos(6.28318 * sqrt(tmin) * 7.0);
            col = julia_bright * (0.50 + 0.50 * band);
        }
        col_frac = col;
    }

    // Mezcla por pesos: cada phase tiene su color propio.
    float wsum = u_w_liso + u_w_nebula + u_w_fractals + 1e-6;
    vec3 base = (base_color * u_w_liso + col_neb * u_w_nebula + col_frac * u_w_fractals) / wsum;

    vec3 col = base;

    // 2) sombra secundaria (atrás) — capa de atmósfera (NO afectada por peludo distortion)
    float s2 = ellipse_soft(uv, u_s2_pos, u_s2_r, u_s2_falloff, u_s1_ecc * 0.7, u_s1_rot * 0.5, u_aspect);
    vec3 dark2 = base * 0.72;
    col = mix(col, dark2, s2 * u_s2_op);

    // 3) silueta = body + head con DISTORSIÓN PINCHUDA durante peludo
    //    Perturbo el UV input con FBM de alta freq antes de calcular silueta.
    //    Amplitud * u_peludo + jitter_freq * tiempo
    vec2 uv_distorted = uv;
    if (u_peludo > 0.01) {
        vec2 noise_in = uv * 14.0 + vec2(u_time * u_jitter_freq, u_time * u_jitter_freq * 0.93);
        float nx = fbm2(noise_in) - 0.5;
        float ny = fbm2(noise_in + vec2(43.7, 17.3)) - 0.5;
        // amplitud crece con peludo — pinchudo VIOLENTO
        float amp = 0.055 * u_peludo;
        uv_distorted = uv + vec2(nx, ny) * amp;
    }

    float body = ellipse_soft(uv_distorted, u_s1_pos, u_s1_r, u_s1_falloff, u_s1_ecc, u_s1_rot, u_aspect);
    float head = ellipse_soft(uv_distorted, u_head_pos, u_head_r, u_head_falloff, 0.05, 0.0, u_aspect);
    float silhouette = 1.0 - (1.0 - body) * (1.0 - head);
    vec3 dark1 = base * 0.40;
    col = mix(col, dark1, silhouette * u_s1_op);

    // 4a) bells light upper-left
    if (u_lt_intensity > 0.001) {
        float lt = ellipse_soft(uv, u_lt_pos, u_lt_r, u_lt_falloff, 0.15, 0.0, u_aspect);
        col += lt * u_lt_intensity * u_lt_tint;
    }
    // 4b) voyager light upper-right (más sutil)
    if (u_lt2_intensity > 0.001) {
        float lt2 = ellipse_soft(uv, u_lt2_pos, u_lt_r, u_lt_falloff, 0.15, 0.0, u_aspect);
        col += lt2 * u_lt2_intensity * u_lt_tint;
    }

    // v3.21: atmósfera estructural anti-banding NATIVA (reemplaza el fog
    // plate en post del v2). Pesada hacia los DARKS, donde el VP9 10Mbps
    // real de YouTube banda (medido 2026-06-12 sobre el archivo servido).
    // Baja frecuencia (~500px) + media (~100px): lo que los P-frames
    // trackean y los DC blocks no pueden aplanar.
    float lum_a = dot(col, vec3(0.299, 0.587, 0.114));
    vec2 auv = uv * vec2(u_aspect, 1.0);
    float a1 = fbm2(auv * 6.5 + vec2(u_time * 0.014, -u_time * 0.009));
    float a2 = fbm2(auv * 23.0 + vec2(-u_time * 0.020, u_time * 0.016));
    float am = (a1 - 0.5) * 0.55 + (a2 - 0.5) * 0.45;
    float aamp = mix(0.22, 0.05, smoothstep(0.04, 0.30, lum_a));
    col *= 1.0 + am * aamp;

    // 5) vignette MUY suave, para no exagerar el contenedor
    vec2 vc = uv - 0.5;
    vc.x *= u_aspect;
    float rv = length(vc);
    float vig = 1.0 - smoothstep(0.42, 1.05, rv) * 0.18;
    col *= vig;

    // v3.18 FIX CRÍTICO: u_seed alto rompe hash21 por pérdida de precisión
    // float32 (mult * 443 = 1e8 → fract garbage). Pre-fract mantiene rango precisado.
    float s = fract(u_seed * 0.000312345);

    // v3.21 ANTI GOP-PUMPING (mismo fix que outbound v20): el ruido
    // re-seedeado POR FRAME se degrada en los P-frames de YouTube y cada
    // keyframe lo resetea → pop periódico. Ruido ESTÁTICO y mínimo: los
    // P-frames lo trackean perfecto, no hay nada que resetear.
    float n = hash21(gl_FragCoord.xy + vec2(137.0, 234.0));
    float grain = (n - 0.5) * 2.0 * u_grain_amt;
    float shadow_boost = 1.0 + (1.0 - dot(col, vec3(0.33))) * 0.5;
    col += grain * shadow_boost;

    // v3.20: gamma 0.78 (era 0.75 - too bright reported). Balance entre
    // visibilidad TV y no over-bright. 0.05 → 0.103.
    col = pow(max(col, vec3(0.0)), vec3(0.78));
    // v3.21: apertura de rango en darks (hereda la curva del post v2,
    // ahora nativa). Más pendiente = menos px por nivel = menos bandas.
    float cmv = 0.075;
    col = (col - cmv) * 1.22 + cmv;
    // v3.21: dither estático luma-only ±1.5/255 (suficiente para el master
    // 10-bit; el anti-banding real es la atmósfera estructural de arriba).
    float dl = fract(sin(dot(gl_FragCoord.xy + vec2(137.0, 91.0), vec2(12.9898, 78.233))) * 43758.5453);
    col += vec3((dl - 0.5) * 3.0 / 255.0);

    // fade in/out global a negro absoluto
    col *= u_fade;

    col = clamp(col, 0.0, 1.0);
    fragColor = vec4(col, 1.0);
}
"""

# ───── Catmull-Rom utility ──────────────────────────────────────────────
def _cr(p0, p1, p2, p3, t):
    p0 = np.asarray(p0, dtype=np.float64)
    p1 = np.asarray(p1, dtype=np.float64)
    p2 = np.asarray(p2, dtype=np.float64)
    p3 = np.asarray(p3, dtype=np.float64)
    t2 = t * t
    t3 = t2 * t
    return 0.5 * (
        2 * p1
        + (-p0 + p2) * t
        + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
        + (-p0 + 3 * p1 - 3 * p2 + p3) * t3
    )

def cr_eval(keys, t):
    ts = [k[0] for k in keys]
    vs = [k[1:] if len(k) > 2 else (k[1],) for k in keys]
    n = len(ts)
    if t <= ts[0]:
        v = vs[0]
        return np.asarray(v, dtype=np.float64) if len(v) > 1 else float(v[0])
    if t >= ts[-1]:
        v = vs[-1]
        return np.asarray(v, dtype=np.float64) if len(v) > 1 else float(v[0])
    i = 0
    while i < n - 1 and not (ts[i] <= t < ts[i + 1]):
        i += 1
    if i >= n - 1:
        v = vs[-1]
        return np.asarray(v, dtype=np.float64) if len(v) > 1 else float(v[0])
    i0 = max(i - 1, 0); i1 = i; i2 = i + 1; i3 = min(i + 2, n - 1)
    p0, p1, p2, p3 = vs[i0], vs[i1], vs[i2], vs[i3]
    seg_t = (t - ts[i1]) / max(ts[i2] - ts[i1], 1e-9)
    out = _cr(p0, p1, p2, p3, seg_t)
    if len(p1) == 1:
        return float(out[0])
    return out

def smooth01(x, a, b):
    """Smoothstep entre a y b. Devuelve 0 en a, 1 en b."""
    if a == b: return 0.0 if x < a else 1.0
    t = (x - a) / (b - a)
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)

def phase_weights(t_min):
    """Devuelve (w_liso, w_nebula, w_fractals) para el background a t_min.
    Schedule:
        0:00–2:00  liso=1
        2:00–2:30  cross-fade liso→nebula
        2:30–4:00  nebula=1
        4:00–4:30  cross-fade nebula→fractales
        4:30–6:30  fractales=1
        6:30–8:30  cross-fade fractales→liso
        8:30–13:00 liso=1 (después del min 10 fijo, como pidió user)
    """
    if t_min < 2.0:
        return (1.0, 0.0, 0.0)
    elif t_min < 2.5:
        k = smooth01(t_min, 2.0, 2.5)
        return (1.0 - k, k, 0.0)
    elif t_min < 4.0:
        return (0.0, 1.0, 0.0)
    elif t_min < 4.5:
        k = smooth01(t_min, 4.0, 4.5)
        return (0.0, 1.0 - k, k)
    elif t_min < 6.5:
        return (0.0, 0.0, 1.0)
    elif t_min < 8.5:
        k = smooth01(t_min, 6.5, 8.5)
        return (k, 0.0, 1.0 - k)
    else:
        return (1.0, 0.0, 0.0)


def lin_eval(keys, t):
    ts = [k[0] for k in keys]
    vs = [k[1] for k in keys]
    if t <= ts[0]: return float(vs[0])
    if t >= ts[-1]: return float(vs[-1])
    for i in range(len(ts) - 1):
        if ts[i] <= t <= ts[i + 1]:
            a = (t - ts[i]) / max(ts[i + 1] - ts[i], 1e-9)
            return float(vs[i] + (vs[i + 1] - vs[i]) * a)
    return float(vs[-1])

# ───── Control track loading ─────────────────────────────────────────────
def load_control(npz_path: Path, n_video_frames: int, video_fps: int):
    """Lee control.npz (a 30fps) y resamplea a video_fps. Suaviza low y flux."""
    if not npz_path.exists():
        print(f"[warn] control track no encontrado en {npz_path}", file=sys.stderr)
        z = np.full(n_video_frames, 0.0, dtype=np.float32)
        return {k: z.copy() for k in ("rms", "rms_sub", "rms_low", "rms_air", "flux", "onset")}

    d = np.load(npz_path)
    src_fps = float(d['fps'])
    n_src = len(d['rms'])
    # resampling lineal por tiempo
    t_video = np.arange(n_video_frames) / video_fps
    t_src = np.arange(n_src) / src_fps
    out = {}
    for k in ("rms", "rms_sub", "rms_low", "rms_air", "flux", "onset"):
        src = d[k].astype(np.float32)
        out[k] = np.interp(t_video, t_src, src).astype(np.float32)
    # suavizado temporal: low (~0.5s) y flux (~0.25s)
    def smooth(x, win):
        kernel = np.ones(win, dtype=np.float32) / win
        return np.convolve(x, kernel, mode='same').astype(np.float32)
    out['rms_low_smooth'] = smooth(out['rms_low'], int(0.5 * video_fps))
    out['rms_air_smooth'] = smooth(out['rms_air'], int(0.5 * video_fps))
    out['flux_smooth']    = smooth(out['flux'],    int(0.25 * video_fps))
    out['rms_smooth']     = smooth(out['rms'],     int(0.5 * video_fps))
    print(f"[control] loaded: n_src={n_src} @ {src_fps}fps → n_video={n_video_frames} @ {video_fps}fps")
    print(f"[control] rms_low  : min={out['rms_low_smooth'].min():.3f} max={out['rms_low_smooth'].max():.3f} mean={out['rms_low_smooth'].mean():.3f}")
    print(f"[control] flux     : min={out['flux_smooth'].min():.3f} max={out['flux_smooth'].max():.3f} mean={out['flux_smooth'].mean():.3f}")
    print(f"[control] rms_air  : min={out['rms_air_smooth'].min():.3f} max={out['rms_air_smooth'].max():.3f} mean={out['rms_air_smooth'].mean():.3f}")
    return out

# ───── moderngl setup ───────────────────────────────────────────────────
def make_gl(width: int, height: int):
    ctx = moderngl.create_standalone_context(require=330)
    prog = ctx.program(vertex_shader=VERTEX, fragment_shader=FRAGMENT)
    quad = np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype="f4")
    vbo = ctx.buffer(quad.tobytes())
    vao = ctx.vertex_array(prog, [(vbo, "2f", "in_pos")])
    # 32-bit float framebuffer → elimina cuantización 8-bit y arcos/bandas
    color_tex = ctx.texture((width, height), 4, dtype='f4')
    fbo = ctx.framebuffer(color_attachments=[color_tex])
    fbo.use()
    prog["u_aspect"].value = width / height
    return ctx, prog, vao, vbo, fbo, color_tex

# ───── Render 1 frame ───────────────────────────────────────────────────
def render_frame(prog, vao, fbo, width, height, i, ctrl, rng):
    t_sec = i / FPS
    t_min = t_sec / 60.0

    # color
    rgb = cr_eval(PALETTE_STATIONS, t_min)
    rgb = np.clip(rgb, 0.0, 1.0)

    # sombra primaria position + jitter (vibración por flux)
    xy = cr_eval(SHADOW_TRAJ, t_min)
    flux_v = float(ctrl['flux_smooth'][i])
    # jitter pseudo-aleatorio determinístico (no random — para no titilar):
    jitter_x = (np.sin(t_sec * 13.7) * 0.5 + np.cos(t_sec * 9.1) * 0.5) * 0.012 * flux_v
    jitter_y = (np.sin(t_sec * 11.3) * 0.5 + np.cos(t_sec * 7.7) * 0.5) * 0.012 * flux_v
    s1_pos = (float(xy[0] + jitter_x), float(xy[1] + jitter_y))

    # tamaño primario: crece con low (peludo) — devora la pantalla en pico
    low_v = float(ctrl['rms_low_smooth'][i])
    s1_r = SHADOW_R_BASE * (1.0 + 2.2 * low_v)   # hasta ~3.2x en pico

    # opacidad primaria: base lineal × (1 + 0.3*low + 0.10*flux), cap 0.95
    s1_op_base = lin_eval(SHADOW_OP_KEYS, t_min)
    s1_op = s1_op_base * (1.0 + 0.30 * low_v + 0.10 * flux_v)
    # Late silhouette fade: silueta muere entre 11:00 y 12:00 — elimina
    # overlap con bells light y curvas visibles en zonas oscuras finales.
    late_fade = float(np.clip((12.0 - t_min) / 1.0, 0.0, 1.0))
    # End fade: últimos 30s a 0 (redundante con late_fade, pero conservado)
    end_fade = float(np.clip((13.0 - t_min) / 0.5, 0.0, 1.0))
    s1_op = s1_op * late_fade * end_fade
    s1_op = float(np.clip(s1_op, 0.0, 0.95))

    # secundaria: misma trayectoria + offset, también crece (atmósfera)
    s2_pos = (s1_pos[0] + SHADOW2_OFFSET[0], s1_pos[1] + SHADOW2_OFFSET[1])
    s2_r = SHADOW2_R_BASE * (1.0 + 1.5 * low_v)
    # s2 dies between 9:00 and 11:00 — después de bells no aporta y crea
    # overlays gradient ancho visibles como ondas en zonas oscuras.
    s2_late_fade = float(np.clip((11.0 - t_min) / 2.0, 0.0, 1.0))
    s2_op = float(np.clip(s1_op * SHADOW2_OP_MULT * s2_late_fade, 0.0, 0.85))

    # light event
    in_window = (LIGHT_T_WINDOW[0] <= t_min <= LIGHT_T_WINDOW[1])
    air_v = float(ctrl['rms_air_smooth'][i])
    # rampa de entrada/salida suave sobre la ventana
    if in_window:
        w0, w1 = LIGHT_T_WINDOW
        edge = 0.20         # 12s de rampa a cada lado
        ramp_in  = np.clip((t_min - w0) / edge, 0.0, 1.0)
        ramp_out = np.clip((w1 - t_min) / edge, 0.0, 1.0)
        ramp = float(min(ramp_in, ramp_out))
    else:
        ramp = 0.0
    lt_intensity = LIGHT_PEAK * ramp * np.clip(air_v / 0.4, 0.0, 1.0)

    # grano técnico — mínimo, solo anti-banding
    grain_amt = 0.0007

    # set uniforms
    prog["u_color"].value = (float(rgb[0]), float(rgb[1]), float(rgb[2]))
    prog["u_s1_pos"].value = s1_pos
    prog["u_s1_op"].value = float(s1_op)
    prog["u_s1_r"].value = float(s1_r)
    prog["u_s1_falloff"].value = float(SHADOW_FALLOFF)
    prog["u_s1_ecc"].value = float(SHADOW_ECC)
    prog["u_s1_rot"].value = float(np.deg2rad(SHADOW_ROT_DEG))
    prog["u_s2_pos"].value = s2_pos
    prog["u_s2_op"].value = float(s2_op)
    prog["u_s2_r"].value = float(s2_r)
    prog["u_s2_falloff"].value = float(SHADOW2_FALLOFF)
    # head de la silueta: offset desde el body
    head_pos = (s1_pos[0] + SHADOW_HEAD_OFFSET[0], s1_pos[1] + SHADOW_HEAD_OFFSET[1])
    prog["u_head_pos"].value = head_pos
    prog["u_head_r"].value = float(SHADOW_HEAD_R)
    prog["u_head_falloff"].value = float(SHADOW_HEAD_FALLOFF)

    # phases del background (función de t_min)
    w_liso, w_neb, w_frac = phase_weights(t_min)
    prog["u_w_liso"].value = float(w_liso)
    prog["u_w_nebula"].value = float(w_neb)
    prog["u_w_fractals"].value = float(w_frac)
    prog["u_time"].value = float(t_sec)

    # peludo + jitter freq
    peludo_v = float(np.clip(low_v - 0.2, 0.0, 1.0) * 1.3)  # solo cuando low es alto
    prog["u_peludo"].value = float(peludo_v)
    # jitter freq: 2 Hz normal, 8 Hz peludo (tembleque violento)
    jf = 2.0 + 6.0 * peludo_v
    prog["u_jitter_freq"].value = float(jf)
    prog["u_lt_pos"].value = LIGHT_POS
    prog["u_lt_intensity"].value = float(lt_intensity)
    prog["u_lt_r"].value = float(LIGHT_R)
    prog["u_lt_falloff"].value = float(LIGHT_FALLOFF)
    prog["u_lt_tint"].value = LIGHT_TINT

    # voyager light: max intensidad cerca de cada momento (ventana ±5s)
    voy_amp = 0.0
    for vm in VOYAGER_MOMENTS_MIN:
        dt = (t_min - vm) * 60.0   # segundos
        # bump gaussiana ancho 4s
        amp = np.exp(-(dt * dt) / (2.0 * 4.0 * 4.0))
        voy_amp = max(voy_amp, amp)
    prog["u_lt2_pos"].value = VOYAGER_POS
    prog["u_lt2_intensity"].value = float(VOYAGER_PEAK * voy_amp)

    # fade in (0 → 3s) + fade out (12:45 → 13:00) a negro absoluto
    fade_in  = float(np.clip(t_sec / 3.0, 0.0, 1.0))
    fade_out = float(np.clip((780.0 - t_sec) / 15.0, 0.0, 1.0))
    prog["u_fade"].value = float(min(fade_in, fade_out))
    prog["u_grain_amt"].value = float(grain_amt)
    # seed per-frame para proper TPDF dither (amp 1/255 imperceptible)
    prog["u_seed"].value = float(i * 47.31 + 0.91)

    vao.render(moderngl.TRIANGLE_STRIP)
    # Read float32 framebuffer (no quantization yet) → convert to uint16
    # Stream as rgb48le (16-bit RGB little-endian) → ffmpeg → 10-bit encoder
    # 65536 levels per channel = 256x more precision than 8-bit → cero arcos
    raw = fbo.read(components=3, alignment=1, dtype='f4')
    arr = np.frombuffer(raw, dtype=np.float32).reshape(height, width, 3)
    arr_u16 = np.clip(arr * 65535.0, 0.0, 65535.0).astype('<u2')   # little-endian uint16
    arr_u16 = arr_u16[::-1, :, :]   # flip vertical
    return arr_u16.tobytes()

# ───── Pretest: contact sheet (15 frames a lo largo del track) ──────────
def pretest(width, height):
    """Genera contact sheet de 15 frames distribuidos a lo largo del track entero.
    Permite ver el rango dinámico de cabo a rabo (no solo 3 momentos sueltos).
    """
    # Render preview-resolution para velocidad (luego se tilea)
    pw, ph = 640, 360
    ctx, prog, vao, vbo, fbo, color_tex = make_gl(pw, ph)
    rng = np.random.default_rng(0xC1055)
    n_video = int(round(DURATION_S * FPS))
    ctrl = load_control(CONTROL_NPZ, n_video, FPS)

    # 15 puntos: 0, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600, 660, 720, 750, 779
    times_s = [0, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600, 660, 720, 750, 779]
    frames = []
    for t_s in times_s:
        idx = int(t_s * FPS)
        _ = render_frame(prog, vao, fbo, pw, ph, idx, ctrl, rng)   # warm
        raw = render_frame(prog, vao, fbo, pw, ph, idx, ctrl, rng)
        # raw is now uint16 (16-bit). Para PNG pretest convertimos a uint8.
        arr16 = np.frombuffer(raw, dtype='<u2').reshape(ph, pw, 3)
        arr = (arr16 >> 8).astype(np.uint8)
        frames.append((t_s, arr.copy()))
        print(f"[pretest] t={t_s}s frame={idx}")

    # Tile en grilla 5x3 = 5 columnas, 3 filas (de los 15 frames)
    cols, rows = 5, 3
    label_h = 24
    sheet_w = pw * cols
    sheet_h = (ph + label_h) * rows
    sheet = Image.new("RGB", (sheet_w, sheet_h), (0, 0, 0))
    from PIL import ImageDraw
    try:
        from PIL import ImageFont
        font = ImageFont.load_default()
    except Exception:
        font = None
    draw = ImageDraw.Draw(sheet)
    for i, (t_s, arr) in enumerate(frames):
        r, c = i // cols, i % cols
        x = c * pw
        y = r * (ph + label_h)
        img = Image.fromarray(arr, "RGB")
        sheet.paste(img, (x, y))
        m = t_s // 60
        s = t_s % 60
        draw.text((x + 6, y + ph + 4), f"t={m:02d}:{s:02d}", fill=(180, 200, 180), font=font)

    out = HERE / "pretest_contact_sheet.png"
    sheet.save(out, compress_level=3)
    print(f"[pretest] sheet → {out}")

    # Render adicional 1 frame en 4K en el pico peludo para ver detalle
    fbo.release(); color_tex.release()
    ctx2, prog2, vao2, vbo2, fbo2, ct2 = make_gl(width, height)
    idx_peak = int(4.3 * 60 * FPS)
    _ = render_frame(prog2, vao2, fbo2, width, height, idx_peak, ctrl, rng)
    raw = render_frame(prog2, vao2, fbo2, width, height, idx_peak, ctrl, rng)
    arr16 = np.frombuffer(raw, dtype='<u2').reshape(height, width, 3)
    img4k = Image.fromarray((arr16 >> 8).astype(np.uint8), 'RGB')
    img4k.save(HERE / "pretest_peludo_pico_4k.png", compress_level=3)
    fbo2.release(); ct2.release(); vao2.release(); vbo2.release(); prog2.release(); ctx2.release()
    print(f"[pretest] peludo pico 4K → pretest_peludo_pico_4k.png")
    vao.release(); vbo.release(); prog.release(); ctx.release()

# ───── Render full → ffmpeg pipe ────────────────────────────────────────
def render_full(width, height, fps, n_frames, out_mp4, audio_wav, with_audio, duration_s,
                start_s: float = 0.0):
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg no está en PATH")
    if out_mp4.exists():
        out_mp4.unlink()

    print(f"[render] {width}x{height} @ {fps}fps, {duration_s}s desde t={start_s}s = {n_frames} frames")
    print(f"[render] → {out_mp4}")

    args = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-stats",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-pix_fmt", "rgb48le", "-s", f"{width}x{height}", "-r", str(fps),
        # Tag input as BT.709 sRGB so zscale knows the source colorspace.
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "rgb",
        "-i", "-",
    ]
    if with_audio and audio_wav.exists():
        args += ["-ss", f"{start_s}", "-t", f"{duration_s}", "-i", str(audio_wav)]
    args += [
        # v3.21: SDR BT.709 limpio. FUERA gradfun (empeoraba, ver iter logs
        # 06-09) y FUERA noise=allf=t (ruido TEMPORAL = alimentaba el GOP
        # pumping de YouTube — mismo diagnóstico que outbound v20).
        # Encode unificado con outbound: 100M VBR + psy-rd.
        "-vf", "format=yuv420p10le",
        "-c:v", "libx265", "-profile:v", "main10", "-pix_fmt", "yuv420p10le",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-x265-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709:repeat-headers=1:bitrate=100000:vbv-maxrate=110000:vbv-bufsize=200000:psy-rd=2.5:aq-strength=1.0",
        "-preset", "medium", "-r", str(fps),
    ]
    if with_audio and audio_wav.exists():
        args += ["-c:a", "aac", "-b:a", "320k", "-shortest"]
    args += ["-movflags", "+faststart", str(out_mp4)]

    print(f"[ffmpeg] {' '.join(args[:6])} ... {out_mp4}")
    proc = subprocess.Popen(args, stdin=subprocess.PIPE)

    ctx, prog, vao, vbo, fbo, color_tex = make_gl(width, height)
    # v3.21: control SIEMPRE a duración completa — render_frame indexa con
    # frame absoluto, así un segmento (--start) usa los mismos uniforms.
    n_total = int(round(DURATION_S * fps))
    ctrl = load_control(CONTROL_NPZ, n_total, fps)
    rng = np.random.default_rng(0xC1055)
    start_frame = int(round(start_s * fps))

    t_start = time.time(); t_last = t_start
    try:
        for k in range(n_frames):
            i = min(start_frame + k, n_total - 1)
            buf = render_frame(prog, vao, fbo, width, height, i, ctrl, rng)
            proc.stdin.write(buf)
            if (k + 1) % 100 == 0 or k == n_frames - 1:
                now = time.time()
                dt = now - t_last; t_last = now
                elapsed = now - t_start
                rate = (k + 1) / max(elapsed, 1e-6)
                eta = (n_frames - (k + 1)) / max(rate, 1e-6)
                print(f"  [{k+1:>5}/{n_frames}] {rate:.2f}fps  elapsed {elapsed/60:.1f}m  eta {eta/60:.1f}m  last100 {dt:.1f}s")
                sys.stdout.flush()
    finally:
        try: proc.stdin.close()
        except Exception: pass
        ret = proc.wait()
        fbo.release(); color_tex.release(); vao.release(); vbo.release(); prog.release(); ctx.release()
        if ret != 0:
            raise RuntimeError(f"ffmpeg exit {ret}")
    print(f"[done] {out_mp4}")

# ───── CLI ──────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--width", type=int, default=W)
    ap.add_argument("--height", type=int, default=H)
    ap.add_argument("--fps", type=int, default=FPS)
    ap.add_argument("--seconds", type=float, default=DURATION_S)
    ap.add_argument("--start", type=float, default=0.0,
                    help="Segundo inicial (render de segmento para iterar zonas)")
    ap.add_argument("--pretest", action="store_true")
    ap.add_argument("--no-audio", action="store_true")
    ap.add_argument("--out", type=str, default=str(OUT_MP4))
    args = ap.parse_args()
    if args.pretest:
        pretest(args.width, args.height); return
    n = int(round(args.seconds * args.fps))
    render_full(args.width, args.height, args.fps, n, Path(args.out), AUDIO_WAV, not args.no_audio, args.seconds,
                start_s=args.start)

if __name__ == "__main__":
    main()
