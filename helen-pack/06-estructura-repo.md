# Estructura de repositorio para un sello discográfico

Especificación de la organización del repositorio de Spiral Out: un sello, un artista
(ÆM), un release publicado (*Heliopause*), un framework de audio en Python, un sitio y
tres canales de difusión, en un único repo.

Documento de referencia para replicar la estructura.

---

## 1. Criterio de inclusión de archivos

Git versiona texto de forma incremental y binarios de forma completa: cada versión de un
binario se almacena entera y permanente. Dos restricciones que definen la política:

- **`git add` escribe el archivo al object store.** El espacio en disco se consume en el
  `add`, no en el `commit`. Deshacer el add no libera el espacio; requiere `git gc`.
- **Un binario commiteado es permanente.** Removerlo de la historia exige reescribir el
  repo (`git filter-repo`), lo que invalida todos los clones existentes.

Consecuencia: el `.gitignore` se escribe **antes del primer commit**. Cobertura mínima:
`*.wav`, `*.aiff`, `*.flac`, `*.mp3`, `*.mp4`, `*.zip` y las carpetas de proyecto del
DAW.

Criterio por archivo: **¿se puede regenerar?**

| Caso | Destino | Ejemplo |
|---|---|---|
| Regenerable desde código | Repo: solo la fuente | `compose_*.py` (5 KB) en lugar del WAV renderizado (300 MB) |
| No regenerable, texto | Repo | letras, notas de sesión, metadata, textos públicos, decisiones, contactos |
| No regenerable, binario grande | Backup externo (disco + Drive o Backblaze) | multitracks, tomas, masters, stems |
| Referencia de comparación | Repo, opcional | MP3 del mix v3 para comparar contra v4 |

El criterio depende del flujo de producción:

| Flujo | Fuente original | Va al repo |
|---|---|---|
| Composición por código | El script | El script; el audio se regenera |
| Grabación en DAW | Los multitracks | Solo texto; el audio va a backup |

Git no funciona como backup de audio en ninguno de los dos casos.

---

## 2. Árbol

```
spiralout/
├── CLAUDE.md              instrucciones para el asistente
├── README.md
├── Taskfile.yml           comandos del proyecto
├── docs/                  documentos numerados: concepto, planes, decisiones
├── dashboard/             tablero de estado (data.json + index.html)
├── transmissions/         releases; 01/ es Heliopause
│   └── 01/
│       ├── README.md
│       ├── themes/        una carpeta por track
│       ├── artwork/       tapa, banners, imágenes
│       ├── release/       metadata, textos, masters (ignorado)
│       └── video/
├── site/                  sitio web
├── redes/                 assets de redes sociales, por plataforma
├── scripts/               utilidades de línea de comandos
├── lab/                   experimentos de sonido
├── player/                reproductor web local para los renders
└── framework/             motor de audio en Python
```

`transmissions/NN/` implementa un catálogo numerado: cada release es una carpeta hermana
(`02/`, `03/`) con la misma estructura interna, y los comandos de render seleccionan la
activa por variable de entorno (`TX=02 task render:all`). Un proyecto de un solo release
sustituye el nivel `NN/` por una carpeta única.

---

## 3. `CLAUDE.md` — configuración del asistente

Archivo que el asistente carga automáticamente al inicio de cada sesión. Establece el
contexto que de otro modo hay que reconstruir en cada conversación.

Distribución: uno por área — raíz, `site/`, `transmissions/`, `framework/`. El de cada
subcarpeta se carga al operar dentro de ella, lo que mantiene cada archivo acotado.

Contenido por tipo:

| Tipo | Función | Ejemplo |
|---|---|---|
| Perfil de trabajo | Fija idioma y prioridades de decisión | "Español en comentarios y docstrings; prioridad al resultado sonoro sobre la elegancia del código" |
| Reglas duras | Prohibiciones en imperativo | No modificar el motivo protegido sin aprobación; no commitear WAVs; no agregar atribución de IA a los commits; correr QA espectral después de cada render |
| Antipatrones | Error técnico + corrección | `abs()` como excitador genera intermodulaciones audibles como distorsión — usar `tanh`; ruido filtrado con corte > 1 kHz suena a estática — sesgar a ≤ 800 Hz |
| Terminología del proyecto | Traduce vocabulario propio | "menos opacity" sobre una foto significa subir el alpha del overlay |
| Fuentes de verdad | Desambigua qué documento manda | "El estado está en `dashboard/data.json`; los planes de composición están congelados y no son fuente de estado" |
| Comandos | Entradas habituales | 4–5 líneas de `task ...` |

La sección de antipatrones concentra el mayor rendimiento por línea escrita: documenta
errores no deducibles del código, que de otro modo se repiten.

**Memoria del asistente.** Notas persistentes entre sesiones, almacenadas fuera del
repo: preferencias, correcciones, diagnósticos. Diferencia operativa con `CLAUDE.md`: el
`CLAUDE.md` lo escribe el equipo y se versiona; la memoria la escribe el asistente y no
es parte del repo.

---

## 4. `docs/` — documentos numerados

Archivos con prefijo numérico correlativo: `00_concepto.md`, `12_release_pipeline.md`,
`38_capas_dark_ambient.md`.

Función del prefijo:

- Referencia inequívoca en conversación y en otros documentos.
- Orden cronológico de las decisiones.

Contenido: concepto y cosmología del release, el texto narrativo que origina los textos
públicos, plan de release, guía de estilo visual, playbooks de difusión, anatomía de las
capas de sonido, contactos de prensa.

Regla de registro: lo decidido se documenta; **lo descartado se documenta con el
motivo**. El doc de difusión mantiene una tabla de palancas pagas con el campo
"descartada porque X", que cierra la discusión de forma permanente.

Núcleo mínimo, cinco documentos: concepto, plan de release, textos, metadata, prensa.

---

## 5. Documentos canónicos de release

### `textos.md` — voz pública

Archivo único con todo el texto público del release, redactado antes de necesitarlo:

- Bio del artista en tres extensiones: tagline de una línea, corta (150 caracteres, tope
  de Spotify), larga (Bandcamp, Apple).
- Descripción del release, corta y larga.
- Un texto por track.
- Frases para redes, en cada idioma de publicación.
- Reglas de voz, incluido el listado de lo que no se dice.

Función: distribuidor, Bandcamp y Spotify piden la bio con topes de caracteres
distintos. Con el archivo, cada formulario se completa por copia y todas las plataformas
declaran lo mismo; sin el archivo, el texto se redacta durante el upload y divergen
entre plataformas.

### `metadata.md` — datos canónicos

Tabla por track: título exacto, artista como debe figurar, número de track, **ISRC**.
Campos globales: género principal, año, sello, copyright, fecha de release, nombre exacto
del release.

Función: los mismos datos se cargan en el distribuidor, Bandcamp, la metadata embebida
de los archivos, MusicBrainz y el press kit. Sin fuente única, las variantes de un
título se propagan a todo el ecosistema, donde la corrección es costosa y parcial.

Los ISRC identifican cada grabación de forma única, los asigna el distribuidor y se
registran al recibirlos: se requieren para MusicBrainz, reclamos de regalías y
correcciones posteriores.

---

## 6. Dashboard — estado del proyecto

Dos archivos, sin dependencias ni build, servidos por un servidor local estático:

```
dashboard/
├── data.json     datos
└── index.html    HTML + CSS + JS en un archivo
```

**Los porcentajes se calculan, no se almacenan.** `data.json` contiene solo el estado de
cada tarea; `index.html` cuenta y calcula al cargar. Un porcentaje almacenado queda
desactualizado en el primer cambio de estado.

### Estructura de `data.json`

```json
{
  "meta": { "updated": "2026-08-05", "next_review": "2026-08-31" },

  "projects": [
    {
      "id": "heliopause",
      "title": "ÆM · Heliopause",
      "brief": "El release y su difusión.",
      "description": "Texto largo, visible al entrar al proyecto",
      "color": "#503c5a",
      "phases": [
        {
          "id": "distribucion",
          "title": "Distribución + plataformas",
          "tasks": [
            {
              "id": "cdbaby-upload",
              "title": "Subir el disco a CD Baby",
              "status": "done",
              "owner": "user",
              "note": "Hecho 16/06. Tarda 2-5 días en Spotify.",
              "blockedBy": "master-final",
              "eta": "2026-09-28"
            }
          ]
        }
      ]
    }
  ],

  "recurring": { "items": [ ... ] },
  "lab":       { "experiments": [ ... ] }
}
```

Campos de una tarea:

| Campo | Contenido |
|---|---|
| `status` | `done` / `todo` / `in_progress` / `blocked` |
| `owner` | responsable de la ejecución |
| `note` | contexto: por qué se decidió o se descartó |
| `blockedBy` | id de la tarea bloqueante |
| `eta` | fecha estimada |

### Tres secciones, con semántica distinta

| Sección | Contenido | Progreso |
|---|---|---|
| `projects` | Trabajo finito, en fases y tareas | Barra calculada sobre tareas cerradas |
| `recurring` | Trabajo sin fin: métricas, cola de posts, reportes periódicos | Sin barra. Próxima fecha calculada (última ejecución + periodicidad); vencidas en rojo |
| `lab` | Experimentos, con estado `pending` / `in_progress` / `done` / `dead` | Sin barra, por diseño |

La separación es funcional, no cosmética: una tarea recurrente no se cierra por
definición, por lo que computarla dentro del progreso de un proyecto lo mantiene por
debajo del 100 % de forma permanente. Los experimentos tampoco admiten porcentaje: al
cerrarse o promoverse a proyecto conservan una referencia al resultado.

### Fuente única de estado

El `CLAUDE.md` establece que las consultas de estado se responden leyendo `data.json`, y
no los planes de fases ya cerradas. Sin esa regla explícita el asistente responde con
documentos vencidos.

---

## 7. `Taskfile.yml` — comandos del proyecto

El proyecto usa [Task](https://taskfile.dev): equivalente a `Makefile`, declarado en
YAML. Un archivo en la raíz con todos los comandos.

```yaml
vars:
  PYTHON: python3.10

tasks:
  install:
    desc: Instala las dependencias
    cmds:
      - "{{.PYTHON}} -m pip install --user numpy scipy"

  serve:
    desc: Levanta el reproductor local
    cmds:
      - "{{.PYTHON}} player/serve.py --port 8765"

  qa:spectral:
    desc: Analiza los WAV renderizados y detecta distorsión
    cmds:
      - "{{.PYTHON}} scripts/qa_spectral.py"
```

`task --list` enumera los comandos con su descripción. Nomenclatura agrupada por dos
puntos: `render:all`, `qa:spectral`, `site:deploy`, `release:plan`.

Funciones que cumple:

- **Estabiliza invocaciones.** Los comandos reales llevan flags que no se retienen; el
  alias sí.
- **Habilita la ejecución por el asistente.** Con la task documentada en `CLAUDE.md`, la
  invocación es correcta en el primer intento; sin ella, el asistente construye el
  comando y sus flags por inferencia.
- **Documenta las operaciones del repo** sin documento aparte: `task --list` es el
  inventario.

Tasks pertinentes en un flujo de grabación: conversión de masters a formatos de release
(FLAC, MP3 320, WAV 44.1/24), embedding de metadata y artwork, validación de loudness
contra los targets de plataforma, backup de audio al disco externo.

---

## 8. Componentes condicionados al flujo de trabajo

| Componente | Condición que lo justifica |
|---|---|
| `framework/` | La composición se escribe en código. Un flujo de grabación en DAW no lo usa |
| `player/` | Necesidad de escuchar renders sin abrir un DAW |
| `transmissions/NN/` | Catálogo con más de un release. Un release único no requiere el nivel |
| Dashboard | Volumen de tareas superior al manejable de memoria. Por debajo, una lista en el README cumple la función |
| `docs/` extenso | Acumulación por avance del proyecto; el punto de partida son cinco documentos |

Orden de creación del conjunto mínimo:

1. **`.gitignore`** — antes del primer commit.
2. **`CLAUDE.md`** — perfil de trabajo, reglas duras, antipatrones conocidos.
3. **`docs/textos.md`** — bios en tres extensiones.
4. **`docs/metadata.md`** — tabla de tracks con espacio para los ISRC.
5. **Backup de audio** externo a git.
