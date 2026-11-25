"""Clases del modelo del proyecto "Registro del estado de ánimo de los empleados".

Aquí se aplican los pilares de la POO:
- Encapsulamiento: atributos privados (con guion bajo) y acceso mediante propiedades.
- Herencia: Feliz, Triste, Tranquilo, Enojado y Ansioso heredan de EstadoAnimo.
- Polimorfismo: cada estado redefine recomendacion() y _dibujar_rasgos().
- Abstracción: la pantalla solo pide "dibuja tu carita"; no sabe cómo se dibuja cada una.
"""
from abc import ABC, abstractmethod
from datetime import datetime

COLOR_LINEA = "#2d2d2d"
COLOR_LAGRIMA = "#3b8be8"


class EstadoAnimo(ABC):
    """Clase padre (abstracta) de los cinco estados de ánimo."""

    def __init__(self, nombre, color, positivo):
        self._nombre = nombre
        self._color = color
        self._positivo = positivo

    @property
    def nombre(self):
        return self._nombre

    @property
    def es_positivo(self):
        """True para los estados de ánimo positivos (feliz, tranquilo)."""
        return self._positivo

    @property
    def color(self):
        return self._color

    @abstractmethod
    def recomendacion(self):
        """Mensaje que se le muestra al empleado según su estado."""

    @abstractmethod
    def _dibujar_rasgos(self, lienzo, cx, cy, r, grosor):
        """Dibuja ojos, cejas y boca propios de cada estado."""

    def dibujar_carita(self, lienzo, cx, cy, r):
        """Dibuja la carita completa en un Canvas de tkinter."""
        grosor = max(2, int(r * 0.07))
        lienzo.create_oval(cx - r, cy - r, cx + r, cy + r,
                           fill=self._color, outline=COLOR_LINEA, width=grosor)
        self._dibujar_rasgos(lienzo, cx, cy, r, grosor)

    @staticmethod
    def _ojos(lienzo, cx, cy, r):
        for signo in (-1, 1):
            x, y, radio = cx + signo * 0.35 * r, cy - 0.2 * r, 0.09 * r
            lienzo.create_oval(x - radio, y - radio, x + radio, y + radio,
                               fill=COLOR_LINEA, outline="")

    @staticmethod
    def todos():
        """Lista con los cinco estados, en el orden de la cartelera."""
        return [Feliz(), Triste(), Tranquilo(), Enojado(), Ansioso()]

    @staticmethod
    def desde_nombre(nombre):
        """Devuelve el objeto de estado que corresponde a un nombre guardado."""
        for estado in EstadoAnimo.todos():
            if estado.nombre == nombre:
                return estado
        raise ValueError(f"Estado de ánimo desconocido: {nombre}")


class Feliz(EstadoAnimo):
    def __init__(self):
        super().__init__("Feliz", "#FFD93D", True)

    def recomendacion(self):
        return "¡Qué bueno! Aprovecha esa energía para empezar el día con ánimo."

    def _dibujar_rasgos(self, lienzo, cx, cy, r, grosor):
        self._ojos(lienzo, cx, cy, r)
        lienzo.create_arc(cx - 0.5 * r, cy - 0.1 * r, cx + 0.5 * r, cy + 0.6 * r,
                          start=200, extent=140, style="arc",
                          outline=COLOR_LINEA, width=grosor + 1)


class Triste(EstadoAnimo):
    def __init__(self):
        super().__init__("Triste", "#74B9FF", False)

    def recomendacion(self):
        return ("Está bien no sentirse bien. Si lo necesitas, habla con alguien "
                "de confianza o con el área de bienestar.")

    def _dibujar_rasgos(self, lienzo, cx, cy, r, grosor):
        self._ojos(lienzo, cx, cy, r)
        lienzo.create_arc(cx - 0.45 * r, cy + 0.3 * r, cx + 0.45 * r, cy + 0.9 * r,
                          start=30, extent=120, style="arc",
                          outline=COLOR_LINEA, width=grosor + 1)
        x = cx + 0.35 * r
        lienzo.create_oval(x - 0.06 * r, cy - 0.05 * r, x + 0.06 * r, cy + 0.22 * r,
                           fill=COLOR_LAGRIMA, outline="")


class Tranquilo(EstadoAnimo):
    def __init__(self):
        super().__init__("Tranquilo", "#A8E6A1", True)

    def recomendacion(self):
        return "Excelente, es un buen estado para concentrarte. ¡Que tengas un buen día!"

    def _dibujar_rasgos(self, lienzo, cx, cy, r, grosor):
        self._ojos(lienzo, cx, cy, r)
        lienzo.create_line(cx - 0.4 * r, cy + 0.4 * r, cx + 0.4 * r, cy + 0.4 * r,
                           fill=COLOR_LINEA, width=grosor + 1, capstyle="round")


class Enojado(EstadoAnimo):
    def __init__(self):
        super().__init__("Enojado", "#FF7B7B", False)

    def recomendacion(self):
        return ("Respira profundo unos segundos antes de empezar. Si algo te molesta, "
                "puedes hablarlo con tu jefe o con bienestar.")

    def _dibujar_rasgos(self, lienzo, cx, cy, r, grosor):
        self._ojos(lienzo, cx, cy, r)
        for signo in (-1, 1):
            lienzo.create_line(cx + signo * 0.6 * r, cy - 0.58 * r,
                               cx + signo * 0.15 * r, cy - 0.36 * r,
                               fill=COLOR_LINEA, width=grosor + 1, capstyle="round")
        lienzo.create_arc(cx - 0.4 * r, cy + 0.35 * r, cx + 0.4 * r, cy + 0.85 * r,
                          start=30, extent=120, style="arc",
                          outline=COLOR_LINEA, width=grosor + 1)


class Ansioso(EstadoAnimo):
    def __init__(self):
        super().__init__("Ansioso", "#D6B4F7", False)

    def recomendacion(self):
        return "Tómate 5 minutos para respirar antes de empezar."

    def _dibujar_rasgos(self, lienzo, cx, cy, r, grosor):
        self._ojos(lienzo, cx, cy, r)
        for signo in (-1, 1):
            lienzo.create_line(cx + signo * 0.6 * r, cy - 0.34 * r,
                               cx + signo * 0.15 * r, cy - 0.56 * r,
                               fill=COLOR_LINEA, width=grosor, capstyle="round")
        puntos = [(-0.4, 0.45), (-0.2, 0.36), (0.0, 0.5), (0.2, 0.36), (0.4, 0.45)]
        coordenadas = []
        for dx, dy in puntos:
            coordenadas += [cx + dx * r, cy + dy * r]
        lienzo.create_line(*coordenadas, smooth=True, fill=COLOR_LINEA, width=grosor + 1)
        x, y = cx + 0.62 * r, cy - 0.4 * r
        lienzo.create_oval(x - 0.06 * r, y - 0.1 * r, x + 0.06 * r, y + 0.12 * r,
                           fill=COLOR_LAGRIMA, outline="")


class Administrador:
    """Único usuario que puede ver los reportes estadísticos."""

    def __init__(self, usuario, nombre):
        self._usuario = usuario
        self._nombre = nombre

    @property
    def usuario(self):
        return self._usuario

    @property
    def nombre(self):
        return self._nombre


class Empleado:
    """Trabajador de la empresa."""

    def __init__(self, id_empleado, nombre, area):
        self._id = str(id_empleado)
        self._nombre = nombre
        self._area = area

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @property
    def area(self):
        return self._area


class RegistroAnimo:
    """Une al empleado, el estado elegido y la fecha y hora. Una vez creado no se modifica."""

    def __init__(self, empleado, estado, fecha_hora=None, id_registro=None):
        self._empleado = empleado
        self._estado = estado
        self._fecha_hora = fecha_hora or datetime.now().replace(microsecond=0)
        self._id = id_registro

    @property
    def empleado(self):
        return self._empleado

    @property
    def estado(self):
        return self._estado

    @property
    def fecha_hora(self):
        return self._fecha_hora

    @property
    def id(self):
        return self._id

    def asignar_id(self, id_registro):
        """La base de datos asigna el id una sola vez, al guardar."""
        if self._id is None:
            self._id = id_registro


class Sesion:
    """Controla que el empleado haya registrado su ánimo antes de entrar al software."""

    def __init__(self, empleado, repositorio):
        self._empleado = empleado
        self._repositorio = repositorio
        self._activa = False

    @property
    def empleado(self):
        return self._empleado

    def registrar_estado(self, estado):
        """Crea el registro, lo guarda en la base de datos y habilita el acceso."""
        registro = RegistroAnimo(self._empleado, estado)
        registro.asignar_id(self._repositorio.guardar_registro(registro))
        self._activa = True
        return registro

    def permitir_acceso(self):
        return self._activa
