"""Estadísticas para el administrador (responsable de bienestar)."""
from datetime import date, datetime, timedelta

from modelos import EstadoAnimo


class ReporteAnimo:
    """Calcula estadísticas con los registros guardados.

    periodo: "hoy", "semana" o "todo".
    """

    def __init__(self, repositorio, area=None, periodo="todo"):
        self._registros = repositorio.listar_registros(
            area=area, desde=self._inicio_periodo(periodo)
        )

    @staticmethod
    def _inicio_periodo(periodo):
        medianoche = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if periodo == "hoy":
            return medianoche
        if periodo == "semana":
            return medianoche - timedelta(days=medianoche.weekday())
        return None

    def registros(self):
        return list(self._registros)

    def total(self):
        return len(self._registros)

    def empleados_distintos(self):
        return len({registro.empleado.id for registro in self._registros})

    def contar_por_estado(self):
        """Diccionario {nombre del estado: cantidad}, con los cinco estados siempre presentes."""
        conteo = {estado.nombre: 0 for estado in EstadoAnimo.todos()}
        for registro in self._registros:
            conteo[registro.estado.nombre] += 1
        return conteo

    def porcentaje_por_estado(self):
        """Diccionario {nombre del estado: porcentaje del total}."""
        total = self.total()
        conteo = self.contar_por_estado()
        return {nombre: (100 * n / total if total else 0) for nombre, n in conteo.items()}

    def estado_mas_frecuente(self):
        """Nombre del estado más repetido, o None si todavía no hay registros."""
        if not self._registros:
            return None
        conteo = self.contar_por_estado()
        return max(conteo, key=conteo.get)

    def total_positivos(self):
        return sum(1 for registro in self._registros if registro.estado.es_positivo)

    def porcentaje_positivo(self):
        total = self.total()
        return 100 * self.total_positivos() / total if total else 0

    def conteo_por_area(self):
        """Diccionario {área: {estado: cantidad}}."""
        datos = {}
        for registro in self._registros:
            area = registro.empleado.area
            if area not in datos:
                datos[area] = {estado.nombre: 0 for estado in EstadoAnimo.todos()}
            datos[area][registro.estado.nombre] += 1
        return datos

    def registros_por_dia(self, dias=7):
        """Lista de (fecha, positivos, requieren atención) de los últimos `dias` días."""
        hoy = date.today()
        serie = []
        for atras in range(dias - 1, -1, -1):
            dia = hoy - timedelta(days=atras)
            del_dia = [r for r in self._registros if r.fecha_hora.date() == dia]
            positivos = sum(1 for r in del_dia if r.estado.es_positivo)
            serie.append((dia, positivos, len(del_dia) - positivos))
        return serie
