import time

from tablero import leer_celda

def armar_metricas(comparaciones, inicio):
    """arma el diccionario de metricas de una corrida de busqueda"""
    tiempo_ms = (time.perf_counter() - inicio) * 1000
    return {
        "comparaciones": comparaciones,
        "tiempo_ms": round(tiempo_ms, 4),
        "profundidad_max": 0,  
    }


def busqueda_lineal(cubo, estado):
    "localiza la primera celda del cubo que tiene un estado
    recorriendolo con ciclos for (z, x, y)"

    comparaciones = 0
    inicio = time.perf_counter()
    tamaño = len(cubo)
    for z in range(1, tamano + 1):
        for x in range(1, tamano + 1):
            for y in range(1, tamano + 1):
                comparaciones += 1
                if leer_celda(cubo, (z, x, y)) == estado:
                    return (z, x, y), armar_metricas(comparaciones, inicio)
    return None, armar_metricas(comparaciones, inicio)
  "punto (tuple o None): (z, x, y) con ejes de 1 a N de la primera celda encontrada, o None si ninguna celda tiene ese estado"
