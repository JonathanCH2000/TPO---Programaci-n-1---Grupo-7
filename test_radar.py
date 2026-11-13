from modulos.radar import (
    busqueda_lineal,
    busqueda_optimizada,
    busqueda_recursiva,
    mapa_probabilidad,
    puntos_mas_probables,
    recorrido_octantes,
    recorrido_propagacion,
    sonar,
)
from modulos.tablero import (
    AGUA,
    AGUA_MARCADA,
    DETECTADO,
    HUNDIDO,
    IMPACTO,
    NAVE,
    crear_cubo,
    escribir_celda,
    leer_celda,
    recorrido_capas,
)

BUSQUEDAS = [busqueda_lineal, busqueda_optimizada, busqueda_recursiva]


# ---------- Las tres busquedas ----------

def test_las_tres_encuentran_la_nave():
    for buscar in BUSQUEDAS:
        cubo = crear_cubo(8)
        escribir_celda(cubo, (3, 5, 4), NAVE)
        punto, metricas = buscar(cubo, NAVE)
        assert punto == (3, 5, 4)


def test_las_tres_devuelven_none_si_no_hay():
    for buscar in BUSQUEDAS:
        punto, metricas = buscar(crear_cubo(8), NAVE)
        assert punto is None


def test_las_tres_encuentran_otros_estados():
    for buscar in BUSQUEDAS:
        cubo = crear_cubo(5)
        escribir_celda(cubo, (2, 3, 3), IMPACTO)
        punto, metricas = buscar(cubo, IMPACTO)
        assert punto == (2, 3, 3)


def test_las_tres_devuelven_las_tres_metricas():
    for buscar in BUSQUEDAS:
        punto, metricas = buscar(crear_cubo(3), NAVE)
        assert set(metricas.keys()) == {"comparaciones", "tiempo_ms", "profundidad_max"}
        assert metricas["tiempo_ms"] >= 0


def test_las_tres_funcionan_con_cubos_de_otros_lados():
    for lado in (1, 2, 3, 5, 7):
        for buscar in BUSQUEDAS:
            cubo = crear_cubo(lado)
            escribir_celda(cubo, (lado, lado, lado), NAVE)
            punto, metricas = buscar(cubo, NAVE)
            assert punto == (lado, lado, lado)


# ---------- Lineal ----------

def test_lineal_sin_resultado_compara_todas_las_celdas():
    punto, metricas = busqueda_lineal(crear_cubo(8), NAVE)
    assert metricas["comparaciones"] == 8 * 8 * 8


def test_lineal_devuelve_la_primera_aparicion():
    cubo = crear_cubo(4)
    escribir_celda(cubo, (1, 2, 3), NAVE)
    escribir_celda(cubo, (4, 4, 4), NAVE)
    punto, metricas = busqueda_lineal(cubo, NAVE)
    assert punto == (1, 2, 3)


def test_lineal_comparaciones_hasta_una_celda_intermedia():
    cubo = crear_cubo(4)
    escribir_celda(cubo, (1, 2, 3), NAVE)  # 4 celdas de x=1 + 3 de x=2
    punto, metricas = busqueda_lineal(cubo, NAVE)
    assert metricas["comparaciones"] == 7


def test_lineal_no_es_recursiva():
    punto, metricas = busqueda_lineal(crear_cubo(3), NAVE)
    assert metricas["profundidad_max"] == 0


# ---------- Optimizada ----------

def test_optimizada_encuentra_una_nave_de_dos_celdas_revisando_pocas_celdas():
    cubo = crear_cubo(8)
    escribir_celda(cubo, (8, 8, 7), NAVE)
    escribir_celda(cubo, (8, 8, 8), NAVE)
    punto, metricas = busqueda_optimizada(cubo, NAVE)
    assert punto in ((8, 8, 7), (8, 8, 8))
    assert metricas["comparaciones"] <= 8 * 8 * 8 // 2


# ---------- Recursiva ----------

def test_recursiva_devuelve_el_mismo_punto_que_la_lineal():
    for punto_nave in [(1, 1, 1), (1, 8, 8), (4, 4, 5), (5, 6, 7), (8, 1, 1), (8, 8, 8)]:
        cubo = crear_cubo(8)
        escribir_celda(cubo, punto_nave, NAVE)
        escribir_celda(cubo, (8, 8, 8), NAVE)
        recursiva, m1 = busqueda_recursiva(cubo, NAVE)
        lineal, m2 = busqueda_lineal(cubo, NAVE)
        assert recursiva == lineal
        assert m1["comparaciones"] == m2["comparaciones"]


def test_recursiva_sin_resultado_compara_todas_las_celdas():
    punto, metricas = busqueda_recursiva(crear_cubo(8), NAVE)
    assert metricas["comparaciones"] == 8 * 8 * 8


def test_recursiva_informa_la_profundidad_real():
    punto, metricas = busqueda_recursiva(crear_cubo(8), NAVE)
    # 9 particiones (3 por cada eje) y una llamada mas para la celda: 10 llamadas anidadas.
    assert metricas["profundidad_max"] == 10


def test_recursiva_con_una_sola_celda():
    punto, metricas = busqueda_recursiva(crear_cubo(1), NAVE)
    assert punto is None
    assert metricas["comparaciones"] == 1
    assert metricas["profundidad_max"] == 1


def test_recursiva_con_cubo_vacio():
    punto, metricas = busqueda_recursiva(crear_cubo(0), NAVE)
    assert punto is None
    assert metricas["comparaciones"] == 0


def test_recursiva_no_modifica_el_cubo():
    cubo = crear_cubo(3)
    escribir_celda(cubo, (2, 2, 2), NAVE)
    busqueda_recursiva(cubo, NAVE)
    assert leer_celda(cubo, (2, 2, 2)) == NAVE
    assert leer_celda(cubo, (1, 1, 1)) == AGUA


# ---------- Sonar ----------

def test_sonar_detecta_solo_las_naves_del_plano():
    cubo = crear_cubo(5)
    escribir_celda(cubo, (3, 1, 1), NAVE)
    escribir_celda(cubo, (3, 4, 2), NAVE)
    escribir_celda(cubo, (4, 1, 1), NAVE)
    detectados = sonar(cubo, "z", 3)
    assert sorted(detectados) == [(3, 1, 1), (3, 4, 2)]
    assert leer_celda(cubo, (3, 1, 1)) == DETECTADO
    assert leer_celda(cubo, (4, 1, 1)) == NAVE


def test_sonar_con_eje_o_valor_invalido_devuelve_none():
    assert sonar(crear_cubo(5), "w", 1) is None
    assert sonar(crear_cubo(5), "z", 9) is None


# ---------- Mapa de probabilidad ----------

def test_mapa_no_incluye_celdas_ya_disparadas():
    cubo = crear_cubo(4)
    escribir_celda(cubo, (1, 1, 1), AGUA_MARCADA)
    escribir_celda(cubo, (2, 2, 2), IMPACTO)
    escribir_celda(cubo, (3, 3, 3), HUNDIDO)
    mapa = mapa_probabilidad(cubo, [2])
    assert (1, 1, 1) not in mapa
    assert (2, 2, 2) not in mapa
    assert (3, 3, 3) not in mapa
    assert len(mapa) == 4 * 4 * 4 - 3


def test_mapa_el_centro_vale_mas_que_la_esquina():
    mapa = mapa_probabilidad(crear_cubo(3), [2])
    assert mapa[(2, 2, 2)] > mapa[(1, 1, 1)]


def test_mapa_las_naves_ocultas_se_ven_como_agua():
    con_nave = crear_cubo(4)
    escribir_celda(con_nave, (2, 2, 2), NAVE)
    assert mapa_probabilidad(con_nave, [3, 2]) == mapa_probabilidad(crear_cubo(4), [3, 2])


def test_mapa_un_impacto_sube_el_puntaje_de_sus_vecinos():
    cubo = crear_cubo(5)
    escribir_celda(cubo, (3, 3, 3), IMPACTO)
    mapa = mapa_probabilidad(cubo, [3])
    assert mapa[(3, 3, 4)] > mapa[(1, 1, 1)]
    assert mapa[(3, 3, 4)] > mapa[(5, 5, 5)]


def test_mapa_una_celda_detectada_es_la_mas_probable():
    cubo = crear_cubo(5)
    escribir_celda(cubo, (2, 4, 4), DETECTADO)
    mapa = mapa_probabilidad(cubo, [3, 2])
    assert (2, 4, 4) in puntos_mas_probables(mapa)


def test_mapa_las_naves_hundidas_no_dejan_pasar_otras():
    cubo = crear_cubo(3)
    for x in range(1, 4):
        escribir_celda(cubo, (2, x, 1), HUNDIDO)
        escribir_celda(cubo, (2, x, 3), HUNDIDO)
    # Con todo el plano z=2 de y=1 e y=3 hundido, ninguna nave de 3 pasa por z=2 en esas filas.
    mapa = mapa_probabilidad(cubo, [3])
    assert mapa[(2, 1, 2)] >= 1


def test_mapa_sin_largos_da_cero_en_todas_las_celdas():
    mapa = mapa_probabilidad(crear_cubo(3), [])
    assert set(mapa.values()) == {0}
    assert len(mapa) == 27


def test_puntos_mas_probables_devuelve_los_empatados():
    mapa = {(1, 1, 1): 5, (1, 1, 2): 9, (1, 1, 3): 9, (1, 2, 1): 1}
    assert puntos_mas_probables(mapa) == [(1, 1, 2), (1, 1, 3)]


def test_puntos_mas_probables_con_mapa_vacio():
    assert puntos_mas_probables({}) == []


# ---------- Recorridos recursivos ----------

def test_octantes_pasa_una_vez_por_cada_celda():
    cubo = crear_cubo(4)
    puntos = recorrido_octantes(cubo)
    assert len(puntos) == 64
    assert set(puntos) == set(recorrido_capas(cubo))


def test_octantes_recorre_primero_un_octante_completo():
    puntos = recorrido_octantes(crear_cubo(4))
    for punto in puntos[:8]:
        assert punto[0] <= 2 and punto[1] <= 2 and punto[2] <= 2


def test_octantes_con_lados_impares_y_chicos():
    for lado in (1, 2, 3, 5):
        cubo = crear_cubo(lado)
        puntos = recorrido_octantes(cubo)
        assert len(puntos) == lado ** 3
        assert len(set(puntos)) == lado ** 3


def test_octantes_con_cubo_vacio():
    assert recorrido_octantes(crear_cubo(0)) == []


def test_propagacion_recorre_el_grupo_de_impactos_conectado():
    cubo = crear_cubo(5)
    for punto in [(2, 2, 2), (2, 2, 3), (2, 2, 4)]:
        escribir_celda(cubo, punto, IMPACTO)
    escribir_celda(cubo, (5, 5, 5), IMPACTO)
    alcanzados = recorrido_propagacion(cubo, (2, 2, 3))
    assert sorted(alcanzados) == [(2, 2, 2), (2, 2, 3), (2, 2, 4)]


def test_propagacion_no_pasa_por_diagonales():
    cubo = crear_cubo(3)
    escribir_celda(cubo, (1, 1, 1), IMPACTO)
    escribir_celda(cubo, (2, 2, 2), IMPACTO)
    assert recorrido_propagacion(cubo, (1, 1, 1)) == [(1, 1, 1)]


def test_propagacion_desde_una_celda_sin_el_estado_devuelve_lista_vacia():
    assert recorrido_propagacion(crear_cubo(3), (1, 1, 1)) == []


def test_propagacion_con_otros_estados():
    cubo = crear_cubo(3)
    escribir_celda(cubo, (1, 1, 1), HUNDIDO)
    escribir_celda(cubo, (1, 1, 2), HUNDIDO)
    escribir_celda(cubo, (1, 1, 3), IMPACTO)
    assert len(recorrido_propagacion(cubo, (1, 1, 1), (HUNDIDO,))) == 2
    assert len(recorrido_propagacion(cubo, (1, 1, 1), (HUNDIDO, IMPACTO))) == 3


def test_propagacion_con_punto_fuera_del_cubo_devuelve_none():
    assert recorrido_propagacion(crear_cubo(3), (9, 1, 1)) is None
