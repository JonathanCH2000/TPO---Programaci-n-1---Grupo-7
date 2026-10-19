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


def busqueda_optimizada(
    cubo: list, estado: int
) -> tuple[tuple[int, int, int] | None, dict]:
    """Localiza una celda del cubo que tiene un estado recorriendolo como un damero:
    Primero las celdas con (z + x + y) par y despues las impares.
    Devuelve el punto encontrado (o None si no hay ninguno) y las metricas de la busqueda."""
    # Toda nave ocupa al menos dos celdas juntas, siempre.
    # Si miramos su paridad (z + x + y): toda nave tiene una celda par.
    # Por eso, si hay una nave, se encuentra revisando solo la mitad del cubo (pares).
    comparaciones = 0

    # Guardar el momento en que empieza la busqueda para medir cuanto tarda.
    inicio = time.perf_counter()
    lado = len(cubo)

    # Primera pasada por las celdas pares (resto 0) y segunda por las impares (resto 1).
    # Incluso si no hay nada en celdas pares, en el peor caso buscamos las impares.
    for resto in (0, 1):
        for z in range(1, lado + 1):
            for x in range(1, lado + 1):
                # Primer y que hace que (z + x + y) tenga la paridad de esta pasada.
                primer_y = 1 if (z + x + 1) % 2 == resto else 2

                # Avanzar de a 2 para pasar solo por celdas de esa paridad.
                for y in range(primer_y, lado + 1, 2):
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
