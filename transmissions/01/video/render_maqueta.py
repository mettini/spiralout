#!/usr/bin/env python3.10
"""Render maqueta — moderngl fragment shader → ffmpeg mp4.

Renderer simple sin feedback chain ni control track — para maquetas con
GLSL fragment shaders standalone (raymarched SDF, KIFS mandalas, etc.).

Uso:
    python3.10 render_maqueta.py \
        --frag shaders/maquetas/saturn_raymarch.frag \
        --out out/maquetas/saturn_raymarch.mp4 \
        --seconds 20 --fps 30 --w 1280 --h 720

Pasa uniforms estándar: u_res, u_time, u_approach (0..1 sobre la duración).
Shaders custom pueden definir más uniforms — pasarlos vía --uniform key=value.
"""
import argparse
import subprocess
from pathlib import Path

import numpy as np
import moderngl


VERT = """
#version 330
in vec2 in_pos;
out vec2 v_uv;
void main() {
    v_uv = in_pos * 0.5 + 0.5;
    gl_Position = vec4(in_pos, 0.0, 1.0);
}
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frag", required=True, help="Path al .frag GLSL")
    ap.add_argument("--out", required=True, help="Path al .mp4 de salida")
    ap.add_argument("--seconds", type=float, default=20.0)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--w", type=int, default=1280)
    ap.add_argument("--h", type=int, default=720)
    ap.add_argument("--crf", type=int, default=18)
    args = ap.parse_args()

    W, H = args.w, args.h
    fps = args.fps
    total_frames = int(args.seconds * fps)

    ctx = moderngl.create_standalone_context()
    vbo = ctx.buffer(np.array([-1, -1, 3, -1, -1, 3], dtype="f4").tobytes())
    frag_src = Path(args.frag).read_text()
    prog = ctx.program(vertex_shader=VERT, fragment_shader=frag_src)
    vao = ctx.vertex_array(prog, [(vbo, "2f", "in_pos")])

    out_tex = ctx.texture((W, H), 3, dtype="f1")
    fbo = ctx.framebuffer([out_tex])

    if "u_res" in prog:
        prog["u_res"].value = (float(W), float(H))

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(fps), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", str(args.crf),
           "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           args.out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    print(f"render maqueta: {args.frag} → {args.out} ({W}x{H}@{fps} {args.seconds}s)")
    for i in range(total_frames):
        t = i / fps
        approach = min(1.0, t / args.seconds)
        if "u_time" in prog:
            prog["u_time"].value = t
        if "u_approach" in prog:
            prog["u_approach"].value = approach
        if "u_camZ" in prog:
            prog["u_camZ"].value = 6.0 - approach * 3.5

        fbo.use()
        ctx.clear(0.0, 0.0, 0.0, 1.0)
        vao.render(moderngl.TRIANGLES)
        frame = np.frombuffer(fbo.read(components=3), dtype="u1").reshape(H, W, 3)
        ff.stdin.write(np.flipud(frame).tobytes())

        if i % max(1, total_frames // 10) == 0:
            print(f"  {100 * i // total_frames:3d}%  frame {i}/{total_frames}")

    ff.stdin.close()
    ff.wait()
    print(f"OK → {args.out}")


if __name__ == "__main__":
    main()
