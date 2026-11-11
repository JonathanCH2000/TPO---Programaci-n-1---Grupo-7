import json
import re

from modulos.errores import ErrorCubo

def crear_historial() -> list:
    """Devuelve una lista vacia para guardar las jugadas de la partida."""
    return []


def registrar_jugada(
    historial: list, jugador: str, arma: str, punto: tuple, resultados: dict, eje: str | None = None, valor: int |None = None) -> list[dict]:
    """Recibe el historial, quien jugo, la letra del arma, el punto y el diccionario punto -> resultado que devolvio el arma.
    Agrega la jugada al final del historial y lo devuelve."""
    # El numero de turno es la cantidad de jugadas que ya hay mas 1.
    numero_turno = len(historial) + 1

    # Guardar los datos de la jugada en un diccionario.
    jugada = {
        "turno": numero_turno,
        "jugador": jugador,
        "arma": arma,
        "punto": punto,
        "eje": eje,
        "valor":valor,
        "resultados": resultados,

    }

    # Agregar la jugada al final del historial.
    historial.append(jugada)

    return historial


def ultima_jugada(historial: list) -> dict | None:
    """Devuelve la ultima jugada del historial, o None si todavia no hay jugadas."""
    # Si el historial esta vacio, no hay jugadas para devolver.
    if len(historial) == 0:
        return None

    # La ultima jugada es la que esta al final de la lista.
    return historial[-1]


def estadisticas(historial: list, jugador: str) -> dict[str, int | float]:
    """Recibe el historial y un jugador; devuelve un diccionario con sus jugadas, cuantas
    celdas dieron cada resultado y su porcentaje de acierto."""
    # Arrancar todo en 0 para que siempre esten las claves, aunque no haya jugadas.
    datos: dict[str, int | float] = {
        "jugadas": 0,
        "agua": 0,
        "impacto": 0,
        "hundido": 0,
        "repetido": 0,
    }

    for jugada in historial:
        # Solo cuentan las jugadas de este jugador.
        if jugada["jugador"] != jugador:
            continue

        datos["jugadas"] += 1

        # Sumar el resultado de cada celda que afecto el arma.
        for resultado in jugada["resultados"].values():
            datos[resultado] = datos.get(resultado, 0) + 1

    # Acierto: celdas con impacto o hundido sobre todas las celdas disparadas.
    aciertos = datos["impacto"] + datos["hundido"]
    disparadas = aciertos + datos["agua"] + datos["repetido"]
    datos["disparadas"] = disparadas

    # Sin celdas disparadas no se puede dividir: el acierto es 0.
    if disparadas == 0:
        datos["acierto"] = 0.0
    else:
        datos["acierto"] = round(aciertos / disparadas * 100, 1)

    return datos


def resumen(historial: list, jugadores: list[str], ganador: str | None) -> str:
    """Recibe el historial, los nombres de los jugadores y el ganador (o None si no hubo);
    devuelve el texto del resumen de la partida con las estadisticas de cada jugador."""
    texto = "===== RESUMEN DE LA PARTIDA =====\n"
    texto += f"Turnos jugados: {len(historial)}\n"

    # Puede no haber ganador, por ejemplo si la partida se guardo antes de terminar.
    if ganador is not None:
        texto += f"Ganador: {ganador}\n"

    # Un bloque con las estadisticas de cada jugador.
    for jugador in jugadores:
        datos = estadisticas(historial, jugador)

        texto += f"\n--- {jugador} ---\n"
        texto += f"Jugadas: {datos['jugadas']}\n"
        texto += (
            f"Celdas disparadas: {datos['disparadas']} "
            f"(agua {datos['agua']}, impacto {datos['impacto']}, "
            f"hundido {datos['hundido']}, repetido {datos['repetido']})\n"
        )
        texto += f"Naves hundidas: {datos['hundido']}\n"
        texto += f"Acierto: {datos['acierto']} %\n"

    return texto


def _leer_partidas() -> dict:
    """Lee las partidas guardadas y devuelve un diccionario.
    Lanza ErrorCubo si no se puede leer o el contenido no es valido."""
    try:
        with open("datos/partidas.json", "r", encoding="utf-8") as archivo:
            partidas = json.load(archivo)

    except FileNotFoundError:
        # Antes del primer guardado todavia no existe el archivo.
        partidas = {}

    except (ValueError, UnicodeError):
        raise ErrorCubo("El archivo de partidas no contiene datos validos.")

    except OSError:
        raise ErrorCubo("No se pudo leer el archivo de partidas.")

    if not isinstance(partidas, dict):
        raise ErrorCubo("El archivo de partidas debe contener un diccionario.")

    return partidas

def guardar_partida(estado: dict, nombre: str) -> None:
    """Guarda la partida.
    Lanza ErrorCubo si el nombre no es valido o no se puede guardar."""
    if re.fullmatch(r"[a-zA-Z0-9_-]{1,30}", nombre) is None:
        raise ErrorCubo(
            "Use de 1 a 30 letras sin acentos, numeros, guion o guion bajo."
        )

    partidas = _leer_partidas()

    # Preparar los datos sin modificar la partida en memoria.
    datos = dict(estado)
    datos["jugadores"] = []
    datos["historial"] = []

    for jugador in estado["jugadores"]:
        jugador_guardado = dict(jugador)
        jugador_guardado["flota"] = []

        for nave in jugador["flota"]:
            nave_guardada = dict(nave)

            nave_guardada["puntos"] = list(nave["puntos"])

            # Guardar cada punto junto a su cantidad de impactos.
            impactos = []

            for punto, cantidad in nave["impactos"].items():
                impactos.append([punto, cantidad])

            nave_guardada["impactos"] = impactos
            jugador_guardado["flota"].append(nave_guardada)

        datos["jugadores"].append(jugador_guardado)

    for jugada in estado["historial"]:
        jugada_guardada = dict(jugada)
        resultados = []

        for punto, resultado in jugada["resultados"].items():
            resultados.append([punto, resultado])

        jugada_guardada["resultados"] = resultados
        datos["historial"].append(jugada_guardada)

    # Si el nombre existe actualiza esa partida.
    partidas[nombre] = datos

    try:
        # Convertir antes de abrir el archivo para escribir.
        texto = json.dumps(partidas, indent=4)

        with open("datos/partidas.json", "w", encoding="utf-8") as archivo:
            archivo.write(texto)

    except (TypeError, ValueError):
        raise ErrorCubo("La partida contiene datos que no se pueden guardar.")

    except OSError:
        raise ErrorCubo(
            "No se pudo guardar. Compruebe que exista la carpeta datos."
        )


def cargar_partida(nombre: str) -> dict:
    """Recupera una partida y reconstruye sus conjuntos y tuplas."""
    partidas = _leer_partidas()

    if nombre not in partidas:
        raise ErrorCubo("No existe una partida con ese nombre.")
    estado = partidas[nombre]

    try:
        if len(estado["jugadores"]) != 2 or estado["turno"] not in (0, 1):
            raise ErrorCubo("Los jugadores o el turno guardado no son validos.")

        for jugador in estado["jugadores"]:
            if len(jugador["cubo"]) == 0 or len(jugador["flota"]) == 0:
                raise ErrorCubo("El cubo o la flota estan vacios.")

            for nave in jugador["flota"]:
                # Recupera el conjunto de puntos de la nave.
                puntos = set()

                for punto in nave["puntos"]:
                    puntos.add(tuple(punto))

                nave["puntos"] = puntos
                # Recupera el diccionario de impactos.
                impactos = {}

                for punto, cantidad in nave["impactos"]:
                    impactos[tuple(punto)] = cantidad
                nave["impactos"] = impactos

        for jugada in estado["historial"]:
            if jugada["punto"] is not None:
                jugada["punto"] = tuple(jugada["punto"])
            resultados = {}

            for punto, resultado in jugada["resultados"]:
                resultados[tuple(punto)] = resultado
            jugada["resultados"] = resultados

    except (KeyError, TypeError, ValueError):
        raise ErrorCubo("La partida tiene datos incompletos o invalidos.")
    return estado

def listar_partidas() -> list[str]:
    """Devuelve los nombres de las partidas guardadas"""
    partidas = _leer_partidas()
    nombres = list(partidas)
    nombres.sort()

    return nombres