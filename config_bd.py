"""Configuración de la conexión a MySQL (la base que se consulta desde MySQL Workbench).

Cambie "clave" por la contraseña que le puso a MySQL al instalarlo.
"""
MYSQL = {
    "host": "localhost",
    "puerto": 3306,
    "usuario": "root",
    "clave": "1002540952",
    "base": "estado_animo",
}


def crear_repositorio():
    """Se conecta a MySQL y devuelve el repositorio que guarda y consulta los datos."""
    try:
        from base_datos_mysql import RepositorioMySQL
    except ImportError as error:
        if (error.name or "").startswith("mysql"):
            raise SystemExit("Falta instalar el conector de MySQL. En la terminal escriba:\n"
                             "    python -m pip install mysql-connector-python") from error
        raise SystemExit(f"Falta un archivo del proyecto o tiene un error: {error}\n"
                         "Revise que todos los archivos .py estén en la misma carpeta.") from error
    try:
        return RepositorioMySQL(**MYSQL)
    except Exception as error:  # error de conexión: clave mala, servidor apagado, etc.
        raise SystemExit(
            "No se pudo conectar con MySQL:\n"
            f"    {error}\n\n"
            "Revise que MySQL esté encendido y que el usuario y la clave de config_bd.py "
            "sean los correctos."
        ) from error