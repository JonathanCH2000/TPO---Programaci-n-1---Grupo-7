from modulos.flota import (
    buscar_nave,
    celda_destruida,
    nave_hundida,
    registrar_impacto,
)
from modulos.tablero import (
    AGUA,
    AGUA_MARCADA,
    HUNDIDO,
    IMPACTO,
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


def torpedo(
    cubo: list, flota: list, punto: tuple
) -> tuple[list[tuple[int, int, int]], str] | None:
    """Recibe el cubo y la flota del rival y un punto; marca el disparo y devuelve el resultado."""
    # El punto apuntado esta fuera del cubo.
    if not punto_valido(cubo, punto):
        return None

    # El torpedo afecta solo la celda apuntada.
    resultado = _disparar_celda(cubo, flota, punto)

    # Devolver las celdas afectadas y el resultado.
    return [punto], resultado


def _disparar_celda(cubo: list, flota: list, punto: tuple) -> str:
    """Recibe el cubo, la flota del rival y un punto valido; dispara a esa celda
    y devuelve el resultado: "agua", "impacto", "hundido" o "repetido"."""
    # Ver que hay en la celda y si alguna nave la ocupa.
    estado = leer_celda(cubo, punto)
    nave = buscar_nave(flota, punto)

    # Hay una nave y esa celda todavia no esta destruida.
    # El portaaviones aguanta dos impactos por celda: se marca como impacto y se le suma el impacto a la nave.
    if nave is not None and not celda_destruida(nave, punto):
        escribir_celda(cubo, punto, IMPACTO)
        registrar_impacto(flota, punto)
        resultado = "impacto"

        # Si con este impacto la nave quedo hundida, todas sus celdas pasan a hundido.
        if nave_hundida(nave):
            for punto_nave in nave["puntos"]:
                escribir_celda(cubo, punto_nave, HUNDIDO)
            resultado = "hundido"

    # Habia agua sin explorar: se marca como agua.
    elif estado == AGUA:
        escribir_celda(cubo, punto, AGUA_MARCADA)
        resultado = "agua"

    # La celda ya habia recibido un disparo antes.
    else:
        resultado = "repetido"

    return resultado
