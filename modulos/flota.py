def crear_flota():
    """Devuelve una lista vacia para guardar las naves ubicadas."""
    return []


def datos_nave(tipo):  # temporal para probar
    """Recibe la letra de una nave, devuelve sus datos o None."""
    for datos in CATALOGO:
        if datos[0] == tipo:
            return datos
    return None


def cantidad_ubicada(flota, tipo):  # temporal para probar
    """Recibe flota y tipo; devuelve cuantas naves de ese tipo hay."""
    cantidad = 0

    for nave in flota:
        if nave[0] == tipo:
            cantidad += 1
    return cantidad


def obtener_puntos(tipo, desde, hasta):
    """Recibe tipo y extremos; devuelve sus puntos o None."""
    datos = datos_nave(tipo)

    if datos is None:
        return None

    puntos = []

    if tipo == "E":
        if hasta != (desde[0] + 1, desde[1] + 1, desde[2] + 1):
            return None

        for z in range(desde[0], hasta[0] + 1):
            for x in range(desde[1], hasta[1] + 1):
                for y in range(desde[2], hasta[2] + 1):
                    puntos.append((z, x, y))

    else:
        distintos = 0
        eje = -1

        for i in range(3):
            if desde[i] != hasta[i]:
                distintos += 1
                eje = i

        if distintos != 1:
            return None

        primero = min(desde[eje], hasta[eje])
        ultimo = max(desde[eje], hasta[eje])

        for numero in range(primero, ultimo + 1):
            punto = [desde[0], desde[1], desde[2]]
            punto[eje] = numero
            puntos.append((punto[0], punto[1], punto[2]))

    if len(puntos) != datos[2]:
        return None

    return puntos


def ubicar_nave(cubo, flota, tipo, desde, hasta):  # a completar
    """cubo, flota, nave, punto desde, punto hasta → cubo y flota actualizados, o excepción."""
    if tipo == "F":
        return cubo, flota


def menu_ubicacion_flota(numero):
    """Menu de ubicación de la flota. Ubicacion manual o automática."""
    if numero == 1:
        jugador1 = input("Ingresar el nombre del jugador 1: ")
        print(
            "--- Flota de",
            jugador1,
            "---\n 1 - Ubicacion manual\n 2 - Ubicacio automatica \n",
        )
        opcion = input("Elegir una opción: ")
        if opcion == "1":
            ubicar_flota_manual(flota)

        if opcion == "2":
            ubicacion_automatica()


def ubicacion_automatica():
    """cubo, catálogo, semilla → flota ubicada."""

    pass


def ubicar_flota_manual(flota):
    ocupados = set()

    while sum(flota.values()) > 0:
        impresion_pendientes(flota)
        letra = input("Nave (F/D/S/C/P/E): ").upper()
        ubicacion = input(
            "Desde - Hasta [Plano(z),Coordenadas (x),(y)) - (Plano(z),Coordenadas (x),(y)] : "
        )
        z, x, y = ubicacion.split("-")

        while sum(flota.values()) > 0:
            if flota.get(letra, 0) > 0:
                flota[letra] -= 1
                print("Ubicada.")
            else:
                print("Esa nave no existe o ya no quedan pendientes.")

    pass


def impresion_pendientes(flota):
    """Imprime las naves pendientes de ubicación."""

    texto_pendientes = "Pendientes: "
    for letra, cantidad in flota.items():
        if cantidad > 0:
            texto_pendientes += f"{letra} x{cantidad} "
    print(texto_pendientes)


# Letra, nombre, celdas y cantidad.
CATALOGO = [
    ("F", "Fragata", 2, 3),
    ("D", "Destructor", 3, 2),
    ("S", "Submarino", 3, 2),
    ("C", "Crucero", 4, 1),
    ("P", "Portaaviones", 5, 1),
    ("E", "Estacion orbital", [[[1, 1]], [[1, 1]]], 1),
]


flota = {"F": 3, "D": 2, "S": 2, "C": 1, "P": 1, "E": 1}
