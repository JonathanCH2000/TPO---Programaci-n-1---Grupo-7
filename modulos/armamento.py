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


def torpedo(cubo, punto):
    """Recibe un cubo y un punto; marca el disparo y devuelve el resultado."""
    if not punto_valido(cubo, punto):
        return None

    estado = leer_celda(cubo, punto)

    if estado == NAVE:
        escribir_celda(cubo, punto, IMPACTO)
        resultado = "impacto"
    elif estado == AGUA:
        escribir_celda(cubo, punto, AGUA_MARCADA)
        resultado = "agua"
    else:
        resultado = "repetido"

    return [punto], resultado
