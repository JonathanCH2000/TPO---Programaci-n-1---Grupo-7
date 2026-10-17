import random

from modulos.errores import ErrorUbicacion
from modulos.tablero import (
    AGUA,
    NAVE,
    escribir_celda,
    leer_celda,
    punto_valido,
    puntos_vecinos,
)

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
) -> tuple[list, list]:
    """Recibe cubo, flota, tipo de nave y los extremos del tramo.
    Marca la nave en el cubo, la agrega a la flota y devuelve (cubo, flota).
    Lanza ErrorUbicacion si la nave no se puede ubicar en esa ubicacion."""
    modelo_nave = datos_nave(tipo)

    if modelo_nave is None:
        raise ErrorUbicacion("La nave no existe en el catalogo.")

    if cantidad_ubicada(flota, tipo) >= modelo_nave[3]:
        raise ErrorUbicacion("Ya se ubicaron todas las naves de ese tipo.")

    # Queda al menos 1 nave del tipo seleccionado para ubicar.
    puntos = _obtener_puntos(tipo, desde, hasta)

    if puntos is None:
        raise ErrorUbicacion("El tramo no tiene la forma o el largo de la nave.")

    for punto in puntos:
        if not punto_valido(cubo, punto):
            raise ErrorUbicacion("La nave se sale del cubo.")

        if not _cumple_restriccion(cubo, tipo, punto):
            raise ErrorUbicacion("La nave no cumple la restriccion de ubicacion de su tipo.")

        if leer_celda(cubo, punto) != AGUA:
            raise ErrorUbicacion("La celda ya esta ocupada por otra nave.")

        if _hay_nave_cerca(cubo, punto):
            raise ErrorUbicacion("Tiene que quedar al menos una celda libre con las otras naves.")

    for punto in puntos:
        # Escribir sobre las celdas correspondientes la ubicacion de la nave.
        escribir_celda(cubo, punto, NAVE)

    # Agregar la nave a la flota: su tipo, el conjunto de puntos que ocupa y sus impactos (ninguno todavia).
    nave = {"tipo": tipo, "puntos": set(puntos), "impactos": {}}
    flota.append(nave)

    return cubo, flota


def ubicacion_automatica(
    cubo: list, catalogo: list, semilla: int | None
) -> list[dict] | None:
    """Ubica al azar todas las naves del catalogo respetando las reglas y devuelve la flota."""
    # Con la misma semilla siempre sale la misma flota. Con None sale una distinta cada vez.
    random.seed(semilla)

    # Empezar con la flota vacia.
    flota = crear_flota()
    lado = len(cubo)

    # Recorrer cada tipo de nave del catalogo.
    for modelo_nave in catalogo:
        tipo = modelo_nave[0]
        intentos = 0

        # Repetir hasta ubicar todas las naves de este tipo.
        while cantidad_ubicada(flota, tipo) < modelo_nave[3]:
            # Si despues de muchos intentos no entra, el cubo ya no tiene lugar.
            if intentos == 1000:
                return None

            intentos += 1

            # Elegir un punto al azar dentro del cubo.
            desde = (
                random.randint(1, lado),
                random.randint(1, lado),
                random.randint(1, lado),
            )

            # Calcular donde termina la nave.
            hasta = _extremo_al_azar(modelo_nave, desde)

            # Intentar ubicarla. Si no cumple las reglas, no se agrega y se prueba otro punto.
            try:
                ubicar_nave(cubo, flota, tipo, desde, hasta)
            except ErrorUbicacion:
                pass

    return flota


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
        if nave["tipo"] == tipo:
            cantidad += 1
    return cantidad


def registrar_impacto(flota: list, punto: tuple) -> dict | None:
    """Recibe flota y punto; suma un impacto a la nave que ocupa ese punto y la devuelve.
    Si ninguna nave ocupa ese punto, devuelve None."""
    for nave in flota:
        # Buscar la nave que ocupa ese punto.
        if punto in nave["puntos"]:
            # Sumar un impacto a esa celda. Si todavia no tenia ninguno, arranca en 0.
            nave["impactos"][punto] = nave["impactos"].get(punto, 0) + 1
            return nave

    # El punto no pertenece a ninguna nave: fue agua.
    return None


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
    # Verificamos si hay una nave en las coordenadas del parametro.
    if leer_celda(cubo, punto) == NAVE:
        return True

    # Revisar las 26 celdas que lo rodean, incluidas las diagonales (no 27 porque arriba chequeamos (0,0,0))
    for vecino in puntos_vecinos(cubo, punto, True):
        if leer_celda(cubo, vecino) == NAVE:
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


def _extremo_al_azar(modelo_nave: tuple, desde: tuple) -> tuple[int, int, int]:
    """Calcula el otro extremo de la nave a partir de desde, en un eje al azar."""
    # La estacion orbital es un bloque de 2x2x2: el extremo es la esquina opuesta.
    if modelo_nave[0] == "E":
        return (desde[0] + 1, desde[1] + 1, desde[2] + 1)

    # Elegir al azar en que eje va la nave (0 = z, 1 = x, 2 = y).
    eje = random.randint(0, 2)

    # Copiar el punto inicial.
    hasta = [desde[0], desde[1], desde[2]]

    # Avanzar en ese eje el largo de la nave menos 1 (la celda inicial ya cuenta).
    hasta[eje] = hasta[eje] + modelo_nave[2] - 1

    return (hasta[0], hasta[1], hasta[2])
