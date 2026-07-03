# Banding detection + sistema de validación de zurcos

> Aprendizaje 2026-06-06 durante la iteración de los videos de
> Transmission 01 (outbound + crossing). Persistido acá para que futuras
> producciones tengan el sistema desde el día 1 y no repitan los
> errores que ya pagamos.

## TL;DR

- **El detector visual a ojo de Claude (extraer frames con Read tool) NO ES CONFIABLE**. Los frames se renderean a baja resolución en el tool y banding subtle se pasa por alto.
- **YouTube re-encodea a 8-bit yuv420p para SDR fallback**, lo que reintroduce banding incluso si el upload era 10-bit HDR HLG.
- **HEVC `psy-rd` smoothea dither sutil del shader** → puede destruir el dither de 4/255 que pusimos.
- **El "raw HLG as SDR" extraction es lo que ve la mayoría de los players** (no aplican tone-map propio salvo apps HDR-aware). Banding visible en raw HLG = visible para usuarios.
- **El detector programático es OBLIGATORIO**: `banding_detect.py` en `transmissions/01/video/`. Validado contra test bench sintético `banding_test_bench.py`.

---

## 1. Por qué necesitamos un detector programático

### El problema con validación visual humana / a-ojo

Lo siguiente pasó en la iteración de Transmission 01:

1. Renderizé outbound + crossing en HDR HLG 4K 80 Mbps.
2. Validé visualmente extrayendo PNGs con `ffmpeg -ss N -frames:v 1`.
3. Reporté "todo OK" al user.
4. User abrió el MP4 en su player → ZURCOS VISIBLES en outbound 3:35, crossing primera mitad entera.
5. El issue: los PNGs extraídos se rendereaban en preview a 1080p, donde banding sutil de 1-step quantization no es percibible. Pero al ver el MP4 a fullscreen 4K, ES VISIBLE.

**Conclusión**: validación a ojo del agente sobre frames extraídos en preview NO ES SUFICIENTE. Necesitamos un detector que opere sobre el frame ORIGINAL a resolución completa y dé scores cuantitativos.

### Lo que la validación visual a ojo NO captura

- **Banding sutil 1-step en zonas oscuras**: 1/255 step en luma 10-20 = 5-10% visual jump. Invisible en preview chico, MUY visible a 4K full-screen.
- **Patterns periódicos diagonales**: el ojo los ve como ondas. En preview chico parecen smooth.
- **HEVC encoding artifacts**: ringing, block edges. No son banding clásico pero el user los percibe como similar.

---

## 2. El detector — `banding_detect.py`

Script en `transmissions/01/video/banding_detect.py`.

### Algoritmo (v9 final — DEFINITIVO)

Para cada frame muestreado:

1. **Luma**: `luma = 0.299*R + 0.587*G + 0.114*B`
2. **Gradient local** (raw): `grad = |∇luma|` — preserva spikes en band edges
3. **Laplacian smoothed**: `lap = |∇²(luma * G_σ=3)|` — smoothing previo elimina el HEVC residual noise para no contaminar el filtro de curvature
4. **Patches 128×128** sliding (no overlap)
5. Para cada patch:
   - Skip si `patch_range < 0.3` (zona flat, no hay gradient real)
   - Skip si `median(lap) > 0.5` (no es zona LINEAR — hay curvatura tipo halo o textura)
   - **Banded patch** si CUALQUIERA de:
     - `p99(grad) / mean(grad) > 5.0` (spike ratio — plateaus con step edges esporádicos)
     - **`max_run >= 30 AND n_transitions <= 12`** en horizontal o vertical scan line del centro del patch (signature directa de "long flat runs separated by few transitions")
6. **Metric primaria**: `banded_pct` = % del frame total que está dentro de un banded patch.

### Por qué v9 agregó run-length check

V8 confiaba sólo en la spike-ratio signature. Funcionaba en synthetic
cases pero al validar con pixel scan en video real (`outbound t=212`),
descubrí que el HEVC encoder **smoothea el dither** entre bandas. El
resultado: pixel scan horizontal mostraba runs de 50+ pixels con valor
idéntico ([34,34,34,34,...]), pero la spike-ratio del gradient no era
suficiente para triggear v8.

Solution: comprobar directamente runs de luma en scan lines.

| Caso | max_run | n_transitions | Verdict |
|---|---|---|---|
| Banding subtle 1-step | 64+ | 2-5 | BANDED ✓ |
| Banding severe | 100+ | 1-3 | BANDED ✓ |
| Smooth dithered | 1-3 | 100+ | CLEAN ✓ |
| Gaussian halo (design) | 5-10 | 20-30 | CLEAN ✓ |
| Texture | 9-25 | 16-40 | CLEAN ✓ |

Run-length signature es el discriminador limpio: banding tiene MUCHOS pixels
en pocos plateaus, texture tiene POCOS pixels en muchas variaciones.

### Verdict thresholds

| `banded_pct` | Verdict |
|---|---|
| < 2% | CLEAN ✓ |
| 2-10% | MILD banding (visible en zonas oscuras) |
| 10-25% | VISIBLE banding |
| > 25% | SEVERE banding (zurcos prominentes) |

### Test bench obligatorio

El detector se valida contra 6 casos sintéticos antes de aplicarse a un video real:

| Case | Descripción | Expected `banded_pct` |
|---|---|---|
| A | Smooth gradient con dither 8/255 | < 5% (CLEAN) |
| B | Smooth gradient con dither 4/255 | < 5% (CLEAN) |
| C | Quantized 8-levels sin dither | > 40% (SEVERE BANDED) |
| D | Gaussian halo con dither (design feature) | < 5% (CLEAN) |
| E | 1-step 8-bit banding sin dither (subtle) | > 10% (BANDED) |
| F | High-freq texture | < 5% (CLEAN) |

Si el detector FALLA cualquier caso, **NO USAR** hasta recalibrar. Generado por `banding_test_bench.py`.

```bash
VENV=...
$VENV banding_detect.py --test          # corre test bench
$VENV banding_detect.py video.mp4       # analiza video
$VENV banding_detect.py video.mp4 --interval 10  # sample cada 10s
```

Output:
- Per-frame scores en consola
- `/tmp/banding_<videoname>/frame_tNNNN.png` — frames extraídos
- `/tmp/banding_<videoname>/BANDING_tNNNN.png` — overlay rojo en zonas detectadas como banded (solo si banded_pct > 10%)
- `results.json` — todos los scores serializados

### Limitaciones CONOCIDAS del detector v9

1. **Patches 128×128 son grandes**: en escenas con detalle fine, los
   patches pueden cruzar zonas heterogéneas. Si el detector confunde dos
   zonas adyacentes (una banded otra texture), el resultado por patch
   puede ser inválido.

2. **No detecta encoding artifacts no-banding** (block edges, mosquito
   noise, ringing): estos son artifacts perceptualmente similares a
   banding pero estructuralmente distintos.

3. **Patches con mucho noise puede dar falso positivo si por casualidad
   un scan line tiene < 12 transitions**: muy raro, pero posible.

---

## 3. Workflow validación de un video render

**Obligatorio antes de pasar path al user**:

```bash
cd transmissions/NN/video
# 1. Validar detector primero
$VENV banding_detect.py --test
# Si no pasa: STOP. No usar detector hasta recalibrar.

# 2. Analizar el video
$VENV banding_detect.py out/<track>.mp4 --interval 10

# 3. Si avg banded_pct > 10% → NO ENTREGAR. Re-rederizar con fixes.
# 4. Si avg banded_pct < 10% → verificar visualmente:
#    - Mirar los top 5 worst frames con sus heatmaps
#    - Verificar que las zonas marcadas son realmente banded (no false pos)
#    - Verificar que las zonas no marcadas no tienen banding visible 4K
# 5. Sólo si validación visual confirma score → entregar al user
```

---

## ⚠️ BUG CRÍTICO 2026-06-07 — hash21 float32 precision

**Síntoma**: TODO el video tiene bandas. Cambiar encoder (HEVC↔AV1), HDR↔SDR,
gamma lift, dither amplitude — nada lo mueve. Detector reporta 60-100% banded.

**Root cause**: La función `hash21` clásica de GLSL pierde precisión cuando
`u_seed` es grande. La señal `u_seed` se incrementa por frame:
`seed_val = i * 47.31 + 0.91`. A partir del frame ~100, u_seed > 4700.
Multiplicaciones internas del hash (`p * vec2(443.8975, 397.2973)`) llevan
los valores a 10^6+, y luego `* p.x` los lleva a 10^8+. Float32 tiene 7
dígitos significativos: a 10^8, la precisión es ±10 unidades. El `fract()`
final retorna basura semi-constante.

**Resultado**: dither efectivo = ~5% del intentado. Cada pixel
recibe casi el mismo "noise" que su vecino → bandas visibles.

**Diagnóstico**: render 2 frames con `seed_val` distinto, comparar el mismo
pixel. Diff std debería ser ~600 unidades 16-bit con dither 8/255 activo.
Si diff std < 50, el hash está roto.

```python
# diagnostic snippet
buf1 = render_frame(gl, W, H, frame_i_a, ctrl)
buf2 = render_frame(gl, W, H, frame_i_b, ctrl)
img1 = np.frombuffer(buf1, dtype='<u2').reshape(H, W, 3)
img2 = np.frombuffer(buf2, dtype='<u2').reshape(H, W, 3)
diff = img2.astype(int) - img1.astype(int)
print(f"diff std: {diff[:,:,1].std():.1f}  (should be ~600 if dither at 8/255)")
```

**Fix**: pre-`fract` el seed antes de usarlo en cualquier hash:

```glsl
float s = fract(u_seed * 0.000312345);  // mapeo a [0,1) sin perder precisión
// luego usar `s` en vez de `u_seed`
float dhR = hash21(rot1 + vec2(s * 113.0, s * 191.0));
```

Aplicado en `outbound/render.py` v10 y `crossing/render.py` v3.18 el 2026-06-07.

**Impacto del fix** (outbound 720p):
- avg banded_pct: 58.9% → 2.2%
- t=212 (user complaint): 96% → 0%
- t=242 (humo): 96% → 0%

**Lección**: cualquier shader que use hashes basados en `fract(sin(...))` o
mixing polynomial tiene que mantener inputs en rango precisado en float32
(≤ 10^4 idealmente). Todo seed que crezca debe pasar por `fract(seed * small)`
antes de hash.

## 4. Causas conocidas de banding en nuestro pipeline

### Causa 1: 8-bit final delivery
**Problema**: Mucho banding sutil en zonas oscuras. Mas allá de cualquier fix shader-side.

**Diagnóstico**: YouTube re-encodea SDR a 8-bit yuv420p. HDR HLG triggers 10-bit pipeline pero **el SDR fallback que muchos players usan es 8-bit**.

**Fix**: paleta lift en shader para que verde anegrado viva en zona con más bits útiles. `pow(0.82)` gamma lift sube darks ~60%.

### Causa 2: Dither insuficiente
**Problema**: 1/255 dither isotrópico no rompe bandas en gradients muy lentos.

**Diagnóstico**: HEVC `psy-rd` smoothea el dither sutil cuando el bitrate es alto y el contenido es simple. El encoder considera el dither como "noise compressible".

**Fix sospechado** (a probar):
- Subir dither shader a 4/255 ó 8/255
- Cambiar a blue noise pre-calculado (void-and-cluster) en vez de hash IGN
- Encoding params: `no-strong-intra-smoothing=1`, `psy-rd=4.0`, `aq-strength=1.5` en x265

### Causa 3: HEVC `nal-hrd=cbr` puede smooth-out detalles
**Problema**: CBR forzado a 80 Mbps en contenido simple desperdicia bits en bloques bright + comprime mas los darks de lo que debería.

**Fix sospechado**: usar `crf=12` (visually lossless) en lugar de CBR. Pero pierde garantía de bitrate floor.

### Causa 4: zscale BT.709 → BT.2020 HLG conversion
**Problema**: la transformación lineal de color puede tener rounding errors si la precisión interna no es suficiente.

**Mitigación aplicada**: tag input como `bt709` antes del `-i -` para que zscale tenga la info correcta.

---

## 5. Errores específicos cometidos (para no repetir)

### Error: "validé visualmente y está OK" sin programmatic check
**Cuándo pasó**: render HDR HLG 80 Mbps de Transmission 01.
**Resultado**: entregué outbound + crossing con banding severo. User tuvo que enojarse para que armara el detector.
**Regla nueva**: SIEMPRE correr `banding_detect.py` antes de entregar path al user. **Sin excepción**.

### Error: extraction sin tone-map confunde
**Cuándo pasó**: cuando extraje frames con ffmpeg sin tone-map, los visualicé y los validé. Pero la imagen mostraba el HLG signal como SDR — visualmente distinto a lo que un player HDR-aware muestra.
**Regla nueva**: hacer DOS extracciones por frame critic:
1. Raw (no tone-map) — lo que ven players default
2. Tone-mapped (zscale + mobius) — lo que ven players HDR-aware
   Comparar ambas.

### Error: confundí design features con banding
**Cuándo pasó**: marqué los halos del ovulo de outbound como "banded" porque tienen rings concéntricos visibles.
**Regla nueva**: el detector debe distinguir banding (plateaus planos en gradient linear) de design features (curvatura continua tipo Gaussian halo). Filtro `median(|Lap|) > 0.5` excluye design features por curvatura.

### Error: thresholds calibrados sin test bench
**Cuándo pasó**: setié thresholds del detector ad-hoc y arrojaba resultados inconsistentes.
**Regla nueva**: cualquier cambio de threshold tiene que pasar el test bench sintético antes de aplicarse a videos reales.

### Error: patch size chico (32×32) miss banding en zonas muy oscuras
**Cuándo pasó**: con patches 32×32, dark scenes en crossing tenían < 1% in_zone porque patch range < threshold.
**Regla nueva**: usar patch size 128×128 para escenas dark con gradient gradual. Las bandas pueden estar separadas 100-200 pixels, patches chicos no las capturan.

---

## 6. Próximos pasos para erradicar banding

Ordenados por costo-beneficio:

1. **Modo iteración 720p** en render.py (`--res 720p` o similar): cycles de 10 min en vez de 1h30 → permite probar fixes rápido.
2. **Encoding params x265**: probar `psy-rd=4.0 aq-strength=1.5 no-strong-intra-smoothing=1 strong-intra-smoothing=0` para preservar dither.
3. **Dither shader subido a 8/255**: doble lo actual.
4. **Blue noise dither precomputado** (void-and-cluster, no IGN hash): patrones perceptivamente más smooth.
5. **CRF 14 + maxrate cap** en vez de CBR strict: deja al encoder usar más bits en zonas críticas.
6. **Si nada funciona**: paleta lift más fuerte (R floor 0.08 en vez de 0.05).

Cada fix → render 720p → detector → comparar score → decidir si vale la pena render 4K.

---

## 7. Referencias relacionadas

- [`21_distribution_encoding.md`](21_distribution_encoding.md) — pipeline HDR HLG + palette lift + dual versions (master + YT trim)
- [`20_technical_reference_videos.md`](20_technical_reference_videos.md) — referencias técnicas per-track
- `transmissions/01/video/banding_detect.py` — detector v8
- `transmissions/01/video/banding_test_bench.py` — test cases sintéticos
- `/tmp/banding_synthetic/` — outputs del test bench
- `/tmp/banding_<videoname>/` — outputs del detector sobre un video
