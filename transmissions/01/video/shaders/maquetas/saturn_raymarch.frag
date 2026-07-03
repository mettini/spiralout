#version 330
// =============================================================================
//  Saturn approach — GLSL raymarched (SDF sphere + torus + dust atmosphere)
// =============================================================================
//  Técnica: ray marching de SDFs (Inigo Quilez 2008, iquilezles.org).
//  - Esfera SDF para el cuerpo del planeta.
//  - Torus SDF para los anillos (tilteado).
//  - Combinados con min() = unión de surfaces.
//  - Lambertian shading con luz direccional off-screen.
//  - Cámara dolly forward sobre eje Z (uniform u_camZ).
//  - Background = noise stars + dust gradient.
//  - Post: vignette suave + grain leve (NO chroma aberration cheap).
//
//  Aplicado a Spiral Out con paleta cosmic dust: violet dusk planet + amber
//  ring + dust blue background. Sin verde phosphor.

in vec2 v_uv;
out vec4 fragColor;

uniform vec2  u_res;
uniform float u_time;
uniform float u_camZ;       // posición Z de cámara (mueve forward al acercarse)
uniform float u_approach;   // 0..1 — proximidad (afecta detalle, atmosphere)

// ---- noise (forward — usado por SDF para displacement) ----------------------
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

// ---- SDF primitives ---------------------------------------------------------
float sdSphere(vec3 p, float r) {
    return length(p) - r;
}
float sdTorus(vec3 p, vec2 t) {
    vec2 q = vec2(length(p.xz) - t.x, p.y);
    return length(q) - t.y;
}

// Rotation matrix around X axis
mat3 rotX(float a) {
    float c = cos(a), s = sin(a);
    return mat3(1, 0, 0,  0, c, -s,  0, s, c);
}

// Scene SDF — planeta con displacement noise (no esfera perfecta) y anillos con
// múltiples bandas finas (no 2 toros precisos). Más "atmospheric body", menos CGI.
float map(vec3 p) {
    // Planet with subtle displacement = breaks perfect sphere
    float n = vnoise3(p * 4.0) - 0.5;
    float planet = sdSphere(p, 0.85 + n * 0.015);

    // Rings: múltiples bandas finas a distintos radios → da feel "dust shell"
    // en vez de "2 anillos sólidos".
    vec3 pr = rotX(0.35) * p;
    float ring1 = sdTorus(pr, vec2(1.20, 0.013));
    float ring2 = sdTorus(pr, vec2(1.28, 0.010));
    float ring3 = sdTorus(pr, vec2(1.40, 0.014));
    float ring4 = sdTorus(pr, vec2(1.52, 0.011));
    float ring5 = sdTorus(pr, vec2(1.62, 0.009));
    float rings = min(min(ring1, ring2), min(ring3, min(ring4, ring5)));
    return min(planet, rings);
}

// Identify which surface we hit (planet vs ring)
int matID(vec3 p) {
    float n = vnoise3(p * 4.0) - 0.5;
    float d_planet = sdSphere(p, 0.85 + n * 0.015);
    vec3 pr = rotX(0.35) * p;
    float d1 = sdTorus(pr, vec2(1.20, 0.013));
    float d2 = sdTorus(pr, vec2(1.28, 0.010));
    float d3 = sdTorus(pr, vec2(1.40, 0.014));
    float d4 = sdTorus(pr, vec2(1.52, 0.011));
    float d5 = sdTorus(pr, vec2(1.62, 0.009));
    float d_rings = min(min(d1, d2), min(d3, min(d4, d5)));
    if (d_planet < d_rings) return 0;
    return 1;
}

// Normal via gradient
vec3 normal(vec3 p) {
    float e = 0.002;
    vec2 h = vec2(e, 0);
    return normalize(vec3(
        map(p + h.xyy) - map(p - h.xyy),
        map(p + h.yxy) - map(p - h.yxy),
        map(p + h.yyx) - map(p - h.yyx)
    ));
}

// Background = deep cosmic dust + MULTI-LAYER PARALLAX stars
// 3 capas de estrellas a profundidad distinta. La capa cercana se mueve más
// rápido al acercarnos (proporcional a u_approach) → parallax real.
vec3 background(vec2 uv) {
    // Dust gradient
    vec3 dustNear = vec3(0.07, 0.05, 0.14);
    vec3 dustFar  = vec3(0.015, 0.018, 0.038);
    float r = length(uv - 0.5);
    vec3 col = mix(dustNear, dustFar, smoothstep(0.0, 0.75, r));

    // 3 star layers — cada una con shift proporcional a u_approach (parallax)
    for (int layer = 0; layer < 3; layer++) {
        float density = 180.0 + float(layer) * 80.0;   // capas más finas atrás
        float speed = 0.04 + float(layer) * 0.10;       // cercana se mueve más
        vec2 shift = vec2(u_approach * speed, -u_approach * speed * 0.3);
        vec2 sp = floor((uv + shift) * density);
        float s = hash(sp + float(layer) * 17.0);
        float thresh = 0.996 - float(layer) * 0.0012;   // capas atrás menos densas
        if (s > thresh) {
            float bright = (s - thresh) * 250.0 * (0.35 + 0.6 * hash(sp + 5.7));
            vec3 starCol = mix(vec3(0.6, 0.65, 0.78), vec3(0.85, 0.78, 0.55), hash(sp + 11.0));
            col += starCol * bright * (1.0 - float(layer) * 0.25);
        }
    }
    // Bruma cósmica de nubes lejanas — fbm grande, MUY tenue (no domina)
    float clouds = fbm3(vec3(uv * 1.3, u_time * 0.01));
    col += vec3(0.10, 0.07, 0.16) * smoothstep(0.55, 0.78, clouds) * 0.22;
    return col;
}

void main() {
    vec2 uv = v_uv;
    vec2 p = (uv * 2.0 - 1.0);
    p.x *= u_res.x / u_res.y;

    // ⭐ Atmospheric refraction: warpear el ray con noise de baja freq → da el
    // feel "painterly/refracted" sin perder structure. Sutil pero importante.
    float refractAmp = 0.025 * (1.0 - 0.4 * u_approach);    // más sutil al acercar
    vec2 warp = vec2(
        fbm3(vec3(uv * 2.0, u_time * 0.04)) - 0.5,
        fbm3(vec3(uv * 2.0 + 4.7, u_time * 0.04)) - 0.5
    ) * refractAmp;
    p += warp;

    // Camera: starts far (camZ ≈ 6.0), moves forward to ≈ 2.5 over u_approach
    float camZ = mix(6.0, 2.5, u_approach);
    vec3 ro = vec3(0.0, 0.15, camZ);
    vec3 rd = normalize(vec3(p, -1.6));

    float corner = (1.0 - u_approach);
    rd = normalize(rd + vec3(-0.25, 0.15, 0.0) * corner);

    // Raymarch
    float t = 0.0;
    bool hit = false;
    int mid = -1;
    vec3 pos;
    for (int i = 0; i < 96; i++) {
        pos = ro + rd * t;
        float d = map(pos);
        if (d < 0.001) { hit = true; mid = matID(pos); break; }
        if (t > 12.0) break;
        t += d * 0.85;                                 // safer than full step
    }

    vec3 col;
    if (hit) {
        vec3 n = normal(pos);
        vec3 lightDir = normalize(vec3(0.7, 0.3, 0.6)); // off-screen warm key light
        float diffuse = max(0.0, dot(n, lightDir));
        float ambient = 0.12;

        if (mid == 0) {
            // Planet — bandas latitudinales procedurales (Júpiter/Saturno style)
            // mezclando 3 escalas de noise → density real, no gradient liso.
            float lat = pos.y;                                            // latitud
            float bandPattern = sin(lat * 9.0) * 0.5 + 0.5;               // bandas primarias
            // perturbar bandas con noise 3D para que no sean líneas rectas (turbulencia)
            float turb = fbm3(pos * 3.5 + vec3(0.0, u_time * 0.01, 0.0));
            bandPattern = clamp(bandPattern + (turb - 0.5) * 0.55, 0.0, 1.0);
            // micro-detalle adicional (nubes locales)
            float clouds = fbm3(pos * 7.0 + vec3(turb, 0.0, 0.0));
            // 3 colores de banda
            vec3 bandDark   = vec3(0.20, 0.13, 0.32);
            vec3 bandMid    = vec3(0.42, 0.30, 0.58);
            vec3 bandLight  = vec3(0.62, 0.50, 0.80);
            vec3 bodyCol = mix(bandDark, bandMid, bandPattern);
            bodyCol = mix(bodyCol, bandLight, clouds * clouds * 0.55);     // peaks de claro
            col = bodyCol * (ambient + diffuse * 0.85);
            // Rim atmosférico
            float rim = pow(1.0 - max(0.0, dot(n, -rd)), 3.0);
            col += vec3(0.78, 0.62, 0.40) * rim * 0.25;
            // Day/night terminator más marcado
            float terminator = smoothstep(0.0, 0.3, diffuse);
            col *= mix(0.55, 1.0, terminator);
        } else {
            // Ring — amber, semi-translucent feel via fresnel
            float fres = pow(1.0 - abs(dot(n, -rd)), 2.0);
            vec3 ringCol = mix(vec3(0.78, 0.55, 0.22), vec3(0.95, 0.80, 0.42), fres);
            col = ringCol * (ambient + diffuse * 0.90);
            // Slight transparency = fade with depth
            float depthFade = exp(-t * 0.05);
            col *= mix(0.6, 1.0, depthFade);
        }
    } else {
        col = background(uv);
    }

    // Atmospheric haze
    float fog = 1.0 - exp(-t * 0.04);
    col = mix(col, vec3(0.05, 0.04, 0.08), fog * 0.35);

    // ⭐ Foreground dust particles — sugieren stuff between camera and planet
    // = abstracción ("no estás mirando una foto, hay material entre vos y eso").
    // Pequeños puntos brillantes que derivan, muy pocos.
    vec2 dustUV = uv * 80.0 + vec2(u_time * 0.15, -u_time * 0.05);
    float dust = hash(floor(dustUV));
    if (dust > 0.997) {
        float dustB = (dust - 0.997) * 300.0 * (0.4 + 0.6 * hash(floor(dustUV) + 8.3));
        col += vec3(0.7, 0.6, 0.45) * dustB * 0.6;
    }

    // ⭐ Bloom suave (multi-tap) — los highlights del rim y los anillos brillan
    // un poco más allá de su silueta. Da feel cinematográfico, no CGI seco.
    // 8 samples en un círculo alrededor de uv, sumamos las brightnesses.
    // Pero como no tenemos render target intermedio, este pseudo-bloom se basa
    // en la luma del propio col (no real bloom). Adecuado para feel painterly.
    float lum = dot(col, vec3(0.299, 0.587, 0.114));
    col += col * smoothstep(0.55, 0.95, lum) * 0.18;

    // Vignette suave
    float vig = 1.0 - 0.42 * length(uv - 0.5);
    col *= vig;

    // ⭐ Painterly noise overlay — leve, abstrae el feel CGI puro
    float painterly = fbm3(vec3(uv * 4.0, u_time * 0.03));
    col *= mix(0.92, 1.08, painterly);

    // Grain sutil
    float grain = (hash(uv * u_res + u_time) - 0.5) * 0.030;
    col += vec3(grain);

    col = clamp(col, 0.0, 1.0);
    col = pow(col, vec3(0.92));

    fragColor = vec4(col, 1.0);
}
