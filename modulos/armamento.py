from modulos.errores import ErrorJugada, ErrorMunicion
from modulos.flota import (
    buscar_nave,
    celda_destruida,
    nave_hundida,
    registrar_impacto,
)
from modulos.radar import sonar
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

# Tipos de nave que el barrido laser no alcanza.
NAVES_INMUNES_LASER = {"S"}


def crear_municion() -> dict[str, int | str]:
    """Devuelve la municion inicial de un jugador: un diccionario letra del arma -> municion."""
    municion = {}

    # Cada arma arranca con la municion que indica el catalogo.
    for letra, _, cantidad in CATALOGO_ARMAS:
        municion[letra] = cantidad

    return municion


def usar_municion(municion: dict, letra: str) -> dict[str, int | str]:
    """Recibe la municion de un jugador y la letra de un arma; descuenta
    un uso y devuelve la municion actualizada.
    Lanza ErrorMunicion si el arma no existe o si ya no le queda municion."""
    if letra not in municion:
        raise ErrorMunicion("El arma no existe.")

    # Las armas con municion ilimitada (el torpedo) no gastan nada.
    if municion[letra] == "ilimitada":
        return municion

    if municion[letra] == 0:
        raise ErrorMunicion("No queda municion de esa arma.")

    # Se uso una municion, reducir cantidad.
    municion[letra] -= 1
    return municion


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


def barrido_laser(
    cubo: list, flota: list, punto: tuple, eje: str
) -> dict[tuple[int, int, int], str] | None:
    """Recibe el cubo, la flota del rival, un punto y un eje ("x" o "y"); dispara a toda
    la recta sobre ese eje que pasa por el punto. Devuelve un diccionario punto -> resultado."""
    # Posicion de cada eje dentro del punto (z, x, y).
    posiciones = {"x": 1, "y": 2}

    # El punto esta fuera del cubo o el eje no es x ni y.
    if not punto_valido(cubo, punto) or eje not in posiciones:
        return None

    posicion = posiciones[eje]
    resultados = {}

    # Recorrer el eje elegido de 1 a N, dejando fijos los otros dos valores del punto.
    for valor in range(1, len(cubo) + 1):
        celda = list(punto)
        celda[posicion] = valor
        celda = tuple(celda)

        # El laser pasa de largo por las celdas de las naves inmunes, sin tocarlas.
        nave = buscar_nave(flota, celda)
        if nave is not None and nave["tipo"] in NAVES_INMUNES_LASER:
            continue

        resultados[celda] = _disparar_celda(cubo, flota, celda)

    return resultados


def disparar(cubo: list, flota: list, jugada: dict) -> dict[tuple[int, int, int], str]:
    """Recibe el cubo y la flota del rival y una jugada (arma, punto, eje y valor);
    usa el arma elegida y devuelve un diccionario punto -> resultado.
    Lanza ErrorJugada si el arma no esta disponible o el objetivo no es valido."""
    if jugada["arma"] not in ARMAS:
        raise ErrorJugada("Esa arma no esta disponible.")

    # Buscar la funcion del arma en el diccionario y usarla.
    usar_arma = ARMAS[jugada["arma"]]
    resultados = usar_arma(cubo, flota, jugada)

    if resultados is None:
        raise ErrorJugada("El objetivo no es valido.")

    return resultados


# Adaptadores: cada arma recibe datos distintos, pero todos estos reciben lo mismo
# (cubo, flota, jugada) para poder guardarlos juntos en el diccionario ARMAS.
def _usar_torpedo(cubo: list, flota: list, jugada: dict) -> dict | None:
    """Usa el torpedo sobre el punto de la jugada."""
    return torpedo(cubo, flota, jugada["punto"])


def _usar_racimo(cubo: list, flota: list, jugada: dict) -> dict | None:
    """Usa el misil de racimo sobre el punto de la jugada."""
    return misil_racimo(cubo, flota, jugada["punto"])


def _usar_carga(cubo: list, flota: list, jugada: dict) -> dict | None:
    """Usa la carga de profundidad sobre el punto de la jugada."""
    return carga_profundidad(cubo, flota, jugada["punto"])


def _usar_laser(cubo: list, flota: list, jugada: dict) -> dict | None:
    """Usa el barrido laser sobre el punto y el eje de la jugada."""
    return barrido_laser(cubo, flota, jugada["punto"], jugada["eje"])


def _usar_sonar(cubo: list, flota: list, jugada: dict) -> dict | None:
    """Usa el sonar sobre el plano (eje y valor) de la jugada. Cada celda detectada
    queda con el resultado "detectado", para tener el mismo formato que las demas armas."""
    detectados = sonar(cubo, jugada["eje"], jugada["valor"])

    # El eje o el valor no son validos.
    if detectados is None:
        return None

    resultados = {}
    for punto in detectados:
        resultados[punto] = "detectado"

    return resultados


# Letra del arma -> funcion que la usa. La onda expansiva (O) y el torpedo guiado (G)
# se agregan en la entrega 3.
ARMAS = {
    "T": _usar_torpedo,
    "R": _usar_racimo,
    "C": _usar_carga,
    "L": _usar_laser,
    "S": _usar_sonar,
}


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
