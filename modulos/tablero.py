# Estados posibles de una celda del cubo.
AGUA = 0
NAVE = 1
AGUA_MARCADA = 2
IMPACTO = 3
HUNDIDO = 4
DETECTADO = 5


def crear_cubo(lado: int = 8) -> list[list[list[int]]]:
    """Recibe el lado del cubo y devuelve un cubo con todas sus celdas en agua."""
    cubo = []

    # Armar cada capa de z.
    for _ in range(lado):
        capa = []

        # Armar cada fila de x dentro de la capa.
        for _ in range(lado):
            fila = []

            # Llenar la fila con celdas de agua, una por cada valor de y.
            for _ in range(lado):
                fila.append(AGUA)

            capa.append(fila)

        cubo.append(capa)

    return cubo


def punto_valido(cubo: list, punto: tuple) -> bool:
    """Recibe un cubo y un punto; devuelve True si esta dentro del cubo."""
    # El punto tiene que tener exactamente tres valores: z, x e y.
    if len(punto) != 3:
        return False

    # Cada valor tiene que estar entre 1 y el lado del cubo.
    for numero in punto:
        if numero < 1 or numero > len(cubo):
            return False

    return True


def leer_celda(cubo: list, punto: tuple) -> int:
    """Recibe un cubo y un punto valido; devuelve el estado de la celda."""
    z, x, y = punto

    # Se resta 1 porque los ejes van de 1 a N y las listas empiezan en 0.
    return cubo[z - 1][x - 1][y - 1]


def escribir_celda(cubo: list, punto: tuple, estado: int) -> list[list[list[int]]]:
    """Recibe cubo, punto y estado; modifica la celda y devuelve el cubo."""
    z, x, y = punto

    # Se resta 1 porque los ejes van de 1 a N y las listas empiezan en 0.
    cubo[z - 1][x - 1][y - 1] = estado

    return cubo


def contar_celdas(cubo: list, estado: int) -> int:
    """Recibe cubo y estado; devuelve cuantas celdas tienen ese estado."""
    cantidad = 0

    # Recorrer todas las celdas del cubo y contar las que tienen ese estado.
    for capa in cubo:
        for fila in capa:
            for celda in fila:
                if celda == estado:
                    cantidad += 1

    return cantidad


def dibujar_capa(cubo: list, z: int, mostrar_naves: bool = False) -> str | None:
    """Recibe cubo y z; devuelve el dibujo de esa capa."""
    # La capa pedida no existe en el cubo.
    if z < 1 or z > len(cubo):
        return None

    # Simbolo de cada estado, en el mismo orden que sus numeros (AGUA = 0, NAVE = 1, ...).
    signos = ["~", "N", "o", "X", "#", "?"]
    capa = cubo[z - 1]
    lado = len(cubo)

    # Ancho de cada columna: lo que ocupa el x mas largo (ej: "x8" o "x10") mas un espacio.
    ancho = len(f"x{lado}") + 1

    # Ancho del margen izquierdo: lo que ocupa el y mas largo (ej: "y8" o "y10") mas dos espacios.
    margen = len(f"y{lado}") + 2

    # Titulo de la capa.
    dibujo = f"========= CAPA z = {z} =========\n"

    # Encabezado: dejar libre el margen y escribir los valores de x.
    dibujo += " " * margen

    for x in range(1, lado + 1):
        etiqueta = f"x{x}"
        # Completar con espacios a la derecha hasta el ancho de la columna.
        dibujo += f"{etiqueta:<{ancho}}"

    dibujo += "\n"

    # Una linea por cada valor de y.
    for y in range(lado):
        etiqueta = f"y{y + 1}"
        dibujo += f"{etiqueta:<{margen}}"

        # Un simbolo por cada valor de x.
        for x in range(lado):
            estado = capa[x][y]

            # Si no hay que mostrar las naves, se ven como agua.
            if estado == NAVE and not mostrar_naves:
                estado = AGUA

            dibujo += f"{signos[estado]:<{ancho}}"

        dibujo += "\n"

    return dibujo
