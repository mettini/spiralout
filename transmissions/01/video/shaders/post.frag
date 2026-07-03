#version 330
// Capa B — pase de GRADE final. Toma el buffer de acumulación y lo lleva a la
// imagen final: paleta (fósforo mono | color sucio), grano CRT, scanlines,
// aberración cromática, vignette, fade de cierre.

in vec2 v_uv;
out vec4 fragColor;

uniform sampler2D srcTex;
uniform vec2  u_res;
uniform float u_time;
uniform float u_grain;        // intensidad del grano
uniform float u_vignette;     // 0..1
uniform float u_collapse;     // fade de cierre (loop seam)
uniform float u_palette;      // 0 = fósforo mono ; 1 = color (passthrough)
uniform float u_chroma;       // aberración cromática (concepto B)
uniform float u_solarize;     // solarización (concepto B)

float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

void main() {
    float ca = u_chroma * length(v_uv - 0.5);

    // --- Concepto A: fósforo verde monocromo ---
    float I = pow(clamp(texture(srcTex, v_uv).r, 0.0, 3.0), 0.85);
    vec3 phos = vec3(0.651, 0.839, 0.373);              // #a6d65f
    vec3 colMono = phos * I + vec3(0.18, 0.22, 0.12) * smoothstep(1.0, 2.2, I);

    // --- Concepto B: color sucio + aberración cromática + solarización ---
    vec3 colC;
    colC.r = texture(srcTex, v_uv + vec2(ca, 0.0)).r;
    colC.g = texture(srcTex, v_uv).g;
    colC.b = texture(srcTex, v_uv - vec2(ca, 0.0)).b;
    colC = clamp(colC, 0.0, 3.0);
    colC = mix(colC, 1.0 - exp(-colC * 1.5), u_solarize); // look químico de 2001
    colC *= vec3(1.0, 0.92, 0.85);                        // mineral/terroso, no neón

    // u_palette ahora es BLEND 0..1: 0 = fósforo puro, 1 = color sucio.
    // El director lo sube en el pico del delirio (túnel/mandala) y lo baja al verde.
    vec3 col = mix(colMono, colC, clamp(u_palette, 0.0, 1.0));

    // scanlines suaves (CRT / proyección)
    float scan = 0.97 + 0.03 * sin(v_uv.y * u_res.y * 3.14159);    // sutil, evita moiré
    col *= scan;

    // grano
    float gr = (hash21(v_uv * u_res + vec2(u_time * 37.0)) - 0.5) * u_grain;
    col += gr;

    // vignette
    float vig = smoothstep(0.95, 0.25, length(v_uv - 0.5));
    col *= mix(1.0, vig, u_vignette);

    // fade de cierre → negro central (cose el loop con la apertura de Outbound)
    col *= (1.0 - 0.3 * u_collapse);

    fragColor = vec4(clamp(col, 0.0, 1.0), 1.0);
}
