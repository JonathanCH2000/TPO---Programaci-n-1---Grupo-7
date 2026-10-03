from modulos.tablero import (
    AGUA,
    AGUA_MARCADA,
    IMPACTO,
    NAVE,
    escribir_celda,
    leer_celda,
    punto_valido,
)

# Letra, nombre y municion inicial.
CATALOGO_ARMAS = [
    ("T", "Torpedo", "ilimitada"),
    ("R", "Misil de racimo", 3),
    ("C", "Carga de profundidad", 2),
    ("S", "Sonar", 4),
    ("L", "Barrido laser", 2),
    ("O", "Onda expansiva", 1),
    ("G", "Torpedo guiado", 1),
]


def torpedo(cubo: list, punto: tuple) -> tuple[list[tuple[int, int, int]], str] | None:
    """Recibe un cubo y un punto; marca el disparo y devuelve el resultado."""
    # El punto apuntado esta fuera del cubo.
    if not punto_valido(cubo, punto):
        return None

    # Ver que hay en la celda apuntada.
    estado = leer_celda(cubo, punto)

    # Habia una nave: se marca como impacto.
    if estado == NAVE:
        escribir_celda(cubo, punto, IMPACTO)
        resultado = "impacto"

    # Habia agua sin explorar: se marca como agua.
    elif estado == AGUA:
        escribir_celda(cubo, punto, AGUA_MARCADA)
        resultado = "agua"

    # La celda ya habia recibido un disparo antes.
    else:
        resultado = "repetido"

    # Devolver las celdas afectadas (el torpedo afecta solo una) y el resultado.
    return [punto], resultado
