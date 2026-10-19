# Bitácora del grupo 7

## Integrantes

| Nombre                        | Usuario de GitHub     |
| ----------------------------- | --------------------- |
| CHAMBI HUACA JONATHAN AGUSTIN | JonathanCH2000        |
| COSENTINI RODRIGO             | cosentinirodrigo-1994 |
| PEÑA CAMILA ISABEL            | camijk                |
| PUEGHER NICOLAS ALEJANDRO     | npuegher              |
| VILLAGRAN AGUSTIN URIEL       | -                     |

## Entrega 1

**Integrador:** PUEGHER NICOLAS ALEJANDRO

| Módulo                   | Responsable/s                    | Qué se hizo                                                                                                 |
| ------------------------ | -------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `tablero.py`             | CHAMBI HUACA, PUEGHER            | Creación del cubo, validación de puntos, lectura y escritura de celdas, dibujo de una capa de z             |
| `flota.py`               | CHAMBI HUACA, COSENTINI, PUEGHER | Catálogo de naves, ubicación manual y automática, reglas de ubicación (separación y restricciones por tipo) |
| `radar.py`               | PEÑA, PUEGHER                    | Búsqueda lineal con métricas                                                                                |
| `armamento.py`           | CHAMBI HUACA, PUEGHER            | Catálogo de armas y torpedo                                                                                 |
| `registro.py`            | PUEGHER                          | Historial de la partida en memoria                                                                          |
| `partida.py` / `main.py` | CHAMBI HUACA, PUEGHER            | Menú principal, submenú de ubicación, submenú para ver capas del cubo                                       |

**Notas:**

- Los nombres que empiezan con `_` son internos de cada módulo y no se importan desde afuera.

## Entrega 2

**Integrador:** PUEGHER NICOLAS ALEJANDRO

| Módulo                   | Responsable/s | Qué se hizo                                                                                                                          |
| ------------------------ | ------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `tablero.py`             | PUEGHER       | Vecinos de una celda, planos fijando x y fijando y, puntos de un plano, dibujo de cualquier corte                                    |
| `flota.py`               | PUEGHER       | Cada nave como diccionario con conjunto de puntos e impactos, registro de impactos, naves averiadas y hundidas, flota hundida        |
| `radar.py`               | PUEGHER       | Búsqueda optimizada por paridad (damero) con métricas, sonar por planos                                                              |
| `armamento.py`           | PUEGHER       | Misil de racimo, carga de profundidad, barrido láser, munición, elección del arma con un diccionario                                 |
| `registro.py`            | PUEGHER       | Jugadas con el resultado de cada celda, estadísticas por jugador, resumen al terminar                                                |
| `errores.py`             | PUEGHER       | Excepciones propias con clase base: `ErrorCubo`, `ErrorUbicacion`, `ErrorMunicion`, `ErrorJugada`                                    |
| `partida.py` / `main.py` | PUEGHER       | Estado de la partida, turnos y victoria, partidas uno contra uno y contra la máquina, menús con diccionarios, captura de excepciones |
| `docs/`                  | PUEGHER       | README actualizado y `decisiones.md` con las decisiones de diseño                                                                    |
