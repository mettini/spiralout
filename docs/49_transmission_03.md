# 49 — Transmission 03 (rojo)

> Estado: **rumbo bajado, sin nombre ni narrativa**. Bajado por el user el
> 2026-08-28. No hay lab abierto todavía.
>
> **Ojo con una entrada vieja**: el backlog decía "TX03 = Rescue 100". Eso ya no
> corre. `Rescue 101` se fusionó como track 2 de TX02 (ver `docs/39`). TX03 está
> libre.

## Lo único decidido

**Color: rojo.** Entra como accent de transmisión, igual que el azul de Athanor,
sobre la paleta core de `docs/14_design_system.md`. Rojo después de azul, y los dos
después del fósforo de TX01.

## La forma del disco

### Track 1 · el que migra de género

Arranca **dark ambient** y termina en **techno oscuro**. Un solo track que cambia
de mundo sin cortar.

**La conexión son las turbinas de un cohete espacial.**

Esa elección resuelve el problema técnico sola, y por eso conviene dejar escrito
por qué funciona: una turbina arrancando **es** las dos cosas en secuencia. Al
principio es un drone (ruido de banda ancha, sin pulso, que es dark ambient), y a
medida que sube de vueltas ese ruido **adquiere periodicidad**: la frecuencia de
paso de álabes se vuelve audible y de ahí sale un pulso. O sea que el drone no se
reemplaza por un beat, **se convierte** en beat. La transición no es un corte ni
un fundido, es un objeto físico acelerando.

Implicancia para la composición: el tempo del techno debería salir de la turbina y
no elegirse antes. Si la turbina llega a N revoluciones por segundo, ese es el
tempo, y el track queda amarrado a algo real en vez de a una grilla.

### Tracks 2 y 3 · más claros

**Acid y trippie.** Más luminosos que el track 1.

Acid implica 303 o emulación: filtro resonante barrido con acento y slide. Es lo
primero del proyecto que pediría un secuenciador con groove propio, no el
enfoque de composición por código de los discos anteriores. Hay que ver si se
resuelve en el framework `aem` o si entra otra herramienta.

## Arco de la trilogía (hipótesis, sin confirmar)

| | Disco | Color | Qué pasa |
|---|---|---|---|
| 01 | Heliopause | fósforo | la sonda cruza el umbral |
| 02 | Athanor | azul | la caída al planeta, narrada por la entidad |
| 03 | ? | rojo | ? |

Si TX03 abre con turbinas de cohete, lo natural es que sea **el despegue**: lo que
en TX02 cayó, en TX03 se va. Eso cerraría el viaje. **Es una lectura mía, no una
decisión del user**, y no debería filtrarse a ningún texto público hasta que él la
confirme o la reemplace.

## Lo que falta

1. Nombre del disco.
2. Narrativa y punto de vista (TX02 fijó que la entidad narra los tres tracks del
   disco; TX03 tiene que definir el suyo).
3. Si sigue la regla de 11:11 por track que se decidió en TX02.
4. De dónde salen las turbinas: grabación real, síntesis, o archivo NASA. Hay
   material de lanzamientos en dominio público y el proyecto ya sabe tratarlo.
5. Con qué se hace el acid.

## Enganches con lo que ya existe

- `docs/14_design_system.md` — la paleta core y el mecanismo de accent por
  transmisión.
- `docs/39_transmission_02.md` — TX02, de donde viene la continuidad narrativa.
- `docs/27_lab_experiments_and_references.md` — experimentos abiertos que podrían
  alimentar este disco, sobre todo el "Silicon" (síntesis desde la máquina).
- `docs/22_game_of_life_sintes_modulares.md` — autómatas y modular, si el acid se
  resuelve por patch generativo.
