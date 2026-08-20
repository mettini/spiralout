# 47 · Protocolo de entrega

Regla del user, agosto 2026: **antes de decir que algo está listo, se corre el examen
automático y se reporta el veredicto con números.** No existe el criterio "se ve bien".

Vale para cualquier entregable del proyecto: video, master, artwork, sitio.

---

## Por qué existe

Durante la ronda 6 del video di por resuelto lo que no estaba, varias veces y por causas
distintas:

| Qué pasó | Por qué |
|---|---|
| Reporté "antes 32, ahora 32" | **medí el archivo viejo**: el build había fallado y no chequeé la fecha |
| Marqué planos como buenos y salieron negros | **medí una cadena distinta** de la que se renderiza (sin `brightness`, con otro contraste) |
| Escalé la curva de grado y no mejoró | **no verifiqué que la escalada sirviera**, ni probé otro punto de entrada |
| Dije que las reglas se cumplían | la guarda **solo verificaba dos de las cuatro** |
| Sincronicé cortes con la melodía | la sincronía se perdía en el render por **deriva de duración** que nadie medía |

El patrón es siempre el mismo: **verifiqué una parte y afirmé sobre el todo.**

---

## El examen

```bash
python3.10 lab/thermal_mass/video/qa_entrega.py
```

Devuelve PASA o FALLA por criterio y un veredicto final. Si algo falla, no se entrega.

Lo primero que imprime es **la fecha y el tamaño del archivo que está midiendo**,
precisamente porque ya pasó reportar sobre uno viejo.

| # | Criterio | Umbral |
|---|---|---|
| 1 | Reglas de repetición (`PLAN_RONDA6` §V2) | las cuatro, sin excepción |
| 2 | Sin texto, logo ni corte interno | todo plano dentro de una ventana medida |
| 3 | Sin deriva de duración | video contra audio, menos de 0,1 s |
| 4 | Cortes sobre los cambios de nota del moog | los 7 a menos de 0,1 s |
| 5 | Sin judder | cuadros exactamente repetidos, menos del 2% |
| 6 | Sin fogonazos ni estrobos | cero hallazgos |
| 7 | Sin planos relámpago | ninguno de menos de 6 s |
| 8 | Sin pantalla negra | hasta 6 planos con más del 70% casi negro |
| 9 | QA espectral del audio | limpio |

**El umbral 8 no es cero a propósito.** Parte de este video tiene que ser negro: la
medusa en el fondo del océano no se puede iluminar sin arruinarla. Seis es el margen
para lo que es negro por decisión y no por defecto.

---

## Las tres reglas de método

**Medir sobre la salida, no sobre el plan.** El plan dice lo que se pidió; el archivo
dice lo que pasó. Entre los dos hubo hasta 1,65 s de diferencia acumulada.

**Medir la cadena real, no una parecida.** Si la validación usa parámetros distintos de
los del render, predice sobre otra cosa. Los parámetros de cada tratamiento viven en una
sola tabla y los dos lados la leen.

**Verificar que el arreglo arregló.** Aplicar una corrección y seguir de largo no es
arreglar: hay que volver a medir lo mismo que se midió antes, sobre el archivo nuevo.

---

## Cuándo se corre

- Antes de decir que un entregable está listo
- Antes de pasar de 1080 a 4K
- Después de cualquier cambio en `planos.py`, `montaje.sh` o las capas de audio

Los escáneres que lo alimentan:

| Archivo | Qué hace |
|---|---|
| `ventanas.py` | escanea cada fuente cada 0,5 s buscando texto, logos y **cortes internos**, y guarda las ventanas limpias en `ventanas.json` |
| `verificar.py` | renderiza cuadros de **cada plano tal como va a salir** y busca texto, rectas y siluetas reconocibles |
| `revisar.py` | sobre la salida final: texto quemado, fogonazos y estrobos |
| `qa_entrega.py` | el examen completo, con veredicto |
