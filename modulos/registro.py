def crear_historial() -> list:
    """Devuelve una lista vacia para guardar las jugadas de la partida."""
    return []


def registrar_jugada(
    historial: list, jugador: str, arma: str, punto: tuple, resultado: str
) -> list[dict]:
    """Agrega una jugada al final del historial y lo devuelve."""
    # El numero de turno es la cantidad de jugadas que ya hay mas 1.
    numero_turno = len(historial) + 1

    # Guardar los datos de la jugada en un diccionario.
    jugada = {
        "turno": numero_turno,
        "jugador": jugador,
        "arma": arma,
        "punto": punto,
        "resultado": resultado,
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


def guardar_partida():
    """estado, nombre → archivo escrito."""
    pass


def cargar_partida():
    """nombre → estado, o excepción."""
    pass


def listar_partidas():
    """→ nombres de las partidas guardadas."""
    pass
