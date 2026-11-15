import pytest

from modulos.armamento import ARMAS, crear_municion, disparar, torpedo, torpedo_guiado, usar_municion
from modulos.errores import ErrorJugada, ErrorMunicion
from modulos.flota import crear_flota, ubicar_nave
from modulos.tablero import IMPACTO, HUNDIDO, NAVE, crear_cubo, leer_celda


def armar(tipo, desde, hasta):
    cubo = crear_cubo(8)
    flota = crear_flota()
    ubicar_nave(cubo, flota, tipo, desde, hasta)
    return cubo, flota


def test_el_torpedo_guiado_esta_en_el_diccionario_de_armas():
    assert "G" in ARMAS


def test_sin_impactos_previos_lanza_error_jugada():
    cubo, flota = armar("D", (3, 3, 3), (3, 3, 5))
    with pytest.raises(ErrorJugada):
        torpedo_guiado(cubo, flota)


def test_sin_impactos_previos_no_modifica_el_cubo():
    cubo, flota = armar("D", (3, 3, 3), (3, 3, 5))
    with pytest.raises(ErrorJugada):
        torpedo_guiado(cubo, flota)
    assert leer_celda(cubo, (3, 3, 4)) == NAVE


def test_dispara_a_una_celda_contigua_de_la_nave_impactada():
    cubo, flota = armar("D", (3, 3, 3), (3, 3, 5))
    torpedo(cubo, flota, (3, 3, 3))
    resultados = torpedo_guiado(cubo, flota)
    assert list(resultados.keys()) == [(3, 3, 4)]
    assert resultados[(3, 3, 4)] == "impacto"
    assert leer_celda(cubo, (3, 3, 4)) == IMPACTO


def test_busca_de_forma_recursiva_pasando_por_las_celdas_ya_destruidas():
    cubo, flota = armar("C", (4, 3, 3), (4, 3, 6))
    torpedo(cubo, flota, (4, 3, 3))
    torpedo(cubo, flota, (4, 3, 4))
    resultados = torpedo_guiado(cubo, flota)
    assert list(resultados.keys()) == [(4, 3, 5)]


def test_puede_hundir_la_nave():
    cubo, flota = armar("F", (3, 3, 3), (3, 3, 4))
    torpedo(cubo, flota, (3, 3, 3))
    resultados = torpedo_guiado(cubo, flota)
    assert resultados == {(3, 3, 4): "hundido"}
    assert leer_celda(cubo, (3, 3, 3)) == HUNDIDO


def test_una_nave_hundida_ya_no_sirve():
    cubo, flota = armar("F", (3, 3, 3), (3, 3, 4))
    torpedo(cubo, flota, (3, 3, 3))
    torpedo(cubo, flota, (3, 3, 4))
    with pytest.raises(ErrorJugada):
        torpedo_guiado(cubo, flota)


def test_en_un_portaaviones_tambien_busca_una_celda_que_siga_a_flote():
    cubo, flota = armar("P", (6, 3, 3), (6, 3, 7))
    torpedo(cubo, flota, (6, 3, 3))
    resultados = torpedo_guiado(cubo, flota)
    # La celda de al lado sigue intacta: la elige antes que la ya impactada una vez.
    assert list(resultados.keys()) == [(6, 3, 4)]


def test_funciona_por_el_diccionario_de_armas():
    cubo, flota = armar("D", (3, 3, 3), (3, 3, 5))
    torpedo(cubo, flota, (3, 3, 5))
    jugada = {"arma": "G", "punto": None, "eje": None, "valor": None}
    resultados = disparar(cubo, flota, jugada)
    assert list(resultados.keys()) == [(3, 3, 4)]


def test_solo_tiene_una_municion():
    municion = crear_municion()
    usar_municion(municion, "G")
    with pytest.raises(ErrorMunicion):
        usar_municion(municion, "G")
