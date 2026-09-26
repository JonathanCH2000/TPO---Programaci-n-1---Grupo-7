# Letra, nombre, celdas y cantidad.
CATALOGO = [
    ("F", "Fragata", 2, 3),
    ("D", "Destructor", 3, 2),
    ("S", "Submarino", 3, 2),
    ("C", "Crucero", 4, 1),
    ("P", "Portaaviones", 5, 1),
    ("E", "Estacion orbital", 8, 1)
]
def crear_flota():
    """Devuelve una lista vacia para guardar las naves ubicadas."""
    return []

def datos_nave(tipo): #temporal para probar
    """Recibe la letra de una nave, devuelve sus datos o None."""
    for datos in CATALOGO:
        if datos[0] == tipo:
            return datos
    return None

def cantidad_ubicada(flota, tipo): # temporal para probar
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

def ubicar_nave(cubo, flota, tipo, desde, hasta): # a completar
    """cubo, flota, nave, punto desde, punto hasta → cubo y flota actualizados, o excepción."""
    return cubo, flota


def ubicacion_automatica():
    """cubo, catálogo, semilla → flota ubicada."""
    pass
