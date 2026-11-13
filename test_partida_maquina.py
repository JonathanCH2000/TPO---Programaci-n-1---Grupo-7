from modulos.partida import (
    ELEGIR_JUGADA,
    ejecutar_turno,
    hay_ganador,
    nueva_partida_maquina_vs_maquina,
    turno_maquina,
)


def armar_estado(niveles):
    return nueva_partida_maquina_vs_maquina(8, niveles)


def test_hay_un_nivel_1_y_un_nivel_2():
    assert sorted(ELEGIR_JUGADA.keys()) == [1, 2]


def test_las_maquinas_guardan_su_dificultad():
    estado = armar_estado((2, 1))
    assert estado["jugadores"][0]["dificultad"] == 2
    assert estado["jugadores"][1]["dificultad"] == 1


def test_nivel_1_dispara_un_torpedo_y_pasa_el_turno():
    estado = armar_estado((1, 1))
    turno_maquina(estado)
    assert estado["historial"][-1]["arma"] == "T"
    assert estado["turno"] == 1


def test_nivel_2_empieza_con_un_torpedo_porque_no_hay_naves_averiadas():
    estado = armar_estado((2, 1))
    turno_maquina(estado)
    assert estado["historial"][-1]["arma"] == "T"


def test_nivel_2_usa_el_torpedo_guiado_si_hay_una_nave_averiada():
    estado = armar_estado((2, 1))
    rival = estado["jugadores"][1]
    punto = sorted(rival["flota"][0]["puntos"])[0]
    ejecutar_turno(estado, {"arma": "T", "punto": punto, "eje": None, "valor": None})
    estado["turno"] = 0
    turno_maquina(estado)
    assert estado["historial"][-1]["arma"] == "G"
    assert estado["jugadores"][0]["municion"]["G"] == 0


def test_nivel_2_no_repite_el_torpedo_guiado():
    estado = armar_estado((2, 1))
    rival = estado["jugadores"][1]
    punto = sorted(rival["flota"][2]["puntos"])[0]
    ejecutar_turno(estado, {"arma": "T", "punto": punto, "eje": None, "valor": None})
    estado["turno"] = 0
    turno_maquina(estado)
    estado["turno"] = 0
    turno_maquina(estado)
    armas = [jugada["arma"] for jugada in estado["historial"]]
    assert armas.count("G") == 1


def test_nivel_2_no_dispara_dos_veces_al_mismo_lugar():
    estado = armar_estado((2, 2))
    for _ in range(25):
        turno_maquina(estado)
    for jugador in ("Maquina 1", "Maquina 2"):
        puntos = []
        for jugada in estado["historial"]:
            if jugada["jugador"] == jugador:
                for punto, resultado in jugada["resultados"].items():
                    assert resultado != "repetido"


def test_partida_completa_de_nivel_1_termina_con_ganador():
    estado = armar_estado((1, 1))
    turnos = 0
    while hay_ganador(estado) is None and turnos < 2000:
        turno_maquina(estado)
        turnos += 1
    assert hay_ganador(estado) in ("Maquina 1", "Maquina 2")
