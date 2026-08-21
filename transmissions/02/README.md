# Transmission 02

Segunda transmisión. En composición.

| Track | Nombre | Estado |
|---|---|---|
| 01 | `bj3_n_pt` | audio 11:11 masterizado · video 1080 aprobado · falta el 4K |

## bj3 n pt

Egipcio antiguo, "hierro del cielo": el nombre con que se llamaba al metal
meteorítico antes de que existiera la metalurgia del hierro. El `3` está por la
ꜣ (alef egiptológica), porque el glifo tiene forma de tres y el disco está
construido sobre el tres.

Salió del lab `thermal_mass` y se promovió acá cuando quedó claro que era el primer
track de la transmisión y no un experimento. El nombre del lab quedó en la historia
de git; la técnica que le da nombre (masa térmica) sigue siendo la de la cama.

```bash
python3.10 transmissions/02/bj3_n_pt/tema.py              # el master, 11:11
bash       transmissions/02/bj3_n_pt/video/montaje.sh     # el video 1080
bash       transmissions/02/bj3_n_pt/video/montaje.sh --4k
python3.10 transmissions/02/bj3_n_pt/video/qa_entrega.py  # el examen de entrega
```

**Antes de dar cualquier cosa por lista corré `qa_entrega.py`.** Nueve criterios
medidos sobre el archivo final, con veredicto. El protocolo y por qué existe están en
[`docs/47_protocolo_de_entrega.md`](../../docs/47_protocolo_de_entrega.md).

## Qué hay acá y qué no

Todo lo que sale de correr el código está git-ignoreado y se rehace: los wav de cada
capa, las mezclas, los videos, las fuentes bajadas y el cache de capas. Lo que se
versiona es el código, los docs, `ventanas.json` (las ventanas limpias medidas de cada
fuente) y el plan congelado de cada entregable (`*.plan.txt`), que documenta con qué
material exacto se armó el video que se publicó.
