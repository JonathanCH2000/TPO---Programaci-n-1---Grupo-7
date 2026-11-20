# Operación Cubo - Grupo 7

Trabajo práctico de Programación I los lunes a la noche. Es una batalla naval en 3D: el tablero es un cubo de 8 x 8 x 8 (modificable) y cada jugador (persona o máquina) ubica su flota adentro, en forma manual o automática.

## Requisitos

- Python 3.10 o más nuevo.
- Para jugar no hace falta instalar nada: el juego usa solo la biblioteca estándar de Python.
- Para correr las pruebas hace falta pytest, que figura en `requirements.txt`.

## Cómo ejecutarlo

1. Clonar o descargar el repositorio.
2. Abrir una terminal en la carpeta del proyecto.
3. Ejecutar:

```
python main.py
```

El juego se puede cerrar en cualquier momento con `Ctrl+C`.

## Estructura del proyecto

```
main.py            Punto de entrada del juego
requirements.txt   Lo que hay que instalar para correr las pruebas (pytest)
modulos/
    tablero.py     El cubo: creación, validación de puntos, celdas, vecinos, capas y planos, recorridos, dibujo
    flota.py       Catálogo de naves, ubicación manual y automática, reglas de ubicación, impactos y hundimiento
    radar.py       Búsquedas lineal, optimizada y recursiva con métricas, sonar, mapa de probabilidad, recorridos recursivos
    armamento.py   Catálogo de armas, disparos de cada arma y munición
    registro.py    Historial, estadísticas, resumen, guardado y carga en JSON, exportación y ranking
    errores.py     Excepciones propias del juego (todas heredan de ErrorCubo)
    partida.py     Menús y submenús, ciclo de turnos, los tres formatos de partida, niveles de la máquina
datos/
    partidas.json  Partidas guardadas
    ranking.json   Resultados del ranking
    resumenes.txt  Resúmenes exportados
test/              Pruebas con pytest
docs/
    bitacora.md    Quién trabajó en qué, por entrega
    decisiones.md  Decisiones de diseño y por qué las tomamos
```

## Cómo se escriben los puntos

Cada celda del cubo se indica con tres números separados por comas, en el orden **z, x, y**:

- `3,5,4` es la celda con z = 3, x = 5, y = 4.
- Un tramo se escribe con los dos extremos separados por un guion: `3,5,4-3,5,5`.

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

El menú vuelve a aparecer después de cada opción y solo se cierra con la opción 5.

### Tamaño del cubo

Antes de cada partida nueva, el juego pregunta si se quiere elegir el tamaño del cubo. Se acepta un lado de 8 a 12; si no se elige, se usa 8. Una partida guardada conserva su tamaño.

### Nivel de la máquina

En las partidas contra la máquina se elige su nivel (en la partida máquina contra máquina, uno para cada una):

- **Nivel 1 (fácil):** dispara torpedos al azar a celdas a las que todavía no disparó.
- **Nivel 2 (difícil):** si hay una nave averiada, usa el torpedo guiado mientras le quede. Si no, termina las celdas que necesitan otro impacto y después dispara a las celdas más probables según el mapa de probabilidad.

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
4 - Recorrer el cubo
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

El torpedo guiado no pide objetivo: lo busca solo a partir de un impacto previo.

Si no queda munición del arma, o el objetivo está fuera del cubo, el juego avisa y el mismo jugador vuelve a elegir.

**Ver el cubo:** "Mis disparos" muestra el cubo del rival sin sus naves (solo agua marcada, impactos, hundidos y detectados); "Mi flota" muestra el cubo propio con las naves.

**Guardar y salir:** guarda la partida y vuelve al menú principal. La primera vez se pide un nombre de 1 a 30 caracteres (letras sin tildes, números, guion y guion bajo). Si ya existe una partida con ese nombre, se pide confirmación antes de reemplazarla. Una partida que se continuó se vuelve a guardar con su mismo nombre.

**Recorrer el cubo:** muestra en qué orden visita las celdas cada recorrido (la cantidad de celdas y las primeras 32):

```
1 - Por capas de z
2 - En espiral
3 - Por octantes (recursivo)
4 - Desde un impacto (recursivo)
```

- **Por capas de z:** capa por capa y, dentro de cada capa, fila por fila.
- **En espiral:** cada capa de z desde el borde hacia el centro.
- **Por octantes:** parte el cubo en ocho partes y cada parte otra vez en ocho, hasta llegar a una celda.
- **Desde un impacto:** se elige una celda con impacto y se propaga a las vecinas con impacto o hundidas. Muestra las celdas que ya se le pegaron a esa nave.

**Contra la máquina:** la máquina juega sola y muestra dónde disparó y qué pasó.

Gana el primero que hunde toda la flota rival. Al terminar se muestra un resumen con las estadísticas de cada jugador (jugadas, celdas disparadas, naves hundidas y porcentaje de acierto), el resultado se agrega al ranking y se puede exportar el resumen.

### Continuar una partida guardada

La opción 4 del menú principal lista las partidas guardadas y permite elegir una. La partida sigue en el punto exacto en que se dejó: mismo turno, cubos, flotas, munición e historial. Si el archivo está dañado, el juego avisa y vuelve al menú.

### Ranking

La opción 6 del menú principal muestra los resultados de las partidas terminadas, ordenados por porcentaje de acierto del ganador. Si hay empate, va primero el que ganó con menos jugadas.

## Arsenal

| Arma                 | Letra | Munición  | Celdas que afecta                                                       |
| -------------------- | ----- | --------- | ----------------------------------------------------------------------- |
| Torpedo              | T     | ilimitada | Solo la celda apuntada                                                  |
| Misil de racimo      | R     | 3         | La celda apuntada y sus seis vecinas ortogonales                        |
| Carga de profundidad | C     | 2         | Toda la recta sobre el eje z que pasa por el punto apuntado             |
| Sonar                | S     | 4         | No daña: revela las naves de un plano entero (se elige eje y valor)     |
| Barrido láser        | L     | 2         | Una recta completa sobre el eje x o el eje y, a elección                |
| Onda expansiva       | O     | 1         | Se propaga desde el punto a las vecinas ortogonales, con radio 2        |
| Torpedo guiado       | G     | 1         | Busca una celda a flote de una nave ya averiada (no hace falta apuntar) |

## Flota

| Nave             | Letra | Celdas       | Cantidad | Restricción                          |
| ---------------- | ----- | ------------ | -------- | ------------------------------------ |
| Fragata          | F     | 2            | 3        | Sin restricción                      |
| Destructor       | D     | 3            | 2        | Sin restricción                      |
| Submarino        | S     | 3            | 2        | Solo en la mitad inferior de z       |
| Crucero          | C     | 4            | 1        | No puede ocupar z = 1 ni z = N       |
| Portaaviones     | P     | 5            | 1        | Solo en la mitad superior de z       |
| Estación orbital | E     | bloque 2x2x2 | 1        | No puede tocar ninguna cara del cubo |

Reglas para todas las naves:

- Van en línea recta sobre un solo eje (la estación orbital es un bloque de 2x2x2).
- No pueden salirse del cubo.
- Entre dos naves tiene que quedar al menos una celda libre, también en diagonal.

Tomamos como mitad inferior las capas z = 1 a N // 2 y como mitad superior el resto. Con N = 8: inferior z = 1 a 4, superior z = 5 a 8.

Comportamientos propios:

- **Portaaviones:** cada celda necesita dos impactos para quedar destruida.
- **Submarino:** el barrido láser no lo alcanza.
- **Destructor:** cada vez que recibe un impacto, revela a su dueño una celda ocupada de la flota del atacante.
- **Estación orbital:** quien la hunde recibe un misil de racimo extra.

## Archivos de datos

El juego guarda todo en la carpeta `datos/`, que tiene que existir dentro del proyecto:

- `datos/partidas.json`: partidas guardadas para continuar.
- `datos/ranking.json`: resultados del ranking.
- `datos/resumenes.txt`: resúmenes exportados (cada uno se agrega al final, sin borrar los anteriores).

## Pruebas

Las pruebas están en la carpeta `test/` y se corren con pytest. Si el sistema no deja instalar paquetes con pip, primero hay que crear un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

Después, desde la carpeta del proyecto:

```bash
python -m pip install -r requirements.txt
python -m pytest test -q
```
