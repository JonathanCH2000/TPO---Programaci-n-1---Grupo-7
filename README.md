# Operación Cubo - Grupo 7

Trabajo práctico de Programación I los Lunes a la noche. Es una batalla naval en 3D:
El tablero es un cubo de 8 x 8 x 8 (modificable) y cada jugador (humano o computadora) ubica su flota adentro, manual o automaticamente.

## Requisitos

- Python 3.10 o más nuevo.
- No hace falta instalar nada más, el juego usa solo la biblioteca estándar de Python.

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
    tablero.py     El cubo: creación, validación de puntos, celdas, vecinos, capas y planos, dibujo
    flota.py       Catálogo de naves, ubicación manual y automática, reglas de ubicación, impactos y hundimiento
    radar.py       Búsqueda lineal y optimizada con métricas, sonar por planos
    armamento.py   Catálogo de armas, torpedo, misil de racimo, carga de profundidad, barrido láser, munición
    registro.py    Historial de la partida, estadísticas y resumen final
    errores.py     Excepciones propias del juego (todas heredan de ErrorCubo)
    partida.py     Menús y submenús, ciclo de turnos, partidas uno contra uno y contra la máquina
docs/
    bitacora.md    Quién trabajó en qué, por entrega
    decisiones.md  Decisiones de diseño y por qué las tomamos
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
```

El menú vuelve a aparecer después de cada opción y solo se cierra con la opción 5. Funcionan las opciones 1 y 2; las opciones 3 y 4 se implementan en la entrega 3.

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

**Contra la máquina:** la máquina juega sola, dispara torpedos y muestra dónde disparó y qué pasó.

Gana el primero que hunde toda la flota rival. Al terminar se muestra un resumen con las estadísticas de cada jugador (jugadas, celdas disparadas, naves hundidas y porcentaje de acierto).

## Arsenal

| Arma                 | Letra | Munición  | Celdas que afecta                                                    |
| -------------------- | ----- | --------- | -------------------------------------------------------------------- |
| Torpedo              | T     | ilimitada | Solo la celda apuntada                                               |
| Misil de racimo      | R     | 3         | La celda apuntada y sus seis vecinas ortogonales                     |
| Carga de profundidad | C     | 2         | Toda la recta sobre el eje z que pasa por el punto apuntado          |
| Sonar                | S     | 4         | No daña: revela las naves de un plano entero (se elige eje y valor)  |
| Barrido láser        | L     | 2         | Una recta completa sobre el eje x o el eje y, a elección             |
| Onda expansiva       | O     | 1         | Entrega 3                                                            |
| Torpedo guiado       | G     | 1         | Entrega 3                                                            |

## Flota

| Nave             | Letra | Celdas       | Cantidad | Restricción                          |
| ---------------- | ----- | ------------ | -------- | ------------------------------------ |
| Fragata          | F     | 2            | 3        | Sin restricción                      |
| Destructor       | D     | 3            | 2        | Sin restricción                      |
| Submarino        | S     | 3            | 2        | Solo en la mitad inferior de z       |
| Crucero          | C     | 4            | 1        | No puede ocupar z = 1 ni z = 8       |
| Portaaviones     | P     | 5            | 1        | Solo en la mitad superior de z       |
| Estación orbital | E     | bloque 2x2x2 | 1        | No puede tocar ninguna cara del cubo |

Reglas para todas las naves:

- Van en línea recta sobre un solo eje (la estación orbital es un bloque de 2x2x2).
- No pueden salirse del cubo.
- Entre dos naves tiene que quedar al menos una celda libre, también en diagonal.

Tomamos como mitad inferior las capas z = 1 a 4 y como mitad superior las capas z = 5 a 8.

Comportamientos propios:

- **Portaaviones:** cada celda necesita dos impactos para quedar destruida.
- **Submarino:** el barrido láser no lo alcanza.

