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
python3.10 transmissions/02/bj3_n_pt/video/qa_entrega.py
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
| 8 | Sin pantalla negra | hasta 29 planos con más del 70% casi negro |
| 9 | QA espectral del audio | limpio |
| 10 | Cuadriculado tratado | cero planos de fuente aplastada sin tratamiento |

**El umbral 8 no es cero a propósito.** Parte de este video tiene que ser negro: la
medusa en el fondo del océano no se puede iluminar sin arruinarla. El tope es un
**guardián de regresión**: el user aprobó la versión con 27, así que 29 frena cualquier
cambio que empuje el video a más negro que lo aprobado. Para bajar de verdad hay que
cambiar el material, no el grado.

**El criterio 10 existe porque los otros nueve pasaban y el defecto estaba igual.** El 4K
salió con cuadrados grandes en el primer minuto y lo tuvo que encontrar el user mirando:
ningún criterio miraba la textura.

**Y mide cobertura, no resultado. Vale la pena decir por qué.** La primera versión
intentaba medir el cuadriculado sobre la salida y estaba mal: daba FALLA sobre el video
ya arreglado. Se probaron tres métricas y las tres se dejan engañar:

- **cociente de meseta** (dispersión dentro de la baldosa contra entre baldosas): un
  degradado LISO es plano adentro igual que una meseta, y la salida del modelo es lisa
  por diseño. Marcaba 42 planos en el video corregido contra 34 en el defectuoso.
- **salto en la rejilla**: después del modelo la grilla de la fuente ya no existe, así que
  medir a ese paso no encuentra nada real.
- **pico espectral** (sin necesidad de conocer el paso): lo domina la estructura de la
  imagen, no el bloque. Mediana 878 contra 742, no discrimina.

Así que el criterio verifica que **todo plano de fuente aplastada haya recibido
tratamiento** (el modelo si se amplía 2x o más, blur si no). Es determinístico y frena la
regresión que importa: que alguien rehaga el video sin correr `mejorar.py`.

**Lo que este criterio NO puede hacer es juzgar si el resultado se ve bien.** Eso hoy se
valida a ojo, sobre un antes/después EN MOVIMIENTO, y está bien que quede escrito que es
así en vez de fingir que hay un número.

---

## Las tres reglas de método

**Medir sobre la salida, no sobre el plan.** El plan dice lo que se pidió; el archivo
dice lo que pasó. Entre los dos hubo hasta 1,65 s de diferencia acumulada.

**Medir la cadena real, no una parecida.** Si la validación usa parámetros distintos de
los del render, predice sobre otra cosa. Los parámetros de cada tratamiento viven en una
sola tabla y los dos lados la leen.

**Verificar que el arreglo arregló.** Aplicar una corrección y seguir de largo no es
arreglar: hay que volver a medir lo mismo que se midió antes, sobre el archivo nuevo.

**Cuando el user encuentra algo que el examen no vio, el arreglo incluye el criterio
nuevo.** Si no, el mismo defecto vuelve en la próxima entrega y lo tiene que cazar él de
nuevo. Así entró el criterio 10, y la forma de saber que el criterio sirve es correrlo
contra el archivo defectuoso y ver que FALLA antes de arreglar nada.

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
