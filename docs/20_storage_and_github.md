# 20 — Storage strategy + GitHub readiness

Plan para subir el repo a GitHub sin meterte en problemas de tamaño, y
plan para guardar lo pesado (audios, masters, AI iterations) afuera.

---

## Audit actual

```
Total repo:                          17 GB
├── transmissions/01/out/            11 GB  ← scratch renders (regenerables)
├── transmissions/01/release/         3.8 GB ← masters + distribution
├── transmissions/01/themes/outbound/finals/ 1.7 GB ← finals/v*/master.wav + stems
├── transmissions/01/artwork/         93 MB
│   └── generated/                    80 MB  ← AI iterations (trash mayoritaria)
├── site/                             8.5 MB
└── (resto: code + docs + scripts)    ~6 MB
```

### Lo que YA está gitignored (regenerable o pesado)

- `transmissions/*/out/*/master/` y `out/*/stems/` (scratch renders) ✓
- `transmissions/*/release/` (masters + distribution bundles) ✓
- `transmissions/*/themes/*/finals/*/stems/` y `finals/*/master.wav` ✓
- `transmissions/*/samples/raw/`, `samples/voyager_golden_record/`, `samples/cmb_recordings/` ✓
- `__pycache__/`, `.DS_Store`, `.player.*` ✓

### Lo que falta gitignorear

- [ ] `transmissions/*/artwork/generated/` (80 MB, son AI iterations
      trash mayormente — solo los seleccionados como cover_*.* van)

Después de esa adición, **repo va a pesar ~13 MB**. Cabe sobrado en GitHub
(GitHub recomienda < 1 GB, hard limit a 5 GB).

---

## GitHub — qué va, qué no

### VA al repo

- ✓ Todo el código (`framework/`, `scripts/`, `player/`, `site/`)
- ✓ Todos los `docs/`
- ✓ Todos los `compose_*.py` y `arrangement_*.md` (source de los tracks)
- ✓ `Taskfile.yml`, `README.md`, `CLAUDE.md` y subordinates
- ✓ `transmissions/*/artwork/cover_*.{jpg,png}` (covers finales)
- ✓ `transmissions/*/artwork/banners/` (banners de Bandcamp finales)
- ✓ `transmissions/*/artwork/hexagram/` (mark secundario)
- ✓ `transmissions/*/artwork/generation_briefs/` (texto de los briefs IA)
- ✓ `transmissions/*/themes/*/finals/v*/compose_snapshot.py` y `version.md`

### NO va al repo (gitignored, va a R2)

- ✗ `transmissions/*/out/` — scratch renders
- ✗ `transmissions/*/release/` — masters + distribution
- ✗ `transmissions/*/themes/*/finals/v*/master.wav` y `stems/`
- ✗ `transmissions/*/samples/raw/` etc — samples pesados
- ✗ `transmissions/*/artwork/generated/` — AI iterations (a partir de esta update)

---

## Storage externo — Cloudflare R2

**Recomendado: Cloudflare R2.**

Por qué:
- **Ya estás en Cloudflare** (el site corre en Pages, el dominio en CF DNS) →
  un solo dashboard, un solo API token, un solo $.
- **Costo**: $0.015/GB/mes storage, **cero egreso**. Para 30 GB ≈ $0.45/mes.
  Backblaze B2 es ligeramente más barato pero con costos de egreso si
  alguien baja → para masters + samples + AI iterations es peor.
- **S3-compatible API**: cualquier librería que hable S3 (boto3, rclone,
  AWS CLI) anda con R2 sin cambios.
- **Cloudflare Worker en frente** si querés URLs públicas / paywall /
  delivery (futuro: distribution de FLAC para fans).

### Estructura sugerida del bucket

Un solo bucket `spiral-out` con prefixes por transmission y categoría:

```
spiral-out/
├── transmissions/
│   └── 01/
│       ├── out/                     ← scratch renders mirror
│       │   ├── outbound/
│       │   ├── crossing/
│       │   └── recursion/
│       ├── release/
│       │   ├── masters/             ← master.wav finales
│       │   └── distribution/
│       │       ├── flac/
│       │       ├── mp3_320/
│       │       ├── wav_44k/
│       │       └── aac/
│       ├── finals/                  ← finals/v*/master.wav + stems
│       │   ├── outbound/v1/
│       │   ├── crossing/v1/
│       │   └── recursion/v1/
│       ├── samples/                 ← samples crudos (golden record, cmb)
│       └── artwork/
│           └── generated/           ← iterations IA
└── transmissions/
    └── 02/...
```

### Operativa diaria

- **Subida** después de cada render que querés respaldar:
  ```bash
  task r2:sync:finals   # syncea transmissions/<TX>/themes/*/finals/ al bucket
  task r2:sync:release  # syncea transmissions/<TX>/release/ al bucket
  ```
- **Bajada** cuando arrancás en otra máquina o querés recuperar:
  ```bash
  task r2:pull:finals
  ```
- Las tareas usan `rclone` (más simple que AWS CLI) configurado contra R2.

Te puedo armar las tareas `r2:*` en el Taskfile y un README de setup
(crear bucket, generar API token, configurar rclone) cuando me digas que
arranquemos con eso.

### Costo estimado

| Categoría | Tamaño | $ / mes |
|---|---|---|
| out/ scratch renders | 11 GB | $0.17 |
| release/ (masters + dist) | 4 GB | $0.06 |
| finals/ | 2 GB | $0.03 |
| samples/ | 1 GB | $0.02 |
| artwork/generated/ | 0.1 GB | $0.002 |
| **Total** | **~18 GB** | **~$0.27/mes** |

Menos que un café. Y si llegás a 100 GB con futuros releases, son $1.50.

---

## Plan de migración a GitHub

### Paso 1 — limpiar gitignore (15 min)

Agregar al `.gitignore`:

```
# AI image generation iterations (los seleccionados se promueven a artwork/cover_*)
transmissions/*/artwork/generated/
```

### Paso 2 — crear bucket R2 (15 min)

Vos (tenés que entrar al dashboard de Cloudflare):

1. Cloudflare dashboard → R2 Object Storage → Create bucket "spiral-out"
2. Generate R2 API token (read + write)
3. Pasarme las credenciales (Access Key ID + Secret) por canal seguro o
   pegarlas en `~/.config/rclone/rclone.conf` directamente

### Paso 3 — sync inicial (1-2 horas, depende de tu conexión)

```bash
task r2:sync:all     # primer push de los 18 GB
```

Esto sube TODO lo que hoy es local-only.

### Paso 4 — iniciar repo GitHub (10 min)

```bash
cd ~/Documents/Claude/Projects/My\ First\ Album
git init
git add .
git commit -m "Initial commit — Spiral Out repo"
# crear repo en github.com/<tu-user>/spiral-out
git remote add origin git@github.com:<user>/spiral-out.git
git branch -M main
git push -u origin main
```

Como nunca fue git repo antes (`Is a git repository: false` lo confirmó al
inicio de la conversación), partimos limpio sin historial pesado.

### Paso 5 — renombrar la carpeta local

Hoy se llama `My First Album/`. Cambiar a `spiral-out/`:

```bash
cd ~/Documents/Claude/Projects/
mv "My First Album" spiral-out
```

Después actualizar shortcuts, Claude project config si hace falta, etc.

### Paso 6 — actualizar referencias

- README + CLAUDE.md ya hablan de "Spiral Out" como nombre del repo ✓
- Verificar que no haya rutas hardcoded con "My First Album" en scripts:
  ```bash
  grep -r "My First Album" --include="*.py" --include="*.yml" --include="*.md" .
  ```

---

## Acceso público vs privado

Decisión: ¿el repo es **público o privado**?

### Público

**Pros**:
- Es parte de la narrativa de Spiral Out ("composed in Python, open source
  framework") — coherente con la marca
- Aporta a tu CV / portfolio
- Permite que la comunidad ambient/Python lo vea y contribuya
- Mejora SEO de tu nombre en buscadores
- Wikidata / MusicBrainz pueden linkear como `software` o `instrument`

**Contras**:
- Cualquiera puede clonar y forkear (composiciones son fácilmente
  reproducibles)
- Si tenés ideas o material WIP que preferís no exponer, queda visible

### Privado

**Pros**:
- Control total. WIPs no expuestos.

**Contras**:
- Free GitHub privado tiene límites de colaboradores
- Pierde el angle "open source AI music framework" que es parte del lore

### Mi recomendación

**Público**, pero:
- El framework `aem/` es open source MIT/Apache → reusable
- Los compose files de los tracks son "musical scores" — también públicos
  (es la transparencia del proyecto)
- Las grabaciones (WAVs, FLACs) están **en R2 privado**, no en GitHub
- Las cover arts / press materials están en GitHub (deliverables públicos)

Esa separación deja claro qué es **abierto** (código + scores) y qué es
**la obra terminada** (audio masters, que se distribuyen por Bandcamp /
Spotify, no por git clone).

---

## Riesgo a controlar

**No subir nunca**:
- Credenciales (API keys de R2, Cloudflare, distributors, GA, etc).
- Email lists / contactos privados.
- Documentos con info personal (DNI, contratos, etc).

Usar `.env` files (gitignored) o variables de entorno para credenciales.
Si llegan a colarse en un commit, **rotar inmediatamente** y purgar
historia con `git filter-repo`.
