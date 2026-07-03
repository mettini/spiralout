#version 330
// =============================================================================
//  Stones / Asteroid traversal — GLSL raymarched SDF cluster (Iñigo Quilez)
// =============================================================================
//  Técnica: cluster de SDF spheres con displacement noise (= roca irregular)
//  distribuidas en un volumen 3D, raymarched, con cámara moviéndose forward.
//  El campo se "infinita" reciclando stones (cuando camZ sobrepasa una stone,
//  se reubica adelante).
//
//  Lighting: key warm (luz solar lateral) + ambient frío + rim light.
//  Background: dust cosmic con bruma de polvo cercana (motion blur sutil).
//  Veladura: noise warp + painterly overlay + grano.

in vec2 v_uv;
out vec4 fragColor;

uniform vec2  u_res;
uniform float u_time;
uniform float u_approach;     // 0..1 — proximidad acumulada (vel cámara)

// ---- noise ------------------------------------------------------------------
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

// ---- SDF stones cluster -----------------------------------------------------
//  Cada "stone" tiene posición hash-derived, size hash-derived, displacement noise.
//  Los stones se mueven hacia la cámara via shift en Z (u_time * speed).
//  Cuando un stone pasa por detrás de la cámara, su Z modular wrap lo reubica
//  adelante = stream infinito.
#define NUM_STONES 18
#define STREAM_LEN 24.0

float stoneSDF(vec3 p, vec3 center, float r, float seed) {
    vec3 q = p - center;
    // displacement: 3 octavas de noise para forma rocosa irregular
    float disp = (fbm3(q * 5.0 + vec3(seed)) - 0.5) * 0.18 * r;
    return length(q) - r + disp;
}

float sceneStones(vec3 p, out int hitID) {
    float d = 1e10;
    hitID = -1;
    // velocidad de stream (los stones VIENEN hacia la cámara)
    float streamVel = 1.8;
    float zOffset = mod(u_time * streamVel, STREAM_LEN);
    for (int i = 0; i < NUM_STONES; i++) {
        float fi = float(i);
        // position: scattered XY, distinct Z each
        vec3 base = vec3(
            (hash(vec2(fi, 7.1)) - 0.5) * 4.0,         // X spread
            (hash(vec2(fi, 13.3)) - 0.5) * 2.5,        // Y spread
            -mod(fi * 1.6 - zOffset, STREAM_LEN) + 1.0 // Z stream
        );
        float r = 0.15 + hash(vec2(fi, 23.7)) * 0.30;  // varied sizes
        float dst = stoneSDF(p, base, r, fi * 17.3);
        if (dst < d) { d = dst; hitID = i; }
    }
    return d;
}

vec3 stoneNormal(vec3 p) {
    int dummy;
    float e = 0.003;
    vec2 h = vec2(e, 0);
    return normalize(vec3(
        sceneStones(p + h.xyy, dummy) - sceneStones(p - h.xyy, dummy),
        sceneStones(p + h.yxy, dummy) - sceneStones(p - h.yxy, dummy),
        sceneStones(p + h.yyx, dummy) - sceneStones(p - h.yyx, dummy)
    ));
}

// Background = dust + sparse stars con motion blur direccional (forward)
vec3 background(vec2 uv) {
    vec3 col = mix(vec3(0.05, 0.04, 0.07), vec3(0.018, 0.015, 0.030),
                   smoothstep(0.0, 0.75, length(uv - 0.5)));
    // streak stars: las estrellas tienen un alargamiento radial (motion blur del avance)
    vec2 c = uv - 0.5;
    float r = length(c);
    float ang = atan(c.y, c.x);
    vec2 streakUV = uv + vec2(cos(ang), sin(ang)) * 0.0;     // no streak en el centro
    vec2 sp = floor(streakUV * 200.0);
    float s = hash(sp);
    if (s > 0.994) {
        col += vec3(0.65, 0.60, 0.45) * (s - 0.994) * 180.0 * (0.4 + 0.6 * hash(sp + 5.7));
    }
    // bruma cósmica
    float clouds = fbm3(vec3(uv * 1.5, u_time * 0.02));
    col += vec3(0.08, 0.06, 0.10) * smoothstep(0.50, 0.78, clouds) * 0.30;
    return col;
}

void main() {
    vec2 uv = v_uv;
    vec2 p = (uv * 2.0 - 1.0);
    p.x *= u_res.x / u_res.y;

    // Atmospheric refraction warp (sutil)
    vec2 warp = vec2(fbm3(vec3(uv * 2.5, u_time * 0.05)) - 0.5,
                     fbm3(vec3(uv * 2.5 + 4.1, u_time * 0.05)) - 0.5) * 0.020;
    p += warp;

    // Camera: fijo en origen, mirando -Z. Los stones VIENEN hacia nosotros.
    vec3 ro = vec3(0.0, 0.0, 0.0);
    vec3 rd = normalize(vec3(p, -1.5));

    // Raymarch
    float t = 0.0;
    bool hit = false;
    int stoneID = -1;
    vec3 pos;
    for (int i = 0; i < 80; i++) {
        pos = ro + rd * t;
        int curID;
        float d = sceneStones(pos, curID);
        if (d < 0.003) { hit = true; stoneID = curID; break; }
        if (t > 25.0) break;
        t += d * 0.80;
    }

    vec3 col;
    if (hit) {
        vec3 n = stoneNormal(pos);
        // Key light: warm sun lateral
        vec3 lightDir = normalize(vec3(0.6, 0.4, 0.4));
        float diffuse = max(0.0, dot(n, lightDir));
        // Fill light: cool ambient from below-side
        vec3 fillDir = normalize(vec3(-0.5, -0.3, 0.5));
        float fill = max(0.0, dot(n, fillDir)) * 0.3;
        // Rim
        float rim = pow(1.0 - max(0.0, dot(n, -rd)), 2.5);

        // Color per stone (slight variation)
        float fid = float(stoneID);
        vec3 stoneCol = mix(vec3(0.38, 0.30, 0.22), vec3(0.55, 0.42, 0.28),
                            hash(vec2(fid, 3.7)));
        // Surface micro-detail
        float micro = fbm3(pos * 18.0);
        stoneCol *= 0.7 + 0.5 * micro;

        col = stoneCol * (0.08 + diffuse * 0.9) + vec3(0.30, 0.22, 0.12) * fill;
        col += vec3(0.85, 0.70, 0.50) * rim * 0.30;

        // Depth fade — stones lejanos se desvanecen
        float depthFade = exp(-t * 0.08);
        col = mix(background(uv) * 0.5, col, depthFade);
    } else {
        col = background(uv);
    }

    // Atmospheric haze MÁS PESADO — veil de "stuff between camera and stones",
    // estas no son fotos, son atmósfera.
    float fog = 1.0 - exp(-t * 0.06);
    col = mix(col, vec3(0.04, 0.03, 0.06), fog * 0.55);

    // ⭐ Dust soft blobs (sin pixel-grid alias). Tiny gaussian-like blobs que
    // derivan radialmente. Más sutil que streaks pero limpio.
    vec2 c = uv - 0.5;
    for (int dl = 0; dl < 2; dl++) {
        float density = 28.0 + float(dl) * 14.0;
        vec2 cellSize = vec2(1.0 / density);
        vec2 dustUV = (uv + vec2(u_time * (0.30 + float(dl) * 0.20), -u_time * 0.06)) * density;
        vec2 cell = floor(dustUV);
        vec2 frac = fract(dustUV) - 0.5;
        float seedX = hash(cell + float(dl) * 31.0);
        if (seedX > 0.985) {
            // gaussian-ish soft blob (no pixel square)
            float blob = exp(-dot(frac, frac) * 18.0);
            float intensity = (seedX - 0.985) * 60.0;
            col += vec3(0.55, 0.42, 0.28) * blob * intensity;
        }
    }

    // Pseudo-bloom (reducido — menos CGI shiny)
    float lum = dot(col, vec3(0.299, 0.587, 0.114));
    col += col * smoothstep(0.60, 0.95, lum) * 0.12;

    // ⭐ Painterly overlay MÁS FUERTE — desplaza la imagen de "render 3D limpio"
    // hacia "pintura cósmica con stones flotando".
    float painterly = fbm3(vec3(uv * 4.5, u_time * 0.03));
    col *= mix(0.82, 1.20, painterly);

    // ⭐ Chromatic aberration sutil — separa canales R/G/B por ~1px en bordes
    // de luminancia alta. Hace que stones no parezcan render perfect.
    float ca = smoothstep(0.5, 0.95, lum) * 0.02;
    col.r *= 1.0 + ca;
    col.b *= 1.0 - ca;

    // Vignette suave
    float vig = 1.0 - 0.38 * length(uv - 0.5);
    col *= vig;

    // Grain
    col += (hash(uv * u_res + u_time) - 0.5) * 0.030;

    col = clamp(col, 0.0, 1.0);
    col = pow(col, vec3(0.92));

    fragColor = vec4(col, 1.0);
}
