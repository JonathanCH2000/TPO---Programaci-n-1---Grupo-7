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
    puntos_vecinos,
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
) -> dict[tuple[int, int, int], str] | None:
    """Recibe el cubo, la flota del rival y un punto; dispara solo a esa celda.
    Devuelve un diccionario punto -> resultado."""
    # El punto apuntado esta fuera del cubo.
    if not punto_valido(cubo, punto):
        return None

    # El torpedo afecta solo la celda objetivo.
    return {punto: _disparar_celda(cubo, flota, punto)}


def misil_racimo(
    cubo: list, flota: list, punto: tuple
) -> dict[tuple[int, int, int], str] | None:
    """Recibe el cubo, la flota del rival y un punto; dispara a la celda y
    a sus seis vecinos ortogonales. Devuelve un diccionario punto -> resultado."""
    # El punto esta fuera del cubo.
    if not punto_valido(cubo, punto):
        return None

    # La celda y sus vecinos ortogonales que quedan dentro del cubo.
    celdas = [punto] + puntos_vecinos(cubo, punto)
    resultados = {}

    # Disparar a cada celda y guardar su resultado.
    for celda in celdas:
        resultados[celda] = _disparar_celda(cubo, flota, celda)

    return resultados


def carga_profundidad(
    cubo: list, flota: list, punto: tuple
) -> dict[tuple[int, int, int], str] | None:
    """Recibe el cubo, la flota del rival y un punto; dispara a toda la recta sobre
    el eje z que pasa por ese punto. Devuelve un diccionario punto -> resultado."""
    # El punto esta fuera del cubo.
    if not punto_valido(cubo, punto):
        return None

    # Solo importan el x y el y del punto: la carga recorre todos los z.
    _, x, y = punto
    resultados = {}

    # Disparar a la celda de ese x e y en cada capa de z, de la 1 a la N.
    for z in range(1, len(cubo) + 1):
        celda = (z, x, y)
        resultados[celda] = _disparar_celda(cubo, flota, celda)

    return resultados


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
