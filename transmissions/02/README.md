# Transmission 02 · Athanor

Segunda transmisión. En composición. **Nombre: Athanor. Color: azul.**

El athanor es el horno de los alquimistas: alimentación continua, calor bajo y
constante durante días. Lo que lo define técnicamente es la **masa térmica**, que
es la técnica con la que está construida la cama de este disco y el nombre del lab
del que salió el track 1. Concepto completo en `docs/39_transmission_02.md`.

| Track | Nombre | Audio | Video |
|---|---|---|---|
| 01 | `bj3 n pt` | 11:11 masterizado | 1080 aprobado · 4K pendiente |

## bj3 n pt

Egipcio antiguo, "hierro del cielo": el nombre con que se llamaba al metal
meteorítico antes de que existiera la metalurgia del hierro. El `3` está por la
ꜣ (alef egiptológica), porque el glifo tiene forma de tres y el disco está
construido sobre el tres.

Salió del lab `thermal_mass` y se promovió cuando quedó claro que era el primer
track de la transmisión y no un experimento. La técnica que le daba nombre al
lab (masa térmica) sigue siendo la de la cama.

---

## Convención de carpetas

La misma que `01/`. Los wav no van sueltos en la raíz del track: cada cosa
tiene su lugar según **en qué etapa** del proceso está.

```
transmissions/02/
├── themes/bj3_n_pt/            el codigo que genera el audio
│   ├── tema.py                 el arreglo: junta las capas y masteriza
│   ├── render.py               las capas base (thermal_mass, cloud, manifold, flywheel)
│   ├── rain.py voces.py cuerdas.py melodia.py moog.py
│   ├── capas/                  lo que rinde cada modulo por separado      [ignorado]
│   ├── prototypes/             mezclas de prueba y melodias candidatas    [ignorado]
│   ├── finals/v1/              el master aprobado                         [ignorado]
│   └── source/                 las grabaciones de entrada                 [ignorado]
└── video/bj3_n_pt/             el codigo que genera el video
    ├── planos.py               arma la lista de planos con las 4 reglas
    ├── ventanas.py             escanea las fuentes, saca ventanas limpias
    ├── verificar.py            revisa cada plano cuadro por cuadro
    ├── qa_entrega.py           el examen de 9 criterios
    ├── montaje.sh              el render
    ├── ventanas.json           las ventanas limpias medidas       [VERSIONADO]
    ├── fuentes/                el material de archivo bajado      [ignorado]
    ├── generado/               los clips generados                [VERSIONADO]
    └── out/                    los entregables
        ├── bj3_n_pt_1080.mp4                                      [ignorado]
        └── bj3_n_pt_1080.plan.txt                                 [VERSIONADO]
```

**Qué se versiona y qué no.** La regla es: si sale de correr el código, no va
al repo. Los wav de capa, las mezclas, el master y los videos se rehacen.

Las dos excepciones, y por qué:

- **`ventanas.json`** son las ventanas limpias de cada fuente, medidas
  escaneando 41 archivos cada 0,5 s. Cuesta horas y no cambia salvo que entre
  material nuevo.
- **`out/*.plan.txt`** es el plan congelado del entregable: con qué material,
  qué recortes y qué puntos de entrada se armó el video que se publicó. Sin
  eso, el `out/` es un binario sin procedencia.

---

## Comandos

```bash
python3.10 transmissions/02/themes/bj3_n_pt/tema.py         # el master, 11:11
bash       transmissions/02/video/bj3_n_pt/montaje.sh       # el video 1080
bash       transmissions/02/video/bj3_n_pt/montaje.sh --4k  # la entrega
python3.10 transmissions/02/video/bj3_n_pt/qa_entrega.py    # el examen
```

**Antes de dar cualquier cosa por lista corré `qa_entrega.py`.** Nueve criterios
medidos sobre el archivo final, con veredicto. El protocolo y las razones por
las que existe están en [`docs/47`](../../docs/47_protocolo_de_entrega.md).

## Backup

`ÆM/transmissions/02/` en el Drive, con la misma estructura que el `01`. El
README de allá tiene los checksums, el LUFS y **la tabla de licencias de cada
fuente de video**, que es lo que hace falta el día que un agregador pregunte
por derechos de terceros.
