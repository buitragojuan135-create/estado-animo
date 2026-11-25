-- Consultas básicas para ejecutar en MySQL Workbench (seleccione una y presione el rayo).
USE estado_animo;

-- 1. Empleados registrados
SELECT * FROM empleados;

-- 2. Todos los registros, del más reciente al más antiguo
SELECT * FROM vista_registros ORDER BY fecha_hora DESC;

-- 3. Registros de un empleado (cambie el documento)
SELECT * FROM vista_registros WHERE documento = '1001' ORDER BY fecha_hora DESC;

-- 4. Registros de un estado de ánimo (Feliz, Triste, Tranquilo, Enojado, Ansioso)
SELECT * FROM vista_registros WHERE estado = 'Ansioso' ORDER BY fecha_hora DESC;

-- 5. Registros de un área
SELECT * FROM vista_registros WHERE area = 'Ventas' ORDER BY fecha_hora DESC;

-- 6. Registros de hoy
SELECT * FROM vista_registros WHERE DATE(fecha_hora) = CURDATE() ORDER BY fecha_hora DESC;

-- 7. Cantidad de registros por estado de ánimo
SELECT estado, COUNT(*) AS cantidad FROM registros GROUP BY estado ORDER BY cantidad DESC;

-- 8. Cantidad de registros por área
SELECT area, COUNT(*) AS cantidad FROM vista_registros GROUP BY area ORDER BY cantidad DESC;

-- 9. Último registro de cada empleado
SELECT e.id AS documento, e.nombre, e.area, r.estado, r.fecha_hora
FROM empleados e JOIN registros r ON r.empleado_id = e.id
WHERE r.fecha_hora = (SELECT MAX(r2.fecha_hora) FROM registros r2 WHERE r2.empleado_id = e.id)
ORDER BY e.nombre;

-- 10. Total de registros guardados
SELECT COUNT(*) AS total_registros FROM registros;
