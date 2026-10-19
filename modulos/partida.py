import random
import re

from modulos.armamento import crear_municion, disparar, usar_municion
from modulos.errores import ErrorCubo, ErrorUbicacion
from modulos.flota import (
    CATALOGO,
    buscar_nave,
    cantidad_ubicada,
    celdas_destruidas,
    crear_flota,
    datos_nave,
    flota_hundida,
    nave_hundida,
    ubicacion_automatica,
    ubicar_nave,
)
from modulos.registro import crear_historial, registrar_jugada, resumen
from modulos.tablero import (
    AGUA,
    DETECTADO,
    IMPACTO,
    NAVE,
    crear_cubo,
    dibujar_capa,
    leer_celda,
)


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
                _jugar_partida(nueva_partida_1v1())
            case 2:
                _jugar_partida(nueva_partida_vs_maquina())
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


def nueva_partida_vs_maquina(configuracion: int = 8, dificultad: int = 1) -> dict:
    """Recibe la configuracion (el lado del cubo) y la dificultad de la maquina;
    devuelve el estado inicial de una partida de un jugador contra la maquina."""
    # El jugador ubica su flota; la de la maquina se ubica siempre sola.
    jugador = _preparar_jugador(1, configuracion)
    maquina = _preparar_maquina(configuracion, dificultad)

    # Empieza jugando la persona (turno 0).
    estado = {
        "jugadores": [jugador, maquina],
        "turno": 0,
        "historial": crear_historial(),
        "ganador": None,
    }

    return estado


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
    """Recibe el estado con la maquina de turno; elige un objetivo, dispara un torpedo
    y devuelve el estado actualizado."""
    rival = estado["jugadores"][1 - estado["turno"]]

    jugada = {
        "arma": "T",
        "punto": _objetivo_al_azar(rival["cubo"]),
        "eje": None,
        "valor": None,
    }

    return ejecutar_turno(estado, jugada)


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
            cubo, flota = _flota_automatica(lado)
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


def _jugar_partida(estado: dict) -> None:
    """Recibe el estado inicial; alterna los turnos hasta que haya un ganador."""
    # La consigna pide confirmar antes de empezar.
    print("Flotas ubicadas.")
    print("1 - Empezar la partida")
    _pedir_opcion(1)

    while hay_ganador(estado) is None:
        jugador = estado["jugadores"][estado["turno"]]

        print(f"--- Turno de {jugador['nombre']} ---")

        # La maquina juega sola; la persona elige en el menu del turno.
        if jugador["es_maquina"]:
            _turno_de_maquina(estado)
            continue

        print("1 - Disparar")
        print("2 - Ver el cubo")
        opcion = _pedir_opcion(2)

        # Buscar la accion elegida en el diccionario y ejecutarla.
        accion = ACCIONES_TURNO[opcion]
        accion(estado)

    estado["ganador"] = hay_ganador(estado)
    print(f"Gano {estado['ganador']}.")

    # Mostrar el resumen con las estadisticas de los dos jugadores.
    nombres = []
    for jugador in estado["jugadores"]:
        nombres.append(jugador["nombre"])

    print(resumen(estado["historial"], nombres, estado["ganador"]))


def _turno_disparar(estado: dict) -> None:
    """Pide la jugada al jugador de turno y la ejecuta. Si no se puede, avisa el motivo
    y el turno no pasa, para que vuelva a intentar."""
    # Guardar el rival antes de jugar: despues del turno, el turno pasa a el.
    rival = estado["jugadores"][1 - estado["turno"]]
    jugada = _pedir_jugada()

    try:
        ejecutar_turno(estado, jugada)
    except ErrorCubo as error:
        print(error)
    else:
        # La jugada recien hecha es la ultima del historial.
        _mostrar_resultados(rival, estado["historial"][-1])


def _mostrar_resultados(rival: dict, jugada: dict) -> None:
    """Recibe el rival y la jugada hecha; muestra que paso en cada celda afectada
    y, si se pego a una nave, como quedo esa nave."""
    for punto, resultado in jugada["resultados"].items():
        texto = f"{punto[0]},{punto[1]},{punto[2]}: {MENSAJES_RESULTADO[resultado]}"

        # Si se le pego a una nave, agregar como quedo.
        nave = buscar_nave(rival["flota"], punto)
        if nave is not None and resultado in ("impacto", "hundido"):
            texto += " " + _describir_nave(nave)

        print(texto)

    # El sonar ademas resume cuantos contactos encontro en el plano.
    if jugada["arma"] == "S":
        print(
            f"Sonar sobre el plano {jugada['eje']} = {jugada['valor']}. "
            f"{len(jugada['resultados'])} contactos detectados."
        )


def _describir_nave(nave: dict) -> str:
    """Recibe una nave; devuelve un texto con su nombre y si esta averiada o hundida."""
    modelo_nave = datos_nave(nave["tipo"])

    # El nombre sale del catalogo; si el tipo no estuviera, se muestra su letra.
    nombre = nave["tipo"] if modelo_nave is None else modelo_nave[1]

    if nave_hundida(nave):
        return f"Nave hundida: {nombre}."

    return f"Nave averiada: {nombre} ({celdas_destruidas(nave)} de {len(nave['puntos'])})."


# Resultado de una celda -> mensaje para el jugador.
MENSAJES_RESULTADO = {
    "agua": "Agua.",
    "impacto": "Impacto.",
    "hundido": "Impacto.",
    "repetido": "Ya habias disparado ahi.",
    "detectado": "Contacto detectado.",
}


def _turno_de_maquina(estado: dict) -> None:
    """Hace jugar a la maquina de turno y muestra donde disparo y que paso."""
    rival = estado["jugadores"][1 - estado["turno"]]

    turno_maquina(estado)
    jugada = estado["historial"][-1]

    punto = jugada["punto"]
    print(f"Dispara a {punto[0]},{punto[1]},{punto[2]}.")
    _mostrar_resultados(rival, jugada)


def _objetivo_al_azar(cubo: list) -> tuple[int, int, int]:
    """Recibe el cubo del rival; devuelve al azar un punto al que todavia no se disparo.
    Si ya se disparo a todos, devuelve un punto con impacto (el portaaviones necesita
    dos impactos por celda)."""
    sin_disparar = []
    impactados = []
    lado = len(cubo)

    # Separar las celdas segun lo que la maquina puede ver de ellas.
    for z in range(1, lado + 1):
        for x in range(1, lado + 1):
            for y in range(1, lado + 1):
                punto = (z, x, y)
                estado_celda = leer_celda(cubo, punto)

                # Agua y naves ocultas se ven igual: todavia no se disparo ahi.
                if estado_celda in (AGUA, NAVE, DETECTADO):
                    sin_disparar.append(punto)
                elif estado_celda == IMPACTO:
                    impactados.append(punto)

    if len(sin_disparar) > 0:
        return random.choice(sin_disparar)

    return random.choice(impactados)


def _turno_ver_cubo(estado: dict) -> None:
    """Muestra al jugador de turno sus disparos (el cubo del rival, sin sus naves)
    o su propia flota."""
    jugador = estado["jugadores"][estado["turno"]]
    rival = estado["jugadores"][1 - estado["turno"]]

    print("1 - Mis disparos")
    print("2 - Mi flota")
    opcion = _pedir_opcion(2)

    # Opcion -> (cubo a mostrar, si se ven las naves).
    cubos = {1: (rival["cubo"], False), 2: (jugador["cubo"], True)}
    cubo, mostrar_naves = cubos[opcion]

    _ver_cubo(cubo, mostrar_naves)


# Opcion del menu del turno -> funcion que la ejecuta.
ACCIONES_TURNO = {
    1: _turno_disparar,
    2: _turno_ver_cubo,
}


def _preparar_maquina(lado: int, dificultad: int) -> dict:
    """Recibe el lado del cubo y la dificultad; devuelve la maquina con su flota
    ubicada automaticamente."""
    cubo, flota = _flota_automatica(lado)

    maquina = {
        "nombre": "Maquina",
        "es_maquina": True,
        "dificultad": dificultad,
        "cubo": cubo,
        "flota": flota,
        "municion": crear_municion(),
    }

    return maquina


def _flota_automatica(lado: int) -> tuple[list, list]:
    """Recibe el lado del cubo; crea un cubo, ubica toda la flota al azar y devuelve
    (cubo, flota)."""
    cubo = crear_cubo(lado)
    flota = ubicacion_automatica(cubo, CATALOGO, None)

    # Si no entro toda la flota, empezar de nuevo con un cubo vacio.
    while flota is None:
        cubo = crear_cubo(lado)
        flota = ubicacion_automatica(cubo, CATALOGO, None)

    return cubo, flota


def _ver_cubo(cubo: list, mostrar_naves: bool = True) -> None:
    """Muestra las capas del cubo que elija el jugador hasta que decida continuar.
    Las naves se ven solo si mostrar_naves es True."""
    while True:
        # Pedir la capa de z a dibujar.
        print(f"Capa que quiere ver (1 a: {len(cubo)}):")
        capa = _pedir_opcion(len(cubo))

        print(dibujar_capa(cubo, capa, mostrar_naves))

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


def _pedir_arma() -> str:
    """Pide la letra de un arma y la devuelve en mayuscula."""
    # Solo se aceptan las letras de las armas del catalogo, en mayuscula o minuscula.
    patron = r"[TRCSLOG]"

    # Repetir hasta que el usuario escriba una letra valida.
    while True:
        texto = input("Arma (T/R/C/S/L/O/G): ").strip().upper()

        if re.fullmatch(patron, texto):
            return texto

        print("Arma invalida.")


def _pedir_punto() -> tuple[int, int, int]:
    """Pide un punto y lo devuelve como tupla."""
    # Formato aceptado: z,x,y (por ejemplo 4,2,7).
    patron = r"[0-9]+,[0-9]+,[0-9]+"

    # Repetir hasta que el usuario escriba un punto con el formato correcto.
    while True:
        texto = input("Objetivo (z,x,y): ").strip()

        if re.fullmatch(patron, texto):
            # Separar los tres valores y pasarlos a numeros.
            valores = texto.split(",")
            return (int(valores[0]), int(valores[1]), int(valores[2]))

        print("Ejemplo: 4,2,7")


def _pedir_eje(ejes: str) -> str:
    """Recibe los ejes permitidos (por ejemplo "xy"); pide uno y lo devuelve en minuscula."""
    # Solo se acepta una de las letras permitidas, por ejemplo [xy].
    patron = f"[{ejes}]"

    # Repetir hasta que el usuario escriba un eje valido.
    while True:
        texto = input(f"Eje ({'/'.join(ejes)}): ").strip().lower()

        if re.fullmatch(patron, texto):
            return texto

        print("Eje invalido.")


def _pedir_valor() -> int:
    """Pide el valor de un eje y lo devuelve como numero."""
    # Repetir hasta que el usuario escriba un numero.
    while True:
        texto = input("Valor: ").strip()

        if re.fullmatch(r"[0-9]+", texto):
            return int(texto)

        print("Valor invalido.")


def _pedir_jugada() -> dict:
    """Pide el arma y los datos que necesita; devuelve la jugada (arma, punto, eje y valor)."""
    arma = _pedir_arma()

    # Buscar que datos pide esa arma. Las que no figuran en el diccionario piden un punto.
    pedir_datos = DATOS_POR_ARMA.get(arma, _datos_punto)
    jugada = pedir_datos()
    jugada["arma"] = arma

    return jugada


def _datos_punto() -> dict:
    """Pide los datos de las armas que solo apuntan a un punto."""
    return {"punto": _pedir_punto(), "eje": None, "valor": None}


def _datos_laser() -> dict:
    """Pide los datos del barrido laser: un punto y el eje del barrido (x o y)."""
    return {"punto": _pedir_punto(), "eje": _pedir_eje("xy"), "valor": None}


def _datos_sonar() -> dict:
    """Pide los datos del sonar: el eje del plano (z, x o y) y su valor."""
    return {"punto": None, "eje": _pedir_eje("zxy"), "valor": _pedir_valor()}


# Letra del arma -> funcion que pide sus datos. Las demas armas usan _datos_punto.
DATOS_POR_ARMA = {
    "L": _datos_laser,
    "S": _datos_sonar,
}
