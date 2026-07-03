# Distribution encoding — universal compatibility

Knowledge para encodear videos del proyecto que se vean **bien en todos
los devices**: iPhone 15 Pro / 4K UHD HDR TV / Mac Retina P3 / SD TV
vieja / mobile mid-range. Sin banding, sin crushed blacks.

> Pareja con [`20_technical_reference_videos.md`](20_technical_reference_videos.md)
> (la creación de los videos). Este doc es **delivery format**: cómo
> sale el master listo para YouTube/plataformas.

Aplicado a partir de Transmission 01 (junio 2026) tras descubrir que
los uploads SDR mostraban **zurcos en YouTube** y **TVs UHD apagaban**
los videos verde anegrado a casi negro.

---

## 1. El problema raíz

Tu render local se ve perfecto en tu monitor calibrado. Pero al subir a
YouTube, **dos cosas independientes lo arruinan**:

### Problema A — TVs y mobiles crushean blacks

Una paleta como verde anegrado (R ~0.04-0.08, G ~0.08-0.15) vive en
valores 10-30/255 después de quantización 8-bit. Muchos displays:

- **TVs UHD en modo "vivid"/"sport"**: aplican gamma agresiva → todo
  bajo ~15/255 se renderiza como negro plano. El ovulo / silueta /
  estructura dark *desaparece*.
- **Tone mapping automático en TVs HDR**: con SDR input, hacen
  expansión que destruye gradientes dark.
- **Mobile screens con auto-brightness**: en luz ambiente normal,
  crushean los darks aún más.

Tu Mac Retina calibrada NO sufre esto. Por eso vos local lo ves bien
y la TV es una mancha negra.

### Problema B — YouTube re-encodea a 8-bit SDR

Tu master local puede ser 10-bit (1024 niveles por canal). YouTube
**re-encodea a 8-bit yuv420p VP9/AV1** para SDR. 256 niveles no son
suficientes para gradientes muy lentos en zonas oscuras → posterización
visible = los "zurcos" / "ondas concéntricas".

Esto pasa **independientemente del bitrate del source**. Aunque subas a
80 Mbps 10-bit, YouTube lo tira a 8-bit.

YouTube tiene un **segundo pipeline** que preserva 10-bit:
- Source debe estar taggeado como **HDR** (HDR10 / HLG / Dolby Vision)
- YouTube usa VP9 Profile 2 / AV1 main10 → 10-bit preserved
- HDR viewers ven 10-bit directo, SDR viewers ven SDR fallback
  auto-tonemapped

---

## 2. La solución — dos partes independientes

### Parte 1 — Palette lift (fix problema A)

En el shader, antes del dither, aplicar gamma lift:

```glsl
col = pow(max(col, vec3(0.0)), vec3(0.82));
```

Esto sube los darks ~60% sin tocar los brillantes:

| Valor original | Después de `pow(0.82)` | Lift |
|---|---|---|
| 0.05 | 0.087 | +74% |
| 0.10 | 0.158 | +58% |
| 0.30 | 0.378 | +26% |
| 0.50 | 0.564 | +13% |
| 0.90 | 0.917 | +2% |

Resultado:
- Verde anegrado mantiene su **carácter** (relaciones cromáticas
  preservadas)
- Pero **sale del threshold** de crush de TVs (~10/255 → ~20-30/255)
- Bonus: más bits útiles en la zona dark → menos banding incluso en
  SDR re-encode

Donde aplicarlo en el shader: en la última función antes del dither.
Para Transmission 01:
- `outbound/render.py` función `finalize(vec3 col)` (v8 changelog)
- `crossing/render.py` inline antes del `dh1` (v3.17 changelog)

### Parte 2 — HDR HLG encoding (fix problema B)

**HLG (Hybrid Log-Gamma)** es el modo HDR diseñado para
backward-compatibility con SDR. Ventajas para nuestro caso:

1. **Viewers HDR (iPhone 15 Pro, 4K HDR TVs)**: 10-bit pipeline
   preserved → sin banding
2. **Viewers SDR (mobile no-HDR, Mac, SD TVs)**: YouTube auto-tonemap
   HLG→SDR. El "knee" de HLG está en la zona mid-bright (~0.5+). **Tu
   contenido verde anegrado vive todo abajo del knee** → tone-map
   preserva relaciones cromáticas casi idénticas a SDR puro.
3. **Cero riesgo** de color shift catastrófico para paletas dark.

**Caveat real**: si en algún video futuro hacés zonas muy brillantes
(blanco quemado, saturación alta), HLG sí podría tone-mapearlas
distinto en SDR. Para verde anegrado / ambient dark esto no aplica.

---

## 3. Pipeline ffmpeg — el comando exacto

Input: `rgb48le` raw stream desde Python (mantener pipeline 16-bit ya
existente del shader).

```bash
ffmpeg -y \
  -f rawvideo -pix_fmt rgb48le -s {W}x{H} -r {FPS} -i - \
  -ss 0 -t {duration_s} -i {audio_wav} \
  -vf "zscale=tin=709:t=linear:npl=100,format=gbrpf32le,zscale=p=2020,format=yuv420p10le,zscale=t=arib-std-b67:m=2020_ncl:r=tv" \
  -c:v libx265 -profile:v main10 -pix_fmt yuv420p10le \
  -color_primaries bt2020 -color_trc arib-std-b67 -colorspace bt2020nc \
  -x265-params "colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:repeat-headers=1:hdr-opt=1" \
  -b:v 100M -maxrate 130M -bufsize 260M \
  -preset slow \
  -c:a aac -b:a 320k -shortest \
  -movflags +faststart \
  output.mp4
```

### Anatomía del comando

| Bloque | Qué hace |
|---|---|
| `-f rawvideo -pix_fmt rgb48le -s WxH -r FPS -i -` | Recibe stream raw 16-bit del shader Python |
| `-vf "zscale=..."` | Conversión real BT.709 SDR → BT.2020 HLG: linearize → BT.2020 primaries → HLG transfer |
| `-c:v libx265 -profile:v main10` | HEVC 10-bit. Mejor compresión que x264 high10. |
| `-color_primaries / -color_trc / -colorspace` | Metadata HDR para que YouTube/players detecten |
| `-x265-params "colorprim=...repeat-headers=1"` | Re-inyectar metadata HDR en cada keyframe (algunos players solo leen al inicio) |
| `-b:v 100M -maxrate 130M -bufsize 260M` | Bitrate alto. YouTube target SDR 4K es 35-45 Mbps; nosotros mandamos 100M para que su re-encode arranque de fuente impecable |
| `-c:a aac -b:a 320k` | Audio AAC alta calidad. YouTube acepta hasta 384k. |
| `-movflags +faststart` | Mueve moov atom al inicio del archivo (faster streaming start) |

### Requisitos ffmpeg

```bash
ffmpeg -hide_banner -filters | grep -E "zscale|tonemap"
ffmpeg -hide_banner -encoders | grep -E "libx265"
```

Tiene que decir `.SC zscale` (libzimg) y `libx265`. Si no, instalar:

```bash
brew install ffmpeg     # macOS — incluye libzimg + libx265 por default
```

---

## 4. Dual versions — master + YouTube

Por cuestiones de **conteo de duración**: YouTube redondea hacia arriba.
Un video de 480.000s puede mostrar 8:01 por desalineación
audio-AAC vs video-frames (AAC chunks de 23ms).

**Solución**: render dos versiones del mismo material.

### A. Master backup
- Duración exacta del audio master
- Para nuestro archivo histórico
- Path: `transmissions/NN/video/{track}/final_4k.mp4`

### B. YouTube version
- Trim de **0.75 segundos** al final (frame-accurate)
- Asegura que la duración mostrada queda como debe: 8:00 / 13:00 / 3:00
- Path: `transmissions/NN/video/{track}/final_4k_yt.mp4`

### Cómo generar el trim

Lossless stream copy (rápido, ~10 segundos):

```bash
# outbound: master 480.000s -> yt 479.250s (8:00 displayed)
ffmpeg -y -i 1-outbound.mp4 -to 479.25 -c copy -avoid_negative_ts make_zero 1-outbound_yt.mp4

# crossing: master 780.000s -> yt 779.250s (13:00 displayed)
ffmpeg -y -i 2-crossing.mp4 -to 779.25 -c copy -avoid_negative_ts make_zero 2-crossing_yt.mp4

# recursion: master 180.000s -> yt 179.250s (3:00 displayed)
ffmpeg -y -i 3-recursion.mp4 -to 179.25 -c copy -avoid_negative_ts make_zero 3-recursion_yt.mp4
```

Stream copy preserva el HDR HLG tagging + bitrate sin re-encode. El
output queda con duración exacta `-0.75s` = displayed siempre menor al
minuto siguiente.

Por qué 0.75s y no menos: AAC audio puede tener slop de ~23ms por
chunk boundary. 0.75s = margen seguro para que la duración total
(audio o video, lo que YouTube tome como referencia) no rebote al
minuto siguiente.

---

## 4.5. Validación obligatoria — detector de zurcos

**Antes de entregar el path al user**, correr el detector programático.

Ver [`22_banding_detection_validation.md`](22_banding_detection_validation.md)
para algoritmo, test bench y uso. Resumen:

```bash
cd transmissions/NN/video
$VENV banding_detect.py --test                # validar detector
$VENV banding_detect.py out/<track>.mp4       # analizar video
```

Si `avg banded_pct > 10%` → **no entregar, re-renderizar**.

La validación visual a ojo no es suficiente — frames extraídos a preview
chico esconden banding sutil que es visible al 4K full-screen.

## 5. Checklist para nuevo video

Antes de publicar un video, validar:

- [ ] **Shader tiene gamma lift** `pow(0.82)` aplicado pre-dither
- [ ] **Dither isotrópico ≥4/255** (3 hashes sumados, no 1)
- [ ] **Pipeline 16-bit** desde framebuffer (rgb48le → uint16 → ffmpeg)
- [ ] **Encode HDR HLG** con el comando de sección 3
- [ ] **Bitrate ≥80 Mbps** (preferiblemente 100M para 4K)
- [ ] **Audio AAC ≥256k** (preferiblemente 320k)
- [ ] **Dual version**: master + YT-trim 0.75s
- [ ] **Validar en tres devices distintos** antes de upload:
  - Mac Retina (control)
  - Mobile (iPhone si HDR, Android si no)
  - TV (si tenés acceso)
- [ ] **Stills test** de los momentos más oscuros — no debería haber
  ninguna zona indistinguible del fondo

---

## 6. QA workflow para verificar resultado

### Local (pre-upload)
Extraer 5 stills distribuidos del MP4 final:

```bash
ffmpeg -ss 00:00:30 -i video.mp4 -frames:v 1 still_30s.png
# repetir para 25%, 50%, 75%, 90% del runtime
```

Abrir cada uno y verificar:
- ¿Se distingue del fondo el elemento focal? (ej: ovulo, silueta)
- ¿Hay gradientes lentos visibles? (lugar candidato a banding)
- ¿Las zonas oscuras tienen detalle o son negro plano?

### Post-upload YouTube
Cuando el procesamiento esté completo:
- Abrir el video en YouTube en **3 devices**:
  - Mac/Linux desktop → ver en 4K resolution, fullscreen
  - iPhone/HDR mobile → ver en 4K HDR si está disponible
  - SD TV o navegador 720p → ver fallback SDR
- Buscar en zonas oscuras: banding (zurcos concéntricos) o crush
- Comparar con el master local en QuickTime

Si hay banding visible **en HDR pipeline de YouTube** = revisar
metadata HDR (a veces YouTube no detecta el HLG y lo trata como SDR).

---

## 7. Por qué NO PQ (HDR10) y NO Dolby Vision

Ambos son modos HDR válidos pero **peores para nuestro caso**:

- **PQ (Perceptual Quantizer / HDR10)**: signal en nits absolutos
  (0-10000 nits). SDR fallback requiere tone-map agresivo que puede
  alterar verde anegrado significativamente.
- **Dolby Vision**: requiere licencia, metadata dinámica frame-by-frame,
  complejidad técnica alta. Beneficio marginal para ambient dark.

**HLG es el sweet spot**: HDR real + SDR backwards-compatible + sin
licencias + soporte universal en YouTube/players.

---

## 8. Cuándo NO usar HDR HLG

Material que se beneficia de stay-SDR:

- Contenido con **fuerte componente bright** (blanco saturado,
  highlights extremos). HLG tone-map podría volcarlos en SDR fallback.
- Trabajo destinado **principalmente a SDR distribution** (Vimeo SDR
  embeds en website, archivo institucional, master para film festival
  donde piden Rec.709 puro).

Para todo lo demás (YouTube, mobile distribution, social), HLG gana.

---

## 9. Lessons learned (Transmission 01)

- **2026-06-04**: Reportado banding en YouTube outbound 03:40 — local
  perfecto, YT mostraba zurcos concéntricos verdes claros. Ovulo a
  20s era invisible en 4K UHD TV. Causa: pipeline SDR YT 8-bit + paleta
  verde anegrado demasiado dark para tone gamma de TVs típicas.
- **2026-06-05**: Aplicado palette lift `pow(0.82)` + cambio a HDR HLG
  encoding. Re-render outbound + crossing. Recursion solo transcode
  (era AI generado, ya brillante).
- **Conclusión**: el pipeline 16-bit shader-side **no salva** si el
  delivery format es SDR — YouTube tira a 8-bit. HDR HLG es la única
  forma de preservar el 16-bit hasta los devices modernos.
- **Stills tests** del ovulo a t=20s mostraron que la diferencia es
  brutal — sin lift apenas distinguible del fondo; con lift,
  presencia clara con halo verde.

---

## 10. Referencias

- YouTube HDR upload specs: https://support.google.com/youtube/answer/7126552
- BBC HLG spec ITU-R BT.2100: https://www.itu.int/rec/R-REC-BT.2100
- ffmpeg HDR encoding guide: https://trac.ffmpeg.org/wiki/Encode/H.265#HDR
- libx265 HDR params: https://x265.readthedocs.io/en/master/cli.html#cmdoption-x265-hdr10
