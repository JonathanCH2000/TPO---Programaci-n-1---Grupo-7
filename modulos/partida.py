import re

from modulos.flota import (
    CATALOGO,
    cantidad_ubicada,
    crear_flota,
    datos_nave,
    ubicacion_automatica,
    ubicar_nave,
)
from modulos.tablero import crear_cubo, dibujar_capa


def pedir_opcion(maximo):
    """Recibe el maximo y devuelve una opcion valida del menu."""
    while True:
        texto = input("Opcion: ").strip()

        if re.fullmatch(r"[0-9]+", texto):
            opcion = int(texto)

            if opcion >= 1 and opcion <= maximo:
                return opcion

        print("Opcion invalida.")


def pedir_tramo():
    """Pide dos puntos y los devuelve como tuplas."""
    patron = r"[0-9]+,[0-9]+,[0-9]+-[0-9]+,[0-9]+,[0-9]+"

    while True:
        texto = input("Desde-hasta (z,x,y-z,x,y): ").strip()

        if re.fullmatch(patron, texto):
            partes = texto.split("-")
            inicio = partes[0].split(",")
            final = partes[1].split(",")

            desde = (int(inicio[0]), int(inicio[1]), int(inicio[2]))
            hasta = (int(final[0]), int(final[1]), int(final[2]))

            return desde, hasta

        print("Ejemplo: 3,5,4-3,5,5")


def preparar_jugador(numero, tamano):
    """Recibe numero y tamano; devuelve cubo, flota e historial."""
    cubo = crear_cubo(tamano)
    flota = crear_flota()

    print("--- Jugador", numero, "---")
    print("1 - Ubicacion manual")
    print("2 - Ubicacion automatica")
    opcion = pedir_opcion(2)

    match opcion:
        case 1:
            total = 0

            for datos in CATALOGO:
                total += datos[3]

            while len(flota) < total:
                print("--- Naves pendientes ---")

                for datos in CATALOGO:
                    faltan = datos[3] - cantidad_ubicada(flota, datos[0])
                    print(datos[0], "-", datos[1], "x", faltan)

                tipo = input("Nave: ").strip().upper()

                if datos_nave(tipo) is None:
                    print("Nave invalida.")
                else:
                    desde, hasta = pedir_tramo()
                    resultado = ubicar_nave(cubo, flota, tipo, desde, hasta)

                    if resultado is None:
                        print("No se puede ubicar ahi.")
                    else:
                        print("Nave ubicada.")
        case 2:
            # FIX: Esta funcion no espera ningun parametro, arreglar
            flota = ubicacion_automatica(cubo)

            while flota is None:
                cubo = crear_cubo(tamano)
                # FIX: Esta funcion no espera ningun parametro, arreglar
                flota = ubicacion_automatica(cubo)

    # FIX: Esto nunca se llama, de momento no se ubica ninguna flota
    print("Capa que quiere ver:")
    capa = pedir_opcion(len(cubo))
    print(dibujar_capa(cubo, capa, True))

    return [cubo, flota]


def nueva_partida_1v1(configuracion=8):
    """Recibe el tamano; devuelve el estado inicial de dos jugadores."""
    # Mientras para probar el sub menu y ver el dibujo del estado
    jugador_uno = preparar_jugador(1, configuracion)
    jugador_dos = preparar_jugador(2, configuracion)

    return [jugador_uno, jugador_dos]


def nueva_partida_vs_maquina():
    """Configuración, dificultad → estado inicial de una partida contra la máquina."""
    print("Todavia no esta implementado")
    pass


def nueva_partida_maquina_vs_maquina():
    """Configuración, dificultades → estado inicial de una partida entre dos máquinas."""
    print("Todavia no esta implementado")
    pass


def ejecutar_turno():
    """estado, jugada → estado actualizado."""
    print("Todavia no esta implementado")
    pass


def turno_maquina():
    """Estado → estado actualizado, jugado por la máquina."""
    print("Todavia no esta implementado")
    pass


def hay_ganador():
    """Estado → ganador, o ninguno."""
    print("Todavia no esta implementado")
    pass


def continuar_partida():
    """Sigue una partida previa."""
    # NOTE: No se si esto va aca? Lo pongo porque ya estaba para que no se rompa el codigo
    print("Todavia no esta implementado")
    pass


def menu_interactivo():
    """Muestra el menu principal hasta que se elige salir."""
    while True:
        print("===== OPERACION CUBO =====")
        print("1 - Partida uno contra uno")
        print("2 - Partida uno contra la maquina")
        print("3 - Partida maquina contra maquina")
        print("4 - Continuar una partida")
        print("5 - Salir")
        opcion = pedir_opcion(5)

        match opcion:
            case 1:
                nueva_partida_1v1()
                break
            case 2:
                nueva_partida_vs_maquina()
                break
            case 3:
                nueva_partida_maquina_vs_maquina()
                break
            case 4:
                continuar_partida()
                break
            case 5:
                break
