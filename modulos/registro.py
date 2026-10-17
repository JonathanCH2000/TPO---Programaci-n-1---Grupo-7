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
