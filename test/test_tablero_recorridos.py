from modulos.tablero import crear_cubo, recorrido_capas, recorrido_espiral


def test_capas_pasa_una_vez_por_cada_celda():
    puntos = recorrido_capas(crear_cubo(4))
    assert len(puntos) == 64
    assert len(set(puntos)) == 64


def test_capas_recorre_una_capa_de_z_despues_de_la_otra():
    puntos = recorrido_capas(crear_cubo(3))
    assert puntos[0] == (1, 1, 1)
    assert puntos[8] == (1, 3, 3)
    assert puntos[9] == (2, 1, 1)
    assert puntos[-1] == (3, 3, 3)


def test_espiral_pasa_una_vez_por_cada_celda():
    for lado in (1, 2, 3, 4, 5, 8):
        puntos = recorrido_espiral(crear_cubo(lado))
        assert len(puntos) == lado ** 3
        assert len(set(puntos)) == lado ** 3


def test_espiral_recorre_la_primera_capa_de_afuera_hacia_adentro():
    puntos = recorrido_espiral(crear_cubo(3))
    assert puntos[:9] == [
        (1, 1, 1), (1, 2, 1), (1, 3, 1),
        (1, 3, 2), (1, 3, 3),
        (1, 2, 3), (1, 1, 3),
        (1, 1, 2),
        (1, 2, 2),
    ]


def test_espiral_termina_una_capa_antes_de_empezar_la_siguiente():
    puntos = recorrido_espiral(crear_cubo(4))
    for numero in range(16):
        assert puntos[numero][0] == 1
    assert puntos[16][0] == 2


def test_recorridos_con_cubo_vacio():
    assert recorrido_capas(crear_cubo(0)) == []
    assert recorrido_espiral(crear_cubo(0)) == []
