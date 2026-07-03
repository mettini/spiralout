#!/usr/bin/env python3.10
"""Outbound — 3D raymarched re-render v5 (artist iteration pass #5).

Artista: "Muy groso como está quedando, un pelín más". 8 fixes finos:

 1) FADE-IN desde negro 0-5s. Los primeros 5s del frame se multiplican
    por smoothstep(0,5,t). El "inicio fulero" queda oculto.
 2) Stripes verticales a 0:08: dither hash mejorado (multi-componente
    isotropico). Además queda oculto por fade-in (1).
 3) Sweep R→L a 0:14: causado por sparkle_window dejando sparkle activo
    desde t=0 → cualquier centroid spike a t=14 disparaba un destello en
    diagonal. Fix: gate sparkle_window a empezar a t=42s (los tilin tilin
    reales son a 50.27, 57.07, 59.33).
 4) Sparkle: difundido (halo más ancho) + menos brillante (peak ×0.70) +
    dos tipos alternados (A fast/small en air events, B slow/soft en sub
    events). Lista de event_times PRECOMPUTADA en código:
       AIR  (tipo A): 50.27, 57.07, 59.33, 69.50, 72.43
       SUB  (tipo B): subdivisiones lentas modeladas con sin lentos.
 5) Túnel slower: zCam multiplier 4.5 → 2.85 (~37% reducción).
 5b) Túnel core dimmer + walls boost: core scale 1.9 → 1.30, walls ×1.22.
 5c) Black mark central removido: pow(vanish, 1.4) → smoothstep suave
     sin pico oscuro al medio.
 6) Tunel→humo a 3:28 (no 3:25): boundary 208 → 211. Fade window
     desplazada: pre-boundary 8.0 / post 2.0 → 3:23..3:33 con boundary
     211.
 7) Mandala close a 4:51 (no 4:57): close_phase trigger 0.67 → 0.57.
 8) Portal→partida a 6:30 (no 6:20): boundary 380 → 390. SCENE_PORTAL
    se extiende +10s; SCENE_PARTIDA se acorta 10s.

Targets: 4K 3840x2160 @ 30fps, 8:00 = 14400 frames.
Render: rgb48le (16-bit) → libx264 high10 yuv420p10le CRF 17.
"""
_V4_CHANGELOG_REF = """v4 changelog (reference):

 1) 0:00-0:01: planeta+background aparecen JUNTOS. Sin global fade-in
    en nacer (era t/2s → ahora instantáneo) → no se ve "fondo primero".
 2) Ovulo: levemente MAS brillante que v3 (0.55 → 0.68 multiplier).
    Dirección OK, solo bump.
 3) Sparkle: TINY star — punto chico al centro (radius ~1.5% del planeta)
    + 4 rayos delgados (diffraction spikes) que IRRADIAN. El resto del
    planeta NO se ilumina. (era: 18 rayos + planeta entero brillaba)
 4) Continentes/clouds del ovulo: ANIMADOS. El patrón de fibers + fbm
    advecta lentamente con u_time (subliminal pero visible).
 5) Transition a EXACTAMENTE 1:15.0 (t=75.0). Dive empieza AT t=75.0,
    NO antes. Hasta t=75 el ovulo está intacto. Xfade asimétrica
    completa post-boundary (75→83). El artista fue muy claro.
 6) 1:13-1:14: glow tenue dentro del ovulo (centro) aparece y crece →
    hint de que adentro del ovulo está el core del túnel. No más
    "momento muerto".
 7) Tunnel core: MÁS DIFUMINADO. El core se integra con los anillos —
    no es "bola separada en el fondo". exp decay 8.0 → 3.5 + halo más
    ancho. Los rings continúan smooth desde el core.
 8) Tunel → humo: 8s xfade (era 4s) empezando A 3:20 terminando 3:30.
    Asimétrico pre-boundary 200→210 (boundary 208).
 9) 5:49 (t=349): evento visual dentro del portal. Spin acelera + hue
    rotation drift → "se enrosca el ritmo".
10) 6:20 (t=380) portal→partida: fade-WITH-LIGHT (NO black). Whiteout
    breve en lugar de pestañeo negro. Partida arranca YA en movimiento
    (camera offset al inicio para que no esté frenada).
11) 7:36 (t=456) partida→afuera: xfade ~50% más larga (6s → 9s) para
    que se una más smooth.

Scene windows v4 (sin cambios respecto a v3 EXCEPTO el manejo de la
ventana de xfade — los boundaries siguen iguales):
    nacer:   0-75    (75s; dive 75-83 EN XFADE post-boundary)
    tunel:   75-208  (133s)
    humo:    208-263 (55s; xfade 200-210 pre-boundary)
    bloom:   263-312 (49s)
    portal:  312-380 (68s; spin event a 349)
    partida: 380-450 (70s; xfade light no black)
    afuera:  450-480 (30s; xfade 9s smoother)

Targets: 4K 3840x2160 @ 30fps, 8:00 = 14400 frames.
Render: rgb48le (16-bit) → libx264 high10 yuv420p10le CRF 17.
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
AUDIO_WAV = REPO / "transmissions/01/release/masters/01_outbound_master.wav"
CONTROL_NPZ = REPO / "transmissions/01/video/control/outbound.npz"

# ───── Targets ──────────────────────────────────────────────────────────
W, H = 3840, 2160
FPS = 30
DURATION_S = 8 * 60.0
N_FRAMES = int(round(DURATION_S * FPS))

# Verde anegrado dominante
COLOR_GREEN = (0.062, 0.155, 0.092)
COLOR_GREEN_DEEP = (0.030, 0.082, 0.050)
COLOR_AMBER = (0.83, 0.63, 0.29)

# ───── v6 DISCRETE EVENT LIST (bells + heartbeats) ────────────────────
# El artista pidió sync EXACTO a momentos musicales específicos en lugar
# de respuesta promediada al envelope. Estos son los disparadores discretos.
#
# BELL events: cada uno dispara un sparkle (TIPO A — star burst chico +
# halo difundido). Lista compuesta por:
#   - peaks detectados en rms_air (mean+1*std, gap 0.2s): 50.27, 57.07,
#     59.33, 69.50, 72.43 (band-detected, air spikes reales).
#   - tiempos extra que mencionó el artista donde "falta light" o estaba
# v7: BELL events DETECTADOS con precisión sub-segundo (spectral flux air-band).
# Cada tupla: (time_seconds, amplitude). Bells aislados=1.0; secuencias=0.4 each.
BELL_EVENTS = [
    (39.683, 1.0),
    (46.684, 1.0),
    # Sequence ~50s — bells juntos, cada uno más sutil que single
    (50.196, 0.55),
    (50.370, 0.55),
    (50.828, 0.35),
    (51.026, 0.35),
    (51.682, 0.30),
    # Sequence ~57s
    (56.988, 0.55),
    (57.185, 0.55),
    (57.980, 0.30),
    (59.193, 0.30),
    # Single strong bells
    (64.685, 1.0),
    (69.416, 1.0),
    (72.301, 0.6),
]

# v7: HEART events con timestamps DETECTADOS (low-mid band kicks).
# User dijo "0:12, 0:18, 0:22, 0:27" — los reales son 12.25, 17.25, 21.99, 27.25.
# El de "0:18" estaba 0.75s off (es 17.25, no 18.0). Amplitudes UNIFORMES.
HEART_EVENTS = [
    (12.254, 1.0),
    (17.252, 1.0),
    (21.995, 1.0),
    (27.249, 1.0),
]

# Response window (seconds after trigger). Gaussian peak at event time (not +sigma).
EVENT_WINDOW_S = 0.45
EVENT_SIGMA_S  = 0.07

# ───── Scene window definitions (v5) ──────────────────────────────────
# v5 changes:
#   fix #6: tunel→humo boundary 208 → 211 (3:28). humo arranca 3s después.
#   fix #8: portal→partida boundary 380 → 390 (6:30). portal +10s.
SCENES = [
    ("nacer",   0.0,   75.0),
    ("tunel",   75.0,  211.0),   # v5 fix #6: +3s
    ("humo",    211.0, 263.0),   # v5 fix #6: 52s ahora
    ("bloom",   263.0, 312.0),
    ("portal",  312.0, 360.0),   # v6: portal→partida a 6:00 (no 6:30)
    ("partida", 360.0, 420.0),   # v6: partida→afuera a 7:00 (no 7:30)
    ("afuera",  420.0, 480.0),   # v6: closing 60s breathing room
]
XFADE_S = 8.0

# Transiciones especiales. Algunas son dive-into (sin xfade), otras son
# light-flash (NUNCA black). NUNCA crossfade plano.
SPECIAL_XFADE = {
    ("nacer", "tunel"):    8.0,   # v4 fix #5: dive entero POST-boundary 75→83
    ("tunel", "humo"):    10.0,   # v5 fix #6: 3:23→3:33 con boundary 211
    ("humo", "bloom"):     6.0,   # continuum, la flor florece sobre la nube
    ("bloom", "portal"):   3.0,   # dive-into-light, NO fade
    ("portal", "partida"): 4.0,   # v4 fix #10: LIGHT-FLASH (NO black)
    ("partida", "afuera"): 9.0,   # v4 fix #11: ~50% más larga (era 6)
}

# Asymmetric xfade offsets: (pre_boundary_s, post_boundary_s).
# v4 fix #5: nacer→tunel xfade va ENTERO después del boundary (dive desde 75).
# v5 fix #6: tunel→humo ventana 8s antes / 2s después de boundary 211.
ASYMMETRIC_XFADE = {
    ("nacer", "tunel"):  (0.0, 8.0),    # dive 75.0 → 83.0
    ("tunel", "humo"):   (8.0, 2.0),    # fade 203 → 213, boundary 211
}

# Transiciones que usan LIGHT-FLASH (fade a→white, white→b):
LIGHT_FLASH_TRANSITIONS = {("portal", "partida")}

# ───── Shaders ──────────────────────────────────────────────────────────
VERTEX = """
#version 330 core
in vec2 in_pos;
out vec2 v_uv;
void main() {
    v_uv = (in_pos + 1.0) * 0.5;
    gl_Position = vec4(in_pos, 0.0, 1.0);
}
"""

# Common GLSL prelude
COMMON_GLSL = """
#version 330 core
in vec2 v_uv;
out vec4 fragColor;

uniform float u_aspect;
uniform float u_time;       // tiempo dentro de la escena (s desde su inicio)
uniform float u_scene_t;    // 0..1 normalizado dentro de la escena
uniform float u_rms;
uniform float u_rms_sub;
uniform float u_rms_smooth;
uniform float u_rms_air;
uniform float u_onset;
uniform float u_flux;       // proxy motivo voyager (melodía)
uniform float u_sparkle;    // beep voyager (centroid spike) → core sparkle
uniform float u_sparkle_amp; // v6: discrete BELL event response (0..1)
uniform float u_heart_amp;   // v6: discrete HEART event response (0..1)
uniform float u_fade;
uniform float u_seed;

const vec3  GREEN      = vec3(0.062, 0.155, 0.092);
const vec3  GREEN_DEEP = vec3(0.030, 0.082, 0.050);
const vec3  AMBER      = vec3(0.83, 0.63, 0.29);

float hash21(vec2 p) {
    p = fract(p * vec2(443.8975, 397.2973));
    p += dot(p, p.yx + 19.19);
    return fract((p.x + p.y) * p.x);
}
float hash31(vec3 p) {
    p = fract(p * vec3(443.8975, 397.2973, 491.1871));
    p += dot(p, p.yzx + 19.19);
    return fract((p.x + p.y + p.z) * p.x);
}
float vnoise3(vec3 pp) {
    vec3 ip = floor(pp);
    vec3 fp = fract(pp);
    vec3 sf = fp * fp * (3.0 - 2.0 * fp);
    float n000 = hash31(ip);
    float n100 = hash31(ip + vec3(1,0,0));
    float n010 = hash31(ip + vec3(0,1,0));
    float n110 = hash31(ip + vec3(1,1,0));
    float n001 = hash31(ip + vec3(0,0,1));
    float n101 = hash31(ip + vec3(1,0,1));
    float n011 = hash31(ip + vec3(0,1,1));
    float n111 = hash31(ip + vec3(1,1,1));
    float nx00 = mix(n000, n100, sf.x);
    float nx10 = mix(n010, n110, sf.x);
    float nx01 = mix(n001, n101, sf.x);
    float nx11 = mix(n011, n111, sf.x);
    float nxy0 = mix(nx00, nx10, sf.y);
    float nxy1 = mix(nx01, nx11, sf.y);
    return mix(nxy0, nxy1, sf.z);
}
float fbm3(vec3 pp) {
    float acc = 0.0; float amp = 0.5; vec3 q = pp;
    for (int oct = 0; oct < 4; oct++) {
        acc += amp * vnoise3(q);
        q = q * 2.02; amp *= 0.5;
    }
    return acc;
}
float fbm3_2(vec3 pp) {
    float acc = 0.0; float amp = 0.5; vec3 q = pp;
    for (int oct = 0; oct < 2; oct++) {
        acc += amp * vnoise3(q);
        q = q * 2.02; amp *= 0.5;
    }
    return acc;
}

// v14: film-grain estructural, fix de cuadriculado. Cambios vs v13:
//  - cada temporal step ROTA las coords (no solo desplaza) → mata grilla.
//  - 2 octavas con offset relativamente primo entre ellas (no múltiples
//    de 2.0 estrictos).
//  - Slower temporal: 6 Hz en vez de 10 Hz.
// Solo luma. Retorna ~[-0.5, 0.5].
float grain_luma(vec2 fc, float t) {
    float ti = floor(t * 6.0);
    // rotación 2D por step temporal — ángulo derivado del step
    float ang = ti * 0.913 + 0.31;
    float cs = cos(ang); float sn = sin(ang);
    mat2 rot = mat2(cs, -sn, sn, cs);
    vec2 tshift = vec2(ti * 7.13, ti * 3.71);
    vec2 q = rot * fc / 2.5 + tshift;
    float acc = 0.0;
    float amp = 0.6;
    for (int oct = 0; oct < 2; oct++) {
        vec2 ip = floor(q);
        vec2 fp = fract(q);
        vec2 sf = fp * fp * (3.0 - 2.0 * fp);
        float n00 = hash21(ip);
        float n10 = hash21(ip + vec2(1.0, 0.0));
        float n01 = hash21(ip + vec2(0.0, 1.0));
        float n11 = hash21(ip + vec2(1.0, 1.0));
        float nx0 = mix(n00, n10, sf.x);
        float nx1 = mix(n01, n11, sf.x);
        acc += amp * mix(nx0, nx1, sf.y);
        // multiplier no-entero entre octavas → desfase irracional
        q = rot * q * 2.13 + vec2(11.7, -5.3);
        amp *= 0.5;
    }
    return acc - 0.45;
}

vec3 camRayLook(vec2 uv, vec3 eye, vec3 target, vec3 upHint, float fov) {
    vec3 f = normalize(target - eye);
    vec3 r = normalize(cross(f, upHint));
    vec3 u = cross(r, f);
    vec2 ndc = (uv * 2.0 - 1.0);
    ndc.x *= u_aspect;
    float tanH = tan(fov * 0.5);
    return normalize(r * ndc.x * tanH + u * ndc.y * tanH + f);
}

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}
vec3 rgb2hsv(vec3 c) {
    vec4 K = vec4(0.0, -1.0/3.0, 2.0/3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

vec3 finalize(vec3 col) {
    // v11: gamma 0.78 (user reportó demasiada luz con 0.70). Mantiene visibilidad
    // sin sobre-iluminar. 0.05 -> 0.103 (vs 0.143 con 0.70).
    col = pow(max(col, vec3(0.0)), vec3(0.78));
    // v5 fix #2: dither multi-componente ISOTROPICO para evitar bandas
    // verticales. Usamos 3 hashes con coords rotadas + jitter en X/Y
    // separados → break de cualquier patrón axial.
    vec2 fc = gl_FragCoord.xy;
    // v10 FIX CRÍTICO: u_seed va a 300000+ en frames altos, lo cual rompe
    // hash21 por pérdida de precisión float32 (mult * 443 = 1e8 → fract garbage).
    // Pre-fract el seed mantiene los valores en rango precisado.
    float s = fract(u_seed * 0.000312345);
    // v20: también estático (era temporal vía s → alimentaba el pumping)
    float n  = hash21(fc + vec2(137.0, 234.0));
    float grain = (n - 0.5) * 2.0 * 0.0010;
    float shadow_boost = 1.0 + (1.0 - dot(col, vec3(0.33))) * 0.5;
    col += grain * shadow_boost;
    // jitter coords con rotación + offset distinto por canal (isotrópico)
    vec2 rot1 = vec2(fc.x * 1.317 + fc.y * 0.741, fc.y * 1.219 - fc.x * 0.503);
    vec2 rot2 = vec2(fc.x * 0.831 - fc.y * 1.471, fc.y * 0.913 + fc.x * 1.117);
    vec2 rot3 = vec2(fc.x * 2.131 + fc.y * 0.291, fc.y * 1.881 - fc.x * 0.617);
    // v20 — ANTI GOP-PUMPING (medido en el VP9 real de YouTube, 2026-06-12):
    // YT sirve 2160p VP9 a ~10Mbps con keyframe cada ~3-5s. El ruido TEMPORAL
    // (dither RGB ±8/255 + grain rotando 6Hz) se degrada en los P-frames y
    // cada keyframe lo resetea → pop visible (SAD 20-30x baseline en 0:09,
    // 6:10 — el "salto y vuelve" del user). Fix: ruido mínimo y ESTÁTICO;
    // el anti-banding lo hace la atmósfera estructural (v17-v19), que los
    // P-frames sí trackean.
    //  - dither: luma-only ±1.5/255, ESTÁTICO (sin u_seed → no cambia por
    //    frame). Suficiente para romper la cuantización del master 10-bit.
    //  - grain: luma-only 1.5-3/255, ESTÁTICO (t=0 → textura fija tipo
    //    placa de film; a esta amplitud no se percibe el patrón).
    float dl = hash21(rot1 + vec2(113.0, 191.0));
    col += vec3((dl - 0.5) * 3.0 / 255.0);
    float gl = grain_luma(fc, 0.0);
    float luma_pre = dot(col, vec3(0.299, 0.587, 0.114));
    float gamp = mix(1.5, 3.0, smoothstep(0.05, 0.7, luma_pre));
    col += vec3(gl) * gamp / 255.0;
    col *= u_fade;
    return clamp(col, 0.0, 1.0);
}
"""

# ─── Scene 1: NACER — esfera (ovulo/planeta) — v4 ──────────────────────
SCENE_NACER = COMMON_GLSL + """
// v4 fixes:
//  #1 planeta+bg juntos desde t=0. Nada precede al planeta.
//  #2 levemente más brillante que v3: multiplier 0.55 → 0.68.
//  #3 sparkle TINY: punto chico (1.5% radius) + 4 rayos delgados; el
//     planeta NO se ilumina globalmente.
//  #4 continents/clouds animadas: u_time advecta el patrón de fibers
//     y desplaza el fbm de la superficie (subliminal).
//  #5 dive in-scene REMOVIDO. La ovulo está intacta TODO el scene.
//     El dive ocurre via xfade asimétrica afuera (75→83).
//  #6 a partir de t=73 aparece un glow tenue creciendo en el centro del
//     ovulo (hint del core del túnel adentro).

vec3 render_scene() {
    vec2 uv = v_uv;
    float t = u_time;

    // Fix #5: hasta t=75 NO hay dive. Desde t=75 el dive ocurre durante
    // la xfade post-boundary 75→83 (nacer todavía rendering como scene_a).
    float dive_k = smoothstep(75.0, 83.0, t);
    dive_k = pow(dive_k, 1.6);
    float zEye = mix(2.6, 0.10, dive_k);
    vec3 eye = vec3(0.0, 0.0, zEye);
    vec3 ro = eye;
    float fov = mix(radians(40.0), radians(85.0), dive_k);
    vec3 rd = camRayLook(uv, eye, vec3(0.0), vec3(0.0, 1.0, 0.0), fov);

    // Heartbeat respira (sutil)
    float pulse_enable = smoothstep(22.0, 30.0, t);
    float beat = 0.5 + 0.5 * sin(t * 6.28318);
    beat = pow(beat, 6.0);
    // v6: DISCRETE heart pulses at exact musical moments (0:12, 0:18,
    // 0:22, 0:27). u_heart_amp es Gaussian bump (0..1) que sube por
    // 400ms en cada event. Pulse = ±2% radius scale.
    // v11 FIX: beat + rms_sub continuos hacían latir el ovulo cuando no debía
    // (user reportó "late el ovulo a 0:09 sin heart pulse"). Removido.
    // Sólo u_heart_amp (eventos discretos exactos) controla pulse.
    float r = 0.95
            + 0.011  * u_heart_amp;

    // Fondo presente desde el primer frame (fix #1)
    vec3 col = GREEN_DEEP * 0.45;

    float tHit = -1.0;
    vec3 pHit;
    float b = dot(rd, ro);
    float c = dot(ro, ro) - r * r;
    float disc = b * b - c;
    if (disc > 0.0) {
        float t1 = -b - sqrt(disc);
        if (t1 > 0.0) {
            tHit = t1;
            pHit = ro + rd * t1;
        }
    }

    // Halo simultáneo al planeta
    float halo = 0.0;
    {
        float bb = dot(rd, ro);
        float dd = length(ro - rd * (-bb));
        halo = exp(-pow(max(dd - r, 0.0) * 3.5, 2.0)) * 0.55;
    }
    col += GREEN * halo * (0.6 + 0.4 * beat * pulse_enable);

    if (tHit > 0.0) {
        vec3 N = normalize(pHit);
        vec3 view = -rd;
        float frontDot = max(dot(N, view), 0.0);
        float rAng = acos(clamp(frontDot, 0.0, 1.0));

        vec3 tangBase = normalize(cross(N, view));
        float tang = atan(dot(N - view * frontDot, tangBase),
                          dot(N - view * frontDot, cross(view, tangBase)));

        // Fix #4: animar continentes — drift en frecuencia angular + 3D fbm
        // con offset temporal. El patrón rota lento (~0.02 rad/s) y el
        // fbm advecta con u_time*0.025 → continentes que se mueven.
        float surface_drift = t * 0.02;       // rotación lenta del patrón
        float fbm_drift     = t * 0.025;
        float fibFreq = 40.0;
        // sample con offset temporal: la "geografía" de la superficie deriva
        float fbm_blur = fbm3(vec3(N * 4.0) + vec3(fbm_drift,
                                                    fbm_drift * 0.7,
                                                    -fbm_drift * 0.5));
        float fibers = 0.5 + 0.5 * cos((tang + surface_drift) * fibFreq
                                        + rAng * 2.5
                                        + fbm_blur * 5.5);
        fibers = pow(fibers, 1.4);
        fibers = mix(fibers, fbm_blur * 0.7 + 0.3, 0.4);

        float fres = pow(1.0 - frontDot, 2.5);
        float sss = max(dot(N, normalize(vec3(0.3, 0.5, 1.0))), 0.0);
        sss = pow(sss, 1.6);

        vec3 c_pupil = GREEN_DEEP * 0.55;
        vec3 c_iris  = mix(GREEN_DEEP * 0.45, GREEN * 1.20, fibers);
        vec3 c_limb  = GREEN_DEEP * 0.25;

        float pupilCore = 1.0 - exp(-pow(rAng / 0.30, 3.5));
        vec3 iris_col = mix(mix(c_pupil, c_iris, pupilCore), c_limb,
                            smoothstep(0.95, 1.40, rAng));
        iris_col += GREEN * sss * 0.22;
        vec3 H = normalize(view + normalize(vec3(0.25, 0.5, 1.0)));
        float spec = pow(max(dot(N, H), 0.0), 32.0) * 0.14;
        iris_col += vec3(spec) * GREEN * 1.6;
        iris_col += GREEN * fres * 0.40;

        // Fix #2: levemente más brillante (0.55 → 0.68)
        iris_col *= 0.68;

        // Glow sutil al centro (NO hoyo negro)
        float core_glow_inner = exp(-pow(rAng / 0.10, 2.0)) * 0.35;
        iris_col += GREEN * core_glow_inner;

        iris_col *= (1.0 + 0.03 * u_rms_smooth * pulse_enable);

        // Fix #6: glow tenue creciendo desde t=73 (1:13) que hint el core
        // del túnel adentro del ovulo. Aparece smooth 73→75.
        float hint_k = smoothstep(73.0, 75.0, t);
        // pequeño bright dot en el centro, color del core del tunel (verde-amber)
        float hint_core = exp(-pow(rAng / 0.05, 2.0)) * hint_k * 0.55;
        float hint_halo = exp(-pow(rAng / 0.18, 2.0)) * hint_k * 0.20;
        iris_col += vec3(0.55, 0.95, 0.55) * hint_core;
        iris_col += GREEN * hint_halo;

        // v6: SPARKLE driven by DISCRETE BELL events (u_sparkle_amp).
        // Reemplaza el sistema sparkle_window+u_sparkle (continuo, mal sync)
        // por Gaussian bumps centrados exactamente en cada bell timestamp
        // (40, 47, 50.27, 57.07, 59.33, 65, 69.50, 72.43). u_sparkle_amp
        // sube 0→1 en ~80ms tras el trigger y baja en ~320ms (window 400ms).
        // → cada bell tiene su destello propio, sin parpadeo de envelope.
        //
        // Visual: estrellita pequeña al centro (1.4%) + 4 rayos diffraction
        // delgados + halo difundido (rAng/0.20 radius) para que la luz
        // "salga" del ovulo cuando suena la campana.
        float center_dot_A = exp(-pow(rAng / 0.014, 2.0));
        float ray_4  = pow(abs(cos(tang * 2.0)),          80.0);
        float ray_4b = pow(abs(cos(tang * 2.0 + 1.5708)), 80.0);
        float ray_pattern = max(ray_4, ray_4b);
        float ray_radial  = exp(-rAng * 10.0);
        float diffuse_halo = exp(-pow(rAng / 0.20, 1.6));
        float sparkle_full = (ray_pattern * ray_radial * 0.50)
                           + (center_dot_A * 0.95)
                           + (diffuse_halo * 0.35);
        iris_col += vec3(0.82, 1.0, 0.66) * sparkle_full * u_sparkle_amp * 0.85;

        col = iris_col;
    }

    // v17: atmósfera de baja frecuencia (anti-banding estructural, ver bloom).
    // El fondo del nacer daba wide 12-28% en 0:02-1:02 (detector v12).
    vec2 auv17 = (v_uv - 0.5) * vec2(u_aspect, 1.0);
    float at1 = fbm3(vec3(auv17 * 7.0, u_time * 0.020));
    float at2 = fbm3(vec3(auv17 * 2.6 + 13.7, u_time * 0.013));
    // v18: octava de frecuencia MEDIA (~80-160px). Las bajas (250-600px)
    // cambian <1 nivel por bloque de 16-32px y VP9 colapsa los DC igual
    // (macroblocking visto en el emulado 4:12). Esta escala fuerza diffs
    // de 2-3 niveles entre bloques vecinos.
    float at3 = fbm3(vec3(auv17 * 27.0, u_time * 0.031));
    float am17 = (at1 - 0.5) * 0.42 + (at2 - 0.5) * 0.26 + (at3 - 0.5) * 0.32;
    col *= 1.0 + am17 * 0.12;
    // v21: aditivo en darks profundos (fondo del nacer, wide 58-62% en
    // master v20 a 0:02/1:02).
    float lum_n = dot(col, vec3(0.299, 0.587, 0.114));
    col += vec3(am17 * 0.020 * (1.0 - smoothstep(0.05, 0.16, lum_n)));

    // Vignette suave
    vec2 vc = v_uv - 0.5; vc.x *= u_aspect;
    float rv = length(vc);
    float vig_amt = mix(0.35, 0.05, dive_k);
    col *= 1.0 - smoothstep(0.55, 1.1, rv) * vig_amt;

    // Durante el dive (75→83), oscurecer al final y pupila negra crece
    // para que la composite con tunel haga sentido (matching).
    float dark_amt = smoothstep(0.70, 1.0, dive_k);
    col *= mix(1.0, 0.08, dark_amt);
    vec2 vc2 = v_uv - 0.5; vc2.x *= u_aspect;
    float rv2 = length(vc2);
    float pupil_radius = mix(0.05, 1.5, dive_k);
    float pupil_mask = 1.0 - smoothstep(pupil_radius * 0.5, pupil_radius, rv2);
    col *= mix(1.0, 0.0, pupil_mask * dark_amt);

    return col;
}

void main() {
    vec3 col = render_scene();
    fragColor = vec4(finalize(col), 1.0);
}
"""

# ─── Scene 2: TÚNEL — anillos concéntricos al core, ball más chica ──────
SCENE_TUNEL = COMMON_GLSL + """
// v3 fix #7:
//  - El core ball glow más PEQUEÑO (radius x ~0.6).
//  - Anillos concéntricos al core. El vanishing point del túnel coincide
//    con la posición del core (en pantalla = centro de la imagen).
//    Para esto, anulamos el offset de la cámara en X/Y (eran sin/cos
//    drifts que descentraban el túnel del core en pantalla).

float wallTex(vec3 p) {
    float z = p.z;
    float ang = atan(p.y, p.x);
    float rings = 0.5 + 0.5 * sin(z * 2.2);
    rings = pow(rings, 6.0);
    float cracks = 0.5 + 0.5 * sin(ang * 36.0 + z * 0.7) * sin(z * 0.85 + ang * 5.3);
    cracks = pow(cracks, 2.0);
    float grain = fbm3(vec3(ang * 4.0, z * 0.7, 0.0));
    return clamp(0.20 + rings * 0.55 + cracks * 0.35 + grain * 0.20, 0.0, 1.4);
}

vec3 render_scene() {
    vec2 uv = v_uv;
    // v5 fix #5: velocidad reducida ~37% (4.5 → 2.85). Camera Z avanza
    // más lento → el corredor del túnel respira, no nos arrastra.
    float zCam = -u_time * 2.85;
    // Roll muy pequeño (sensación de avance sin marear) pero SIN traslación
    // X/Y → asegura que el vanishing point esté en el centro.
    float roll = sin(u_time * 0.14) * 0.10;
    vec3 ro = vec3(0.0, 0.0, zCam);
    vec3 up = vec3(sin(roll), cos(roll), 0.0);
    vec3 fwd = vec3(0.0, 0.0, -1.0);
    vec3 rd = camRayLook(uv, ro, ro + fwd, up, radians(70.0));

    float R = 1.6;
    vec2 ox = ro.xy;
    vec2 dx = rd.xy;
    float a = dot(dx, dx);
    float b = 2.0 * dot(ox, dx);
    float c = dot(ox, ox) - R * R;
    float t_hit = -1.0;
    vec3 col = GREEN_DEEP * 0.25;
    if (a > 1e-6) {
        float disc = b * b - 4.0 * a * c;
        if (disc > 0.0) {
            float sq = sqrt(disc);
            float t1 = (-b + sq) / (2.0 * a);
            float t2 = (-b - sq) / (2.0 * a);
            t_hit = max(t1, t2);
            if (t_hit > 1000.0 || t_hit <= 0.0) t_hit = -1.0;
        }
    }

    float axialDist = length(vec2(rd.x, rd.y));
    // v4 fix #7: core MÁS DIFUMINADO. Antes 8.0 (bola concentrada que se
    // veía como pelota separada). Ahora 3.5 + un halo más ancho → el core
    // se integra con los rings, no es ball separada en el fondo.
    float vanish = exp(-axialDist * 3.5);
    // Halo extra ancho que se solapa con las paredes (continuidad)
    float halo_wide = exp(-axialDist * 1.4) * 0.55;
    float slow_breath = 0.5 + 0.5 * sin(u_time * 0.35);
    float core_pulse = 0.55 + 0.20 * u_flux + 0.10 * slow_breath;
    vanish *= core_pulse;
    halo_wide *= core_pulse;

    if (t_hit > 0.0) {
        vec3 p = ro + rd * t_hit;
        float surf = wallTex(p);
        vec3 N = normalize(-vec3(p.xy, 0.0));
        vec3 lp = vec3(0.0, 0.0, zCam - 60.0);
        vec3 L = normalize(lp - p);
        float diff = max(dot(N, L), 0.0);
        float rim = pow(1.0 - abs(dot(N, -rd)), 2.0);
        float fog = exp(-t_hit * 0.030);

        // v5 fix #5b: walls boost +22% para que la estructura del corredor
        // sea más visible (el core ya no domina).
        vec3 base = GREEN_DEEP * 0.85;
        vec3 lit = base * (0.36 + 0.86 * diff) + GREEN * rim * 1.05;
        lit *= (0.30 + 1.10 * surf);
        lit += GREEN * core_pulse * vanish * 0.15;
        col = mix(GREEN_DEEP * 0.20, lit, fog);
    }

    // CORE color hue-shifted con flux.
    float hue_shift = (u_flux - 0.5) * 0.10;
    vec3 core_hsv = vec3(0.32 + hue_shift, 0.55, 1.0);
    vec3 core_col = hsv2rgb(core_hsv);
    // v5 fix #5b: CORE dimmer 30%. Antes ×1.9, ahora ×1.30.
    col += core_col * vanish * 1.30;
    col += core_col * halo_wide * 0.60;
    // v5 fix #5c: black mark central removido. Antes pow(vanish, 1.4)
    // dejaba un pequeño hueco oscuro de transición (donde pow exponencial
    // baja antes de subir). Ahora suavizamos con una rampa lineal en
    // intensidad: peak central sin "rosquilla".
    float peak = smoothstep(0.40, 1.0, vanish);
    col += vec3(0.85, 1.0, 0.55) * peak * 0.18;

    vec2 vc = v_uv - 0.5; vc.x *= u_aspect;
    float rv = length(vc);
    col *= 1.0 - smoothstep(0.6, 1.2, rv) * 0.30;
    return col;
}

void main() {
    vec3 col = render_scene();
    fragColor = vec4(finalize(col), 1.0);
}
"""

# ─── Scene 3: HUMO — sin cambios estéticos ─────────────────────────────
SCENE_HUMO = COMMON_GLSL + """
float cloudDensity(vec3 p) {
    vec3 q = p * 0.45 + vec3(u_time * 0.06, u_time * 0.03, -u_time * 0.05);
    float warp = fbm3_2(q * 0.5) * 1.3;
    vec3 q2 = q + vec3(warp);
    float n = fbm3(q2);
    float d = smoothstep(0.25, 0.62, n);
    return d * 1.4;
}

vec3 render_scene() {
    vec2 uv = v_uv;
    vec3 ro = vec3(sin(u_time * 0.05) * 0.5, cos(u_time * 0.04) * 0.3, -u_time * 0.4);
    vec3 fwd = vec3(0.0, 0.0, -1.0);
    vec3 rd = camRayLook(uv, ro, ro + fwd, vec3(0.0, 1.0, 0.0), radians(60.0));

    float t = 0.2;
    float dt = 0.18;
    float trans = 1.0;
    vec3 acc = vec3(0.0);
    vec3 lightDir = normalize(vec3(-0.5, 0.6, -0.4));
    for (int i = 0; i < 70; i++) {
        vec3 p = ro + rd * t;
        float dens = cloudDensity(p);
        if (dens > 0.005) {
            float shadow = 0.0;
            for (int s = 0; s < 3; s++) {
                vec3 sp = p + lightDir * (0.6 + float(s) * 0.9);
                shadow += cloudDensity(sp) * 0.55;
            }
            float lit = exp(-shadow * 1.2);
            float mu = dot(rd, lightDir);
            float hg = (1.0 - 0.6 * 0.6) / pow(1.0 + 0.36 - 1.2 * mu, 1.5);
            vec3 lightCol = GREEN * 1.55;
            vec3 baseCol = mix(GREEN_DEEP * 0.5, lightCol * (0.7 + 0.4 * hg), lit);
            float absorb = dens * dt;
            acc += trans * baseCol * absorb * 2.6;
            trans *= exp(-absorb * 2.0);
            if (trans < 0.02) break;
        }
        t += dt;
        if (t > 22.0) break;
    }
    vec3 bg = GREEN_DEEP * 0.45;
    vec3 col = acc + trans * bg;
    // v22: rango radial + hue travel (ver bloom; versión suave para humo).
    vec2 uvh22 = (v_uv - 0.5) * vec2(u_aspect, 1.0);
    col *= mix(1.18, 0.62, smoothstep(0.15, 1.05, length(uvh22)));
    float lumh22 = dot(col, vec3(0.299, 0.587, 0.114));
    col *= mix(vec3(0.86, 1.02, 1.16), vec3(1.06, 1.02, 0.84),
               smoothstep(0.03, 0.20, lumh22));
    // v19: lift sutil del piso de luma. La zona Y 28-46 del humo es donde
    // VP9 deja bloques planos visibles (Weber: a Y=30 un step de 1 nivel
    // se percibe ~2x más que a Y=50). Sube el piso sin cambiar el carácter
    // y ataca también el reclamo "oscuros en YouTube".
    col = col * 1.10 + vec3(0.008);
    // v17: atmósfera de baja frecuencia (anti-banding estructural, versión
    // suave — sin tocar contraste para no romper la continuidad con bloom).
    // El user reportó banding "desde 4:20" = cola del humo. Ver bloom v17.
    vec2 auv = (v_uv - 0.5) * vec2(u_aspect, 1.0);
    float atmo1 = fbm3(vec3(auv * 7.0, u_time * 0.020));
    float atmo2 = fbm3(vec3(auv * 2.6 + 13.7, u_time * 0.013));
    // v18: + octava media (~80-160px) y amp 0.18 — el humo es la escena que
    // peor macroblockeaba en el emulado (4:12: 89% wide, plateau 544px) y
    // es la que mejor tolera textura visible (es humo).
    float atmo3 = fbm3(vec3(auv * 27.0, u_time * 0.031));
    float amod = (atmo1 - 0.5) * 0.42 + (atmo2 - 0.5) * 0.26 + (atmo3 - 0.5) * 0.32;
    col *= 1.0 + amod * 0.18;
    // v21: componente ADITIVO en darks profundos. El multiplicativo aporta
    // ~nada donde col≈0.05 (master v20 midió 78-90% wide en 3:32-4:02).
    // Esto es estructura ABSOLUTA (±4-5 niveles) que rompe bandas en
    // cualquier cadena: VLC, YouTube, TV.
    float lum_h = dot(col, vec3(0.299, 0.587, 0.114));
    // v21b: octava FINA (~40-80px) solo para el aditivo de darks — es la
    // escala que rompe plateaus de verdad (las gruesas solo los desplazan).
    float atmo4 = fbm3(vec3(auv * 55.0, u_time * 0.043));
    float amod_f = amod * 0.6 + (atmo4 - 0.5) * 0.4;
    col += vec3(amod_f * 0.035 * (1.0 - smoothstep(0.05, 0.18, lum_h)));
    col *= (1.0 + 0.06 * u_rms_smooth);
    return col;
}

void main() {
    vec3 col = render_scene();
    fragColor = vec4(finalize(col), 1.0);
}
"""

# ─── Scene 4: BLOOM — flor 2D que crece y luego CIERRA (sin bastones) ──
# v3 fix #9: el bloom dura 49s (263-312). Sube radio hasta ~33s (296)
# y después CIERRA progresivamente hasta 49s (312), con el centro
# dejando un brillo intenso (entrega al portal a través de la luz).
SCENE_BLOOM = COMMON_GLSL + """
float cloudDensity(vec3 p) {
    vec3 q = p * 0.45 + vec3(u_time * 0.06, u_time * 0.03, -u_time * 0.05);
    float warp = fbm3_2(q * 0.5) * 1.3;
    vec3 q2 = q + vec3(warp);
    float n = fbm3(q2);
    float d = smoothstep(0.25, 0.62, n);
    return d * 1.4;
}

float roseFlower(vec2 uv2, float radius, float petals, float sharpness) {
    float th = atan(uv2.y, uv2.x);
    float r  = length(uv2);
    float rose = abs(cos(petals * th * 0.5));
    float edge = radius * (0.35 + 0.65 * rose);
    float mask = 1.0 - smoothstep(edge - 0.02, edge + 0.02 * sharpness, r);
    return mask;
}

vec3 render_scene() {
    vec2 uv = v_uv;

    // Fondo humo más tenue
    vec3 ro = vec3(sin(u_time * 0.05) * 0.5, cos(u_time * 0.04) * 0.3, -u_time * 0.4);
    vec3 fwd = vec3(0.0, 0.0, -1.0);
    vec3 rd = camRayLook(uv, ro, ro + fwd, vec3(0.0, 1.0, 0.0), radians(60.0));
    float tF = 0.2;
    float dtF = 0.22;
    float trans = 1.0;
    vec3 acc = vec3(0.0);
    vec3 lightDir = normalize(vec3(-0.5, 0.6, -0.4));
    for (int i = 0; i < 40; i++) {
        vec3 p = ro + rd * tF;
        float dens = cloudDensity(p);
        if (dens > 0.005) {
            float shadow = cloudDensity(p + lightDir * 1.0) * 0.55;
            float lit = exp(-shadow * 1.2);
            vec3 baseCol = mix(GREEN_DEEP * 0.5, GREEN * 1.4, lit);
            float absorb = dens * dtF;
            acc += trans * baseCol * absorb * 2.3;
            trans *= exp(-absorb * 1.8);
            if (trans < 0.05) break;
        }
        tF += dtF;
        if (tF > 16.0) break;
    }
    vec3 col = acc + trans * (GREEN_DEEP * 0.4);
    col *= mix(1.0, 0.45, u_scene_t);

    vec2 uv2 = (v_uv - 0.5);
    uv2.x *= u_aspect;

    // v5 fix #7: mandala empieza a CERRAR a 4:51 (no 4:57).
    // Bloom span: 263-312s (49s). 4:51 = 291s → progress (291-263)/49 = 0.57.
    // Cierre se completa a 4:58 (~0.90) para que entregue luz al portal.
    float open_phase  = smoothstep(0.0, 0.57, u_scene_t);
    float close_phase = smoothstep(0.57, 0.90, u_scene_t);
    // bloom_k = open mientras no cierra, después decrece
    float bloom_k = open_phase * (1.0 - close_phase);

    float radius = 0.05 + bloom_k * 0.50;
    float petals = 6.0 + 6.0 * bloom_k;
    float sharpness = mix(2.5, 1.2, bloom_k);

    float m1 = roseFlower(uv2, radius, petals, sharpness);
    vec2 uv2b = vec2(cos(0.4) * uv2.x - sin(0.4) * uv2.y,
                     sin(0.4) * uv2.x + cos(0.4) * uv2.y);
    float m2 = roseFlower(uv2b, radius * 0.65, petals + 2.0, sharpness);

    // Core glow crece monotónicamente durante TODO el bloom → al final
    // (t=1.0) el centro es muy brillante (fix #10: portal entra por LUZ).
    float core_r = length(uv2);
    float core_intensity = u_scene_t;
    float core_glow = exp(-core_r * (10.0 - 6.0 * bloom_k - 3.0 * close_phase))
                    * core_intensity;

    vec3 petal_col = mix(GREEN_DEEP * 0.8, GREEN * 1.5, bloom_k);
    petal_col = mix(petal_col, mix(GREEN, AMBER * 0.7, 0.15) * 1.4, bloom_k * 0.6);
    vec3 core_col = mix(GREEN * 1.2, mix(GREEN * 1.5, AMBER * 1.2, 0.4), bloom_k);

    col += petal_col * m1 * (0.35 + 0.65 * bloom_k);
    col += petal_col * m2 * (0.18 + 0.30 * bloom_k);
    col += core_col * core_glow * (1.6 + 2.5 * close_phase);
    // En la fase de cierre, el verde-amber del core se vuelve casi blanco
    // (luz pura — fix #10 prep)
    col += vec3(0.9, 1.0, 0.7) * core_glow * close_phase * 0.9;

    float halo = exp(-pow(max(core_r - radius, 0.0) * 5.0, 2.0)) * 0.35 * bloom_k;
    col += GREEN * halo;

    // ── v22: RANGO TONAL REAL + HUE TRAVEL ─────────────────────────────
    // El fondo del bloom era casi plano (12-24 niveles en toda la pantalla)
    // → contornos de cuantización cada ~160px, lo MAS visible que existe
    // (screenshot del user 2026-06-12, líneas topográficas). Dos armas:
    // 1) gradiente radial deliberado: esquinas profundas, centro luminoso →
    //    50+ niveles → contornos <40px que se funden perceptualmente.
    float rr22 = length(uv2);
    col *= mix(1.28, 0.55, smoothstep(0.10, 1.05, rr22));
    // 2) hue travel: el tono viaja con la luminancia (teal profundo en
    //    darks → verde cálido cerca del halo). Un contorno de luma puro
    //    desaparece cuando el color cambia con él.
    float lum22 = dot(col, vec3(0.299, 0.587, 0.114));
    col *= mix(vec3(0.84, 1.02, 1.20), vec3(1.08, 1.02, 0.80),
               smoothstep(0.03, 0.22, lum22));

    // ── v17 FASE 2 (docs/video/27, variante C validada en stills) ──────
    // Anti-banding ESTRUCTURAL. El bloom era un gradiente puro: a 4:25 el
    // frame entero vivía en Y 60-91 (31 niveles → bandas de ~800px post-
    // YouTube). El grain per-pixel (v13-v16) no sobrevive al VP9 de YT;
    // la estructura de BAJA frecuencia espacial (~250-600px en 4K) sí —
    // vive en los coeficientes DCT bajos que todo encoder preserva.
    // Métrica wide (detector v12): 38.9% → 4.5% en t=4:25.
    vec2 auv = (v_uv - 0.5) * vec2(u_aspect, 1.0);
    float atmo1 = fbm3(vec3(auv * 7.0, u_time * 0.020));
    float atmo2 = fbm3(vec3(auv * 2.6 + 13.7, u_time * 0.013));
    // v18: + octava media (~80-160px), ver humo.
    float atmo3 = fbm3(vec3(auv * 27.0, u_time * 0.031));
    float atmo_mod = (atmo1 - 0.5) * 0.42 + (atmo2 - 0.5) * 0.26 + (atmo3 - 0.5) * 0.32;
    col *= 1.0 + atmo_mod * 0.18;
    // v21: aditivo en darks profundos (ver humo).
    float lum_b = dot(col, vec3(0.299, 0.587, 0.114));
    float atmo4b = fbm3(vec3(auv * 55.0, u_time * 0.043));
    float amod_fb = atmo_mod * 0.6 + (atmo4b - 0.5) * 0.4;
    col += vec3(amod_fb * 0.035 * (1.0 - smoothstep(0.05, 0.18, lum_b)));
    // Apertura de rango tonal: contraste suave alrededor de la media
    // oscura (más rango = menos px por nivel = sin bandas).
    float cm = 0.085;
    col = (col - cm) * 1.45 + cm;

    col *= (1.0 + 0.05 * u_rms_smooth);
    return col;
}

void main() {
    vec3 col = render_scene();
    fragColor = vec4(finalize(col), 1.0);
}
"""

# ─── Scene 5: PORTAL — kaleidoscopio MORPHEANTE dinámico (fix #11) ─────
# v3 fix #10/#11: reemplaza el chamber estático. La cámara avanza
# por un kaleidoscopio fractal que MORPHEA en tiempo real (los parámetros
# del fold/IFS cambian con u_time → la pared NO es estática). Además
# la cámara ROTA en roll continuamente. Sin paredes de cartón.
SCENE_PORTAL = COMMON_GLSL + """
// Inicio: cámara YA está dentro de la luz (continuación del bloom-light).
// Durante 68s: navega un fractal foldedo donde:
//   - El parámetro de fold (offset vec3) oscila con sin(u_time*X).
//   - La rotación entre folds barre 0 → 2π.
//   - La cámara hace roll continuo (no estático).
// Esto produce un patrón que MORPHEA orgánicamente.

vec3 render_scene() {
    vec2 uv = v_uv;
    float t = u_time;
    float st = u_scene_t;

    // v4 fix #9: a 5:49 (t_global=349) el ritmo se enrosca → spin acelera
    // + hue shift dramatic. portal scene empieza a t_global=312, así que
    // local_t = 349 - 312 = 37s. El "enrolling" arranca a local_t=37 y se
    // intensifica gradualmente hasta el fin del portal (local_t=68).
    float enroll_k = smoothstep(37.0, 47.0, t);   // ramp 5:49 → 5:59
    // boost de roll (rotación de cámara) durante enroll
    float roll_speed = 0.25 + enroll_k * 0.85;
    float roll = t * 0.25 + enroll_k * (t - 37.0) * 0.85;
    vec3 ro = vec3(sin(t * 0.13) * 0.15, cos(t * 0.11) * 0.12, -t * 0.45);
    vec3 fwd = vec3(sin(t * 0.07) * 0.08, cos(t * 0.06) * 0.06, -1.0);
    vec3 up  = vec3(sin(roll), cos(roll), 0.0);
    vec3 rd = camRayLook(uv, ro, ro + normalize(fwd), up, radians(72.0));

    // Folding params MORPHEANTES — clave de fix #11
    // Durante enroll: morph speed se DUPLICA (pattern morphea más rápido)
    float morph_speed = 1.0 + enroll_k * 1.0;
    float ts = t * morph_speed;
    vec3 fold_off = vec3(
        0.8 + 0.35 * sin(ts * 0.20),
        0.6 + 0.30 * sin(ts * 0.17 + 1.3),
        0.5 + 0.25 * sin(ts * 0.13 + 2.1)
    );
    float scale_mod = 1.32 + 0.10 * sin(ts * 0.11);
    // rot_a acelera con enroll
    float rot_a = t * 0.08 + enroll_k * (t - 37.0) * 0.30;

    float tt = 0.1;
    vec3 col = vec3(0.0);
    float trans = 1.0;
    for (int i = 0; i < 70; i++) {
        vec3 p = ro + rd * tt;
        vec3 q = p;
        for (int j = 0; j < 5; j++) {
            q = abs(q);
            if (q.x < q.y) q.xy = q.yx;
            if (q.x < q.z) q.xz = q.zx;
            // rotación entre folds (morpheante)
            float ca = cos(rot_a + float(j) * 0.3);
            float sa = sin(rot_a + float(j) * 0.3);
            q.xz = mat2(ca, -sa, sa, ca) * q.xz;
            q = q * scale_mod - fold_off;
        }
        // emisión por proximidad al "core" del espacio plegado
        float emission = exp(-length(q) * 0.4) * 0.55;
        float wallD = length(q.xy);
        float wallEm = exp(-pow(wallD - 1.0, 2.0) * 0.6) * 0.85;
        // anillos en Z folded
        float rings = 0.5 + 0.5 * cos(q.z * 3.5);
        rings = pow(rings, 4.0);
        // luminancia ambar en rim
        float amber_rim = exp(-pow(wallD - 1.4, 2.0) * 1.2) * 0.45;
        col += trans * (
              GREEN * (emission + wallEm * 1.3 + rings * 0.45)
            + mix(GREEN, AMBER * 0.7, 0.35) * amber_rim
        ) * 0.32;
        trans *= 0.94;
        if (trans < 0.04) break;
        tt += 0.16;
        if (tt > 14.0) break;
    }

    // Glow central — siempre presente, asegura que NUNCA haya negro
    // (fix #10 supporting: el frame nunca colapsa a negro).
    vec2 vc = v_uv - 0.5; vc.x *= u_aspect;
    float rv = length(vc);
    // Al ENTRAR (st<0.1) el centro es muy brillante (continúa de bloom-light)
    float entry_boost = (1.0 - smoothstep(0.0, 0.10, st)) * 1.8;
    col += GREEN * exp(-rv * 3.5) * (0.45 + entry_boost);
    col += vec3(0.85, 1.0, 0.62) * pow(exp(-rv * 6.0), 1.8) * (0.30 + entry_boost * 0.5);

    // v4 fix #9: hue shift dramatic durante enroll (5:49+)
    if (enroll_k > 0.01) {
        vec3 hsv = rgb2hsv(col);
        hsv.x = fract(hsv.x + enroll_k * 0.08 * sin(t * 0.6));
        hsv.y = clamp(hsv.y * (1.0 + enroll_k * 0.20), 0.0, 1.0);
        col = hsv2rgb(hsv);
    }

    // Audio reactivity: respiración lenta + flux
    col *= (1.0 + 0.10 * u_rms_smooth + 0.08 * u_flux);

    // v17: atmósfera de baja frecuencia (anti-banding, wide 14-32% en 5:12-5:52)
    vec2 auv17 = (v_uv - 0.5) * vec2(u_aspect, 1.0);
    float at1 = fbm3(vec3(auv17 * 7.0, u_time * 0.020));
    float at2 = fbm3(vec3(auv17 * 2.6 + 13.7, u_time * 0.013));
    // v18: octava de frecuencia MEDIA (~80-160px). Las bajas (250-600px)
    // cambian <1 nivel por bloque de 16-32px y VP9 colapsa los DC igual
    // (macroblocking visto en el emulado 4:12). Esta escala fuerza diffs
    // de 2-3 niveles entre bloques vecinos.
    float at3 = fbm3(vec3(auv17 * 27.0, u_time * 0.031));
    col *= 1.0 + ((at1 - 0.5) * 0.42 + (at2 - 0.5) * 0.26 + (at3 - 0.5) * 0.32) * 0.12;

    // Vignette
    col *= 1.0 - smoothstep(0.65, 1.2, rv) * 0.25;
    return col;
}

void main() {
    vec3 col = render_scene();
    fragColor = vec4(finalize(col), 1.0);
}
"""

# ─── Scene 6: PARTIDA — espiral magnetar (fix #12: ahora va PRIMERO) ───
# Sin cambios estéticos — es la sección que al artista LE GUSTA.
SCENE_PARTIDA = COMMON_GLSL + """
float spiralEmission(vec3 p, float a, float b, float thickness) {
    vec2 q = p.xy;
    float r = length(q);
    if (r < 0.05) return 0.0;
    float theta = atan(q.y, q.x);
    float thetaCurve = log(r / a) / b;
    float dtheta = mod(theta - thetaCurve + 3.14159, 3.14159) - 1.57079;
    float arc = abs(r * dtheta);
    float em = exp(-(arc * arc) / (thickness * thickness));
    em *= exp(-r * 0.18);
    return em;
}

vec3 render_scene() {
    vec2 uv = v_uv;
    float k = clamp(u_scene_t, 0.0, 1.0);
    // v4 fix #10: la escena DEBE arrancar ya en movimiento.
    // - cam_drift: oscilación leve YA presente desde t=0 (sin/cos no dependen de k)
    // - z avance YA en marcha: bias inicial (z baja desde 4.0 al arranque)
    // - spiral rotation también ya con velocidad (u_time*0.22 desde t=0)
    // - Plus: roll de cámara desde el frame 0 → motion perceptible
    float roll = u_time * 0.15;
    vec3 up_v = vec3(sin(roll) * 0.10, cos(roll) * 0.99, sin(roll) * 0.05);
    vec3 ro = vec3(sin(u_time * 0.35) * 0.35,
                   cos(u_time * 0.28) * 0.22,
                   4.0 - 2.5 * k);
    vec3 target = vec3(sin(u_time * 0.18) * 0.10,
                       cos(u_time * 0.14) * 0.08,
                       -4.0);
    vec3 rd = camRayLook(uv, ro, target, normalize(up_v), radians(55.0));

    float a = 0.18;
    float b = 0.30;
    float thickness = mix(0.20, 0.35, k);
    float t = 0.0;
    float dt = 0.30;
    vec3 acc = vec3(0.0);
    float trans = 1.0;
    for (int i = 0; i < 50; i++) {
        vec3 p = ro + rd * t;
        // spin más rápido desde el inicio (motion ya en marcha)
        float ang = u_time * 0.35;
        float ca = cos(ang), sa = sin(ang);
        vec3 pr = vec3(ca * p.x - sa * p.y, sa * p.x + ca * p.y, p.z);
        float zMask = exp(-pow(pr.z / 4.5, 2.0));
        float em = spiralEmission(pr, a, b, thickness) * zMask;
        float fogDens = 0.05 + 0.03 * fbm3_2(p * 0.4);
        vec3 emCol = GREEN * 1.8;
        acc += trans * emCol * em * dt * 1.8;
        trans *= exp(-fogDens * dt * 0.5);
        if (trans < 0.05) break;
        t += dt;
        if (t > 16.0) break;
    }
    vec3 bg = GREEN_DEEP * 0.45;
    vec3 col = bg * trans + acc;

    vec2 vc = v_uv - 0.5; vc.x *= u_aspect;
    float rv = length(vc);
    col += GREEN * exp(-rv * 5.5) * 0.30 * (0.4 + 0.6 * k);
    col += vec3(0.8, 1.0, 0.6) * pow(exp(-rv * 8.0), 1.5) * 0.18 * k;

    // v17: atmósfera de baja frecuencia (anti-banding, wide hasta 33% en 7:22+)
    vec2 auv17 = (v_uv - 0.5) * vec2(u_aspect, 1.0);
    float at1 = fbm3(vec3(auv17 * 7.0, u_time * 0.020));
    float at2 = fbm3(vec3(auv17 * 2.6 + 13.7, u_time * 0.013));
    // v18: octava de frecuencia MEDIA (~80-160px). Las bajas (250-600px)
    // cambian <1 nivel por bloque de 16-32px y VP9 colapsa los DC igual
    // (macroblocking visto en el emulado 4:12). Esta escala fuerza diffs
    // de 2-3 niveles entre bloques vecinos.
    float at3 = fbm3(vec3(auv17 * 27.0, u_time * 0.031));
    col *= 1.0 + ((at1 - 0.5) * 0.42 + (at2 - 0.5) * 0.26 + (at3 - 0.5) * 0.32) * 0.12;

    return col;
}

void main() {
    vec3 col = render_scene();
    fragColor = vec4(finalize(col), 1.0);
}
"""

# ─── Scene 7: AFUERA — humo amarillo con beams (fix #12: ahora ÚLTIMO) ──
SCENE_AFUERA = COMMON_GLSL + """
float beamMask(vec3 p, vec3 origin, vec3 dir, float halfWidth) {
    vec3 r = p - origin;
    vec3 perp = r - dir * dot(r, dir);
    float d = length(perp);
    return exp(-(d * d) / (halfWidth * halfWidth));
}

vec3 render_scene() {
    vec2 uv = v_uv;
    vec3 ro = vec3(sin(u_time * 0.04) * 0.4, cos(u_time * 0.03) * 0.25, -u_time * 0.18);
    vec3 fwd = vec3(0.0, 0.0, -1.0);
    vec3 rd = camRayLook(uv, ro, ro + fwd, vec3(0.0, 1.0, 0.0), radians(62.0));

    vec3 b1_o = vec3(-3.0, 2.5, -u_time * 0.5);
    vec3 b1_d = normalize(vec3(0.5, -0.3, -1.0));
    vec3 b2_o = vec3(2.5, 2.0, -u_time * 0.5 - 1.0);
    vec3 b2_d = normalize(vec3(-0.4, -0.25, -1.0));
    vec3 b3_o = vec3(0.0, -3.0, -u_time * 0.5 - 0.5);
    vec3 b3_d = normalize(vec3(0.1, 0.6, -1.0));
    vec3 b4_o = vec3(-1.0, 0.0, -u_time * 0.5 - 3.0);
    vec3 b4_d = normalize(vec3(0.6, 0.4, -1.0));

    float t = 0.2;
    float dt = 0.35;
    vec3 acc = vec3(0.0);
    float trans = 1.0;
    for (int i = 0; i < 45; i++) {
        vec3 p = ro + rd * t;
        float fogDens = 0.08 + 0.06 * fbm3_2(p * 0.30 + vec3(u_time * 0.03));
        float e1 = beamMask(p, b1_o, b1_d, 1.2);
        float e2 = beamMask(p, b2_o, b2_d, 1.0);
        float e3 = beamMask(p, b3_o, b3_d, 1.4);
        float e4 = beamMask(p, b4_o, b4_d, 0.9);
        float em = e1 + e2 * 0.85 + e3 * 0.75 + e4 * 0.95;
        em *= (0.6 + 0.4 * sin(u_time * 0.25 + p.z * 0.1));
        vec3 emCol = mix(GREEN * 1.4, vec3(0.85, 1.0, 0.62), 0.4);
        acc += trans * emCol * em * fogDens * dt * 1.6;
        trans *= exp(-fogDens * dt * 0.6);
        if (trans < 0.04) break;
        t += dt;
        if (t > 18.0) break;
    }
    vec3 bg = GREEN_DEEP * 0.55;
    vec3 col = bg * trans + acc;
    col *= (1.0 + 0.05 * u_rms_smooth);

    vec2 vc = v_uv - 0.5; vc.x *= u_aspect;
    float rv = length(vc);
    col *= 1.0 - smoothstep(0.55, 1.15, rv) * 0.25;

    // v17: atmósfera de baja frecuencia (anti-banding, cierre 7:52 wide 19%)
    vec2 auv17 = (v_uv - 0.5) * vec2(u_aspect, 1.0);
    float at1 = fbm3(vec3(auv17 * 7.0, u_time * 0.020));
    float at2 = fbm3(vec3(auv17 * 2.6 + 13.7, u_time * 0.013));
    // v18: octava de frecuencia MEDIA (~80-160px). Las bajas (250-600px)
    // cambian <1 nivel por bloque de 16-32px y VP9 colapsa los DC igual
    // (macroblocking visto en el emulado 4:12). Esta escala fuerza diffs
    // de 2-3 niveles entre bloques vecinos.
    float at3 = fbm3(vec3(auv17 * 27.0, u_time * 0.031));
    col *= 1.0 + ((at1 - 0.5) * 0.42 + (at2 - 0.5) * 0.26 + (at3 - 0.5) * 0.32) * 0.12;
    return col;
}

void main() {
    vec3 col = render_scene();
    fragColor = vec4(finalize(col), 1.0);
}
"""

SCENE_SHADERS = {
    "nacer":   SCENE_NACER,
    "tunel":   SCENE_TUNEL,
    "humo":    SCENE_HUMO,
    "bloom":   SCENE_BLOOM,
    "portal":  SCENE_PORTAL,
    "partida": SCENE_PARTIDA,
    "afuera":  SCENE_AFUERA,
}

# Composite shader. Modes:
#  0 = mix lineal
#  1 = edge_invade (humo desde bordes — no usado en v4)
#  2 = eye_close — DEPRECADO en v4 (era fade-to-black)
#  3 = light_flash — fix #10: fade a→LIGHT (whiteout), LIGHT→b. NUNCA black.
COMPOSITE_GLSL = """
#version 330 core
in vec2 v_uv;
out vec4 fragColor;
uniform sampler2D u_tex_a;
uniform sampler2D u_tex_b;
uniform float u_w;             // 0..1 across the xfade window
uniform float u_mode;          // 0 = mix, 1 = edge_invade, 2 = eye_close, 3 = light_flash
uniform float u_aspect;
void main() {
    vec3 a = texture(u_tex_a, v_uv).rgb;
    vec3 b = texture(u_tex_b, v_uv).rgb;
    if (u_mode > 2.5) {
        // LIGHT_FLASH (fix #10): a -> light burst -> b. NUNCA negro.
        // En el medio (w≈0.5) la pantalla es casi blanca (verde-blanco).
        // Curva: brillo crece a w=0.5, decrece a 0/1.
        // No es un sustain — es un pestañeo de LUZ corto.
        float w = u_w;
        // flash bell-shape: max en w=0.5
        float flash = exp(-pow((w - 0.5) / 0.18, 2.0));
        // light color: verde claro tirando a blanco
        vec3 light_col = vec3(0.92, 1.0, 0.78);
        // base mix tradicional para preservar continuidad
        vec3 base_mix = mix(a, b, smoothstep(0.0, 1.0, w));
        // boost de luz aditivo en el flash
        vec3 c = base_mix + light_col * flash * 0.85;
        // y un slight tint hacia la luz en el medio
        c = mix(c, light_col, flash * 0.40);
        fragColor = vec4(c, 1.0);
    } else if (u_mode > 1.5) {
        // EYE-CLOSE (deprecado v4) — mantenido por compat
        float w = u_w;
        float close = 1.0 - smoothstep(0.0, 0.45, w);
        float open  = smoothstep(0.55, 1.0, w);
        vec3 c = a * close + b * open;
        fragColor = vec4(c, 1.0);
    } else if (u_mode > 0.5) {
        vec2 d = vec2(min(v_uv.x, 1.0 - v_uv.x),
                      min(v_uv.y, 1.0 - v_uv.y));
        float edgeDist = min(d.x, d.y);
        float threshold = mix(-0.02, 0.55, u_w);
        float m = 1.0 - smoothstep(threshold - 0.10, threshold + 0.05, edgeDist);
        vec3 c = mix(a, b, m);
        fragColor = vec4(c, 1.0);
    } else {
        vec3 c = mix(a, b, u_w);
        fragColor = vec4(c, 1.0);
    }
}
"""

# ───── Control loading ──────────────────────────────────────────────────
def load_control(npz_path: Path, n_video_frames: int, video_fps: int):
    if not npz_path.exists():
        print(f"[warn] no control track at {npz_path}", file=sys.stderr)
        z = np.full(n_video_frames, 0.0, dtype=np.float32)
        return {k: z.copy() for k in (
            "rms", "rms_sub", "rms_low", "rms_air", "flux", "onset", "centroid",
            "rms_smooth", "rms_sub_smooth", "rms_air_smooth", "onset_smooth",
            "flux_smooth", "sparkle",
        )}
    d = np.load(npz_path)
    src_fps = float(d['fps'])
    n_src = len(d['rms'])
    t_video = np.arange(n_video_frames) / video_fps
    t_src = np.arange(n_src) / src_fps
    out = {}
    for k in ("rms", "rms_sub", "rms_low", "rms_air", "flux", "onset", "centroid"):
        src = d[k].astype(np.float32)
        out[k] = np.interp(t_video, t_src, src).astype(np.float32)

    def smooth(x, win):
        win = max(1, int(win))
        kernel = np.ones(win, dtype=np.float32) / win
        return np.convolve(x, kernel, mode='same').astype(np.float32)

    out['rms_smooth']     = smooth(out['rms'],     int(0.5 * video_fps))
    out['rms_sub_smooth'] = smooth(out['rms_sub'], int(0.3 * video_fps))
    out['rms_air_smooth'] = smooth(out['rms_air'], int(0.5 * video_fps))
    out['onset_smooth']   = smooth(out['onset'],   int(0.15 * video_fps))
    out['flux_smooth']    = smooth(out['flux'],    int(2.0 * video_fps))
    fs = out['flux_smooth']
    p5, p95 = float(np.percentile(fs, 5)), float(np.percentile(fs, 95))
    if p95 - p5 > 1e-6:
        out['flux_smooth'] = np.clip((fs - p5) / (p95 - p5), 0.0, 1.0).astype(np.float32)

    centroid = out['centroid']
    c_long = smooth(centroid, int(2.0 * video_fps))
    spike = np.clip(centroid - c_long * 1.4, 0.0, 1.0)
    spike_max = float(np.percentile(spike, 99))
    if spike_max > 1e-6:
        spike = np.clip(spike / spike_max, 0.0, 1.0)
    spike = smooth(spike, int(0.10 * video_fps))
    spike = np.clip(spike * 3.0, 0.0, 1.0).astype(np.float32)
    out['sparkle'] = spike

    print(f"[control] {n_src} @ {src_fps}fps -> {n_video_frames} @ {video_fps}fps")
    return out


# ───── Scene scheduling ─────────────────────────────────────────────────
def _xfade_for(name_a, name_b):
    return SPECIAL_XFADE.get((name_a, name_b), XFADE_S)

def _xfade_window(name_a, name_b, boundary):
    """Returns (start_s, end_s) of the xfade window.
    By default centered on boundary. ASYMMETRIC_XFADE overrides with
    (pre_seconds, post_seconds) → window = (boundary - pre, boundary + post).
    """
    key = (name_a, name_b)
    if key in ASYMMETRIC_XFADE:
        pre, post = ASYMMETRIC_XFADE[key]
        return boundary - pre, boundary + post
    xf = _xfade_for(name_a, name_b)
    return boundary - xf / 2, boundary + xf / 2

def _mode_for(name_a, name_b):
    """Returns composite mode: 0=mix, 1=edge_invade, 3=light_flash."""
    if (name_a, name_b) in LIGHT_FLASH_TRANSITIONS:
        return 3.0
    return 0.0

def scene_at(t_sec: float):
    """Returns (scene_a_idx, scene_b_idx, w_b, mode).

    Soporta xfade asimétricas (ver ASYMMETRIC_XFADE). Cuando hay xfade
    asimétrica POST-boundary, scene_a sigue rendering aunque t_sec >= e.
    Cuando es PRE-boundary, scene_b empieza a renderear antes de t_sec >= s.
    """
    n = len(SCENES)
    for i, (name, s, e) in enumerate(SCENES):
        # Outgoing xfade (this scene → next)
        if i < n - 1:
            next_name = SCENES[i + 1][0]
            x0, x1 = _xfade_window(name, next_name, e)
            if x0 <= t_sec < x1:
                w = (t_sec - x0) / max(x1 - x0, 1e-6)
                w = max(0.0, min(1.0, w))
                mode = _mode_for(name, next_name)
                return i, i + 1, w, mode
        # Incoming xfade (previous scene → this scene)
        if i > 0:
            prev_name = SCENES[i - 1][0]
            x0, x1 = _xfade_window(prev_name, name, s)
            if x0 <= t_sec < x1:
                w = (t_sec - x0) / max(x1 - x0, 1e-6)
                w = max(0.0, min(1.0, w))
                mode = _mode_for(prev_name, name)
                return i - 1, i, w, mode
        # Plain inside scene
        if s <= t_sec < e:
            return i, i, 0.0, 0.0
    return n - 1, n - 1, 0.0, 0.0


# ───── GL setup ─────────────────────────────────────────────────────────
def build_gl(width, height):
    ctx = moderngl.create_standalone_context(require=330)
    progs = {}
    for name, src in SCENE_SHADERS.items():
        prog = ctx.program(vertex_shader=VERTEX, fragment_shader=src)
        prog["u_aspect"].value = width / height
        progs[name] = prog

    composite = ctx.program(vertex_shader=VERTEX, fragment_shader=COMPOSITE_GLSL)
    composite["u_tex_a"].value = 0
    composite["u_tex_b"].value = 1
    try:
        composite["u_aspect"].value = width / height
    except KeyError:
        pass

    quad = np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype="f4")
    vbo = ctx.buffer(quad.tobytes())
    vaos = {n: ctx.vertex_array(p, [(vbo, "2f", "in_pos")]) for n, p in progs.items()}
    vao_composite = ctx.vertex_array(composite, [(vbo, "2f", "in_pos")])

    tex_a = ctx.texture((width, height), 4, dtype='f4')
    tex_b = ctx.texture((width, height), 4, dtype='f4')
    tex_out = ctx.texture((width, height), 4, dtype='f4')
    fbo_a = ctx.framebuffer(color_attachments=[tex_a])
    fbo_b = ctx.framebuffer(color_attachments=[tex_b])
    fbo_out = ctx.framebuffer(color_attachments=[tex_out])
    return {
        "ctx": ctx, "progs": progs, "vaos": vaos,
        "composite": composite, "vao_composite": vao_composite,
        "vbo": vbo,
        "tex_a": tex_a, "tex_b": tex_b, "tex_out": tex_out,
        "fbo_a": fbo_a, "fbo_b": fbo_b, "fbo_out": fbo_out,
    }


def _set_uni(prog, name, value):
    try:
        prog[name].value = value
    except KeyError:
        pass


def _event_amp(t_sec: float, events: list, window_s: float, sigma_s: float) -> float:
    """v7: Gaussian bump amplitude at t_sec given list of (time, amplitude) tuples.
    Peak occurs EXACTLY at event time (no offset). Response is symmetric:
    exp(-(dt)^2 / (2*sigma^2)) for dt in [-window/4, window]. Multiple events
    accumulate, clamped to 1. Each event has its own peak amplitude."""
    amp = 0.0
    half = window_s * 0.25  # también responde un poco antes del trigger
    for ev in events:
        if isinstance(ev, tuple):
            ev_t, ev_amp = ev
        else:
            ev_t, ev_amp = ev, 1.0
        dt = t_sec - ev_t
        if -half <= dt <= window_s:
            amp += float(ev_amp * np.exp(-(dt * dt) / (2.0 * sigma_s * sigma_s)))
    return min(amp, 1.0)


def set_scene_uniforms(prog, name, t_sec, ctrl, i, seed_val, fade):
    s, e = next((ss, ee) for nm, ss, ee in SCENES if nm == name)
    local_t = max(0.0, t_sec - s)
    scene_t = local_t / max(e - s, 1e-6)
    _set_uni(prog, "u_time", float(local_t))
    _set_uni(prog, "u_scene_t", float(scene_t))
    _set_uni(prog, "u_rms", float(ctrl["rms"][i]))
    _set_uni(prog, "u_rms_sub", float(ctrl["rms_sub_smooth"][i]))
    _set_uni(prog, "u_rms_smooth", float(ctrl["rms_smooth"][i]))
    _set_uni(prog, "u_rms_air", float(ctrl["rms_air_smooth"][i]))
    _set_uni(prog, "u_onset", float(ctrl["onset_smooth"][i]))
    _set_uni(prog, "u_flux", float(ctrl["flux_smooth"][i]))
    _set_uni(prog, "u_sparkle", float(ctrl["sparkle"][i]))
    # v6 DISCRETE event response (driven by BELL_EVENTS / HEART_EVENTS)
    sparkle_amp = _event_amp(t_sec, BELL_EVENTS,  EVENT_WINDOW_S, EVENT_SIGMA_S)
    heart_amp   = _event_amp(t_sec, HEART_EVENTS, EVENT_WINDOW_S, EVENT_SIGMA_S)
    _set_uni(prog, "u_sparkle_amp", float(sparkle_amp))
    _set_uni(prog, "u_heart_amp",   float(heart_amp))
    _set_uni(prog, "u_fade", float(fade))
    _set_uni(prog, "u_seed", float(seed_val))


def render_frame(gl, width, height, i, ctrl):
    t_sec = i / FPS
    # v5 fix #1: FADE-IN desde negro 0-5s. El artista pidió tapar el
    # arranque fulero con un fade que va entrando hasta t=5s. A t=0 todo
    # es 100% negro; a t=5 todo full. Esto hide stripes (0:08 era visible
    # incluso bajo el ovulo, pero el fade cubre todo arranque), sweep
    # (0:14, ya no hay) y cualquier glitch inicial.
    # Smoothstep 0..5 con curve suave.
    x = max(0.0, min(1.0, t_sec / 5.0))
    fade_in = x * x * (3.0 - 2.0 * x)
    fade_out = float(np.clip((DURATION_S - t_sec) / 5.0, 0.0, 1.0))
    fade = fade_in * fade_out
    seed_val = i * 47.31 + 0.91

    ai, bi, w, mode = scene_at(t_sec)
    name_a = SCENES[ai][0]
    name_b = SCENES[bi][0]

    gl["fbo_a"].use()
    gl["ctx"].clear(0.0, 0.0, 0.0, 1.0)
    set_scene_uniforms(gl["progs"][name_a], name_a, t_sec, ctrl, i, seed_val, fade)
    gl["vaos"][name_a].render(moderngl.TRIANGLE_STRIP)

    if w > 0.0001 and ai != bi:
        gl["fbo_b"].use()
        gl["ctx"].clear(0.0, 0.0, 0.0, 1.0)
        set_scene_uniforms(gl["progs"][name_b], name_b, t_sec, ctrl, i, seed_val, fade)
        gl["vaos"][name_b].render(moderngl.TRIANGLE_STRIP)
        gl["fbo_out"].use()
        gl["ctx"].clear(0.0, 0.0, 0.0, 1.0)
        gl["tex_a"].use(0)
        gl["tex_b"].use(1)
        ws = w * w * (3.0 - 2.0 * w)
        gl["composite"]["u_w"].value = float(ws)
        gl["composite"]["u_mode"].value = float(mode)
        gl["vao_composite"].render(moderngl.TRIANGLE_STRIP)
        raw = gl["fbo_out"].read(components=3, alignment=1, dtype='f4')
    else:
        raw = gl["fbo_a"].read(components=3, alignment=1, dtype='f4')

    arr = np.frombuffer(raw, dtype=np.float32).reshape(height, width, 3)
    arr_u16 = np.clip(arr * 65535.0, 0.0, 65535.0).astype('<u2')
    arr_u16 = arr_u16[::-1, :, :]
    return arr_u16.tobytes()


def render_contact(width=640, height=360, out_path=None, times=None):
    gl = build_gl(width, height)
    n_video = int(round(DURATION_S * FPS))
    ctrl = load_control(CONTROL_NPZ, n_video, FPS)
    if times is None:
        # v6 verification: hearts (12,18,22,27), bells (40,47,50,57,65,70),
        # boundary 6:00 portal→partida (358, 362), boundary 7:00 partida→
        # afuera (418, 422), plus closer (478).
        times = [12, 18, 22, 27, 40, 47, 50, 57, 65, 70,
                 358, 362, 418, 422, 478]
    frames = []
    for t_s in times:
        idx = int(t_s * FPS)
        idx = min(idx, n_video - 1)
        raw = render_frame(gl, width, height, idx, ctrl)
        u16 = np.frombuffer(raw, dtype='<u2').reshape(height, width, 3)
        arr = (u16.astype(np.uint32) * 255 // 65535).astype(np.uint8)
        frames.append((t_s, arr))
        print(f"[contact] t={t_s}s ok")
    cols = 6
    rows = (len(frames) + cols - 1) // cols
    label_h = 24
    sheet = Image.new("RGB", (width * cols, (height + label_h) * rows), (0, 0, 0))
    from PIL import ImageDraw, ImageFont
    try: font = ImageFont.load_default()
    except Exception: font = None
    draw = ImageDraw.Draw(sheet)
    for i, (t_s, arr) in enumerate(frames):
        r, c = i // cols, i % cols
        x = c * width; y = r * (height + label_h)
        img = Image.fromarray(arr, "RGB"); sheet.paste(img, (x, y))
        m = t_s // 60; s = t_s % 60
        draw.text((x + 6, y + height + 4), f"t={m:02d}:{s:02d}", fill=(180, 220, 180), font=font)
    if out_path is None:
        out_path = HERE / "contact_v3.png"
    sheet.save(out_path, compress_level=3)
    print(f"[contact] sheet -> {out_path}")


def render_full(width, height, fps, n_frames, out_mp4, audio_wav, with_audio, duration_s,
                start_s: float = 0.0):
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg no está en PATH")
    if out_mp4.exists():
        out_mp4.unlink()
    print(f"[render] {width}x{height} @ {fps}fps, {duration_s}s desde t={start_s}s = {n_frames} frames")
    print(f"[render] -> {out_mp4}")
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
        # v15: SDR DIRECTO BT.709, grain ya viene del shader (no gradfun, no noise
        # filter — esos competían con el grain del shader). Bitrate 100 Mbps VBR
        # (techo YouTube 4K) con vbv 110/200 para picos.
        "-vf", "format=yuv420p10le",
        "-c:v", "libx265", "-profile:v", "main10", "-pix_fmt", "yuv420p10le",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-x265-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709:repeat-headers=1:bitrate=100000:vbv-maxrate=110000:vbv-bufsize=200000:psy-rd=2.5:aq-strength=1.0",
        "-preset", "medium", "-r", str(fps),
    ]
    if with_audio and audio_wav.exists():
        args += ["-c:a", "aac", "-b:a", "320k", "-shortest"]
    args += ["-movflags", "+faststart", str(out_mp4)]

    print(f"[ffmpeg] writing -> {out_mp4}")
    proc = subprocess.Popen(args, stdin=subprocess.PIPE)

    gl = build_gl(width, height)
    # v17: el control SIEMPRE se carga a duración completa — render_frame
    # indexa con frame absoluto, así un render de segmento (--start) usa
    # exactamente los mismos uniforms que el render full.
    n_total = int(round(DURATION_S * fps))
    ctrl = load_control(CONTROL_NPZ, n_total, fps)
    start_frame = int(round(start_s * fps))
    t_start = time.time(); t_last = t_start
    try:
        for k in range(n_frames):
            i = min(start_frame + k, n_total - 1)
            buf = render_frame(gl, width, height, i, ctrl)
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
        if ret != 0:
            raise RuntimeError(f"ffmpeg exit {ret}")
    print(f"[done] {out_mp4}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--width", type=int, default=W)
    ap.add_argument("--height", type=int, default=H)
    ap.add_argument("--fps", type=int, default=FPS)
    ap.add_argument("--seconds", type=float, default=DURATION_S)
    ap.add_argument("--start", type=float, default=0.0,
                    help="Segundo inicial (render de segmento para iterar zonas)")
    ap.add_argument("--pretest", action="store_true",
                    help="Render full 18-frame contact sheet at 640x360")
    ap.add_argument("--no-audio", action="store_true")
    ap.add_argument("--out", type=str, default=str(OUT_MP4))
    args = ap.parse_args()
    if args.pretest:
        render_contact()
        return
    n = int(round(args.seconds * args.fps))
    render_full(args.width, args.height, args.fps, n, Path(args.out), AUDIO_WAV, not args.no_audio, args.seconds,
                start_s=args.start)


if __name__ == "__main__":
    main()
