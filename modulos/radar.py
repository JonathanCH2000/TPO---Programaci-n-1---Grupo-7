import time

from modulos.tablero import (
    DETECTADO,
    NAVE,
    escribir_celda,
    leer_celda,
    puntos_plano,
)


def busqueda_lineal(
    cubo: list, estado: int
) -> tuple[tuple[int, int, int] | None, dict]:
    """Localiza la primera celda del cubo que tiene un estado recorriendolo con ciclos for (z, x, y).
    Devuelve el punto encontrado (o None si no hay ninguno) y las metricas de la busqueda."""
    comparaciones = 0

    # Guardar el momento en que empieza la busqueda para medir cuanto tarda.
    inicio = time.perf_counter()
    lado = len(cubo)

    # Recorrer todas las celdas del cubo en orden: primero z, despues x y despues y.
    for z in range(1, lado + 1):
        for x in range(1, lado + 1):
            for y in range(1, lado + 1):
                # Contar cada celda que se revisa.
                comparaciones += 1

                # Si la celda tiene el estado buscado, devolver su punto y las metricas.
                if leer_celda(cubo, (z, x, y)) == estado:
                    return (z, x, y), _armar_metricas(comparaciones, inicio)

    # Se recorrio todo el cubo y ninguna celda tiene ese estado.
    return None, _armar_metricas(comparaciones, inicio)


def sonar(cubo: list, eje: str, valor: int) -> list[tuple[int, int, int]] | None:
    """Recibe el cubo del rival, un eje ("z", "x" o "y") y su valor; marca como detectadas
    las celdas con nave de ese plano. Devuelve los puntos detectados."""
    puntos = puntos_plano(cubo, eje, valor)

    # El eje no existe o el valor esta fuera del cubo.
    if puntos is None:
        return None

    detectados = []

    # Revisar cada celda del plano: las que tienen una nave oculta pasan a detectadas.
    for punto in puntos:
        if leer_celda(cubo, punto) == NAVE:
            escribir_celda(cubo, punto, DETECTADO)
            detectados.append(punto)

    return detectados


def _armar_metricas(comparaciones: int, inicio: float) -> dict[str, int | float]:
    """Arma el diccionario de metricas de una corrida de busqueda."""
    # Calcular cuanto tardo la busqueda, pasado a milisegundos.
    tiempo_ms = (time.perf_counter() - inicio) * 1000

    # La busqueda lineal no es recursiva, por eso la profundidad maxima es 0.
    return {
        "comparaciones": comparaciones,
        "tiempo_ms": round(tiempo_ms, 4),
        "profundidad_max": 0,
    }
