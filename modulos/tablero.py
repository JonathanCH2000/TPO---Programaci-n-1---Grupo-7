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


def puntos_vecinos(
    cubo: list, punto: tuple, diagonales: bool = False
) -> list[tuple[int, int, int]]:
    """Recibe cubo, punto y si se cuentan las diagonales; devuelve los puntos vecinos dentro del cubo."""
    z, x, y = punto
    vecinos = []

    # Probar cada combinacion de pasos en z, x e y.
    for paso_z in (-1, 0, 1):
        for paso_x in (-1, 0, 1):
            for paso_y in (-1, 0, 1):
                # Contar en cuantos ejes de movimiento hay para identificar las diagonales.
                ejes_movidos = abs(paso_z) + abs(paso_x) + abs(paso_y)

                # Sin moverse en ningun eje es el mismo punto: no es vecino, ignorar.
                if ejes_movidos == 0:
                    continue

                # Sin diagonales solo valen los que se mueven en un unico eje, osea ejes_movidos == 1.
                if not diagonales and ejes_movidos > 1:
                    continue

                # Calculamos el posible vecino, sumandole al parametro los 3 movimientos de los for loops.
                vecino = (z + paso_z, x + paso_x, y + paso_y)

                # Solo se agregan los vecinos validando que sus puntos sean correctos y no fuera del cubo.
                if punto_valido(cubo, vecino):
                    vecinos.append(vecino)

    return vecinos


def plano_x(cubo: list, x: int) -> list[list[int]] | None:
    """Recibe cubo y x; devuelve el plano de ese x como matriz [z][y]."""
    # El valor de x no existe en el cubo, planos de 1 a N.
    if x < 1 or x > len(cubo):
        return None

    plano = []

    # De cada capa de z, guardamos la fila x de cada una (hacemos una copia para evitar modificar la original).
    for capa in cubo:
        plano.append(list(capa[x - 1]))

    return plano


def plano_y(cubo: list, y: int) -> list[list[int]] | None:
    """Recibe cubo e y; devuelve el plano de esa y como matriz [z][x]."""
    # El valor de y no existe en el cubo, planos de 1 a N.
    if y < 1 or y > len(cubo):
        return None

    plano = []

    # Recorrer cada capa z.
    for capa in cubo:
        linea = []

        # De cada fila de x, nos quedamos solo con la celda de y.
        for fila in capa:
            linea.append(fila[y - 1])

        plano.append(linea)

    return plano


def dibujar_capa(cubo: list, z: int, mostrar_naves: bool = False) -> str | None:
    """Recibe cubo y z; devuelve el dibujo de esa capa."""
    # La capa pedida no esta en el cubo.
    if z < 1 or z > len(cubo):
        return None

    # La capa se guarda como [x][y]: x va en las columnas e y en las filas.
    return _dibujar_plano(cubo[z - 1], f"CAPA z = {z}", "x", "y", mostrar_naves)


def dibujar_plano_x(cubo: list, x: int, mostrar_naves: bool = False) -> str | None:
    """Recibe cubo y x; devuelve el dibujo del plano en x."""
    # Obtenemos el plano x.
    plano = plano_x(cubo, x)

    # El plano pedido no existe en el cubo.
    if plano is None:
        return None

    # El plano x se guarda como [z][y]: z va en las columnas e y en las filas.
    return _dibujar_plano(plano, f"PLANO x = {x}", "z", "y", mostrar_naves)


def dibujar_plano_y(cubo: list, y: int, mostrar_naves: bool = False) -> str | None:
    """Recibe cubo e y ; devuelve el dibujo del plano en y."""
    # Obtenemos el plano x.
    plano = plano_y(cubo, y)

    # El plano pedido no existe en el cubo.
    if plano is None:
        return None

    # El plano x se guarda como [z][x]: z va en las columnas y x en las filas.
    return _dibujar_plano(plano, f"PLANO y = {y}", "z", "x", mostrar_naves)


def _dibujar_plano(
    plano: list, titulo: str, eje_columnas: str, eje_filas: str, mostrar_naves: bool
) -> str:
    """Recibe un plano [columna][fila], su titulo y los nombres de sus ejes; devuelve su dibujo."""
    # Simbolo de cada estado, en el mismo orden que sus numeros (AGUA = 0, NAVE = 1, etc).
    signos = ["~", "N", "o", "X", "#", "?"]
    lado = len(plano)

    # Ancho de cada columna: lo que ocupa la etiqueta mas larga (por ejemplo "x8" o "x10") mas un espacio.
    ancho = len(f"{eje_columnas}{lado}") + 1

    # Ancho del margen izquierdo: lo que ocupa la etiqueta de fila mas larga mas dos espacios.
    margen = len(f"{eje_filas}{lado}") + 2

    # Titulo del plano.
    dibujo = f"========= {titulo} =========\n"

    # Encabezado: dejar libre el margen y escribir las etiquetas de las columnas.
    dibujo += " " * margen

    for columna in range(1, lado + 1):
        etiqueta = f"{eje_columnas}{columna}"

        # Completar con espacios a la derecha hasta el ancho de la columna.
        dibujo += f"{etiqueta:<{ancho}}"

    dibujo += "\n"

    # Una linea por cada fila.
    for fila in range(lado):
        etiqueta = f"{eje_filas}{fila + 1}"

        # Escribir la etiqueta de la fila completando con espacios hasta el ancho del margen.
        dibujo += f"{etiqueta:<{margen}}"

        # Un simbolo por cada columna.
        for columna in range(lado):
            estado = plano[columna][fila]

            # Si no hay que mostrar las naves, se ven como agua.
            if estado == NAVE and not mostrar_naves:
                estado = AGUA

            # Escribir el simbolo con el mismo ancho que las etiquetas, alineado debajo de su columna.
            dibujo += f"{signos[estado]:<{ancho}}"

        dibujo += "\n"

    return dibujo
