# Operación Cubo - Grupo 7

Trabajo práctico de Programación I los Lunes a la noche. Es una batalla naval en 3D:
El tablero es un cubo de 8 x 8 x 8 (modificable) y cada jugador (humano o computadora) ubica su flota adentro, manual o automaticamente.

## Requisitos

- Python 3.10 o mas nuevo
- Para jugar se utiliza solamente la biblioteca estandar de Python
- Para ejecutar las pruebas se necesita pytest

## Cómo ejecutarlo

1. Clonar o descargar el repositorio.
2. Abrir una terminal en la carpeta del proyecto.
3. Ejecutar:

```
python main.py
```

## Estructura del proyecto

```
main.py            Punto de entrada del juego
modulos/
    tablero.py     Creacion del cubo, validacion de puntos, celdas, capas, planos y recorridos
    flota.py       Catalogo de naves, ubicacion, restricciones, impactos y hundimiento
    radar.py       Busquedas lineal, optimizada y recursiva, sonar, recorridos y mapa de probabilidad
    armamento.py   Catalogo de armas, disparos, onda expansiva, torpedo guiado y municion
    registro.py    Historial, estadisticas, guardado y carga, exportacion y ranking
    errores.py     Excepciones propias del juego
    partida.py     Menus, preparacion de partidas, turnos y niveles de maquina
datos/
    partidas.json  Partidas guardadas
    ranking.json   Resultados del ranking
    resumenes.txt  Resumenes exportados
test/
    test_armamento_guiado.py    Pruebas del torpedo guiado
    test_flota.py              Pruebas de ubicacion y restricciones
    test_partida_maquina.py    Pruebas de los niveles de maquina
    test_radar.py              Pruebas de busquedas y mapa de probabilidad
    test_registro.py           Pruebas de historial y estadisticas
    test_tablero_recorridos.py Pruebas de recorridos
docs/
    bitacora.md    Responsables y tareas por entrega
    decisiones.md Decisiones de diseño del grupo
    ```

## Cómo se escriben los puntos

Cada celda del cubo se indica con tres números separados por comas, en el orden **z, x, y**:

- `3,5,4` es la celda con z = 3, x = 5, y = 4.
- Un tramo se escribe con los dos extremos separados por un guión: `3,5,4-3,5,5`.

## Menús

### Menú principal

```
===== OPERACION CUBO =====
1 - Partida uno contra uno
2 - Partida uno contra la maquina
3 - Partida maquina contra maquina
4 - Continuar una partida guardada
5 - Salir
6 - Ver ranking
```

Las opciones 3 y 4 permiten jugar maquina contra maquina y continuar una partida guardada. La opcion 6 muestra el ranking. La opcion 5 cierra el programa

### Ubicación de la flota

Al empezar una partida, cada jugador elige cómo ubicar su flota:

```
--- Flota de Jugador 1 ---
1 - Ubicacion manual
2 - Ubicacion automatica
```

**Ubicación manual:** el juego muestra las naves que faltan, se elige una por su letra y se escribe el tramo. Ejemplo:

```
Nave: F
Desde-hasta (z,x,y-z,x,y): 1,1,1-1,1,2
Nave ubicada.
```

Si la nave no entra en ese lugar, el juego avisa el motivo (por ejemplo, "La nave se sale del cubo.").

**Ubicación automática:** el juego ubica toda la flota al azar respetando las mismas reglas. La flota de la máquina se ubica siempre así.

### Ver el cubo

Después de ubicar la flota, y durante la partida, se puede ver el cubo cortado de tres formas:

```
1 - Capa de z
2 - Plano de x
3 - Plano de y
```

Se elige el corte, después el valor del eje fijo, y se puede ver otro corte o continuar.

```
========= CAPA z = 1 =========
     x1 x2 x3 x4 x5 x6 x7 x8
y1   N  ~  N  ~  N  ~  ~  ~
y2   N  ~  N  ~  N  ~  ~  ~
y3   ~  ~  ~  ~  ~  ~  ~  ~
```

Referencias:

| Símbolo | Significado         |
| ------- | ------------------- |
| `~`     | Agua sin explorar   |
| `N`     | Nave propia         |
| `o`     | Agua marcada        |
| `X`     | Impacto             |
| `#`     | Hundido             |
| `?`     | Detectado por sonar |

### Turnos

Con las dos flotas ubicadas, el juego pide confirmación para empezar y alterna los turnos. En cada turno:

```
--- Turno de Jugador 1 ---
1 - Disparar
2 - Ver el cubo
3 - Guardar y salir
```

**Disparar:** se elige el arma por su letra y después el objetivo. Cada arma pide lo que necesita:

```
Arma (T/R/C/S/L/O/G): T
Objetivo (z,x,y): 4,2,7
4,2,7: Impacto. Nave averiada: Destructor (1 de 3).
```

```
Arma (T/R/C/S/L/O/G): L
Objetivo (z,x,y): 3,1,4
Eje (x/y): x
```

```
Arma (T/R/C/S/L/O/G): S
Eje (z/x/y): z
Valor: 3
Sonar sobre el plano z = 3. 2 contactos detectados.
```

Si no queda munición del arma, o el objetivo está fuera del cubo, el juego avisa y el mismo jugador vuelve a elegir.

**Ver el cubo:** "Mis disparos" muestra el cubo del rival sin sus naves (solo agua marcada, impactos, hundidos y detectados); "Mi flota" muestra el cubo propio con las naves.

**Contra la maquina:** antes de empezar se elige su dificultad

- **Nivel 1:** dispara torpedos a puntos elegidos al azar entre las celdas pendientes de explorar
- **Nivel 2:** utiliza el torpedo guiado cuando tiene municion y hay una nave averiada. Si no, intenta completar celdas que todavia necesitan impactos y luego elige objetivos con el mapa de probabilidad

La maquina muestra el arma utilizada y el resultado de su turno

Gana el primero que hunde toda la flota rival. Al terminar se muestra un resumen con las estadísticas de cada jugador (jugadas, celdas disparadas, naves hundidas y porcentaje de acierto).

## Arsenal

| Arma                 | Letra | Munición  | Celdas que afecta                                                    |
| -------------------- | ----- | --------- | -------------------------------------------------------------------- |
| Torpedo              | T     | ilimitada | Solo la celda apuntada                                               |
| Misil de racimo      | R     | 3         | La celda apuntada y sus seis vecinas ortogonales                     |
| Carga de profundidad | C     | 2         | Toda la recta sobre el eje z que pasa por el punto apuntado          |
| Sonar                | S     | 4         | No daña: revela las naves de un plano entero (se elige eje y valor)  |
| Barrido láser        | L     | 2         | Una recta completa sobre el eje x o el eje y, a elección             |
| Onda expansiva | O | 1 | Se propaga por vecinos ortogonales con radio inicial 2, aplicando un disparo por celda |
| Torpedo guiado | G | 1 | Busca de forma recursiva una celda contigua de una nave averiada que todavia no este hundida |

## Flota

| Nave             | Letra | Celdas       | Cantidad | Restricción                          |
| ---------------- | ----- | ------------ | -------- | ------------------------------------ |
| Fragata          | F     | 2            | 3        | Sin restricción                      |
| Destructor       | D     | 3            | 2        | Sin restricción                      |
| Submarino        | S     | 3            | 2        | Solo en la mitad inferior de z       |
| Crucero          | C     | 4            | 1        | No puede ocupar z = 1 ni z = N      |
| Portaaviones     | P     | 5            | 1        | Solo en la mitad superior de z       |
| Estación orbital | E     | bloque 2x2x2 | 1        | No puede tocar ninguna cara del cubo |

Reglas para todas las naves:

- Van en línea recta sobre un solo eje (la estación orbital es un bloque de 2x2x2).
- No pueden salirse del cubo.
- Entre dos naves tiene que quedar al menos una celda libre, también en diagonal.

La mitad inferior comprende las capas de z = 1 a N // 2 y la superior, las restantes. Con N = 8, corresponden a las capas 1 a 4 y 5 a 8

Comportamientos propios:

- **Portaaviones:** cada celda necesita dos impactos para quedar destruida.
- **Submarino:** el barrido láser no lo alcanza.
- **Destructor:** al recibir un nuevo impacto revela una celda ocupada del rival de su propietario
- **Estacion orbital:** quien la hunde recibe un misil de racimo adicional. El premio se entrega una sola vez, al terminar de hundirla

## Tamano del tablero

Antes de iniciar una partida se pregunta si se desea elegir el tamano del cubo
Si no se modifica, se utiliza 8 x 8 x 8. El grupo establece tambien 8 como tamano minimo
El valor elegido se aplica a los tres modos de partida. Al continuar una partida guardada se conserva su tamano original

## Guardar y continuar una partida

Durante el turno de una persona, la opcion 3 permite guardar y salir al menu principal
Al guardar una partida nueva se pide un nombre de entre 1 y 30 caracteres. Se permiten letras sin acentos, numeros, guion y guion bajo
Si el nombre ya existe, se solicita confirmacion antes de reemplazarla
La opcion 4 del menu principal muestra las partidas guardadas y permite elegir una para continuar. Se recuperan el turno, los cubos, las flotas, la municion y el historial

Al volver a guardar una partida cargada se conserva su nombre
Si no se puede cargar, se muestra un mensaje y se vuelve al menu

## Partida maquina contra maquina

La opcion 3 del menu principal crea dos maquinas con sus propias flotas y municion
Las maquinas alternan sus turnos y el juego muestra los resultados de los disparos. Gana la primera que hunde toda la flota rival
Se puede elegir un nivel diferente para cada maquina

## Exportacion del resumen

Al terminar una partida se muestra el resumen y se pregunta si se desea exportarlo
Los resumenes se agregan a datos/resumenes.txt sin borrar los anteriores

## Ranking

La opcion 6 del menu principal permite consultar los resultados guardados en datos/ranking.json
El ranking se ordena por mayor porcentaje de acierto. Si hay empate, se prioriza la menor cantidad de jugadas

## Archivos de datos

La carpeta datos debe existir dentro del proyecto

- datos/partidas.json guarda las partidas que se pueden continuar
- datos/resumenes.txt conserva los resumenes exportados
- datos/ranking.json guarda los resultados del ranking

## Pruebas

Las pruebas se encuentran en la carpeta test y se ejecutan con pytest

Para instalar pytest:
```bash
python -m pip install pytest
```

Desde la carpeta que contiene main.py, ejecutar:

```bash
python -m pytest test -q
```

