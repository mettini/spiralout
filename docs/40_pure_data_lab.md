# 40 — El lab de Pure Data

> Data operativa para el track 2 de TX02 (**Rescue 101**, flora y fauna del
> planeta). Recolectada el 2026-08-06.
>
> El lab del track vive en `lab/rescue_101/`. Este doc es la caja de herramientas:
> qué instalar, qué objetos existen, qué técnica sirve para qué, y cómo se enchufa
> con el pipeline que ya tenemos.

## Por qué Pd y no otra cosa

Tres razones, y la tercera es la que importa para este repo.

1. **Es gratis y open source**, sin cuenta, sin licencia, sin nube.
2. **Es dataflow puro**: cajitas conectadas con cables. No hay un "arreglo" ni una
   línea de tiempo, así que **no invita a componer, invita a dejar corriendo**. Para
   un track de once minutos de fauna que nunca se repite, eso es exactamente lo que
   se quiere.
3. **Un patch de Pd es un archivo de texto plano.** Un `.pd` se abre con un editor
   y se lee. Eso significa que **entra al repo como fuente** igual que un
   `compose_*.py`, se le hace diff, y el WAV que sale se puede tirar porque se
   regenera. Es la misma regla que ya rige todo el proyecto.

Lo que Pd **no** va a ser: la mezcla. La mezcla sigue en el framework de Python o en
Live. Pd genera material y lo escupe a WAV.

## El triángulo de herramientas de TX02

Los tres tracks quedan con tres motores distintos, y no es capricho: cada motor
produce un tipo de material distinto y eso separa los tracks solo.

| Track | Motor | Qué produce |
|---|---|---|
| 1 · el pasaje por la atmósfera | **Python + numpy** (`framework/`, `scripts/paulstretch.py`) | Deformación de grabaciones. Determinista, offline, mineral |
| 2 · **Rescue 101** | **Pure Data** | Generación por reglas. Vivo, nunca igual dos veces, orgánico |
| 3 · **+H** | **VCV Rack 2** (o Cardinal como plugin) | Modulación de voltaje. Se autoorganiza, no se toca |

## Qué instalar

Hay dos sabores y conviene tener los dos. No es redundancia, hacen cosas distintas.

### plugdata — el que vas a usar para construir

**Es lo primero que hay que bajar.** `https://plugdata.org` — gratis, GPL-3.

Es un fork moderno de Pd con dos ventajas concretas:

- **Trae ELSE y Cyclone adentro**, o sea 600+ objetos extra sin instalar nada. Sin
  esto, Pd vanilla pelado no tiene ni granular ni caos ni resonadores, que es
  justamente todo lo que necesitamos.
- **La interfaz es humana.** La de Pd vanilla es de 1996 y se nota.

Corre solo, como programa aparte. No hace falta ningún DAW.

> Dato al margen, por si alguna vez sirve: plugdata también se puede exportar como
> plugin AU/VST3 y meter el patch adentro de un DAW. **No lo necesitamos.** Para este
> track el patch corre suelto y escupe un WAV, y el WAV entra al pipeline que ya
> tenemos.

### Pd vanilla — el que vamos a usar para renderizar

`https://msp.ucsd.edu/software.html`, versión actual **0.56** (ELSE pide 0.56-2 o
superior). Para macOS baja un `.tar.gz`.

Sirve para una sola cosa, pero importante: **renderizar sin interfaz desde la
terminal**, con `pd -nogui -batch`. Eso es lo que hace que el track sea
reproducible y que se pueda meter en el `Taskfile`. Los patches son los mismos
archivos, así que se construye en plugdata y se rinde en vanilla.

Si se instala Pd vanilla solo, las librerías se bajan desde adentro del programa:
**Help → Find Externals** (se llama *deken*), buscar `else`, y queda en
`~/Documents/Pd/externals`. Después hay que declararla en Preferences o poner
`[declare -lib else]` en el patch.

Bonus: cuando bajás ELSE por deken viene adentro la carpeta
`Live-Electronics-Tutorial`, que son cientos de patches de ejemplo comentados. Es la
mejor documentación que existe de Pd moderno.

## Los primeros veinte minutos (leer esto antes que nada)

> Pd no se parece a nada que hayas usado. No hay línea de tiempo, no hay pistas, no
> hay play. Abrís y ves una hoja en blanco. Es normal sentirse perdido: lo que falta
> no es talento, son cinco reglas.

**Hay dos patches de arranque en `lab/rescue_101/patches/`.** Abrilos con plugdata,
en ese orden. Están comentados adentro del propio patch.

| Patch | Qué hace |
|---|---|
| `00_hola.pd` | Un seno que **arranca solo**, sin tocar nada. Existe para verificar que sale sonido y, si no sale, para decirte dónde está el problema |
| `01_bicho.pd` | El primer bicho: un canto sintético que nunca repite la misma nota |

### Las cinco reglas

**1. Hay dos modos, y ese es el 90% de la confusión inicial.**
`Cmd+E` alterna entre ellos.

- **Modo edición**: el cursor es una manito. Ahí *construís*: arrastrás cajas, tirás
  cables. Los clics **no** hacen nada musical.
- **Modo ejecución**: el cursor es una flecha. Ahí *tocás*: hacés clic en los botones
  y en los mensajes y el patch responde.

Si hacés clic en algo y no pasa nada, casi seguro estás en el modo equivocado.

**2. Si no prendés DSP, no suena. Nunca.**

**DSP** es *digital signal processing*, y en Pd es el nombre del **motor de audio**.
Pd tiene dos mitades que corren por separado: la de eventos (números, clics, bangs),
que anda siempre, y la de audio, que calcula 44.100 muestras por segundo y **arranca
apagada**. Con el DSP apagado el patch funciona perfecto, los números se mueven, y no
sale un sonido. No te avisa de nada.

Se prende con `Cmd+/` y se apaga con `Cmd+.`. En plugdata es el **botón de power
arriba a la derecha**, al lado del medidor de nivel.

**Si el power está prendido y sigue sin sonar, quedan tres sospechosos, en este
orden:**

1. **El volumen de plugdata.** Tiene su propio fader en la barra de arriba, aparte del
   volumen de macOS. Si está abajo no suena nada aunque el patch ande.
2. **La salida de audio.** `Settings` (el engranaje) → `Audio` → **Output Device**. Si
   quedó apuntando a la Volt 276 y la Volt no está enchufada, no hay sonido. Ponelo en
   los parlantes de la Mac para probar.
3. **El patch.** Que es lo último que hay que sospechar, no lo primero.

`00_hola.pd` está armado justo para separar esos tres casos: arranca solo y tiene dos
números en pantalla, un contador y un medidor. Si el contador se mueve, el patch está
vivo. Si el medidor marca cerca de 74, el sonido **existe** y el problema es de ahí
para afuera: volumen o salida de audio.

**3. Tres tipos de caja, tres atajos.**
En modo edición, se crean donde está el cursor:

| Atajo | Qué crea | Para qué |
|---|---|---|
| `Cmd+1` | **Objeto** (caja de bordes rectos) | Hace algo: `osc~`, `metro`, `random` |
| `Cmd+2` | **Mensaje** (caja con el borde derecho mordido) | Guarda un valor y lo dispara cuando le hacés clic |
| `Cmd+5` | **Comentario** | Texto suelto, no hace nada |

Escribís adentro, hacés clic afuera y la caja se crea. Si el objeto no existe, la caja
queda punteada: o está mal escrito o falta la librería.

**4. Entradas arriba, salidas abajo, y la de más a la izquierda es la caliente.**
Los cables van de una salida (borde de abajo) a una entrada (borde de arriba). En modo
edición, arrastrás desde el pico de abajo hasta la caja de destino.

La regla que hay que memorizar: **la entrada de más a la izquierda es la "caliente"**,
la que dispara el cálculo. Las demás son "frías": guardan el valor y esperan. Por eso
`[+ ]` con un 5 en la entrada derecha no hace nada hasta que le llegue algo por la
izquierda.

**5. Cable grueso es audio, cable fino son números.**
Los objetos que terminan en `~` (se dice "tilde") trabajan con señal de audio, 22050
veces por segundo, y sus cables se dibujan gruesos. Los que no llevan tilde trabajan
con eventos sueltos: un número, un bang, una lista, y se dibujan finos.

**No se mezclan de cualquier forma.** Un número no entra a una entrada de señal salvo
que el objeto lo permita explícitamente. El puente entre los dos mundos son `line~` y
`vline~`, que convierten "andá a 0.3 en 500 ms" (un mensaje) en una rampa de audio.

### Las cuatro cajas que ya te alcanzan para jugar

- `[metro 900]` es el reloj: manda un **bang** (un "¡ahora!") cada 900 ms. Se prende
  con un 1 y se apaga con un 0.
- `[random 600]` tira un entero entre 0 y 599 cada vez que le llega un bang.
- `[osc~ 220]` es un seno a 220 Hz. Si le enchufás señal por la izquierda, la
  frecuencia pasa a salir de ahí.
- `[dac~]` son los parlantes. Dos entradas: izquierda y derecha.

Con eso está armado `01_bicho.pd` entero. Nada más que eso.

### Cuando algo no anda

| Síntoma | Casi siempre es |
|---|---|
| No suena nada | DSP apagado. Si no, el volumen de plugdata o el Output Device (ver la regla 2) |
| Hago clic y no pasa nada | Estás en modo edición (`Cmd+E`) |
| La caja quedó punteada | Nombre mal escrito, o falta la librería |
| "error: signal outlet connect to nonsignal inlet" | Estás metiendo un cable grueso donde va uno fino |
| Cruje al prender el volumen | Te falta un `line~`: el salto instantáneo es un clic |

La ventana **Pd** (`Cmd+R`, o el panel de la consola en plugdata) es donde aparecen
los errores. Tenela a la vista: en Pd los errores no se muestran encima del patch.

### El atajo que más rinde

Clic derecho sobre cualquier objeto → **Help**. Abre un patch de ayuda que **suena**,
con todos los parámetros y ejemplos andando. No es documentación escrita: es un patch
que podés tocar. Para los objetos de ELSE la ayuda es especialmente buena.

## El vocabulario mínimo

De los ~600 objetos, estos son los que vamos a tocar. Los que dicen **ELSE** vienen
de esa librería (o sea que ya están en plugdata).

### Cargar y reproducir grabaciones

| Objeto | Qué hace |
|---|---|
| `soundfiler` | Carga un WAV entero a un array en memoria. Es el punto de entrada de todo |
| `array` / `table` | El buffer donde vive la grabación |
| `tabread4~` | Lee el array con interpolación. La base de cualquier reproducción a velocidad arbitraria |
| `readsf~` | Streamea del disco, para archivos largos que no entran en RAM |
| `player~` **ELSE** | Reproductor listo, con velocidad y loop |
| `sfload` **ELSE** | Carga más cómoda que `soundfiler` |

### Granular

| Objeto | Qué hace |
|---|---|
| `grain.synth~` **ELSE** | Sintetizador granular completo. **El caballito de batalla del track** |
| `gran.player~` **ELSE** | Reproductor granular sobre un archivo |
| `pvoc.player~` **ELSE** | **Phase vocoder**: time-stretch tipo paulstretch, en tiempo real |
| `pvoc.live~` **ELSE** | Lo mismo sobre entrada en vivo |

`pvoc.player~` es el mismo principio que `scripts/paulstretch.py`, pero jugable con
un fader. Sirve para explorar rápido y después clavar el valor en Python.

### Análisis (el sample maneja al sinte)

| Objeto | Qué hace |
|---|---|
| `env~` | Seguidor de envolvente. Saca el volumen de una señal como número |
| `sigmund~` | Detector de altura y de picos espectrales. Te dice **qué nota** está sonando |
| `fiddle~` | El detector de altura viejo, todavía útil |
| `bonk~` | Detector de ataques. Te avisa **cuándo** golpea algo |
| `timbreID` (externo aparte) | Clasificación de timbre. Reconoce "esto suena como aquello" |

### Síntesis y resonancia

| Objeto | Qué hace |
|---|---|
| `osc~` / `phasor~` | Seno y diente de sierra, el ladrillo básico |
| `pluck~` **ELSE** | **Karplus-Strong**: cuerda pulsada. Con parámetros raros da pájaros y bichos |
| `resonator~` / `resonbank~` **ELSE** | Bancos de resonadores. Le ponen "cuerpo físico" a un ruido |
| `resonant~` **ELSE** | Un resonador solo |
| `bob~` / `lop~` / `bp~` | Filtros. `bob~` es el Moog emulado |

### Azar y caos (el motor generativo)

| Objeto | Qué hace |
|---|---|
| `random` + `metro` | El azar básico, y el reloj. Aceptan mensaje `seed` |
| `coin` **ELSE** | Moneda cargada: pasa con probabilidad N |
| `lfnoise~` / `stepnoise~` / `rampnoise~` **ELSE** | Ruido lento. La modulación orgánica de siempre |
| `randpulse~` **ELSE** | Pulsos a intervalos aleatorios |
| `lorenz~` `henon~` `logistic~` `ikeda~` `latoocarfian~` `gbman~` `cusp~` `quad~` `fbsine~` `standard~` `lincong~` **ELSE** | **Osciladores caóticos.** No son ruido y no son periódicos: son sistemas deterministas que nunca se repiten. Es lo más parecido a un ser vivo que hay en un sinte |
| `gendyn~` **ELSE** | La síntesis dinámica estocástica de Xenakis |

Los caóticos son la razón de fondo para usar Pd en este track. Un `lfnoise~`
modulando un filtro suena a sinte. Un `lorenz~` haciendo lo mismo suena a que algo
está **decidiendo**.

### Salida

| Objeto | Qué hace |
|---|---|
| `writesf~` | Graba a WAV. Con `open`, `start`, `stop` |
| `dac~` | Salida a los parlantes |

## Las cuatro técnicas que nos importan

### 1 · Granular sobre grabación de campo

La grabación entra a un array y se lee en pedacitos de 20 a 200 ms, cada uno con su
propia envolvente, superpuestos. Cambiando cuatro números cambia todo:

- **Tamaño del grano**: chico (5-30 ms) da textura y silba; grande (100-500 ms) deja
  reconocer la fuente.
- **Densidad**: cuántos por segundo. Poca densidad da goteo, mucha da nube.
- **Posición de lectura**: fija da un pad estático; caminando lento da la sensación de
  atravesar el lugar; aleatoria dentro de una ventana da vida sin ir a ningún lado.
- **Dispersión de altura**: cada grano un poco desafinado respecto al otro. Es lo que
  hace que suene a coro y no a delay.

Para Rescue 101, la posición de lectura tiene que **caminar muy lento** hacia
adelante. Once minutos de grabación de campo recorridos en cámara lenta.

### 2 · Análisis → síntesis: la fauna real maneja a la fauna sintética

Esta es la técnica fuerte del track y vale explicarla, porque resuelve el problema
conceptual de fondo.

El problema: si grabamos pájaros de acá y los ponemos, suena a **documental de la
naturaleza terrestre**. Y el planeta de TX02 no es la Tierra.

La solución: **grabar fauna real, pero usar solo su forma, no su sonido.**

```
grabación de un pájaro
        │
        ├── sigmund~ ──→ la altura, nota por nota ──┐
        ├── env~     ──→ la envolvente de volumen ──┤
        └── bonk~    ──→ cuándo empieza cada canto ─┤
                                                    ▼
                                        una voz sintética
                                     (pluck~ / osc~ + resonbank~)
```

Lo que sale tiene el **fraseo** de un ser vivo, porque el fraseo es real, y el
**timbre** de algo que no existe. Nadie va a poder decir qué bicho es, pero todos van
a sentir que está vivo. Eso es exactamente la voz del proyecto: misterio, no
explicación.

Y no lo inventamos nosotros. KMRU cuenta que para *Dissolution Grip* miró los
espectrogramas de sus grabaciones de campo y **replicó esas formas con síntesis**,
partiendo de que un sonido natural es un montón de tonos simples apilados. Nosotros
hacemos lo mismo pero automatizado.

### 3 · Modelado físico para bichos

Andy Farnell escribió el libro sobre esto: *Designing Sound* (MIT Press), con todos
los patches en Pd. La sección **Lifeforms** tiene insectos y cantos de pájaro
resueltos sin una sola grabación.

Los dos principios que se repiten:

- **Insectos**: no es ruido. Es intermodulación extrema entre dos osciladores
  simples. El chirrido de un grillo es un pulso muy rápido con un cuerpo resonante
  arriba, o sea `randpulse~` → `resonbank~`.
- **Pájaros**: es casi todo **movimiento de altura**. Una onda filtrada con una
  envolvente de frecuencia agresiva ya lee como canto. El timbre importa mucho menos
  que la curva.

Ojo con nuestro antipatrón: **ruido filtrado con corte arriba de 1 kHz suena a
fritura**, no a insecto (`memory/pattern_noise_fritura.md`). Si un bicho tiene que
brillar, el brillo sale de resonadores, no de ruido agudo.

### 4 · La estructura generativa

Once minutos no se escriben, se dejan pasar. El patch necesita tres niveles de
tiempo corriendo a la vez:

- **Rápido** (milisegundos): los granos y los cantos.
- **Medio** (5 a 40 segundos): qué voces están activas. Acá va `coin` y `random`, que
  encienden y apagan cosas. Es lo que hace que el minuto 3 no sea el minuto 8.
- **Lento** (minutos): el arco general. Esto **no** lo dejo al azar. Va escrito, igual
  que la tabla de automatización de `transmissions/02/bj3_n_pt/mix.py`.

La regla que ya aprendimos en thermal_mass y que aplica igual: **el azar decide el
detalle, la mano decide la forma.** Un patch 100% generativo suena a demo de patch.

## Cómo se enchufa con el repo

### Determinismo

`transmissions/02/bj3_n_pt/render.py` tiene `SEMILLA = 24` y por eso rinde igual siempre. En
Pd se consigue lo mismo: los objetos de azar aceptan un mensaje **`seed`** con un
número. Hay que mandarle la semilla a cada uno al cargar el patch, desde un `loadbang`.

Sin semilla, dos renders del mismo patch dan tracks distintos. Que está bien para
explorar y es un problema para cerrar un master.

### Render

```bash
# realtime, escuchando, con writesf~ grabando
pd patches/rescue_101.pd

# offline, sin interfaz, para el render final reproducible
pd -nogui -batch patches/rescue_101_render.pd
```

El patch de render es el mismo más un `writesf~`, un `del` con la duración total y un
mensaje `; pd quit` al final para que el proceso se cierre solo.

Cuando esté andando, esto entra al `Taskfile` como `task tx02:render:rescue`.

### Qué va a git y qué no

| Va | No va |
|---|---|
| Los `.pd` (son texto, se les hace diff) | Los WAV que salen del patch |
| El `README.md` del lab con las decisiones | Las grabaciones de campo crudas si son grandes |
| El script de render | |

Las grabaciones fuente son el caso incómodo: **no se regeneran** (son irrepetibles) y
pesan. Van a un backup aparte, con una línea en el README que diga qué es cada una y
de dónde salió. Igual que en `transmissions/02/bj3_n_pt/`.

## Referencias

- **Andy Farnell, *Designing Sound*** (MIT Press). El libro de audio procedural en
  Pd. Sección *Lifeforms* = insectos, cantos, animales. Es el más directamente útil
  para este track.
- **Alexandre Porres, *Live Electronics Tutorial***
  (`github.com/porres/Live-Electronics-Tutorial`). Viene adentro de ELSE. Cientos de
  patches comentados, actualizados, con la librería moderna.
- **`github.com/porres/pd-else`** — la librería. 595 objetos.
- **Miller Puckette, *Theory and Technique of Electronic Music*** — el libro del que
  creó Pd. Gratis en su sitio. Es teoría de síntesis, no tutorial.
- **`martin-brinkmann.de/pd-patches.html`** — patches de un tipo que hace música con
  Pd de verdad. Los mejores ejemplos de patch generativo que hay dando vueltas.
- **`patchstorage.com`** — repositorio comunitario. Filtrar por Pure Data. Buscar
  *J.a.g.s.* (sintetizador granular completo) como punto de partida.
- **`forum.pdpatchrepo.info`** — el foro. Sigue vivo y la gente contesta.
- **KMRU** sobre su método: usa las grabaciones de tres formas (como composición
  entera, como sample/instrumento, y como textura para síntesis), granulariza con
  *Grain Scanner* en Live, y graba con **micrófonos de contacto**. El de contacto es
  el dato accionable: es barato y capta cosas que un micro de aire no agarra.

## Lo que no vamos a hacer con Pd

Para no perder tiempo, dicho de entrada:

- **No mezclamos en Pd.** No tiene ni faders decentes ni medición. La mezcla es
  Python o Live.
- **No reemplaza al framework.** El framework hace deformación offline determinista y
  lo hace bien. Pd hace generación en tiempo real. Son dos trabajos.
- **No masterizamos en Pd.** Eso ya está resuelto en la cadena de `release/`.
- **No portamos thermal_mass a Pd.** Funciona. No se toca.
