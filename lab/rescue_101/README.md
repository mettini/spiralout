# Rescue 101 — la vida en el planeta

> **TX02, track 2.** Lab de Pure Data.
> Estado: **concepto cerrado, patch sin arrancar.** Falta instalar Pd y salir a
> grabar.
>
> Caja de herramientas y referencias → `docs/40_pure_data_lab.md`
> Concepto de la transmisión → `docs/39_transmission_02.md`
> Anatomía de capas → `docs/38_capas_dark_ambient.md`

## Qué es este track

Caés al planeta en el track 1 y **acá descubrís que hay vida**. Flora y fauna del
lugar: plantas, flores, bichos, algo parecido a pájaros.

Es **el track luminoso de los tres**, y es a propósito. Contra el track 1, que es
mineral y violento (`transmissions/02/bj3_n_pt/`), este es orgánico y paciente. El arco de la
transmisión es descendente y después ascendente: caés, encontrás que hay vida, y en
el track 3 te conectás con algo más grande.

**Referencias**: KMRU, *By Absence* (del álbum *Kin*, 20:22). Grabación de campo más
drone, largo, sin apuro, **no oscuro**. Y Steve Roach del lado del sostenido cálido.

**Duración objetivo**: 11:11.

## La regla estética, que es también el problema técnico

**No es un documental de la naturaleza.** Ese es el riesgo entero del track.

Si grabo pájaros del barrio y los pongo abajo de un pad, suena a app de meditación.
Y el planeta de TX02 no es la Tierra.

La salida es grabar fauna real **y usar solo su forma, no su sonido**:

```
grabación de un pájaro real
        │
        ├── sigmund~ ──→ qué nota canta ────────────┐
        ├── env~     ──→ cómo sube y baja el volumen┤
        └── bonk~    ──→ cuándo arranca cada frase ─┤
                                                    ▼
                                        una voz sintética
                                    (pluck~ + resonbank~)
```

Queda con el fraseo de algo vivo, porque el fraseo es real, y con el timbre de algo
que no existe. **Nadie va a poder decir qué bicho es. Todos van a sentir que está
vivo.**

Eso es la voz del proyecto sin tener que explicar nada.

## Las voces

Mapeadas a las seis capas de `docs/38`. Ojo con el peso: **acá el edificio está al
revés que en el track 1**. Thermal Mass es todo abajo. Rescue 101 vive en el medio y
arriba, y ahí es donde por fin entra la capa de grano que le falta a todo el
proyecto.

| # | Capa | Banda | Nivel | Voz en este track | Motor |
|---|---|---|---|---|---|
| 1 | Sub / cama | 20-120 Hz | **−12 dB** (mucho menos que en track 1) | El planeta respirando abajo. Presente pero no protagonista | grabación estirada, reciclada del track 1 |
| 2 | Cuerpo | 120-400 Hz | −6 dB | Madera, troncos, algo hueco y grande. La "flora" | `resonbank~` excitado con granos |
| 3 | Nube / medio | 250-1500 Hz | **−3 dB, protagonista** | El aire del lugar. Un acorde que no termina de definirse | granular de campo, posición caminando lento |
| 4 | **Detalle / grano** | 1-6 kHz | **−6 dB, protagonista** | **Los bichos.** Chirridos, clicks, frotes. La capa que da escala | `randpulse~` → `resonbank~`, y caóticos |
| 5 | Aire | 6 kHz+ | −15 dB | Que se sienta que es afuera y no un cuarto | grabación de ambiente a ganancia alta |
| 6 | Eventos | ancho | picos a −8 dB | **Los cantos.** Frases que aparecen y se van. Lo único que marca el tiempo | análisis → síntesis (arriba) |

Las capas 4 y 6 son el track. Si esas dos fallan, no hay nada.

## Qué hay que grabar

Lista de caza específica. No hace falta equipo bueno para explorar, el celular sirve
para saber si una fuente da. Para el material definitivo, la Volt 276.

| Para | Grabar |
|---|---|
| **Cantos** (capa 6) | Pájaros de mañana temprano, de cerca. Un solo pájaro y no un coro: necesito la frase limpia para que `sigmund~` la lea. Grillos de noche. Perros lejanos, gatos |
| **Bichos** (capa 4) | Hojas secas apretadas. Ramas quebrándose. Insectos si aparecen. Y sustitutos raros que suenan a bicho: una cremallera lenta, un peine, papel de calcar, hielo en un vaso |
| **Flora** (capa 2) | Golpear un tronco. Bambú. Una maceta de barro. Madera hueca. La caja de una guitarra golpeada con la palma |
| **Aire del lugar** (capa 5) | Un parque a las 6 de la mañana, cinco minutos sin moverse. Viento en hojas. Lluvia lejana. Esto es lo más fácil de conseguir y lo que más rinde |
| **Agua** (transversal) | Un arroyo, una canilla goteando en una pileta llena, agua en una botella |

**Dos cosas prácticas:**

- **Micrófono de contacto.** Es lo que usa KMRU y sale barato. Pegado a un tronco o a
  una planta capta cosas que el micro de aire no agarra: la savia, el crujido interno,
  el bicho caminando adentro de la madera. Para "flora de otro planeta" es la
  herramienta obvia.
- **Grabar largo.** Cinco minutos por fuente, no treinta segundos. El granular
  necesita material para caminar por adentro, y los cantos necesitan varias frases
  distintas para que el análisis tenga de dónde elegir.

Antes de procesar nada, pasar cada grabación por `scripts/check_source.py`, que dice
qué capa sirve y si vale la pena.

## Anatomía del patch

Cinco módulos, cada uno en su archivo, y un patch madre que los abre y los mezcla.
Así se puede tocar uno sin romper el resto y se le hace diff a lo que cambió.

```
rescue_101.pd                 patch madre: carga todo, arco de 11:11, writesf~
├── voz_nube.pd               granular sobre la grabación de ambiente
├── voz_flora.pd              resonbank~ excitado por granos
├── voz_bichos.pd             randpulse~ + resonadores + caóticos
├── voz_cantos.pd             el análisis → síntesis (el corazón del track)
└── voz_cama.pd               el sub, reciclado del track 1
```

### Los tres relojes

El track necesita tres escalas de tiempo corriendo a la vez:

- **Rápido** (ms): los granos, los chirridos, cada canto.
- **Medio** (5 a 40 s): qué voces están prendidas. Acá manda `coin` y `random`. Es lo
  que hace que el minuto 3 no sea el minuto 8.
- **Lento** (minutos): el arco. **Esto va escrito a mano, no al azar**, igual que la
  tabla de automatización de `transmissions/02/bj3_n_pt/mix.py`.

La regla que ya aprendimos en thermal_mass: **el azar decide el detalle, la mano
decide la forma.** Un patch enteramente generativo suena a demo de patch.

### Arco propuesto (11:11)

| Tramo | Qué pasa |
|---|---|
| 0:00 – 1:30 | Solo la cama y el aire. Todavía no sabés si hay algo |
| 1:30 – 3:30 | Entra la nube. El lugar tiene tamaño |
| 3:30 – 5:00 | **Primer bicho.** Uno solo, aislado, sospechoso |
| 5:00 – 7:30 | Los bichos se multiplican. Entra la flora |
| 7:30 – 9:00 | **El primer canto.** Es el evento del track. Algo grande está vivo |
| 9:00 – 10:30 | Todo junto, denso, y por primera vez suena habitado |
| 10:30 – 11:11 | Se retira todo menos el aire. Queda el lugar |

El primer canto a los 7:30 es la apuesta: el oyente ya se resignó a que es un drone
de ambiente y ahí aparece algo que claramente **decidió** cantar.

### Determinismo

Al cargar, un `loadbang` manda `seed` a cada objeto de azar. Sin eso, dos renders
dan tracks distintos, que está perfecto para explorar y es un problema para cerrar un
master. En thermal_mass la semilla es 24 (el hexagrama de Heliopause); acá va a ser
la misma, por continuidad.

## Qué va a git

| Va | No va |
|---|---|
| Los `.pd` | Los WAV que salen |
| Este README con las decisiones | Las grabaciones fuente crudas (van a backup, con su línea acá) |
| El script de render | |

## Próximos pasos

1. **Bajar plugdata** (`plugdata.org`). Corre solo, y trae la librería ELSE adentro
   así no hay que instalar nada a mano.
2. **Bajar Pd vanilla** (`msp.ucsd.edu/software.html`) para poder renderizar sin
   interfaz. Los patches son los mismos archivos.
3. **Salir a grabar** una mañana. Con la lista de caza de arriba. Es lo único que
   nadie puede hacer por él y es lo que bloquea todo lo demás.
4. Armar `voz_cantos.pd` primero, no último. Es el módulo que puede fallar
   conceptualmente y conviene saberlo temprano. Si el análisis → síntesis no
   convence, el track hay que repensarlo.
5. Recién ahí el resto de las voces y el arco.

## Registro

*(vacío — se llena cuando empiece)*
