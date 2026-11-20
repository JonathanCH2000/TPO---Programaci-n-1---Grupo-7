import pytest

from modulos.errores import ErrorCubo
from modulos.registro import (
    crear_historial,
    estadisticas,
    guardar_partida,
    registrar_jugada,
    ultima_jugada,
)


def test_crear_historial():
    """Comprueba que el historial nuevo sea una lista vacia"""
    historial = crear_historial()

    assert historial == []


def test_registrar_jugada():
    """Comprueba que se agregue una jugada con todos sus datos"""
    historial = crear_historial()
    punto = (1, 2, 3)
    resultados = {punto: "impacto"}

    registrar_jugada(historial, "Jugador 1", "T", punto, resultados)

    # Revisa los datos de la jugada guardada
    assert len(historial) == 1
    assert historial[0]["turno"] == 1
    assert historial[0]["jugador"] == "Jugador 1"
    assert historial[0]["arma"] == "T"
    assert historial[0]["punto"] == punto
    assert historial[0]["resultados"] == resultados
    assert historial[0]["eje"] is None
    assert historial[0]["valor"] is None


def test_ultima_jugada_sin_historial():
    """Comprueba que no haya ultima jugada si el historial esta vacio"""
    historial = crear_historial()

    assert ultima_jugada(historial) is None


def test_ultima_jugada():
    """Comprueba que se devuelva la ultima jugada registrada"""
    historial = crear_historial()

    registrar_jugada(historial, "Jugador 1", "T", (1, 1, 1), {(1, 1, 1): "agua"})
    registrar_jugada(historial, "Jugador 2", "T", (2, 2, 2), {(2, 2, 2): "impacto"})

    jugada = ultima_jugada(historial)

    assert jugada["jugador"] == "Jugador 2"
    assert jugada["turno"] == 2


def test_estadisticas():
    """Comprueba las cantidades y el acierto del jugador elegido"""
    historial = crear_historial()

    registrar_jugada(historial, "Jugador 1", "T", (1, 1, 1), {(1, 1, 1): "agua"})
    registrar_jugada(historial, "Jugador 1", "T", (2, 2, 2), {(2, 2, 2): "impacto"})
    registrar_jugada(historial, "Jugador 2", "T", (3, 3, 3), {(3, 3, 3): "agua"})

    datos = estadisticas(historial, "Jugador 1")

    # Revisa las estadisticas del Jugador 1
    assert datos["jugadas"] == 2
    assert datos["agua"] == 1
    assert datos["impacto"] == 1
    assert datos["acierto"] == 50.0


def test_nombre_invalido():
    """Comprueba que un nombre con espacios lance ErrorCubo."""
    # El nombre se rechaza antes de escribir el archivo
    with pytest.raises(ErrorCubo):
        guardar_partida({}, "nombre con espacios")

