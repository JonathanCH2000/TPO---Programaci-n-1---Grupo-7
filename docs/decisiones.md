# Decisiones de diseño

Registro de las decisiones que tomamos como grupo, con las alternativas que consideramos y por qué elegimos cada una.

## Entrega 1

### Mitad inferior y superior del cubo

- **Decisión:** La mitad inferior son las capas de z = 1 a N // 2 y la superior, el resto (con N = 8: inferior z = 1 a 4, superior z = 5 a 8).
- **Por qué:** La consigna no dice cómo partir el cubo. Con división entera la regla funciona para cualquier N; si N es impar, la capa del medio queda en la mitad superior.

## Entrega 2

### Excepciones propias en un módulo aparte (`errores.py`)

- **Decisión:** Todas las excepciones heredan de una clase base `ErrorCubo` y viven en `modulos/errores.py`. Por ahora hay `ErrorUbicacion` y `ErrorMunicion`.
- **Por qué un módulo aparte:** Las lanzan los módulos de dominio (`flota.py`, `armamento.py`) y las ataja el integrador (`partida.py`). Si estuvieran en `partida.py`, `flota.py` tendría que importar `partida.py`, que ya importa `flota.py` (evitamos importar de forma circular).
- **Por qué una clase base:** El integrador puede atajar cualquier error del juego con un solo `except ErrorCubo`, sin conocer cada tipo.

### `ubicar_nave` lanza una excepción en vez de devolver `None`

- **Decisión:** Si la nave no se puede ubicar, lanza `ErrorUbicacion` con el motivo ("La nave se sale del cubo.", "La celda ya esta ocupada por otra nave.", etc.).
- **Por qué:** Lo pide la consigna ("cubo y flota actualizados, o excepción") y el jugador sabe por qué falló. En `ubicacion_automatica` el error se ataja con `pass`, porque ahí fallar es normal (prueba puntos al azar hasta que alguno entra).

### Cada nave es un diccionario con un conjunto y un diccionario adentro

```python
{"tipo": "P", "puntos": {(5, 1, 1), (5, 1, 2), ...}, "impactos": {(5, 1, 1): 2}}
```

- **`puntos` es un conjunto:** Solo importa si un punto pertenece a la nave, no el orden, y `punto in conjunto` es inmediato.
- **`impactos` es un diccionario punto → cantidad:** El portaaviones necesita dos impactos por celda, así que no alcanza con marcar "impactada" (hay que contar).
- **Alternativa descartada:** La tupla `(tipo, puntos)` de la entrega 1. No permitía guardar impactos y obligaba a recordar qué había en cada posición (`nave[0]`).
- La consigna pide manejar el estado con diccionarios y conjuntos.

### Las reglas especiales de las naves son datos, no `if`

- **Decisión:** `IMPACTOS_POR_CELDA = {"P": 2}` en `flota.py` y `NAVES_INMUNES_LASER = {"S"}` en `armamento.py`.
- **Por qué:** La consigna prohíbe resolver estos casos con cadenas de `if` / `elif`. Además, si otra nave tuviera una regla parecida, se agrega una entrada sin tocar la lógica.

### El disparo le pregunta a la flota, no al estado de la celda

- **Decisión:** `_disparar_celda` decide si hay impacto con `buscar_nave` y `celda_destruida` (flota), no mirando si la celda dice `NAVE` (cubo).
- **Por qué:** Después del primer impacto, una celda del portaaviones queda en `IMPACTO` pero todavía aguanta otro. Y una celda que el sonar marcó como `DETECTADO` sigue teniendo una nave. Mirando solo el cubo, los dos casos darían "repetido".
- **Reparto de tareas:** `tablero` guarda los estados de las celdas, `flota` lleva la cuenta de cada nave y `armamento` decide qué pasa con cada disparo.

### Todas las armas devuelven `{punto: resultado}`

- **Decisión:** El torpedo devuelve `{(2, 4, 4): "impacto"}` y el misil de racimo hasta siete entradas. Las demás armas, igual.
- **Por qué:** Las armas que afectan varias celdas pueden dar un resultado distinto en cada una. Con un formato único, el turno trata a todas las armas igual y se pueden elegir desde un diccionario letra → función.

### El barrido láser se saltea las celdas de los submarinos

- **Decisión:** Las celdas de un submarino no se tocan y no aparecen en el resultado del láser.
- **Alternativa descartada:** Reportarlas como "agua". No las oculta, esas celdas no se pueden marcar como agua en el mapa (ahí hay una nave), así que igual quedan sin marcar y se nota el hueco. Para ocultarlas del todo habría que "mentir" también en el cubo, y eso lo complica.
- **Por qué esta:** Con cualquier opción un jugador atento puede deducir que ahí hay algo, así que elegimos la más simple y honesta: el juego nunca dice "agua" donde no la hay. El submarino es **inmune** al láser, no **invisible**.

### Munición: un diccionario por jugador

- **Decisión:** `crear_municion` copia el catálogo en un diccionario letra → cantidad, uno por jugador. El torpedo queda como `"ilimitada"`.
- **Por qué:** Cada jugador gasta su propia munición (el catálogo no se modifica nunca).
- **Orden de los chequeos en `usar_municion`:** cada chequeo evita que el siguiente falle.
  1. **¿Existe el arma?** Si no existe, el programa fallaría al buscarla en el diccionario.
  2. **¿Es ilimitada?** El torpedo tiene `"ilimitada"`, que es un texto (no se le puede restar 1).
  3. **¿Le quedan usos?** Recién acá sabemos que es un número, y se puede restar.

### Sonar

- **Decisión:** Marca como `DETECTADO` solo las celdas en `NAVE` del plano elegido. Los "contactos" son celdas, no naves.
- **Por qué solo `NAVE`:** Las celdas en `IMPACTO` o `HUNDIDO` el rival ya las conoce.

### Búsqueda optimizada: recorrido en damero (paridad)

- **Idea:** Se pinta cada celda según si `z + x + y` es par o impar. Dos celdas contiguas sobre un eje siempre tienen distinta paridad, y toda nave ocupa al menos dos celdas contiguas (**toda nave tiene una celda par**).
- **Estrategia:** Primera pasada solo por las celdas pares (la mitad del cubo) y segunda por las impares. En cada pasada, `y` avanza de a 2, así que las celdas de la otra paridad ni se miran.
- **Resultados:** ubicamos 300 flotas al azar en un cubo de 8 y, en cada una, buscamos la primera celda con `NAVE` con los dos métodos. Contamos cuántas celdas revisó cada uno hasta encontrarla (las "comparaciones"):

  | Método                        | Cómo recorre                                | Celdas revisadas (promedio) |
  | ----------------------------- | ------------------------------------------- | --------------------------- |
  | `busqueda_lineal` (entrega 1) | Todas, una por una, en orden z, x, y        | 32,5                        |
  | `busqueda_optimizada`         | Primero solo las pares, después las impares | 20,8                        |

  La optimizada revisa alrededor de un 36 % menos de celdas. Si no hay ninguna nave, las dos terminan revisando las 512 celdas del cubo (N³ = 8 × 8 × 8): en el peor caso son iguales.

- **¿Para qué la segunda pasada?** La garantía vale para naves enteras, pero la búsqueda busca un estado. Si a una fragata en `(1,1,1)-(1,1,2)` le pegan en `(1,1,2)` (par), la única celda que le queda en `NAVE` es `(1,1,1)` (impar). Lo mismo pasa con el sonar, o buscando estados de celdas sueltas como `IMPACTO`. La segunda pasada hace que la búsqueda sea siempre correcta.
- **Alternativa descartada:** Buscar en la flota, que sabe dónde está cada nave. Sería hacer trampa: la consigna pide localizar la nave en el cubo, como lo haría un jugador.

### Las búsquedas reciben un solo estado, no un conjunto

- **Propuesta considerada:** Recibir un conjunto de estados, por ejemplo `{NAVE, IMPACTO, DETECTADO, HUNDIDO}` ("cualquier parte de una nave"). Con eso la primera pasada alcanzaría siempre.
- **Por qué la dejamos para más adelante:**
  - Los tres métodos (lineal, optimizado y recursivo) tienen que recibir lo mismo para comparar sus métricas en forma justa, y la lineal ya recibe un estado desde la entrega 1.
  - Un pregunta útil para jugar ("¿dónde hay una celda sin dañar?") necesita la segunda pasada.
- **A revisar en la entrega 3:** Cuando sepamos quién usa la búsqueda (máquina, torpedo guiado). El cambio es pasar de `== estado` a `in estados` en los tres métodos.

### Dibujo de los planos

- **Decisión:** `_dibujar_plano` dibuja cualquier matriz poniendo el primer índice en las columnas. La capa z (`[x][y]`) muestra x en columnas e y en filas; el plano x (`[z][y]`), z en columnas e y en filas; el plano y (`[z][x]`), z en columnas y x en filas.
- **Por qué:** Una sola función de dibujo para los tres cortes, sin repetir código.

### Cada jugada del historial guarda todos los resultados del arma

- **Decisión:** La jugada guarda el punto y el diccionario `{punto: resultado}` completo que devolvió el arma, en vez de un solo resultado.
- **Por qué:** Desde que hay armas que afectan varias celdas (racimo, carga de profundidad, láser), un disparo puede dar agua en unas celdas e impacto en otras. Con un solo resultado se perdería información y las estadísticas contarían mal.
- **Alternativa descartada:** Guardar una jugada por cada celda afectada. Un racimo sumaría siete "turnos" al historial y el número de turno dejaría de corresponder a los turnos reales.

### Cómo se calcula el porcentaje de acierto

- **Decisión:** El acierto se mide por **celdas**, no por jugadas: celdas con `impacto` o `hundido` sobre todas las celdas disparadas (`agua`, `impacto`, `hundido` y `repetido`). Los disparos repetidos cuentan como fallo.
- **Por qué por celdas:** Un racimo que acierta en una celda de siete no es lo mismo que un torpedo que acierta en su única celda. Contando por jugada, los dos serían "un acierto".
- **Por qué el repetido es fallo:** Es un disparo desperdiciado, así que debe bajar el porcentaje.
- **Las naves hundidas** se cuentan con los `hundido`: Cada nave hundida produce exactamente un `hundido`, el del impacto que la terminó de hundir.

### Estructura del estado de la partida

```python
estado = {
    "jugadores": [jugador_1, jugador_2],
    "turno": 0,
    "historial": [],
    "ganador": None,
}
jugador = {"nombre": "Jugador 1", "es_maquina": False, "cubo": ..., "flota": ..., "municion": ...}
```

- **Decisión:** Cada jugador tiene su propio cubo con sus naves, su flota y su munición. Al disparar se usa el cubo y la flota del **rival**; para ver los disparos propios se dibuja el cubo del rival sin mostrar sus naves.
- **`"turno"` es un índice (0 o 1):** El jugador actual es `estado["jugadores"][turno]` y el rival `estado["jugadores"][1 - turno]`. Cambiar de turno es `turno = 1 - turno`, sin `if`.
- **`"es_maquina"`:** Los tres formatos de partida (uno contra uno, contra la máquina, máquina contra máquina) usan el mismo estado; lo único que cambia es quién elige la jugada.
- **Por qué diccionarios y listas:** Lo pide la consigna, y en la entrega 3 este mismo estado se guarda en JSON.
- **Alternativa descartada:** Claves fijas `"jugador_1"` y `"jugador_2"`. Para saber quién es el rival habría que preguntar con un `if`.

### Elección del arma con un diccionario y adaptadores

- **Decisión:** `ARMAS` en `armamento.py` asocia cada letra con una función: `{"T": _usar_torpedo, "R": _usar_racimo, ...}`. La función pública `disparar(cubo, flota, jugada)` busca el arma en el diccionario y la usa.
- **Por qué:** La consigna pide resolver la selección del arma con un diccionario que asocie nombre y función, sin cadenas de `if` / `elif`.
- **Problema:** Las armas reciben datos distintos (el láser necesita un eje; el sonar, un eje y un valor y ni siquiera la flota). Para guardarlas en el mismo diccionario, todas tienen que recibir lo mismo.
- **Solución:** Adaptadores chiquitos (`_usar_torpedo`, `_usar_laser`, etc.) con la misma firma `(cubo, flota, jugada)`. Cada uno saca de la jugada lo que necesita su arma. Las armas originales no cambiaron.
- **El sonar** devuelve una lista de puntos; su adaptador la convierte en `{punto: "detectado"}` para que tenga el mismo formato que las demás.
- **La onda expansiva y el torpedo guiado** no están en el diccionario hasta la entrega 3; si se eligen, `disparar` lanza `ErrorJugada`.

### En el turno, la munición se gasta en una copia

- **Problema:** Si se gasta la munición y después el disparo falla (arma no disponible u objetivo fuera del cubo), el jugador pierde un uso sin haber disparado. Si se dispara primero y después se gasta, se puede disparar un arma sin munición.
- **Decisión:** `ejecutar_turno` copia el diccionario de munición, gasta en la copia (si no queda, salta `ErrorMunicion` y no pasa nada), dispara, y **recién si el disparo salió bien** reemplaza la munición del jugador por la copia.
- **Por qué:** El turno es "todo o nada": o se gasta la munición, se dispara, se registra y pasa el turno, o no cambia nada. Así el jugador puede corregir la jugada y volver a intentar.
- **Alternativa descartada:** Gastar y, si el disparo falla, "devolver" la munición. Hay que acordarse de devolverla en cada caso de error y tener en cuenta el torpedo ilimitado.

### Cómo elige la máquina dónde disparar

- **Decisión:** La máquina dispara siempre un torpedo, a un punto **al azar entre las celdas a las que todavía no disparó**. Para ella, el agua sin explorar y las naves ocultas se ven igual, como para una persona.
- **Caso especial:** Cuando ya disparó a todas las celdas, elige al azar entre las que quedaron con impacto (`X`). Si no, nunca le daría el segundo impacto a las celdas del portaaviones y la partida podría no terminar.
- **Alternativa descartada:** Usar la flota del rival para saber dónde están las naves. Sería hacer trampa.
- **Dificultad:** `nueva_partida_vs_maquina` ya recibe la dificultad y la guarda en la máquina, como pide la consigna. Los dos niveles se implementan en la entrega 3; por ahora hay uno solo.

### Los menús se resuelven con diccionarios

- **Decisión:** Cada menú tiene un diccionario opción → función: `OPCIONES_MENU` (menú principal), `FORMAS_DE_UBICAR` (manual o automática), `ACCIONES_TURNO` (disparar o ver el cubo), `DATOS_POR_ARMA` (qué datos pide cada arma).
- **Por qué:** La consigna prohíbe resolver el despacho de opciones con cadenas de `if` / `elif`. En la entrega 1 usábamos `match`, que en la práctica es lo mismo, así que lo reemplazamos.
- **La opción "Salir"** no está en el diccionario: es la única que corta el ciclo del menú, así que se resuelve con un `if` antes de buscar en el diccionario.
