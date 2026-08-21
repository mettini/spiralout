# 43 · El motivo Em + H

> Estado: **decidido**. Bajado por el user el 2026-08-09.
> Es el motivo melódico de TX02 entero, los tres tracks.
> Implementado en `transmissions/02/bj3_n_pt/cuerdas.py` (`MOTIVO`, `SEMITONOS`, `altura()`).

## De dónde sale

TX02 es un disco de amor y su tercer track se llama **+H**, la suma de Em y H.

**H, en notación alemana, es el Si natural.** Ahí B significa Si bemol y H el Si
becuadro. Es la notación con la que Bach firmaba su apellido en notas: B-A-C-H.

Y entonces aparece lo que hace que todo esto funcione:

> **Em = Mi, Sol, Si.** El Si **ya está adentro del acorde**: es su quinta.

H no se le agrega a Em desde afuera. Siempre estuvo ahí. Para un disco cuyo cierre
narrativo es una firma que vuelve con un carácter fundido que antes no estaba
(`docs/10_cuento.md`, ficha de cierre), eso es exacto: no se sumó nada, se reveló.

## El motivo

Tres notas, siempre las mismas. Lo que cambia entre tracks es **cuál es el centro**.

| Track | Motivo | Qué dice |
|---|---|---|
| 1 | **Si → Sol → Mi**, descendente | Algo cae. Termina en Mi: la entidad sigue siendo ella |
| 2 | las mismas, rondando sin cerrar | Hay vida, y no resuelve |
| 3 | **Mi → Sol → Si**, ascendente | Las mismas tres notas al revés, terminando en Si |

Nada se suma y sin embargo cambia todo. Es la **Æ**: dos letras, un solo glifo.

## La afinación

La base de TX02 está en **71,3 Hz**, medido con `check_source.py` sobre
`mix_v2_arco.wav`. Eso es un **Re unos 50 cents bajo**.

Re no está en el acorde de Em, pero sí en la escala: es su séptima. Así que el motivo
suena **sobre su propia séptima**, o sea Em7 con la séptima abajo. Es un acorde que
flota y no resuelve nunca, que es el color que pide un track de once minutos donde
alguien mira caer algo sin entender qué es.

Frecuencias, derivadas de la base y no de un afinador:

| Nota | Semitonos sobre la base | Hz | Octava de chelo |
|---|---|---|---|
| **Mi** | 2 | 80,03 | 160,06 |
| **Sol** | 5 | 95,17 | 190,35 |
| **Si** | 9 | 119,91 | 239,82 |

Todo lo que se toque afinado a esta tabla queda consonante con el tema por
construcción, no por suerte.

## La conexión con Heliopause (verificada 2026-08-09)

Chequeado contra el motivo protegido, **sin tocarlo**. Lectura pura de
`framework/aem/motifs.py` y `framework/aem/voyager_factory.py`.

| | Heliopause (TX01) | Transmission 02 |
|---|---|---|
| Motivo | **D5-F5-A5** = Re menor | Mi-Sol-Si = Mi menor |
| Nota base | drone en **73,42 Hz** = Re2 | **71,3 Hz** = Re, 50 cents abajo |

Dos hallazgos, y ninguno de los dos fue diseñado:

**1. Es el mismo Re, desafinado medio cuarto de tono.** La nota de casa del Voyager
suena en el planeta, pero mal. El planeta no es la Tierra.

**2. Em7 es Mi-Sol-Si-Re.** La séptima del acorde de TX02 es exactamente **la nota
raíz del motivo Voyager**. La armonía de la entidad se traga la nota de casa del
visitante y la deja colgada, sin resolver.

O sea que TX02 no estrena un motivo: **le contesta al de TX01**. El Re que en
Heliopause era el hogar, acá es la disonancia de abajo.

## Dónde está implementado

`transmissions/02/bj3_n_pt/cuerdas.py`:

```python
SEMITONOS = {"mi": 2, "sol": 5, "si": 9}
MOTIVO = (("si", 5.0), ("sol", 4.2), ("mi", 6.5))     # descendente, track 1
altura(nombre, octava)                                 # Hz derivados de FUND = 71,3
```

El track 3 usa la misma tabla con el motivo dado vuelta.

> **El voyager sigue protegido.** Esta comparación fue de solo lectura. Cualquier
> cambio a sus defaults requiere aprobación explícita del user y `task qa:voyager`
> contra el benchmark (`memory/voyager_protegido.md`).
