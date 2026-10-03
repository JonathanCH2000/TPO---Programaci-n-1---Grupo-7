import re

from modulos.flota import (
    CATALOGO,
    cantidad_ubicada,
    crear_flota,
    datos_nave,
    ubicacion_automatica,
    ubicar_nave,
)
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


def nueva_partida_1v1(configuracion: int = 8) -> list[list]:
    """Recibe el lado del cubo; devuelve el estado inicial de dos jugadores."""
    # Cada jugador arma su cubo y ubica su flota.
    jugador_uno = _preparar_jugador(1, configuracion)
    jugador_dos = _preparar_jugador(2, configuracion)

    return [jugador_uno, jugador_dos]


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
    """estado, jugada → estado actualizado."""
    # TODO: se implementa en una entrega posterior.
    print("Todavia no esta implementado")
    return {}


def turno_maquina(estado: dict) -> dict:
    """Estado → estado actualizado, jugado por la máquina."""
    # TODO: se implementa en una entrega posterior.
    print("Todavia no esta implementado")
    return {}


def hay_ganador(estado: dict) -> str | None:
    """Estado → ganador, o ninguno."""
    # TODO: se implementa en una entrega posterior.
    print("Todavia no esta implementado")
    return None


def _preparar_jugador(numero: int, lado: int) -> list:
    """Recibe numero de jugador y lado del cubo; devuelve [cubo, flota] con la flota ubicada."""
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
                    resultado = ubicar_nave(cubo, flota, tipo, desde, hasta)

                    if resultado is None:
                        print("No se puede ubicar ahi.")
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

    return [cubo, flota]


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
