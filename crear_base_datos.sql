-- Base de datos del proyecto "Registro del estado de ánimo de los empleados".
-- En MySQL Workbench: File > Open SQL Script, elija este archivo y presione el rayo (Execute).
-- Es opcional: el programa también crea la base y las tablas solo al ejecutarse.

CREATE DATABASE IF NOT EXISTS estado_animo
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE estado_animo;

CREATE TABLE IF NOT EXISTS empleados (
  id      VARCHAR(30)  PRIMARY KEY,
  nombre  VARCHAR(120) NOT NULL,
  area    VARCHAR(60)  NOT NULL
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS registros (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  empleado_id  VARCHAR(30) NOT NULL,
  estado       VARCHAR(20) NOT NULL,
  fecha_hora   DATETIME    NOT NULL,
  INDEX idx_registros_fecha (fecha_hora),
  CONSTRAINT fk_registro_empleado FOREIGN KEY (empleado_id) REFERENCES empleados (id)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS administradores (
  usuario     VARCHAR(40)  PRIMARY KEY,
  nombre      VARCHAR(120) NOT NULL,
  sal         VARCHAR(32)  NOT NULL,
  clave_hash  VARCHAR(64)  NOT NULL
) ENGINE = InnoDB;

-- Vista práctica: cada registro con los datos del empleado.
CREATE OR REPLACE VIEW vista_registros AS
SELECT r.id AS n, e.id AS documento, e.nombre, e.area, r.estado, r.fecha_hora
FROM registros r JOIN empleados e ON e.id = r.empleado_id;
