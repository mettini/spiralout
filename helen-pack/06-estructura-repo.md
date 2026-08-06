# Cómo estructuramos el repo de un disco

> Escrito para Helen, agosto 2026. Es **cómo lo hicimos nosotros**, no cómo hay que
> hacerlo. Copiá lo que te sirva y tirá el resto. Hay cosas acá que para tu caso son
> claramente demasiado, y están marcadas.
>
> Contexto: Spiral Out es un sello con un artista (ÆM), un disco publicado
> (*Heliopause*), un framework de audio en Python, un sitio y tres canales de
> difusión. Vos tenés un disco por salir. Bastante de esto te va a sobrar.

---

## 1. La idea de fondo: el repo guarda decisiones, no archivos pesados

Esto es lo único que de verdad importa y todo lo demás se deduce de acá.

Un repo de git es **buenísimo** para texto: guarda cada versión, te deja ver qué
cambió, y pesa nada. Y es **malísimo** para binarios grandes: cada versión de un WAV
de 300 MB queda guardada entera, para siempre, aunque después lo borres.

Así que la pregunta para cada archivo es: **¿esto se puede volver a generar?**

- **Si se puede regenerar → no va al repo.** Nuestros WAV renderizados salen de
  scripts de Python, así que guardamos el script (5 KB) y no el audio (300 MB).
- **Si no se puede regenerar → va al repo, o a un backup si es grande.** Una
  grabación de campo, una toma de voz, la tapa original: eso es irreemplazable.

**En tu caso la ecuación se invierte y es importante que lo veas.** Vos no generás
el audio desde código: lo grabás. Tus multitracks y tus tomas **son** la fuente
original y no se pueden regenerar. Entonces:

- **Al repo**: letras, notas de sesión, metadata, textos, decisiones, listas de
  contactos, planes.
- **A un backup aparte** (disco externo + Drive o Backblaze): multitracks, tomas,
  masters, stems. Git no es un backup de audio.
- Lo único de audio que tiene sentido versionar son **referencias chicas**: un MP3
  del mix v3 para poder comparar con el v4. Y eso si querés.

### La cagada que cometimos, para que no la repitas

Nuestra carpeta `.git` pesa **30 GB**. Los archivos que están hoy en el repo suman
**22 MB**.

Fuimos a ver qué eran y son **once archivos huérfanos**, todos videos: uno de 12 GB,
dos de 7,8 GB, y así. Nunca se commitearon. Lo que pasó es que durante el mes de los
renders de video alguien hizo `git add` sobre la carpeta de salida, se dio cuenta,
lo deshizo... y **git ya había copiado los archivos adentro de `.git`**. Ahí
quedaron.

Dos cosas de esto que valen para vos:

1. **Un `git add` ya te cuesta el disco, aunque nunca hagas el commit.** No hace
   falta equivocarse mucho.
2. **En nuestro caso se puede recuperar el espacio** porque nunca llegaron a un
   commit, así que basta un `git gc` y desaparecen. **Si hubiéramos commiteado, no.**
   Ahí queda en la historia para siempre y sacarlo es reescribir todo el repo con
   `git filter-repo`, que es cirugía y rompe el repo de cualquiera que lo haya
   clonado.

**La moraleja: escribí el `.gitignore` ANTES del primer commit.** Diez minutos que
después no se pueden deshacer.

---

## 2. Cómo está armado el nuestro

```
spiralout/
├── CLAUDE.md              ← las instrucciones para Claude (lo más importante)
├── README.md
├── Taskfile.yml           ← los comandos del proyecto
├── docs/                  ← 45 documentos numerados: concepto, planes, decisiones
├── dashboard/             ← el tablero de estado (data.json + un HTML)
├── transmissions/         ← los releases. 01/ es Heliopause
│   └── 01/
│       ├── README.md
│       ├── themes/        ← una carpeta por track
│       ├── artwork/       ← tapa, banners, imágenes
│       ├── release/       ← metadata, textos, masters (ignorado)
│       └── video/
├── site/                  ← el sitio web
├── redes/                 ← assets de redes sociales, por plataforma
├── scripts/               ← utilidades de línea de comandos
├── lab/                   ← experimentos de sonido
└── framework/             ← el motor de audio en Python (esto vos no lo necesitás)
```

Para un disco solo, yo empezaría con mucho menos:

```
tu-disco/
├── CLAUDE.md
├── docs/                  ← concepto, plan de release, decisiones
├── album/
│   ├── README.md          ← qué es este disco, estado de cada tema
│   ├── temas/             ← una carpeta por tema: letra, notas, historial
│   ├── arte/
│   └── release/           ← metadata, textos, ISRCs
├── redes/                 ← los assets por plataforma
└── prensa/                ← press kit, lista de contactos, qué mandaste y cuándo
```

---

## 3. `CLAUDE.md`: lo que más rinde de todo esto

Si te llevás una sola cosa, llevate esta.

Un archivo `CLAUDE.md` en la raíz es **el manual de instrucciones para tu asistente**.
Claude lo lee automáticamente al empezar cada sesión. Sin él, cada conversación
arranca de cero y le tenés que volver a explicar todo. Con él, ya sabe cómo trabajás.

Nosotros tenemos **uno por área** (raíz, `site/`, `transmissions/`, `framework/`), y
el de cada subcarpeta se lee cuando se trabaja ahí. Eso evita un archivo gigante que
nadie mantiene.

### Qué poner adentro

Lo que funciona no es descripción, son **reglas y cicatrices**:

**Quién sos y cómo trabajás.** "Hablo español, el código está comentado en español,
me importa el resultado sonoro y no la elegancia del código." Eso solo ya cambia
todas las respuestas.

**Las reglas duras, en imperativo.** Las nuestras incluyen:

- Nunca cambiar el motivo musical protegido sin aprobación explícita.
- Nunca commitear WAVs.
- Nunca agregar líneas de atribución de IA a los commits.
- Correr el QA espectral después de cada render, antes de decir que algo está listo.

**Los antipatrones que ya te costaron una tarde.** Esta es la parte más valiosa y la
que nadie escribe. Ejemplos reales del nuestro:

- "Usar `abs()` como excitador genera cientos de intermodulaciones y suena a
  fritura. Usar `tanh`."
- "Ruido filtrado con corte arriba de 1 kHz suena a estática, no a aire. Sesgar a
  800 Hz o menos."
- "Cuando el usuario dice 'menos opacity' se refiere a que la FOTO se vea menos, o
  sea SUBIR el alpha del overlay. Invertir la intuición."

Cada una de esas líneas es un error que cometimos dos veces antes de escribirlo.

**Dónde está la verdad de cada cosa.** "El estado del proyecto está en
`dashboard/data.json`, no en los planes viejos, que están congelados." Sin eso, el
asistente te va a citar un plan de hace tres meses con toda seguridad.

**Los comandos.** Cuatro o cinco líneas con lo que se corre habitualmente.

### Y algo aparte: la memoria

Claude además guarda notas entre sesiones (en un directorio propio, fuera del repo).
Ahí van las cosas que aprendió trabajando con vos: preferencias, correcciones,
diagnósticos. Cuando algo te resulta obvio y lo tenés que repetir por segunda vez,
eso va a memoria o al `CLAUDE.md`. La diferencia: el `CLAUDE.md` lo escribís vos y
está en el repo; la memoria la escribe el asistente y es suya.

---

## 4. `docs/` numerados

Cuarenta y cinco archivos, todos con número al principio: `00_concepto.md`,
`12_release_pipeline.md`, `38_capas_dark_ambient.md`.

**Por qué numerados**: porque después podés decir "está en el 38" y se encuentra. Y
porque el número es cronológico, así que ves el orden en que se pensaron las cosas.

Lo que va ahí: concepto, cosmología del disco, el cuento que da origen a los textos,
el plan de release, la guía de estilo visual, los playbooks de difusión, la anatomía
de las capas de sonido, la lista de contactos de prensa.

**La regla de oro**: cuando algo se decide, se escribe. Cuando algo se descarta, **se
escribe por qué**. Nuestro doc de difusión tiene una tabla de palancas pagas donde
cada una dice "descartada porque X". Eso vale más que la lista de lo que sí vamos a
hacer, porque evita volver a discutirlo en tres meses.

Para vos, los que yo tendría desde el día uno:

1. **Concepto del disco** — de qué se trata, en tus palabras.
2. **Plan de release** — fechas, distribuidor, qué falta.
3. **Textos** — ver abajo, es el más útil de todos.
4. **Metadata** — ver abajo.
5. **Prensa** — a quién le mandaste qué y cuándo.

---

## 5. Dos archivos que te van a ahorrar semanas

### `textos.md` — la biblia de voz

Un solo archivo con **todo el texto público del disco, ya escrito**:

- Bio del artista en tres largos: tagline de una línea, corta para Spotify (150
  caracteres), larga para Bandcamp y Apple.
- Descripción del disco, en corta y larga.
- Un texto por tema.
- Trece frases sueltas para redes, en español y en inglés.
- Las reglas de voz: qué nunca se dice.

**Por qué importa tanto**: cuando cargás el disco en el distribuidor, te va a pedir
la bio en tres tamaños distintos, y después Bandcamp te pide otra, y Spotify otra, y
cada formulario tiene un límite de caracteres distinto. Si no lo tenés escrito de
antes, lo improvisás a las once de la noche con el upload a medio hacer, y te queda
una bio distinta en cada plataforma.

Con el archivo, es copiar y pegar. Y todas las plataformas dicen lo mismo, que es
lo que hace que una identidad se sienta sólida.

### `metadata.md` — la fuente de verdad de los datos

La tabla de tu disco: por track, título exacto, artista como debe figurar, número de
track, y el **ISRC** cuando el distribuidor te lo asigne.

Más: género principal, año, sello, copyright, la fecha exacta de release, el nombre
tal cual va a aparecer.

**Por qué**: esos datos se cargan en el distribuidor, en Bandcamp, en la metadata de
los archivos, en MusicBrainz, en el press kit. Si no hay una fuente única, terminás
con el título escrito de tres formas distintas y ese error se propaga a todo el
ecosistema, donde es carísimo de corregir.

Los ISRC en particular: son los identificadores únicos de cada grabación. Te los da
el distribuidor y **hay que anotarlos**, porque después los necesitás para
MusicBrainz, para reclamos de regalías y para cualquier corrección.

---

## 6. El dashboard: cómo está armado

Es un tablero de estado del proyecto. **Dos archivos, sin dependencias, sin build**:

```
dashboard/
├── data.json     ← todos los datos
└── index.html    ← todo el código (HTML + CSS + JS en un archivo)
```

Se abre con un servidor local simple y listo. Nada de npm, nada que se rompa en seis
meses.

### La decisión clave: los porcentajes se calculan, no se escriben

En el JSON **no hay ni un solo porcentaje**. Solo el estado de cada tarea. El HTML
cuenta y calcula al cargar la página.

Eso parece un detalle y es lo que hace que el tablero no mienta: si el número
estuviera escrito, quedaría viejo a la primera tarea que cambia, y a los dos meses
nadie le cree.

### La estructura de `data.json`

```json
{
  "meta": { "updated": "2026-08-05", "next_review": "2026-08-31" },

  "projects": [
    {
      "id": "heliopause",
      "title": "ÆM · Heliopause",
      "brief": "El release y su difusión.",
      "description": "El texto largo, se ve solo al entrar al proyecto",
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

Los campos de una tarea: **`status`** (`done` / `todo` / `in_progress` /
`blocked`), **`owner`** (quién la hace), **`note`** (el contexto, y es la parte más
valiosa: ahí va por qué algo se decidió o se descartó), **`blockedBy`** y **`eta`**.

### Las tres secciones, y por qué están separadas

Esto lo aprendimos mezclándolo mal primero.

**`projects`** — lo que tiene avance y termina. Cada uno con fases y tareas, y su
barra de progreso.

**`recurring`** — lo que **no termina nunca**: revisar métricas, recargar la cola del
programador de posts, mandar un reporte cada tres semanas. Antes las teníamos como
tareas normales y quedaban en 0% para siempre, porque no se pueden terminar. Cada una
tiene su periodicidad y **la próxima fecha se calcula** (última vez + cada cuánto), y
se pinta en rojo si está vencida.

**`lab`** — los experimentos. **Sin barra de progreso**, a propósito. Un lab no es un
plan: se entra, se agarra uno y se ejecuta. Cada uno tiene un estado (pendiente / en
curso / ejecutado / muerto) y, cuando muere o se convierte en proyecto, queda la
referencia a lo que salió.

Mezclar las tres es lo que hace que un tablero se abandone: el progreso general nunca
avanza porque lo tironean las cosas que no terminan.

### Y lo más importante del tablero

Es **la única fuente de verdad del estado**. En nuestro `CLAUDE.md` está escrito que
cuando se pregunte "qué falta" o "en qué estamos", se lea `data.json` y **no** los
planes viejos, que están congelados en una etapa que ya pasó.

Sin esa regla, el asistente te contesta con un plan de marzo y suena muy convincente.

---

## 7. El `Taskfile`: los comandos del proyecto

Usamos [Task](https://taskfile.dev), que es como un `Makefile` pero en YAML y
legible. Un solo archivo en la raíz con todos los comandos del proyecto:

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
    desc: Analiza los WAV renderizados y avisa si hay frituras
    cmds:
      - "{{.PYTHON}} scripts/qa_spectral.py"
```

Y después `task --list` te muestra todo lo que se puede hacer, con su descripción.

### Por qué vale la pena aunque tengas tres comandos

**Porque los nombrás una vez y no los volvés a recordar.** El comando real para
levantar nuestro sitio en local es largo y tiene flags que nadie se acuerda. Con el
Taskfile es `task site:dev`.

**Porque el asistente los usa.** Si en el `CLAUDE.md` dice "para desplegar corré
`task site:deploy`", Claude lo corre bien la primera vez. Si no existe, va a
inventar un comando de wrangler con los flags equivocados.

**Y porque documenta el proyecto sin escribir documentación.** Leer `task --list` te
dice qué se puede hacer con el repo.

Para vos, los que tendrían sentido: convertir los masters a los formatos de release
(FLAC, MP3, WAV 44.1), incrustar la metadata y la tapa en los archivos, validar que
los masters cumplan el nivel de loudness que piden las plataformas, y hacer el backup
del audio al disco externo.

Los nombres van con dos puntos para agrupar: `release:formats`, `release:tag`,
`release:check`.

---

## 8. Qué de todo esto NO copiar

Para ser honesto sobre lo que en tu caso es carga y no ayuda:

- **`framework/`** — nosotros componemos escribiendo código Python. Vos grabás. No
  aplica.
- **`player/`** — un reproductor web local para escuchar los renders. Vos usás tu DAW.
- **La estructura de `transmissions/NN/`** — tiene sentido para un sello con
  releases numerados. Para un disco, una carpeta `album/` alcanza.
- **El dashboard con tres secciones** — si tenés veinte tareas, una lista en el
  README alcanza. El tablero se justifica cuando dejás de acordarte de lo que hay
  pendiente.
- **45 documentos** — eso creció en cuatro meses. Empezá con cinco.

Y lo que yo sí armaría el primer día, en este orden:

1. **`.gitignore`**, antes del primer commit. Con `*.wav`, `*.aiff`, `*.mp3`,
   `*.mp4`, `*.zip` y cualquier carpeta de proyecto del DAW.
2. **`CLAUDE.md`** con cómo trabajás, tus reglas duras y lo que ya te salió mal.
3. **`docs/textos.md`** con las bios en tres tamaños.
4. **`docs/metadata.md`** con la tabla de tracks y un lugar para los ISRC.
5. Un **backup de audio** que no sea git.

Con eso ya estás mejor parada que el 90% de los proyectos, y son un par de horas.
