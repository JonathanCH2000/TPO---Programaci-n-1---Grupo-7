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
    tablero.py     El cubo: creación, validación de puntos, lectura y escritura de celdas, dibujo de capas
    flota.py       Catálogo de naves, ubicación manual y automática, reglas de ubicación
    radar.py       Búsqueda lineal con métricas
    armamento.py   Catálogo de armas y torpedo
    registro.py    Historial de la partida en memoria
    partida.py     Menús y submenús
docs/
    bitacora.md    Quién trabajó en qué, por entrega
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
4 - Continuar una partida
5 - Salir
```

El menú vuelve a aparecer después de cada opción y solo se cierra con la opción 5. En esta entrega funciona la opción 1; las opciones 2, 3 y 4 todavía no están implementadas.

### Ubicación de la flota

Al empezar una partida, cada jugador elige cómo ubicar su flota:

```
--- Jugador 1 ---
1 - Ubicacion manual
2 - Ubicacion automatica
```

**Ubicación manual:** el juego muestra las naves que faltan, se elige una por su letra y se escribe el tramo. Ejemplo:

```
Nave: F
Desde-hasta (z,x,y-z,x,y): 1,1,1-1,1,2
Nave ubicada.
```

Si la nave no entra en ese lugar, el juego avisa y vuelve a preguntar.

**Ubicación automática:** el juego ubica toda la flota al azar respetando las mismas reglas.

### Ver el cubo

Después de ubicar la flota se puede ver el cubo capa por capa (cada capa es un valor de z). Se elige la capa y después se puede ver otra o continuar.

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

