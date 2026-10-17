"""Excepciones del juego. Todas heredan de ErrorCubo para poder atraparlos de forma sencilla."""


class ErrorCubo(Exception):
    """Clase base de todos los errores del juego."""


class ErrorUbicacion(ErrorCubo):
    """Se lanza cuando una nave no se puede ubicar en las coordenadas dadas."""
