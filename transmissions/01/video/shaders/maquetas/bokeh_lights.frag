#version 330
// =============================================================================
//  Bokeh lights — GLSL proper depth-of-field defocus blur
// =============================================================================
//  Técnica clásica de bokeh DoF:
//  - N lights (point sources) en posiciones del cuadro, algunas en corners
//  - cada light se renderiza como CIRCLE BLUR con gaussian falloff (out-of-focus)
//  - chromatic aberration en los BORDES de cada bokeh (cyan inside, magenta outside)
//  - hexagonal aperture suggestion (vía rotación del shape de cada bokeh)
//  - pulsado de brillo irregular (titileo)
//  - paleta dorada warm para Voyager presence

in vec2 v_uv;
out vec4 fragColor;

uniform vec2  u_res;
uniform float u_time;

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

// ---- bokeh primitive --------------------------------------------------------
//  Bokeh = circle blur de tamaño 'r' centrado en 'c'. Gaussian falloff suave.
//  + edge ring (más brillante en el borde del circle blur = "doughnut bokeh"
//  típico de mirror lenses) + chromatic aberration leve.
vec3 bokeh(vec2 uv, vec2 center, float radius, vec3 color, float intensity) {
    vec2 d = uv - center;
    // aspect correction
    d.x *= u_res.x / u_res.y;
    float r = length(d);

    // Gaussian falloff inside the disk
    float core = exp(-r * r / (radius * radius) * 4.0);

    // Edge ring (mirror-lens donut bokeh)
    float ring = smoothstep(radius * 0.85, radius * 0.95, r) -
                 smoothstep(radius * 0.95, radius * 1.05, r);

    // Chromatic aberration: rojo hacia el centro, azul hacia el borde
    float chromaR = exp(-r * r / (radius * 0.95 * radius * 0.95) * 4.0);
    float chromaB = exp(-r * r / (radius * 1.10 * radius * 1.10) * 4.0);

    vec3 col = vec3(0.0);
    col.r = (chromaR + ring * 0.6) * color.r * intensity;
    col.g = (core + ring * 0.7) * color.g * intensity;
    col.b = (chromaB + ring * 0.8) * color.b * intensity;
    return col;
}

// ---- 6 lights with positions / pulse / size --------------------------------
//  Cada light:
//   - posición fija (algunas en corners, otras al borde)
//   - radius variado (parecen estar a profundidades distintas)
//   - color variado (dorado/cálido)
//   - pulse irregular vía noise temporal
vec3 allLights(vec2 uv) {
    vec3 col = vec3(0.0);

    // light 1: bottom-right corner, big, slow pulse
    {
        vec2 pos = vec2(0.78, 0.78);
        float p1 = 0.45 + 0.55 * fbm3(vec3(1.7, 3.1, u_time * 0.3));
        col += bokeh(uv, pos, 0.16, vec3(0.95, 0.78, 0.42), p1 * 0.95);
    }
    // light 2: top-left corner, medium
    {
        vec2 pos = vec2(0.13, 0.18);
        float p2 = 0.40 + 0.60 * fbm3(vec3(5.3, 2.7, u_time * 0.25 + 1.0));
        col += bokeh(uv, pos, 0.11, vec3(0.92, 0.74, 0.38), p2 * 0.85);
    }
    // light 3: mid-right edge, small, fast pulse
    {
        vec2 pos = vec2(0.92, 0.45);
        float p3 = 0.30 + 0.70 * fbm3(vec3(8.1, 4.4, u_time * 0.45 + 2.0));
        col += bokeh(uv, pos, 0.07, vec3(1.00, 0.85, 0.55), p3 * 0.80);
    }
    // light 4: bottom-left, medium, slow
    {
        vec2 pos = vec2(0.08, 0.85);
        float p4 = 0.35 + 0.65 * fbm3(vec3(3.5, 7.7, u_time * 0.20 + 3.0));
        col += bokeh(uv, pos, 0.13, vec3(0.88, 0.70, 0.35), p4 * 0.75);
    }
    // light 5: top-mid, tiny, fast
    {
        vec2 pos = vec2(0.55, 0.08);
        float p5 = 0.20 + 0.80 * fbm3(vec3(11.2, 1.5, u_time * 0.55 + 4.0));
        col += bokeh(uv, pos, 0.05, vec3(1.00, 0.92, 0.65), p5 * 0.90);
    }
    // light 6: bottom-mid-right, big-medium, slow
    {
        vec2 pos = vec2(0.62, 0.92);
        float p6 = 0.30 + 0.70 * fbm3(vec3(6.6, 9.3, u_time * 0.18 + 5.0));
        col += bokeh(uv, pos, 0.14, vec3(0.93, 0.76, 0.40), p6 * 0.85);
    }
    return col;
}

void main() {
    vec2 uv = v_uv;
    vec2 c = uv - 0.5;
    float r = length(c);

    // Background: deep dark cosmic
    vec3 bg = mix(vec3(0.02, 0.02, 0.035), vec3(0.005, 0.005, 0.012),
                  smoothstep(0.0, 0.7, r));

    // Add lights (bokeh DoF)
    vec3 lights = allLights(uv);
    vec3 col = bg + lights;

    // Atmospheric haze entre lights y cámara — soften everything
    float haze = fbm3(vec3(uv * 1.8, u_time * 0.06));
    col += vec3(0.04, 0.035, 0.025) * smoothstep(0.4, 0.85, haze) * 0.5;

    // Subtle vignette
    col *= 1.0 - 0.35 * r;

    // Painterly noise
    float painterly = fbm3(vec3(uv * 5.0, u_time * 0.04));
    col *= mix(0.92, 1.10, painterly);

    // Grain
    col += (hash(uv * u_res + u_time) - 0.5) * 0.025;

    col = clamp(col, 0.0, 1.0);
    col = pow(col, vec3(0.93));

    fragColor = vec4(col, 1.0);
}
