# Game of Life + Síntesis Modular: Plan de Profundización

> Documento de trabajo. La idea es bajar a tierra una pregunta abierta: ¿qué hay en la intersección entre autómatas celulares (Conway) y la síntesis modular, y qué queda por explorar?

---

## 1. Trasfondo conceptual

### 1.1 Por qué los sintes son "un espejo de la naturaleza" (Ernesto Romeo)

Ernesto Romeo —fundador de Klauss (1988), codirector del estudio La Siesta del Fauno con Pablo Gil (2011), docente de la Licenciatura en Artes Electrónicas en UNTREF— ha trabajado esta tesis explícitamente. Su show actual se titula *"Los sintetizadores, un espejo de la naturaleza"* y propone "un paisaje sonoro vivo donde sistemas de síntesis modular y dispositivos electrónicos dialogan con los sonidos del monte chaqueño".

Sus propias palabras (entrevistas):
- *"Cuanto más se profundice la relación emocional con las posibilidades del arte sonoro electroacústico como una forma de reconectar con la naturaleza primigenia, más liberador será el proceso."* (Mixmag)
- *"Una profundización de lo generativo en organismos electroacústicos."* (Revista Wipe)
- *"Las variaciones amplias de frecuencia tienen que ver con la naturaleza electrónica del sonido."* (Agencia Paco Urondo)

La afirmación se sostiene técnicamente por cuatro razones:

**a) Un sinte modular GENERA el sonido, no lo reproduce.**
Un piano sampleado es una fotografía de un piano. Un VCO analógico es una fuente de vibración eléctrica —matemáticamente la misma familia de fenómenos que produce una cuerda, una columna de aire o un cristal piezoeléctrico. No imita: *es* oscilación.

**b) Los procesos modulares describen procesos naturales.**
- Envolventes ADSR → cómo decae cualquier sonido natural, cómo se evapora agua, cómo se enfría un líquido.
- LFOs → ciclos circadianos, mareas, latidos.
- Filtros resonantes → cavidades, cuerpos de guitarra, gargantas, fórmulas vocálicas.
- Ruido blanco/rosa → estadísticamente idéntico a lluvia, mar, viento.

**c) El paradigma modular es ecosistémico, no orquestal.**
Conectás módulos, se influyen mutuamente, el resultado emerge de las relaciones. Don Buchla y Morton Subotnick pensaban explícitamente así en los 60s. La escuela "West Coast" (Buchla, Serge) viene de esa filosofía de "sistema vivo"; la "East Coast" (Moog) es más teclado-céntrica e imitativa. Romeo dicta masterclasses comparando exactamente esas dos filosofías.

**d) El feedback y la no-linealidad producen emergencia.**
Un patch con realimentación, slew limiters, sample & hold y comparators se comporta como un sistema dinámico no-lineal. Mismas matemáticas que rigen poblaciones, clima, fluidos.

### 1.2 Qué es el Game of Life y por qué se conecta

Game of Life (Conway, 1970) es un autómata celular bidimensional:
- Grilla de celdas, cada una viva o muerta.
- 4 reglas locales basadas en vecindario de Moore (8 vecinos):
  - <2 vecinas vivas → muere (subpoblación)
  - 2 o 3 → sobrevive
  - >3 → muere (sobrepoblación)
  - exactamente 3 (estando muerta) → nace

**Lo crítico**: de esas 4 reglas pavas emergen patrones que parecen organismos —gliders, osciladores, naves espaciales, cañones. Es Turing-completo (podés construir una computadora dentro de él).

**Conexión con síntesis modular**: ambos son **sistemas emergentes**. Pocas reglas locales → comportamiento global complejo. Un patch modular bien armado *es* un autómata continuo. Filosóficamente, ambos son menos "composición" y más "cultivo": plantás condiciones iniciales y observás qué crece.

### 1.3 Linaje histórico del cruce

- **Iannis Xenakis** (años 60): composición estocástica, primeros pasos.
- **Brian Eno** (años 70-90): "música generativa" formaliza el principio "pocas reglas → resultado siempre distinto". El término lo acuña él.
- **Eduardo Reck Miranda** (años 90): CAMUS, sistema de generación musical basado en autómatas celulares 2D. Referencia académica clásica.
- **Wolfram** (2002, *A New Kind of Science*): formaliza la clasificación de autómatas (Clase I-IV), donde Game of Life es Clase IV ("complejidad al borde del caos") —exactamente donde uno quisiera estar musicalmente.

---

## 2. Quién ya cruzó los dos mundos

### Hardware comercial / DIY

**Nervous Squirrel — "Conway's Game"** (Dave Cranmer, UK)
- Módulo Eurorack con matriz 8x8 de jacks (64 salidas de trigger independientes)
- Modo MIDI o modo Life autónomo
- Outputs configurables como trigger o gate
- Precio: £420–£440
- Link: https://www.modulargrid.net/e/other-unknown-conway-s-game
- Demo en YouTube: https://www.youtube.com/watch?v=rErT5oEnW5M
- Cobertura CDM (Create Digital Music): https://cdm.link/conways-game-of-life-eurorack/
- Versión prototipo de 2016 basada en código Arduino de Tyler Hyndman (open source): https://github.com/tylo42/Arduino-Game-of-Life

**vtol — "2112"** (Rusia, 2011)
- Secuenciador matricial DIY que simula Game of Life
- Integrado a un sistema modular más amplio del mismo artista
- Cobertura Hackaday: https://hackaday.com/2011/03/27/music-synthesized-from-the-game-of-life/

**Curiosidad relacionada**: Nervous Squirrel también construye un módulo que genera CV y gate a partir del decaimiento radiactivo de mineral de uranio. O sea, física nuclear → modular. El nicho es profundo.

### Software / Académico

**CAMUS** — Eduardo Reck Miranda (años 90)
- Sistema generativo basado en autómatas celulares 2D
- Citado en patentes como antecedente
- Miranda tiene varios libros sobre composición algorítmica que valen la pena: *Composing Music with Computers* (2001), *Computer Sound Design* (2002)

**VCV Rack — módulos de cellular automata**
- VCV Rack es un modular virtual gratuito (https://vcvrack.com/)
- Módulos relevantes: Bogaudio's Automata, Nysthi, Mscellaneous LFSR
- Buscar también: "Bogaudio Walks" para random walks que se asemejan
- Esto es el camino más barato para experimentar: descargar Rack, agarrar un Conway, mapear celdas a osciladores

**Patches en Max/MSP, SuperCollider, Pure Data**
- Hay decenas de implementaciones académicas
- Buscar: "cellular automata music max msp" en GitHub

### Software comercial integrado

- **Ableton Live** + Max for Live: hay devices comunitarios que implementan Conway como secuenciador
- **Reaktor** (Native Instruments): ensembles de la comunidad incluyen autómatas celulares

---

## 3. Discusiones abiertas / qué queda por explorar

> **Nota importante**: esta sección es síntesis y especulación mía sobre el estado del arte. No salió de una sola fuente sino del cruce entre tres cosas: cómo funciona Game of Life mecánicamente (limitación conocida en CS), la existencia de autómatas continuos como Lenia (paper de Bert Wang-Chak Chan, 2018), y la literatura general de sonificación de datos. Son **hipótesis a falsar**, no hechos verificados. Antes de afirmar "nadie hizo X" hay que hacer un barrido sistemático de literatura académica (NIME, ICMC, SMC).

### 3.1 El problema del mapeo

Game of Life es **binario y discreto**: las celdas están vivas o muertas, no a medias. Para música esto es una limitación real:
- Tiende a estabilizarse en patrones cíclicos o a morir entero → repetición o silencio
- El mapeo "celda viva = trigger" desperdicia información estructural (¿dónde está la celda? ¿qué tan vieja? ¿cuántas vecinas tiene?)
- La mayoría de implementaciones existentes usan el mapeo más obvio (celda → trigger)

**Hipótesis para falsar**: hay poca exploración de mapeos sofisticados:
- Densidad regional de la grilla → cutoff de filtro
- Velocidad de cambio (delta entre generaciones) → tempo o intensidad
- Detección de gliders → patrones melódicos identificables
- Centro de masa de la población → pan / espacialización

### 3.2 Lenia y autómatas continuos: territorio fértil

**Lenia** (Bert Wang-Chak Chan, 2018) es la versión continua del Game of Life. Las celdas son valores reales entre 0 y 1, las reglas son funciones continuas. Produce patrones que parecen literalmente medusas, amebas, criaturas marinas.
- Paper original: https://arxiv.org/abs/1812.05433
- Video demo (vale la pena ver): https://www.youtube.com/watch?v=iE46jKYcI4Y

**Hipótesis**: musicalmente Lenia debería sonar mucho más orgánico que Conway porque sus valores continuos mapean directo a CV (control voltage). Conway necesita gates; Lenia podría modular cutoff, pitch, amplitud directamente.
- Búsqueda preliminar sugiere que hay muy poco hecho con Lenia → audio. Verificar.

### 3.3 Otros autómatas musicalmente interesantes (poco explorados)

- **Reglas de Wolfram 1D** (Rule 30, Rule 110): autómatas de una sola línea, mapean naturalmente a un secuenciador lineal de 16 o 32 pasos
- **Reaction-Diffusion** (Gray-Scott): los patrones de Turing en biología (manchas de leopardo, rayas de cebra) → ¿cómo suenan?
- **Boids** (Reynolds, 1987): bandadas que se autoorganizan, ideales para control multidimensional en tiempo real
- **Slime mold** (Physarum polycephalum) computacional: hay implementaciones digitales del moho que resuelven laberintos

### 3.4 La gran pregunta filosófica que (creo que) nadie planteó del todo

Si Romeo dice que los sintes son un espejo de la naturaleza, y Conway/Lenia son simulaciones de vida, entonces **un sistema Lenia → modular es naturaleza simulando naturaleza a través de un espejo de la naturaleza**. ¿Eso es más "natural" o menos? ¿Cuándo deja de ser simulación y empieza a ser fenómeno?

Esto se cruza con discusiones más viejas (Cage, Eno, Subotnick) pero no encontré que se haya formulado específicamente en estos términos. Verificar.

### 3.5 Lo práctico ausente

- No hay (que yo sepa) un álbum completo compuesto puramente con Game of Life como única fuente generativa, lanzado por un artista de la escena modular argentina/latinoamericana. Sería un proyecto concreto y delimitado.
- No hay performance documentada de Romeo o La Siesta del Fauno usando autómatas celulares como núcleo conceptual. Romeo trabaja con naturaleza grabada (el monte chaqueño), pero el cruce con vida simulada podría ser un siguiente paso natural.

---

## 4. Próximos pasos de research

1. **Validar el estado del arte académico**: buscar papers en NIME (New Interfaces for Musical Expression), ICMC (International Computer Music Conference), SMC (Sound and Music Computing). Términos: "cellular automata sonification", "Lenia audio", "Game of Life music generative"
2. **Contactar a Romeo / La Siesta del Fauno**: preguntarle directamente si experimentó con autómatas. Está activo y enseña en UNTREF.
3. **Experimento mínimo viable**: armar un patch en VCV Rack con Conway → 4 voces → grabar 10 minutos. Documentar el mapeo. Sería el "hello world" del proyecto.
4. **Leer**: Miranda, *Composing Music with Computers* (capítulos sobre CA). Wolfram, *A New Kind of Science* (cap. 6 y 7).

---

## Fuentes consultadas

- Synthtopia: https://www.synthtopia.com/content/2023/06/26/new-eurorack-module-conways-game-applies-classic-game-of-life-to-music-sequencing/
- CDM: https://cdm.link/conways-game-of-life-eurorack/
- Matrixsynth: https://www.matrixsynth.com/2016/12/conways-game-of-life-synth-module.html
- Adafruit Blog: https://blog.adafruit.com/2023/08/14/game-of-life-and-eurorack-musicmonday/
- Molten Music: https://moltenmusictechnology.com/nervous-squirrel-conways-game-life-is-an-algorithm/
- Hackaday: https://hackaday.com/2011/03/27/music-synthesized-from-the-game-of-life/
- Diario Norte (Romeo en Resistencia): https://www.diarionorte.com/302309-ernesto-romeo-llega-por-primera-vez-a-resistencia
- Electronic Groove (entrevista a Romeo): https://electronicgroove.com/entrevista-ernesto-romeo/
- Mixmag España (entrevista a Romeo): https://mixmag.es/read/entrevistamos-a-aca-news
- Agencia Paco Urondo (entrevista a Romeo): https://www.agenciapacourondo.com.ar/cultura/ernesto-romeo-el-sintetizador-nos-permite-reconectar-con-una-parte-perdida-del-arte-sonoro
- Revista Wipe (entrevista a Romeo): https://wipe.com.ar/entrevista-a-ernesto-romeo/
- 343 Pro Sessions (masterclass de Romeo): https://pro.343labs.com/products/abril-9-nyc-livestream-ernesto-romeo-sintesis-sonora-y-modulares
- Lenia (paper original): https://arxiv.org/abs/1812.05433
