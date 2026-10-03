from modulos.tablero import AGUA, NAVE, escribir_celda, leer_celda, punto_valido

CATALOGO = [
    ("F", "Fragata", 2, 3),
    ("D", "Destructor", 3, 2),
    ("S", "Submarino", 3, 2),
    ("C", "Crucero", 4, 1),
    ("P", "Portaaviones", 5, 1),
    ("E", "Estacion orbital", 8, 1),
]


def ubicar_nave(
    cubo: list, flota: list, tipo: str, desde: tuple, hasta: tuple
) -> tuple[list, list] | None:
    """Marcar nave en el cubo, agregar nave a la flota y devolver una tupla(cubo, flota)."""
    modelo_nave = datos_nave(tipo)

    # La nave no se encuentra en el catalogo.
    if modelo_nave is None:
        return None

    # No quedan naves del tipo seleccionado para ubicar.
    if cantidad_ubicada(flota, tipo) >= modelo_nave[3]:
        return None

    # Queda al menos 1 nave del tipo seleccionado para ubicar.
    puntos = _obtener_puntos(tipo, desde, hasta)

    # El tramo no tiene la forma o el largo de la nave.
    if puntos is None:
        return None

    for punto in puntos:
        # La nave se sale del cubo.
        if not punto_valido(cubo, punto):
            return None

        # La nave no cumple la restriccion de ubicacion de su tipo.
        if not _cumple_restriccion(cubo, tipo, punto):
            return None

        # La celda ya esta ocupada por otra nave.
        if leer_celda(cubo, punto) != AGUA:
            return None

        # Tiene que quedar al menos una celda libre con las otras naves.
        if _hay_nave_cerca(cubo, punto):
            return None

    for punto in puntos:
        # Escribir sobre las celdas correspondientes la ubicacion de la nave.
        escribir_celda(cubo, punto, NAVE)

    # Agregar a la flota una tupla con (tipo de nave, puntos validos seleccionados)
    flota.append((tipo, puntos))

    return cubo, flota


def ubicacion_automatica():
    """Cubo, catálogo, semilla → flota ubicada."""
    # TODO:
    pass


def crear_flota() -> list:
    """Devuelve una lista vacia para guardar las naves ubicadas."""
    return []


def datos_nave(tipo: str) -> tuple[str, str, int, int] | None:
    """Obtiene el tipo de nave junto a sus datos."""
    for modelo_nave in CATALOGO:
        if modelo_nave[0] == tipo:
            return modelo_nave
    return None


def cantidad_ubicada(flota: list, tipo: str) -> int:
    """Obtiene la cantidad de naves ubicadas del tipo seleccionado."""
    cantidad = 0
    for nave in flota:
        if nave[0] == tipo:
            cantidad += 1
    return cantidad


def _obtener_puntos(
    tipo: str, desde: tuple, hasta: tuple
) -> list[tuple[int, int, int]] | None:
    """Obtiene los puntos de la nave seleccionada usando su tipo junto a las coordenadas desde x hasta y."""
    modelo_nave = datos_nave(tipo)

    # La nave no se encuentra dentro del catalogo.
    if modelo_nave is None:
        return None

    puntos = []

    if tipo == "E":
        # La estacion orbital ocupa un bloque de 2x2x2.
        if hasta != (desde[0] + 1, desde[1] + 1, desde[2] + 1):
            return None

        # Recorrer el bloque y guardar cada una de sus 8 celdas.
        for z in range(desde[0], hasta[0] + 1):
            for x in range(desde[1], hasta[1] + 1):
                for y in range(desde[2], hasta[2] + 1):
                    puntos.append((z, x, y))

    # El resto de las naves ocupa una linea recta sobre un solo eje.
    else:
        ejes_distintos = 0
        eje = -1

        # Buscar en que eje cambia la nave.
        for i in range(3):
            if desde[i] != hasta[i]:
                ejes_distintos += 1
                eje = i

        # La nave debe ir en linea recta sobre un solo eje.
        if ejes_distintos != 1:
            return None

        # Ordenar los extremos por si se escribieron al reves.
        primero = min(desde[eje], hasta[eje])
        ultimo = max(desde[eje], hasta[eje])

        # Armar los puntos de la nave sobre ese eje.
        for numero in range(primero, ultimo + 1):
            punto = [desde[0], desde[1], desde[2]]
            punto[eje] = numero
            puntos.append((punto[0], punto[1], punto[2]))

    # El tramo no tiene el largo de la nave.
    if len(puntos) != modelo_nave[2]:
        return None

    return puntos


def _hay_nave_cerca(cubo: list, punto: tuple) -> bool:
    """Indica si hay alguna nave en el punto o en las celdas que lo rodean."""
    z, x, y = punto

    # Recorrer el punto y las 26 celdas que lo rodean, incluidas las diagonales.
    for paso_z in (-1, 0, 1):
        for paso_x in (-1, 0, 1):
            for paso_y in (-1, 0, 1):
                vecino = (z + paso_z, x + paso_x, y + paso_y)

                if punto_valido(cubo, vecino) and leer_celda(cubo, vecino) == NAVE:
                    return True

    return False


def _cumple_restriccion(cubo: list, tipo: str, punto: tuple) -> bool:
    """Indica si el punto respeta la restriccion de ubicacion del tipo de nave."""
    z = punto[0]
    n = len(cubo)
    mitad = n // 2

    # Submarino: solo en la mitad inferior de z.
    if tipo == "S" and z > mitad:
        return False

    # Crucero: no puede ocupar z = 1 ni z = N.
    if tipo == "C" and (z == 1 or z == n):
        return False

    # Portaaviones: solo en la mitad superior de z.
    if tipo == "P" and z <= mitad:
        return False

    # Estacion orbital: no puede tocar ninguna cara exterior del cubo.
    if tipo == "E":
        for valor in punto:
            if valor == 1 or valor == n:
                return False

    return True
