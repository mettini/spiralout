# 37 — Registro de métricas (revisión semanal)

> Qué se mide, de dónde se saca y cómo se lee. La revisión es **semanal, los
> lunes**, y está en el dashboard como recurrente. El user pasa los números,
> Claude los registra en la tabla de abajo.
>
> Regla que hace que esto no sea burocracia: **cada métrica tiene un umbral o
> una pregunta asociada.** Si un número no cambia nada de lo que vas a hacer, no
> se mide. Mirar por mirar es perder el lunes.

## 1. Qué se mide y dónde

### A · Streaming (Spotify for Artists)
| Métrica | Dónde | Qué decide |
|---|---|---|
| Streams (7 días) | Home / Audience | Si se movió algo respecto de la semana anterior |
| Oyentes mensuales | Home | La única cifra que un curador o un blog va a mirar |
| Seguidores | Audience | Crecimiento real vs. escucha de paso |
| **Fuente de los streams** | Music → Source of streams | **La más importante**: playlist / perfil / externo / biblioteca. Dice de dónde viene la tracción, y por lo tanto qué palanca empujar |
| Saves y playlist adds | Music | Un save vale más que diez streams: es intención de volver |

### B · Bandcamp
| Métrica | Dónde | Qué decide |
|---|---|---|
| Plays | Stats | Si la gente que llega escucha o rebota |
| Ventas | Sales report | Es el único lugar donde hay dinero real |
| Wishlist adds | Stats | Intención sin plata: buen indicador temprano |
| Referrers | Stats | Confirma si IG, YouTube o Reddit traen gente |

### C · YouTube (Studio)
| Métrica | Dónde | Qué decide |
|---|---|---|
| Views por video | Contenido | Cuál de los tres engancha |
| **Retención media (%)** | Audiencia | Si la gente se queda. Es la métrica de calidad del targeting, más que las views |
| Suscriptores ganados | Audiencia | Si el canal empieza a existir o solo pasan |
| Tráfico externo | Alcance → Fuentes | De dónde llegan (búsqueda, sugeridos, IG, Reddit) |

### D · Google Ads (mientras haya campaña)
| Métrica | Dónde | Qué decide |
|---|---|---|
| Impresiones y views | Campaña | Si está entregando |
| **View rate** | Campaña | >15-20% en in-feed = el anuncio le interesa a quien lo ve |
| CPV real vs puja (19,74 ARS) | Campaña | Si hay que subir la puja para entrar en subasta |
| Gasto | Campaña | Contra el prepago de 50.000 ARS |
| Earned actions | Campaña | Subs y views que el canal ganó gracias al ad |
| Dónde se mostraron | Informes | **De acá sale la lista de emplazamientos del mes 2** |

### E · Instagram (perfil profesional)
| Métrica | Dónde | Qué decide |
|---|---|---|
| **Alcance de cuentas NO seguidoras** | Insights | La única métrica de captación. El alcance total con 2 seguidores no dice nada |
| Reproducciones de Reels | Insights | Reels = captación, feed = galería. Se comparan entre sí, no con el feed |
| Guardados y compartidos | Insights | Valen más que los likes: son señal de que el algoritmo distribuya |
| Seguidores | Insights | Crecimiento lento es lo esperado; caídas post-Reel, no |
| Clics en el link de la bio | Insights | El puente real hacia el sitio |

### F · Sitio (Search Console + GA4)
| Métrica | Dónde | Qué decide |
|---|---|---|
| Impresiones y clics | GSC | Si el sitio existe para Google |
| Queries nuevas | GSC | Si "ÆM" o "heliopause" ya son búsquedas propias — eso es marca |
| Páginas indexadas | GSC | Si lo nuevo entra al índice |
| Sesiones a `/aem` | GA4 | Si el anuncio y la bio traen gente al sitio |

### G · Reddit (durante la fase de karma)
| Métrica | Dónde | Qué decide |
|---|---|---|
| Karma de comentarios | Perfil | Umbral operativo: 20-30 habilita el primer post (50 para r/synthesizers) |
| Upvotes en el post propio | El post | 0 upvotes a las 2 horas = el sub no lo levantó, no insistir |

## 2. Lo que NO se mide

- **Likes.** No deciden nada.
- **Alcance total de IG** sin separar seguidores de no seguidores.
- **CPV bajo como señal de éxito.** Un CPV barato puede significar que compraste vistas del país equivocado.
- **Impresiones sin view rate.** Aparecer no es nada.
- **Métricas de Helen.** Los números son suyos, no nuestros (`docs/18`). Se
  observan solo para el reporte que se le manda.

## 3. Registro

Una fila por semana. Se completa el lunes con los números de los 7 días previos.

| Semana | Spotify (streams / oyentes / fuente) | Bandcamp (plays / ventas) | YouTube (views / retención / subs) | Ads (views / view rate / CPV / gasto) | IG (alcance no-seguidores / clics bio) | GSC (impr / clics) | Reddit (karma) | Qué se decidió |
|---|---|---|---|---|---|---|---|---|
| 2026-08-03 | | | | | | | | |

## 4. Estado de la línea de base (2026-07-26)

Para que la primera semana tenga con qué comparar:

- **IG**: 0 posts publicados, 2 seguidores. El Reel de Outbound sale el 27/07.
- **YouTube**: los 3 visualizers publicados el 02/07. Views de dos dígitos
  (11 / 7 / 4 según el selector de videos de Google Ads del 26/07).
- **Ads**: campaña creada el 26/07, primera lectura el 30/07.
- **Reddit**: u/emettini, 1 de karma, 0 contribuciones.
- **Spotify / Bandcamp / GSC**: sin línea de base tomada. **La primera revisión
  es tomarla**, no compararla — no hay con qué.
