"""Excepciones del juego. Todas heredan de ErrorCubo para poder atraparlos de forma sencilla."""


class ErrorCubo(Exception):
    """Clase base de todos los errores del juego."""


class ErrorUbicacion(ErrorCubo):
    """Se lanza cuando una nave no se puede ubicar en las coordenadas dadas."""


class ErrorMunicion(ErrorCubo):
    """Se lanza cuando se quiere usar un arma que no existe o que no tiene municion."""


class ErrorJugada(ErrorCubo):
    """Se lanza cuando una jugada no se puede hacer: el arma no esta disponible
    o el objetivo esta fuera del cubo."""
