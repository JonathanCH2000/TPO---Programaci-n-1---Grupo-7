import re

from modulos.armamento import crear_municion, disparar, usar_municion
from modulos.errores import ErrorUbicacion
from modulos.flota import (
    CATALOGO,
    cantidad_ubicada,
    crear_flota,
    datos_nave,
    flota_hundida,
    ubicacion_automatica,
    ubicar_nave,
)
from modulos.registro import crear_historial, registrar_jugada
from modulos.tablero import crear_cubo, dibujar_capa


def menu_interactivo() -> None:
    """Muestra el menu principal hasta que se elige salir."""
    while True:
        print("===== OPERACION CUBO =====")
        print("1 - Partida uno contra uno")
        print("2 - Partida uno contra la maquina")
        print("3 - Partida maquina contra maquina")
        print("4 - Continuar una partida")
        print("5 - Salir")
        opcion = _pedir_opcion(5)

        # Ejecutar la opcion elegida. Despues de cada una vuelve a mostrarse el menu.
        match opcion:
            case 1:
                nueva_partida_1v1()
            case 2:
                nueva_partida_vs_maquina()
            case 3:
                nueva_partida_maquina_vs_maquina()
            case 4:
                _continuar_partida()
            case 5:
                break


def nueva_partida_1v1(configuracion: int = 8) -> dict:
    """Recibe la configuracion de la partida (por ahora, el lado del cubo: 8 por defecto);
    devuelve el estado inicial de una partida de dos jugadores."""
    # Cada jugador arma su cubo y ubica su flota.
    jugador_uno = _preparar_jugador(1, configuracion)
    jugador_dos = _preparar_jugador(2, configuracion)

    # Estado de la partida: empieza jugando el primero de la lista (turno 0).
    estado = {
        "jugadores": [jugador_uno, jugador_dos],
        "turno": 0,
        "historial": crear_historial(),
        "ganador": None,
    }

    return estado


def nueva_partida_vs_maquina() -> None:
    """Configuración, dificultad → estado inicial de una partida contra la máquina."""
    # TODO: se implementa en una entrega posterior.
    print("Todavia no esta implementado")
    return None


def nueva_partida_maquina_vs_maquina() -> None:
    """Configuración, dificultades → estado inicial de una partida entre dos máquinas."""
    # TODO: se implementa en una entrega posterior.
    print("Todavia no esta implementado")
    return None


def ejecutar_turno(estado: dict, jugada: dict) -> dict:
    """Recibe el estado y la jugada del jugador de turno (arma, punto, eje y valor);
    gasta la municion, dispara al rival, registra la jugada, pasa el turno y devuelve el estado actualizado.
    Lanza ErrorMunicion si no queda municion y ErrorJugada si la jugada no es valida."""
    jugador = estado["jugadores"][estado["turno"]]
    rival = estado["jugadores"][1 - estado["turno"]]

    # Gastar la municion en una copia: si el disparo falla, la original queda intacta.
    municion = dict(jugador["municion"])
    usar_municion(municion, jugada["arma"])

    # Disparar al cubo y la flota del rival.
    resultados = disparar(rival["cubo"], rival["flota"], jugada)

    # El disparo salio bien: recien ahora se guarda el gasto de municion.
    jugador["municion"] = municion

    registrar_jugada(
        estado["historial"],
        jugador["nombre"],
        jugada["arma"],
        jugada["punto"],
        resultados,
    )

    # Pasar el turno al otro jugador (0 -> 1 o 1 -> 0).
    estado["turno"] = 1 - estado["turno"]

    return estado


def turno_maquina(estado: dict) -> dict:
    """Estado → estado actualizado, jugado por la máquina."""
    # TODO: se implementa en una entrega posterior.
    print("Todavia no esta implementado")
    return {}


def hay_ganador(estado: dict) -> str | None:
    """Recibe el estado; devuelve el nombre del ganador (el que hundio toda la flota
    del rival), o None si todavia no gano nadie."""
    for numero in range(len(estado["jugadores"])):
        jugador = estado["jugadores"][numero]
        rival = estado["jugadores"][1 - numero]

        # Gana el jugador cuyo rival ya no tiene naves a flote.
        if flota_hundida(rival["flota"]):
            return jugador["nombre"]

    return None


def _preparar_jugador(numero: int, lado: int) -> dict:
    """Recibe numero de jugador y lado del cubo; ubica su flota y devuelve el jugador:
    un diccionario con su nombre, su cubo, su flota y su municion."""
    cubo = crear_cubo(lado)
    flota = crear_flota()

    print(f"--- Jugador {numero} ---")
    print("1 - Ubicacion manual")
    print("2 - Ubicacion automatica")
    opcion = _pedir_opcion(2)

    match opcion:
        # Ubicacion manual: el jugador elige cada nave y su tramo.
        case 1:
            # Contar cuantas naves hay que ubicar en total.
            total = 0

            for modelo_nave in CATALOGO:
                total += modelo_nave[3]

            # Repetir hasta que esten todas las naves ubicadas.
            while len(flota) < total:
                # Mostrar cuantas faltan de cada tipo.
                print("--- Naves pendientes ---")

                for modelo_nave in CATALOGO:
                    faltan = modelo_nave[3] - cantidad_ubicada(flota, modelo_nave[0])
                    print(f"{modelo_nave[0]} - {modelo_nave[1]} x {faltan}")

                tipo = input("Nave: ").strip().upper()

                # La letra no corresponde a ninguna nave del catalogo.
                if datos_nave(tipo) is None:
                    print("Nave invalida.")
                else:
                    # Pedir el tramo e intentar ubicar la nave.
                    desde, hasta = _pedir_tramo()
                    try:
                        ubicar_nave(cubo, flota, tipo, desde, hasta)
                    except ErrorUbicacion as error:
                        # Mostrar el motivo por el que no se pudo ubicar.
                        print(f"No se puede ubicar ahi. {error}")
                    else:
                        print("Nave ubicada.")

        # Ubicacion automatica: el juego ubica toda la flota al azar.
        case 2:
            flota = ubicacion_automatica(cubo, CATALOGO, None)

            # Si no entro toda la flota, empezar de nuevo con un cubo vacio.
            while flota is None:
                cubo = crear_cubo(lado)
                flota = ubicacion_automatica(cubo, CATALOGO, None)

            print("Flota ubicada.")

    # Le pregunta al usuario si quiere ver varias capas o seguir.
    _ver_cubo(cubo)

    jugador = {
        "nombre": f"Jugador {numero}",
        "es_maquina": False,
        "cubo": cubo,
        "flota": flota,
        "municion": crear_municion(),
    }

    return jugador


def _ver_cubo(cubo: list) -> None:
    """Muestra las capas del cubo que elija el jugador hasta que decida continuar."""
    while True:
        # Pedir la capa de z a dibujar.
        print(f"Capa que quiere ver (1 a: {len(cubo)}):")
        capa = _pedir_opcion(len(cubo))

        # Dibujar la capa mostrando las naves propias.
        print(dibujar_capa(cubo, capa, True))

        # Preguntar si quiere ver otra capa o seguir.
        print("1 - Ver otra capa")
        print("2 - Continuar")
        if _pedir_opcion(2) == 2:
            return


def _continuar_partida() -> None:
    """Retoma una partida guardada (opcion 4 del menu principal)."""
    # TODO: se implementa en otra entrega.
    print("Todavia no esta implementado")


def _pedir_opcion(maximo: int) -> int:
    """Recibe el maximo y devuelve una opcion valida del menu."""
    # Repetir hasta que el usuario escriba una opcion valida.
    while True:
        texto = input("Opcion: ").strip()

        # Solo se aceptan numeros.
        if re.fullmatch(r"[0-9]+", texto):
            opcion = int(texto)

            # El numero tiene que estar entre 1 y el maximo.
            if opcion >= 1 and opcion <= maximo:
                return opcion

        print("Opcion invalida.")


def _pedir_tramo() -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    """Pide dos puntos y los devuelve como tuplas."""
    # Formato aceptado: z,x,y-z,x,y (por ejemplo 3,5,4-3,5,5).
    patron = r"[0-9]+,[0-9]+,[0-9]+-[0-9]+,[0-9]+,[0-9]+"

    # Repetir hasta que el usuario escriba un tramo con el formato correcto.
    while True:
        texto = input("Desde-hasta (z,x,y-z,x,y): ").strip()

        if re.fullmatch(patron, texto):
            # Separar los dos puntos y despues los tres valores de cada uno.
            partes = texto.split("-")
            inicio = partes[0].split(",")
            final = partes[1].split(",")

            # Pasar los valores de texto a numeros.
            desde = (int(inicio[0]), int(inicio[1]), int(inicio[2]))
            hasta = (int(final[0]), int(final[1]), int(final[2]))

            return desde, hasta

        print("Ejemplo: 3,5,4-3,5,5")
