import random
import re

from modulos.armamento import (
    barrido_laser,
    carga_profundidad,
    crear_municion,
    misil_racimo,
    torpedo,
    usar_municion,
)
from modulos.errores import ErrorUbicacion, ErrorCubo
from modulos.flota import (
    CATALOGO,
    cantidad_ubicada,
    crear_flota,
    datos_nave,
    nave_hundida,
    ubicacion_automatica,
    ubicar_nave,
)
from modulos.radar import sonar
from modulos.registro import crear_historial, registrar_jugada, resumen, ultima_jugada
from modulos.tablero import crear_cubo, dibujar_capa, punto_valido

ARMAS = { 
    #diccionario para ayudar con la seleccion de funciones
    "T": torpedo,
    "R": misil_racimo,
    "C": carga_profundidad,
    "S": sonar,
    "L": barrido_laser,
}

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
                estado= nueva_partida_1v1()
                _jugar_partida(estado)
            case 2:
                estado= nueva_partida_vs_maquina()
                _jugar_partida(estado)
            case 3:
                nueva_partida_maquina_vs_maquina()
            case 4:
                _continuar_partida()
            case 5:
                break


def nueva_partida_1v1(configuracion: int = 8) -> dict:
    """Recibe el lado y devuelve el estado inicial de una partida 1 contra 1."""
    jugador_uno = _preparar_jugador(1, configuracion, False)
    jugador_dos = _preparar_jugador(2, configuracion, False)

    return {
        "jugadores": [jugador_uno, jugador_dos],
        "turno": 0,
        "historial": crear_historial(),
        "ganador": None,
    }


def nueva_partida_vs_maquina(configuracion: int = 8, dificultad: str = "normal") -> dict:
    """Recibe configuracion y dificultad. 
        devuelve el estado inicial contra la maquina."""
    jugador = _preparar_jugador(1, configuracion, False)
    maquina = _preparar_jugador(2, configuracion, True)

    return {
        "jugadores": [jugador, maquina],
        "turno": 0,
        "historial": crear_historial(),
        "ganador": None,
        "dificultad": dificultad,
    }


def nueva_partida_maquina_vs_maquina() -> None: #para la entraga 3
    """Configuración, dificultades → estado inicial de una partida entre dos máquinas."""
    # TODO: se implementa en una entrega posterior.
    print("Todavia no esta implementado")
    return None


def ejecutar_turno(estado: dict, jugada: dict) -> dict:
    """Recibe estado y jugada.
        ejecuta el arma y devuelve el estado actualizado.
        Lanza ErrorCubo si la jugada contiene un arma, punto, eje o valor invalido."""
    numero_atacante = estado["turno"]
    numero_rival = 1 - numero_atacante
    atacante = estado["jugadores"][numero_atacante]
    rival = estado["jugadores"][numero_rival]
    arma = jugada.get("arma", "").upper()

    if arma not in ARMAS:
        raise ErrorCubo("El arma no esta disponible.")

    funcion_arma = ARMAS[arma]

    # Comprueba primero los datos 
    # para no gastar municion en una jugada invalida
    if arma == "S":
        eje = jugada.get("eje")
        valor = jugada.get("valor")

        if eje not in ("z", "x", "y"):
            raise ErrorCubo("El eje del sonar no es valido.")
        if type(valor) != int or valor < 1 or valor > len(rival["cubo"]):
            raise ErrorCubo("El valor del plano no es valido.")
    else:
        punto = jugada.get("punto")

        if type(punto) != tuple or not punto_valido(rival["cubo"], punto):
            raise ErrorCubo("El punto no pertenece al cubo.")

        if arma == "L" and jugada.get("eje") not in ("x", "y"):
            raise ErrorCubo("El eje del laser debe ser x o y.")

    usar_municion(atacante["municion"], arma)


    match arma:
        case "S":
            detectados = funcion_arma(rival["cubo"], jugada["eje"], jugada["valor"])
            resultados = {}
            for punto_detectado in detectados:
                resultados[punto_detectado] = "detectado"
            punto = (jugada["eje"], jugada["valor"])
            
        case "L":
            resultados = funcion_arma(
                rival["cubo"], rival["flota"], jugada["punto"], jugada["eje"]
            )
            punto = jugada["punto"]
            
        case _:
            resultados = funcion_arma(
                rival["cubo"], rival["flota"], jugada["punto"]
            )
            punto = jugada["punto"]

    registrar_jugada(estado["historial"], atacante["numero"], arma, punto, resultados)
    estado["ganador"] = hay_ganador(estado)
    if estado["ganador"] is None:
        estado["turno"] = numero_rival

    return estado


def turno_maquina(estado: dict) -> dict:
    """Recibe el estado; crea una jugada al azar y devuelve el estado actualizado."""
    maquina = estado["jugadores"][estado["turno"]]
    lado = len(estado["jugadores"][1 - estado["turno"]]["cubo"])
    disponibles = []

    for letra in ARMAS:
        cantidad = maquina["municion"][letra]
        if cantidad == "ilimitada" or cantidad > 0:
            disponibles.append(letra)

    arma = random.choice(disponibles)
    jugada = {"arma": arma}

    match arma:
        case "S":
            jugada["eje"] = random.choice(("z", "x", "y"))
            jugada["valor"] = random.randint(1, lado)
        case "L":
            jugada["punto"] = _punto_al_azar(lado)
            jugada["eje"] = random.choice(("x", "y"))
        case _:
            jugada["punto"] = _punto_al_azar(lado)

    return ejecutar_turno(estado, jugada)


def hay_ganador(estado: dict) -> int | None:
    """Recibe el estado y devuelve el numero del ganador o None."""
    jugadores = estado["jugadores"]

    for numero in range(len(jugadores)):
        flota = jugadores[numero]["flota"]

        if len(flota) > 0:
            todas_hundidas = True

            for nave in flota:
                if not nave_hundida(nave):
                    todas_hundidas = False

            if todas_hundidas:
                return jugadores[1 - numero]["numero"]

    return None

def _jugar_partida(estado: dict) -> None:
    """Ejecuta los turnos hasta que haya un ganador o se vuelva al menu principal."""
    print("Flotas ubicadas.")
    print("1 - Iniciar partida")
    print("2 - Volver al menu principal")

    if _pedir_opcion(2) == 2:
        return

    while estado["ganador"] is None:
        jugador = estado["jugadores"][estado["turno"]]
        if jugador["maquina"]:
            print("--- Turno de la maquina ---")
        else:
            print("--- Turno del jugador", jugador["numero"], "---")

        if jugador["maquina"]:
            turno_maquina(estado)
            jugada = ultima_jugada(estado["historial"])
            print("La maquina realizo su jugada.")
            _mostrar_resultados(jugada["resultados"])
        else:
            print("1 - Disparar")
            print("2 - Ver el cubo")
            opcion = _pedir_opcion(2)

            if opcion == 2:
                _ver_cubo(jugador["cubo"])
                continue

            jugada = _pedir_jugada(jugador, len(jugador["cubo"]))

            try:
                ejecutar_turno(estado, jugada)
            except ErrorCubo as error:
                print(f"No se pudo realizar la jugada. {error}")
            else:
                ultima = ultima_jugada(estado["historial"])
                _mostrar_resultados(ultima["resultados"])
            finally:
                print()
    jugadores = []

    for jugador in estado["jugadores"]:
        jugadores.append(jugador["numero"])

    print(resumen(estado["historial"], jugadores, estado["ganador"]))

def _preparar_jugador(numero: int, lado: int, maquina: bool) -> dict:
    """Recibe numero, lado y si es maquina; devuelve los datos del jugador."""
    cubo = crear_cubo(lado)
    flota = crear_flota()
    opcion=2

    if not maquina:
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
    if not maquina: #solo si no es maquina
        _ver_cubo(cubo)

    return {
        "numero": numero,
        "maquina": maquina,
        "cubo": cubo,
        "flota": flota,
        "municion": crear_municion(),
        }  


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
        
def _pedir_jugada(jugador: dict, lado: int) -> dict:
    """Pide el arma y el objetivo; devuelve los datos de la jugada."""
    print("--- Armamento ---")

    for letra in ARMAS:
        print(letra, "- Municion:", jugador["municion"][letra])

    while True:
        arma = input("Arma (T/R/C/S/L): ").strip().upper()

        if re.fullmatch(r"[TRCSL]", arma):
            break

        print("Arma invalida.")

    jugada = {"arma": arma}

    match arma:
        case "S":
            jugada["eje"] = _pedir_eje(("z", "x", "y"))
            print("Valor del plano (1 a", lado, "):")
            jugada["valor"] = _pedir_opcion(lado)

        case "L":
            jugada["punto"] = _pedir_punto(lado)
            jugada["eje"] = _pedir_eje(("x", "y"))

        case _:
            jugada["punto"] = _pedir_punto(lado)

    return jugada


def _mostrar_resultados(resultados: dict) -> None:
    """Muestra el resultado de las celdas afectadas."""
    if len(resultados) == 0:
        print("No se encontraron contactos.")
        return

    for punto in resultados:
        print(punto, "->", resultados[punto])


def _pedir_punto(lado: int) -> tuple:
    """Pide y devuelve un punto valido del cubo."""
    patron = r"[0-9]+,[0-9]+,[0-9]+"

    while True:
        texto = input("Objetivo (z,x,y): ").strip()

        if re.fullmatch(patron, texto):
            valores = texto.split(",")

            punto = (
                int(valores[0]),
                int(valores[1]),
                int(valores[2]),
            )

            punto_correcto = True

            for numero in punto:
                if numero < 1 or numero > lado:
                    punto_correcto = False

            if punto_correcto:
                return punto

        print("El punto debe tener valores entre 1 y", lado)


def _pedir_eje(ejes: tuple) -> str:
    """Pide y devuelve uno de los ejes permitidos."""
    while True:
        eje = input("Eje (" + "/".join(ejes) + "): ").strip().lower()

        if eje in ejes:
            return eje

        print("Eje invalido.")


def _punto_al_azar(lado: int) -> tuple:
    """Devuelve un punto al azar dentro del cubo."""
    return (
        random.randint(1, lado),
        random.randint(1, lado),
        random.randint(1, lado),
    )
