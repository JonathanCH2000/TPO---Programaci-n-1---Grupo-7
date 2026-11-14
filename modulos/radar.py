import time

from modulos.tablero import (
    AGUA,
    AGUA_MARCADA,
    DETECTADO,
    HUNDIDO,
    IMPACTO,
    NAVE,
    escribir_celda,
    leer_celda,
    punto_valido,
    puntos_plano,
    puntos_vecinos,
    recorrido_capas,
)

# Celdas a las que todavia no se disparo. Una nave oculta se ve igual que el agua sin explorar.
SIN_DISPARAR = (AGUA, NAVE, DETECTADO)

# Celdas por las que no puede pasar ninguna nave que siga a flote.
NO_PASABLES = (AGUA_MARCADA, HUNDIDO)

# Cuanto suma al puntaje cada celda con pista (impacto o detectada) de una forma posible.
PESO_PISTA = 10


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


def busqueda_recursiva(
    cubo: list, estado: int
) -> tuple[tuple[int, int, int] | None, dict]:
    """Localiza la primera celda del cubo que tiene un estado dividiendo el cubo en mitades
    (divide y venceras): busca en la primera mitad y, si no esta, en la segunda.
    Devuelve el punto encontrado (o None si no hay ninguno) y las metricas de la busqueda;
    profundidad_max es la cantidad maxima de llamadas recursivas anidadas."""
    lado = len(cubo)

    # Guardar el momento en que empieza la busqueda para medir cuanto tarda.
    inicio = time.perf_counter()

    # Las llamadas recursivas comparten este diccionario para ir sumando sus datos.
    seguimiento = {"comparaciones": 0, "profundidad_max": 0}
    punto = None

    # Un cubo sin celdas no tiene nada que buscar.
    if lado > 0:
        punto = _buscar_en_region(
            cubo, estado, (1, lado), (1, lado), (1, lado), 1, seguimiento
        )

    metricas = _armar_metricas(
        seguimiento["comparaciones"], inicio, seguimiento["profundidad_max"]
    )

    return punto, metricas


def _buscar_en_region(
    cubo: list,
    estado: int,
    rango_z: tuple,
    rango_x: tuple,
    rango_y: tuple,
    nivel: int,
    seguimiento: dict,
) -> tuple[int, int, int] | None:
    """Busca el estado dentro de la region que forman los tres rangos (desde, hasta).
    Devuelve el primer punto encontrado o None. Suma sus datos en seguimiento."""
    z_desde, z_hasta = rango_z
    x_desde, x_hasta = rango_x
    y_desde, y_hasta = rango_y

    # Guardar la profundidad mas grande a la que se llego.
    if nivel > seguimiento["profundidad_max"]:
        seguimiento["profundidad_max"] = nivel

    # Caso base: la region es una sola celda, se compara y listo.
    if z_desde == z_hasta and x_desde == x_hasta and y_desde == y_hasta:
        seguimiento["comparaciones"] += 1

        if leer_celda(cubo, (z_desde, x_desde, y_desde)) == estado:
            return (z_desde, x_desde, y_desde)

        return None

    # Caso recursivo: partir al medio el primer eje que tenga mas de una celda (z, x, y),
    # asi se recorre en el mismo orden que la busqueda lineal.
    if z_desde < z_hasta:
        medio = (z_desde + z_hasta) // 2
        primera = ((z_desde, medio), rango_x, rango_y)
        segunda = ((medio + 1, z_hasta), rango_x, rango_y)
    elif x_desde < x_hasta:
        medio = (x_desde + x_hasta) // 2
        primera = (rango_z, (x_desde, medio), rango_y)
        segunda = (rango_z, (medio + 1, x_hasta), rango_y)
    else:
        medio = (y_desde + y_hasta) // 2
        primera = (rango_z, rango_x, (y_desde, medio))
        segunda = (rango_z, rango_x, (medio + 1, y_hasta))

    # Buscar en la primera mitad; si esta ahi, no hace falta mirar la segunda.
    encontrado = _buscar_en_region(
        cubo, estado, primera[0], primera[1], primera[2], nivel + 1, seguimiento
    )

    if encontrado is not None:
        return encontrado

    return _buscar_en_region(
        cubo, estado, segunda[0], segunda[1], segunda[2], nivel + 1, seguimiento
    )


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


def mapa_probabilidad(
    cubo: list, largos: list[int]
) -> dict[tuple[int, int, int], int]:
    """Recibe el cubo del rival y los largos de las naves que siguen a flote; devuelve un
    diccionario punto -> puntaje con cada celda a la que todavia se puede disparar.
    Se prueba cada forma posible de ubicar cada nave en linea recta. Cada forma suma 1 a sus
    celdas, mas PESO_PISTA por cada celda suya que ya tiene un impacto o fue detectada.
    Cuanto mas alto el puntaje, mas probable es que haya una nave ahi."""
    mapa = {}
    puntos = recorrido_capas(cubo)

    # Todas las celdas a las que se puede disparar arrancan en 0.
    for punto in puntos:
        if leer_celda(cubo, punto) in SIN_DISPARAR:
            mapa[punto] = 0

    # Agrupar los largos iguales: se calcula una vez por largo y se multiplica por la cantidad.
    cantidades = {}
    for largo in largos:
        cantidades[largo] = cantidades.get(largo, 0) + 1

    for largo, cantidad in cantidades.items():
        # Probar cada punto de partida sobre cada eje (0 = z, 1 = x, 2 = y).
        for inicio in puntos:
            for eje in range(3):
                forma = _forma_en_linea(cubo, inicio, eje, largo)

                # La forma se sale del cubo o pasa por una celda donde no puede haber nave.
                if forma is None:
                    continue

                # Una forma que pasa por celdas con pista vale mas.
                peso = 1
                for punto in forma:
                    if leer_celda(cubo, punto) in (IMPACTO, DETECTADO):
                        peso += PESO_PISTA

                # Sumar el peso a las celdas de la forma que todavia se pueden disparar.
                for punto in forma:
                    if punto in mapa:
                        mapa[punto] += peso * cantidad

    return mapa


def _forma_en_linea(
    cubo: list, inicio: tuple, eje: int, largo: int
) -> list[tuple[int, int, int]] | None:
    """Recibe el cubo, el punto donde empieza una nave, el eje (0 = z, 1 = x, 2 = y) y su largo.
    Devuelve los puntos que ocuparia, o None si no entra o pasa por una celda donde no puede haber nave."""
    forma = []

    for paso in range(largo):
        punto = list(inicio)
        punto[eje] += paso
        punto = tuple(punto)

        if not punto_valido(cubo, punto) or leer_celda(cubo, punto) in NO_PASABLES:
            return None

        forma.append(punto)

    return forma


def puntos_mas_probables(mapa: dict) -> list[tuple[int, int, int]]:
    """Recibe un mapa de probabilidad; devuelve la lista de puntos con el puntaje mas alto
    (varios si hay empate, vacia si el mapa esta vacio)."""
    mejores = []
    mejor = -1

    for punto, puntaje in mapa.items():
        if puntaje > mejor:
            mejor = puntaje
            mejores = [punto]
        elif puntaje == mejor:
            mejores.append(punto)

    return mejores


def recorrido_octantes(cubo: list) -> list[tuple[int, int, int]]:
    """Recibe el cubo; devuelve todos sus puntos recorridos por octantes: se parte el cubo
    en ocho partes y cada parte se vuelve a partir de forma recursiva hasta llegar a una celda."""
    puntos = []
    lado = len(cubo)

    if lado > 0:
        _recorrer_octantes((1, lado), (1, lado), (1, lado), puntos)

    return puntos


def _recorrer_octantes(
    rango_z: tuple, rango_x: tuple, rango_y: tuple, puntos: list
) -> None:
    """Agrega a puntos las celdas de la region que forman los tres rangos (desde, hasta)."""
    # Caso base: la region es una sola celda.
    if rango_z[0] == rango_z[1] and rango_x[0] == rango_x[1] and rango_y[0] == rango_y[1]:
        puntos.append((rango_z[0], rango_x[0], rango_y[0]))
        return

    # Caso recursivo: partir cada eje en dos mitades y recorrer cada octante.
    for mitad_z in _partir(rango_z):
        for mitad_x in _partir(rango_x):
            for mitad_y in _partir(rango_y):
                _recorrer_octantes(mitad_z, mitad_x, mitad_y, puntos)


def _partir(rango: tuple) -> list[tuple[int, int]]:
    """Recibe un rango (desde, hasta); devuelve sus dos mitades, o el mismo rango si tiene una sola celda."""
    desde, hasta = rango

    if desde == hasta:
        return [rango]

    medio = (desde + hasta) // 2

    return [(desde, medio), (medio + 1, hasta)]


def recorrido_propagacion(
    cubo: list, punto: tuple, estados: tuple = (IMPACTO,)
) -> list[tuple[int, int, int]] | None:
    """Recibe el cubo, un punto de partida y los estados por los que se puede propagar
    (por defecto, impactos). Devuelve los puntos alcanzados pasando de una celda a sus vecinos
    ortogonales de forma recursiva, o None si el punto esta fuera del cubo.
    Si el punto de partida no tiene uno de esos estados, la lista queda vacia."""
    if not punto_valido(cubo, punto):
        return None

    alcanzados = []
    _propagar(cubo, punto, estados, alcanzados)

    return alcanzados


def _propagar(cubo: list, punto: tuple, estados: tuple, alcanzados: list) -> None:
    """Suma el punto a alcanzados y sigue por sus vecinos, siempre que tenga uno de los estados."""
    # Caso base: la celda ya se visito o no tiene un estado por el que se pueda pasar.
    if punto in alcanzados or leer_celda(cubo, punto) not in estados:
        return

    alcanzados.append(punto)

    # Caso recursivo: propagar a cada vecino ortogonal.
    for vecino in puntos_vecinos(cubo, punto):
        _propagar(cubo, vecino, estados, alcanzados)


def _armar_metricas(
    comparaciones: int, inicio: float, profundidad_max: int = 0
) -> dict[str, int | float]:
    """Arma el diccionario de metricas de una corrida de busqueda.
    La profundidad es 0 en las busquedas que no son recursivas."""
    # Calcular cuanto tardo la busqueda, pasado a milisegundos.
    tiempo_ms = (time.perf_counter() - inicio) * 1000

    return {
        "comparaciones": comparaciones,
        "tiempo_ms": round(tiempo_ms, 4),
        "profundidad_max": profundidad_max,
    }
