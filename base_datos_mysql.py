"""Base de datos MySQL (la que se ve y se consulta desde MySQL Workbench).

Tiene los mismos métodos que RepositorioRegistros (SQLite), así que el resto del
programa funciona igual con cualquiera de las dos.
"""
import hashlib
import hmac
import os
from contextlib import contextmanager

import mysql.connector

from modelos import Administrador, Empleado, EstadoAnimo, RegistroAnimo

# Administrador que se crea la primera vez que se ejecuta el programa.
USUARIO_INICIAL = "admin"
CLAVE_INICIAL = "admin123"


def _calcular_hash(clave, sal):
    """La clave nunca se guarda en texto plano: solo su hash con sal."""
    return hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), sal, 100_000).hex()


class RepositorioMySQL:
    def __init__(self, host="localhost", puerto=3306, usuario="root", clave="",
                 base="estado_animo"):
        self._config = {"host": host, "port": puerto, "user": usuario, "password": clave}
        self._base = base
        self._crear_base_y_tablas()

    # ----- conexión -----
    @contextmanager
    def _conexion(self):
        con = mysql.connector.connect(database=self._base, **self._config)
        try:
            yield con
            con.commit()
        finally:
            con.close()

    @staticmethod
    def _consultar(con, sql, parametros=()):
        cursor = con.cursor()
        cursor.execute(sql, parametros)
        return cursor

    def _crear_base_y_tablas(self):
        # 1) Crear la base de datos si no existe (así no hace falta correr el script a mano)
        con = mysql.connector.connect(**self._config)
        try:
            cursor = con.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{self._base}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            con.commit()
        finally:
            con.close()
        # 2) Crear las tablas
        with self._conexion() as con:
            self._consultar(con,
                "CREATE TABLE IF NOT EXISTS empleados ("
                "id VARCHAR(30) PRIMARY KEY, "
                "nombre VARCHAR(120) NOT NULL, "
                "area VARCHAR(60) NOT NULL) ENGINE=InnoDB")
            self._consultar(con,
                "CREATE TABLE IF NOT EXISTS registros ("
                "id INT AUTO_INCREMENT PRIMARY KEY, "
                "empleado_id VARCHAR(30) NOT NULL, "
                "estado VARCHAR(20) NOT NULL, "
                "fecha_hora DATETIME NOT NULL, "
                "INDEX idx_registros_fecha (fecha_hora), "
                "CONSTRAINT fk_registro_empleado FOREIGN KEY (empleado_id) "
                "REFERENCES empleados(id)) ENGINE=InnoDB")
            self._consultar(con,
                "CREATE TABLE IF NOT EXISTS administradores ("
                "usuario VARCHAR(40) PRIMARY KEY, "
                "nombre VARCHAR(120) NOT NULL, "
                "sal VARCHAR(32) NOT NULL, "
                "clave_hash VARCHAR(64) NOT NULL) ENGINE=InnoDB")
            cantidad = self._consultar(con, "SELECT COUNT(*) FROM administradores").fetchone()[0]
        if cantidad == 0:
            self.crear_administrador(USUARIO_INICIAL, "Administrador", CLAVE_INICIAL)

    # ----- administradores -----
    def crear_administrador(self, usuario, nombre, clave):
        sal = os.urandom(16)
        with self._conexion() as con:
            self._consultar(
                con,
                "REPLACE INTO administradores (usuario, nombre, sal, clave_hash) "
                "VALUES (%s, %s, %s, %s)",
                (usuario, nombre, sal.hex(), _calcular_hash(clave, sal)))

    def verificar_administrador(self, usuario, clave):
        with self._conexion() as con:
            fila = self._consultar(
                con,
                "SELECT usuario, nombre, sal, clave_hash FROM administradores WHERE usuario = %s",
                (usuario,)).fetchone()
        if fila is None:
            return None
        if hmac.compare_digest(_calcular_hash(clave, bytes.fromhex(fila[2])), fila[3]):
            return Administrador(fila[0], fila[1])
        return None

    # ----- empleados y registros -----
    def guardar_empleado(self, empleado):
        with self._conexion() as con:
            self._consultar(
                con,
                "INSERT INTO empleados (id, nombre, area) VALUES (%s, %s, %s) "
                "ON DUPLICATE KEY UPDATE nombre = VALUES(nombre), area = VALUES(area)",
                (empleado.id, empleado.nombre, empleado.area))

    def guardar_registro(self, registro):
        """Guarda la respuesta del empleado y devuelve el id del registro."""
        with self._conexion() as con:
            cursor = self._consultar(
                con,
                "INSERT INTO registros (empleado_id, estado, fecha_hora) VALUES (%s, %s, %s)",
                (registro.empleado.id, registro.estado.nombre, registro.fecha_hora))
            return cursor.lastrowid

    def listar_areas(self):
        with self._conexion() as con:
            filas = self._consultar(
                con, "SELECT DISTINCT area FROM empleados ORDER BY area").fetchall()
        return [fila[0] for fila in filas]

    def resumen_empleados(self):
        """Una fila por empleado: id, nombre, área, cantidad de registros, último estado y fecha."""
        consulta = (
            "SELECT e.id, e.nombre, e.area, COUNT(r.id), "
            "(SELECT estado FROM registros WHERE empleado_id = e.id "
            " ORDER BY fecha_hora DESC, id DESC LIMIT 1), "
            "(SELECT fecha_hora FROM registros WHERE empleado_id = e.id "
            " ORDER BY fecha_hora DESC, id DESC LIMIT 1) "
            "FROM empleados e LEFT JOIN registros r ON r.empleado_id = e.id "
            "GROUP BY e.id, e.nombre, e.area ORDER BY e.nombre"
        )
        with self._conexion() as con:
            filas = self._consultar(con, consulta).fetchall()
        return [(f[0], f[1], f[2], f[3], f[4], f[5].strftime("%Y-%m-%d %H:%M:%S") if f[5] else None)
                for f in filas]

    def listar_registros(self, area=None, desde=None):
        """Devuelve objetos RegistroAnimo, del más antiguo al más reciente."""
        consulta = (
            "SELECT r.id, e.id, e.nombre, e.area, r.estado, r.fecha_hora "
            "FROM registros r JOIN empleados e ON e.id = r.empleado_id WHERE 1 = 1"
        )
        parametros = []
        if area:
            consulta += " AND e.area = %s"
            parametros.append(area)
        if desde:
            consulta += " AND r.fecha_hora >= %s"
            parametros.append(desde)
        consulta += " ORDER BY r.fecha_hora, r.id"
        with self._conexion() as con:
            filas = self._consultar(con, consulta, parametros).fetchall()
        return [
            RegistroAnimo(Empleado(f[1], f[2], f[3]), EstadoAnimo.desde_nombre(f[4]), f[5], f[0])
            for f in filas
        ]