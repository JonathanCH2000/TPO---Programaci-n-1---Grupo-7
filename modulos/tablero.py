AGUA = 0
NAVE = 1
AGUA_MARCADA = 2
IMPACTO = 3
HUNDIDO = 4
DETECTADO = 5


def crear_cubo(tamano=8):
    """Recibe el tamano y devuelve un cubo con todas sus celdas en agua."""
    cubo = []

    for z in range(tamano):
        capa = []

        for x in range(tamano):
            fila = []

            for y in range(tamano):
                fila.append(AGUA)

            capa.append(fila)

        cubo.append(capa)

    return cubo


def punto_valido(cubo, punto):
    """Recibe un cubo y un punto; devuelve True si esta dentro del cubo."""
    if len(punto) != 3:
        return False

    for numero in punto:
        if numero < 1 or numero > len(cubo):
            return False

    return True


def leer_celda(cubo, punto):
    """Recibe un cubo y un punto valido; devuelve el estado de la celda."""
    z, x, y = punto

    return cubo[z - 1][x - 1][y - 1]


def escribir_celda(cubo, punto, estado):
    """Recibe cubo, punto y estado; modifica la celda y devuelve el cubo."""
    z, x, y = punto
    cubo[z - 1][x - 1][y - 1] = estado

    return cubo


def contar_celdas(cubo, estado):
    """Recibe cubo y estado; devuelve cuantas celdas tienen ese estado."""
    cantidad = 0

    for capa in cubo:
        for fila in capa:
            for celda in fila:
                if celda == estado:
                    cantidad += 1

    return cantidad


def dibujar_capa(cubo, z, mostrar_naves=False):
    """Recibe cubo y z; devuelve el dibujo de esa capa."""
    if z < 1 or z > len(cubo):
        return None

    signos = ["~", "N", "o", "X", "#", "?"]
    capa = cubo[z - 1]
    dibujo = "========= CAPA z = " + str(z) + " =========\n     "

    for x in range(1, len(cubo) + 1):
        dibujo += "x" + str(x) + " "

    dibujo += "\n"

    for y in range(len(cubo)):
        dibujo += "y" + str(y + 1) + "   "

        for x in range(len(cubo)):
            estado = capa[x][y]

            if estado == NAVE and not mostrar_naves:
                estado = AGUA

            dibujo += signos[estado] + "  "

        dibujo += "\n"

    return dibujo
