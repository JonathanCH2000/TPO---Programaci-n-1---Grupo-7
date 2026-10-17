def crear_historial() -> list:
    """Devuelve una lista vacia para guardar las jugadas de la partida."""
    return []


def registrar_jugada(
    historial: list, jugador: str, arma: str, punto: tuple, resultados: dict
) -> list[dict]:
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
    datos = {"jugadas": 0, "agua": 0, "impacto": 0, "hundido": 0, "repetido": 0}

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

    # Sin celdas disparadas no se puede dividir: el acierto es 0.
    if disparadas == 0:
        datos["acierto"] = 0.0
    else:
        datos["acierto"] = round(aciertos / disparadas * 100, 1)

    return datos


def guardar_partida(estado: dict, nombre: str) -> None:
    """estado, nombre → archivo escrito."""
    # TODO: se implementa en otra entrega.
    return None


def cargar_partida(nombre: str) -> dict:
    """nombre → estado, o excepción."""
    # TODO: se implementa en otra entrega.
    return {}


def listar_partidas() -> list[str]:
    """→ nombres de las partidas guardadas."""
    # TODO: se implementa en otra entrega.
    return []
