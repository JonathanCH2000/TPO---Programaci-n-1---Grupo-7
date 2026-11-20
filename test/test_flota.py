import pytest

from modulos.errores import ErrorUbicacion
from modulos.flota import crear_flota, ubicar_nave
from modulos.tablero import AGUA, NAVE, crear_cubo, leer_celda


def test_crear_flota():
    """Comprueba que la flota nueva sea una lista vacia"""
    flota = crear_flota()

    assert flota == []


def test_ubicar_fragata():
    """Comprueba que una fragata se agregue a la flota y al cubo"""
    cubo = crear_cubo(8)
    flota = crear_flota()

    ubicar_nave(cubo, flota, "F", (1, 1, 1), (1, 1, 2))

    # La fragata ocupa dos celdas
    assert len(flota) == 1
    assert flota[0]["tipo"] == "F"
    assert flota[0]["puntos"] == {(1, 1, 1), (1, 1, 2)}
    assert leer_celda(cubo, (1, 1, 1)) == NAVE
    assert leer_celda(cubo, (1, 1, 2)) == NAVE


def test_nave_fuera_del_cubo():
    """Comprueba que se rechace una nave que sale del tablero"""
    cubo = crear_cubo(8)
    flota = crear_flota()

    with pytest.raises(ErrorUbicacion):
        ubicar_nave(cubo, flota, "F", (1, 1, 8), (1, 1, 9))

    # El intento fallido no debe agregar la nave ni ocupar celdas
    assert flota == []
    assert leer_celda(cubo, (1, 1, 8)) == AGUA


def test_largo_incorrecto():
    """Comprueba que se rechace una fragata de tres celdas"""
    cubo = crear_cubo(8)
    flota = crear_flota()

    # Una fragata debe ocupar dos celdas
    with pytest.raises(ErrorUbicacion):
        ubicar_nave(cubo, flota, "F", (1, 1, 1), (1, 1, 3))

    assert flota == []


def test_naves_superpuestas():
    """Comprueba que dos naves no puedan ocupar las mismas celdas"""
    cubo = crear_cubo(8)
    flota = crear_flota()

    ubicar_nave(cubo, flota, "F", (1, 1, 1), (1, 1, 2))

    with pytest.raises(ErrorUbicacion):
        ubicar_nave(cubo, flota, "F", (1, 1, 1), (1, 1, 2))
    assert len(flota) == 1


def test_naves_en_diagonal():
    """Comprueba que las naves tampoco puedan tocarse en diagonal"""
    cubo = crear_cubo(8)
    flota = crear_flota()

    ubicar_nave(cubo, flota, "F", (1, 1, 1), (1, 1, 2))

    # La segunda fragata queda pegada en diagonal a la primera
    with pytest.raises(ErrorUbicacion):
        ubicar_nave(cubo, flota, "F", (2, 2, 3), (2, 2, 4))
    assert len(flota) == 1
    assert leer_celda(cubo, (2, 2, 3)) == AGUA


def test_restriccion_submarino():
    """Comprueba que el submarino solo pueda ubicarse en la mitad inferior"""
    cubo = crear_cubo(8)
    flota = crear_flota()

    # En un cubo de 8, la mitad inferior comprende z de 1 a 4
    with pytest.raises(ErrorUbicacion):
        ubicar_nave(cubo, flota, "S", (5, 1, 1), (5, 1, 3))

    assert flota == []

    ubicar_nave(cubo, flota, "S", (4, 1, 1), (4, 1, 3))

    assert len(flota) == 1
    assert flota[0]["tipo"] == "S"


def test_restriccion_crucero():
    """Comprueba que el crucero no pueda ocupar la primera ni la ultima capa"""
    cubo = crear_cubo(8)
    flota = crear_flota()

    with pytest.raises(ErrorUbicacion):
        ubicar_nave(cubo, flota, "C", (1, 1, 1), (1, 1, 4))
    with pytest.raises(ErrorUbicacion):
        ubicar_nave(cubo, flota, "C", (8, 1, 1), (8, 1, 4))
    assert flota == []

    # Una capa intermedia permite ubicar el crucero
    ubicar_nave(cubo, flota, "C", (2, 1, 1), (2, 1, 4))
    assert len(flota) == 1
    assert flota[0]["tipo"] == "C"


def test_restriccion_portaaviones():
    """Comprueba que el portaaviones solo pueda ubicarse en la mitad superior"""
    cubo = crear_cubo(8)
    flota = crear_flota()

    with pytest.raises(ErrorUbicacion):
        ubicar_nave(cubo, flota, "P", (4, 1, 1), (4, 1, 5))
    assert flota == []

    # En un cubo de 8, la mitad superior comienza en z igual a 5
    ubicar_nave(cubo, flota, "P", (5, 1, 1), (5, 1, 5))
    assert len(flota) == 1
    assert flota[0]["tipo"] == "P"


def test_restriccion_estacion_orbital():
    """Comprueba que la estacion orbital quede dentro del cubo sin tocar sus caras"""
    cubo = crear_cubo(8)
    flota = crear_flota()

    # Probar bloques que tocan las caras exteriores de cada eje
    for eje in range(3):
        for borde in (1, 7):
            desde = [3, 3, 3]
            desde[eje] = borde
            hasta = [desde[0] + 1, desde[1] + 1, desde[2] + 1]

            with pytest.raises(ErrorUbicacion):
                ubicar_nave(cubo, flota, "E", tuple(desde), tuple(hasta))

    assert flota == []

    # Este bloque de 2 x 2 x 2 queda completamente en el interior
    ubicar_nave(cubo, flota, "E", (3, 3, 3), (4, 4, 4))

    assert len(flota) == 1
    assert flota[0]["tipo"] == "E"
    assert len(flota[0]["puntos"]) == 8

