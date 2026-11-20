from modulos.partida import menu_interactivo


def main() -> None:
    """Punto de partida del juego."""
    try:
        menu_interactivo()
    except (KeyboardInterrupt, EOFError):
        print("\nJuego cerrado.")


if __name__ == "__main__":
    main()
