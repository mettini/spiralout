# 42 · La lengua de la entidad

> Estado: **fórmulas fijadas, primeras tomas grabadas**.
> Es material de obra, no una nota de trabajo: de acá salen los coros de TX02.
> Punto de vista y narrador → `docs/39` §El punto de vista.

## Qué es

La entidad que narra TX02 recita en **protoindoeuropeo**. Cuatro fórmulas, siempre
las mismas. No hay traducción pública ni explicación: es la voz de la civilización
del planeta y punto.

## Por qué esa lengua y no otra

| Razón | |
|---|---|
| **No está atestiguada** | No existe un solo texto en PIE. Es una reconstrucción deducida comparando las lenguas que salieron de él. Cada forma se escribe con asterisco porque nadie la vio escrita nunca |
| **Es la misma forma que el cuento** | Una hipótesis sobre un idioma, igual que la ficha de cierre de `docs/10_cuento.md` enumera hipótesis "por orden de proposición, no por verosimilitud" |
| **Es anterior a la separación** | Es el ancestro común del sánscrito, el griego y el latín. Para un disco que termina en una fusión, una lengua de antes de la división |
| **Nadie puede corregirla** | La pronunciación está discutida entre los propios lingüistas. El misterio queda blindado |
| **Suena no humana de por sí** | Laringales y grupos consonánticos que no existen en ninguna lengua viva |

**Descartadas**: sánscrito (mantra new age) y latín (iglesia), los dos gastados.
**Evaluadas y en reserva**: hurrita (el Himno a Nikkal de Ugarit, ~1400 a.C., la
melodía anotada más antigua que se conoce) y sumerio (el idioma atestiguado más
antiguo, lengua aislada, con corpus real de conjuros).

## Las cuatro fórmulas

| # | Forma reconstruida | Cómo se dice | Significa |
|---|---|---|---|
| 1 | \*ḱléwos ń̥dʰgʷʰitom | KLÉ·uos ən·də·GUÍ·tom | fama imperecedera |
| 2 | \*dyḗws ph₂tḗr | DIÉUS pa·TÉR | padre cielo |
| 3 | \*h₂epōm nepōts | ha·PÓM ne·PÓTS | el descendiente de las aguas |
| 4 | \*(h₁e)gʷʰent h₃ógʷʰim | e·GUÉNT Ó·guim | mató a la serpiente |

Las columnas 2 y 3 son aproximaciones sayables, no dictamen. Las reconstrucciones
varían entre autores.

### De dónde sale cada una

1. **\*ḱléwos ń̥dʰgʷʰitom.** La fórmula poética reconstruida más famosa. Se dedujo
   porque aparece por separado en Homero (*κλέος ἄφθιτον*) y en el Rigveda
   (*śrávas ákṣitam*), dos tradiciones que no se tocaron. Es la prueba de que hubo
   poesía en esta lengua, y la frase poética más antigua que se puede reconstruir.
2. **\*dyḗws ph₂tḗr.** Dio Zeus, Júpiter y el Dyaus pitar védico. El nombre más viejo
   que se le puso a algo que está arriba.
3. **\*h₂epōm nepōts.** Dio el Apām Napāt védico, el Nechtan irlandés y el Neptuno
   latino. **Es la que más se merece estar acá**: el track está hecho enteramente de
   grabaciones de lluvia.
4. **\*(h₁e)gʷʰent h₃ógʷʰim.** La fórmula mitológica central, la que reaparece en el
   mito del dragón en media docena de tradiciones sin contacto entre sí.

## Los seis sonidos que no existen en castellano

| Signo | Qué es | Cómo hacerlo |
|---|---|---|
| ʰ | aspiración | La consonante más un soplido, como la "t" inglesa de *top* |
| ʷ | labializada | Consonante con labios redondeados. `gʷ` es "gu" de *guante* pero como UN sonido |
| ḱ | palatal | Una "k" más adelante, contra el paladar. Aproximar "ky" |
| ń̥ | sonante silábica | La "n" funciona como vocal, es una sílaba sola |
| h₁ h₂ h₃ | laringales | Nadie sabe cómo sonaban. Tiñen de "a" lo que tienen al lado |
| ō ḗ | vocal larga | Sostenida, el doble de tiempo |

## Cómo se recita

- **A la mitad de la velocidad natural, sosteniendo las vocales.** Esto se estira
  mucho, y el estirado funciona sobre material sostenido, no sobre ritmo de habla.
- **Casi en monotono**, plano, sin actuar. La entidad no está enojada ni es solemne.
- **No forzar el gutural.** La profundidad se fabrica después, y forzándola se mete
  ruido de garganta que no se saca más.
- Tres tomas reales por frase, no copias del mismo archivo.

**La afinación NO es problema del que graba.** Se corrige después por velocidad de
cinta, que es lo que hay que hacer igual. Ver abajo.

## Las tomas (2026-08-08)

| Toma | Archivo | F0 medida | Carácter |
|---|---|---|---|
| limpia | `Ortiz de Ocampo 4.m4a` | 100,4 Hz | recitada plana |
| gutural | `Ortiz de Ocampo 5.m4a` | 97,6 Hz | medio cantada |

Las dos vinieron a ~75 kbps AAC mono, o sea del teléfono. **Para la definitiva hay
que regrabar en WAV por la Volt**: el estirado extremo amplifica los artefactos del
codec, porque cada cuadro espectral queda sostenido un segundo entero en vez de pasar
en 20 ms.

## Cómo se transforma en coro

`lab/thermal_mass/voces.py`.

Las tres voces del stack **se derivan de la fundamental de la base, no de la toma**,
así el coro no se apoya sobre el tema sino que es el tema:

| Voz | Frecuencia | Rol |
|---|---|---|
| sub | 35,65 Hz | una octava abajo de la base. El peso |
| raíz | 71,30 Hz | la fundamental, al unísono. El cuerpo |
| quinta | 106,95 Hz | la quinta justa (3/2). El brillo, más atrás |

**Por velocidad de cinta, nunca con pitch shifter.** Bajar por velocidad hunde los
formantes junto con el tono, y esa es exactamente la diferencia entre "voz grave" y
"voz de otra cosa". Un shifter que preserva formantes suena a chipmunk al revés.

Lo demás: entradas escalonadas y desafinación leve entre repeticiones (sin eso las
copias se suman en fase y vuelve a sonar a una sola voz), saturación con `tanh` para
el cuerpo, y una sala muy larga, que es la otra mitad del sonido.

> **Dos trampas ya documentadas que aplican acá.** La saturación tira armónicos a
> 1,5-4 kHz, la banda que marca `task qa:spectral`: por eso el LPF va **después** del
> `tanh` y no antes (`T_VOICE_PAD_HARMONICS`). Y el exciter va con `tanh`, nunca con
> `abs()` (`memory/abs_rectifier_exciter_antipattern.md`).
