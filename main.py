"""Programa principal: ejecute `python main.py` desde esta carpeta."""
from config_bd import crear_repositorio
from interfaz import Aplicacion


def main():
    Aplicacion(crear_repositorio()).mainloop()


if __name__ == "__main__":
    main()
