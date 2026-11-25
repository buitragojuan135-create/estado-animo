"""Interfaz gráfica (tkinter).

Flujo:
- Inicio: el usuario elige entrar como Empleado o como Administrador.
- Empleado: se identifica, elige su carita y entra al software de trabajo.
- Administrador: inicia sesión con usuario y clave y es el único que ve los reportes.
"""
import csv
import sqlite3
import tkinter as tk
from math import ceil
from tkinter import filedialog, messagebox, ttk

from modelos import Empleado, EstadoAnimo, Sesion
from reportes import ReporteAnimo

# ---------- Paleta y medidas ----------
FUENTE = "Segoe UI"
BLANCO = "#FFFFFF"
TEXTO = "#23332B"
GRIS = "#6B7A70"
VERDE = "#2E9E77"
VERDE_OSCURO = "#238262"
AZUL = "#3B6FD4"
AZUL_OSCURO = "#2F5AB0"
NARANJA = "#F0A030"
CLARO = "#F2F8E4"
BORDE = "#D5E3B8"
FONDO = "#EEF5DA"
DEGRADADO_ARRIBA = "#1F8A70"
DEGRADADO_ABAJO = "#CDEB95"
POSITIVO = "#2e9e5b"
ATENCION = "#d64545"
AREAS = ["Ventas", "Soporte", "Contabilidad", "Recursos Humanos", "Sistemas", "Otra"]
PERIODOS = {"Hoy": "hoy", "Esta semana": "semana", "Todo": "todo"}
MARGEN_TARJETA = 22
TOPE_TARJETA = 140


def mezclar(color_a, color_b, t):
    """Mezcla dos colores hexadecimales. t = 0 da color_a y t = 1 da color_b."""
    a = [int(color_a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(color_b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def rect_redondeado(lienzo, x1, y1, x2, y2, r, **opciones):
    """Dibuja un rectángulo con esquinas redondeadas en un Canvas."""
    puntos = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
              x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return lienzo.create_polygon(puntos, smooth=True, **opciones)


class Boton(tk.Canvas):
    """Botón redondeado con efecto al pasar el mouse."""

    def __init__(self, padre, texto, comando, color=VERDE, color_hover=VERDE_OSCURO,
                 texto_color=BLANCO, ancho=300, alto=50, tamano=13, fondo=BLANCO):
        super().__init__(padre, width=ancho, height=alto, bg=fondo,
                         highlightthickness=0, cursor="hand2")
        self._comando = comando
        self._color = color
        self._color_hover = color_hover
        self._activo = True
        self._forma = rect_redondeado(self, 1, 1, ancho - 1, alto - 1, min(22, alto // 2),
                                      fill=color, outline="")
        self._texto = self.create_text(ancho / 2, alto / 2, text=texto, fill=texto_color,
                                       font=(FUENTE, tamano, "bold"))
        self.bind("<Enter>", lambda _e: self._pintar(self._color_hover))
        self.bind("<Leave>", lambda _e: self._pintar(self._color))
        self.bind("<Button-1>", lambda _e: self._comando() if self._activo else None)

    def _pintar(self, color):
        if self._activo:
            self.itemconfig(self._forma, fill=color)

    def desactivar(self):
        self._activo = False
        self.itemconfig(self._forma, fill="#C9D2C6")
        self.itemconfig(self._texto, fill="#8A968D")
        self.config(cursor="arrow")


class BotonSecundario(Boton):
    """Botón discreto para acciones como Volver o Salir."""

    def __init__(self, padre, texto, comando, ancho=300):
        super().__init__(padre, texto, comando, color=CLARO, color_hover=BORDE,
                         texto_color=TEXTO, ancho=ancho, alto=40, tamano=11)


class TarjetaRol(tk.Canvas):
    """Tarjeta grande para elegir cómo ingresar (Empleado o Administrador)."""

    def __init__(self, padre, titulo, detalle, comando, icono, color):
        super().__init__(padre, width=290, height=300, bg=BLANCO,
                         highlightthickness=0, cursor="hand2")
        self._color = color
        self._fondo = rect_redondeado(self, 4, 4, 286, 296, 28, fill=CLARO,
                                      outline=BORDE, width=2)
        if icono == "carita":
            EstadoAnimo.todos()[0].dibujar_carita(self, 145, 100, 56)
        else:
            self._dibujar_grafico(145, 100)
        self.create_text(145, 190, text=titulo, font=(FUENTE, 20, "bold"), fill=TEXTO)
        self.create_text(145, 222, text=detalle, font=(FUENTE, 11), fill=GRIS, width=240)
        rect_redondeado(self, 60, 248, 230, 284, 18, fill=color, outline="")
        self.create_text(145, 266, text="Ingresar", fill=BLANCO, font=(FUENTE, 12, "bold"))
        self.bind("<Enter>", lambda _e: self.itemconfig(self._fondo, fill=BLANCO, outline=color))
        self.bind("<Leave>", lambda _e: self.itemconfig(self._fondo, fill=CLARO, outline=BORDE))
        self.bind("<Button-1>", lambda _e: comando())

    def _dibujar_grafico(self, cx, cy):
        self.create_oval(cx - 56, cy - 56, cx + 56, cy + 56,
                         fill=mezclar(self._color, BLANCO, 0.8), outline="")
        base = cy + 32
        for desplazamiento, alto in ((-28, 26), (-8, 44), (12, 62)):
            self.create_rectangle(cx + desplazamiento, base - alto, cx + desplazamiento + 16,
                                  base, fill=self._color, outline="")


class CaritaOpcion(tk.Canvas):
    """Una de las cinco caritas de la cartelera. Se resalta al pasar el mouse."""

    def __init__(self, padre, estado, comando):
        super().__init__(padre, width=150, height=190, bg=BLANCO,
                         highlightthickness=0, cursor="hand2")
        self._fondo = rect_redondeado(self, 4, 4, 146, 186, 24, fill=BLANCO,
                                      outline=BORDE, width=2)
        estado.dibujar_carita(self, 75, 78, 50)
        self.create_text(75, 158, text=estado.nombre, font=(FUENTE, 14, "bold"), fill=TEXTO)
        self.bind("<Enter>", lambda _e: self.itemconfig(
            self._fondo, fill=mezclar(estado.color, BLANCO, 0.75), outline=estado.color))
        self.bind("<Leave>", lambda _e: self.itemconfig(self._fondo, fill=BLANCO, outline=BORDE))
        self.bind("<Button-1>", lambda _e: comando())


class Aplicacion(tk.Tk):
    """Ventana principal: fondo con degradado, encabezado con caritas y una tarjeta central."""

    def __init__(self, repositorio):
        super().__init__()
        self._repositorio = repositorio
        self.title("¿Cómo se siente hoy?")
        self.geometry("1100x720")
        self.minsize(1000, 700)
        self._configurar_estilos()

        self._lienzo = tk.Canvas(self, highlightthickness=0, bg=DEGRADADO_ARRIBA)
        self._lienzo.pack(fill="both", expand=True)
        self._tarjeta = tk.Frame(self._lienzo, bg=BLANCO)
        self._cuerpo = tk.Frame(self._tarjeta, bg=BLANCO)
        self._cuerpo.pack(padx=40, pady=26)
        self._ventana_tarjeta = self._lienzo.create_window(
            0, TOPE_TARJETA, window=self._tarjeta, anchor="n")
        self._lienzo.bind("<Configure>", self._redibujar_fondo)
        self.mostrar_inicio()

    # ----- aspecto general -----
    def _configurar_estilos(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("TCombobox", fieldbackground=CLARO, background=CLARO,
                         bordercolor=BORDE, arrowcolor=TEXTO, padding=7)
        estilo.configure("TNotebook", background=FONDO, borderwidth=0)
        estilo.configure("TNotebook.Tab", padding=(20, 8), font=(FUENTE, 11, "bold"),
                         background="#DCE9BF", foreground=GRIS)
        estilo.map("TNotebook.Tab", background=[("selected", BLANCO)],
                   foreground=[("selected", VERDE_OSCURO)])
        estilo.configure("Treeview", rowheight=28, font=(FUENTE, 11), fieldbackground=BLANCO)
        estilo.configure("Treeview.Heading", font=(FUENTE, 11, "bold"),
                         background=VERDE, foreground=BLANCO, padding=6)
        estilo.map("Treeview.Heading", background=[("active", VERDE_OSCURO)])

    def _redibujar_fondo(self, _evento=None):
        c = self._lienzo
        ancho, alto = c.winfo_width(), c.winfo_height()
        if ancho < 50 or alto < 50:
            return
        c.delete("fondo")
        for y in range(0, alto, 4):
            c.create_rectangle(0, y, ancho, y + 4, outline="", tags="fondo",
                               fill=mezclar(DEGRADADO_ARRIBA, DEGRADADO_ABAJO, y / alto))
        for x, y, r in ((0.08, 0.15, 150), (0.93, 0.1, 110), (0.88, 0.85, 190), (0.05, 0.9, 120)):
            c.create_oval(ancho * x - r, alto * y - r, ancho * x + r, alto * y + r,
                          fill="white", stipple="gray12", outline="", tags="fondo")
        c.create_text(ancho / 2, 40, text="¿Cómo se siente hoy?", fill=BLANCO,
                      font=(FUENTE, 30, "bold"), tags="fondo")
        for i, estado in enumerate(EstadoAnimo.todos()):
            self._carita_de_fondo(estado, ancho / 2 + (i - 2) * 56, 88, 18)
        c.tag_lower("fondo")
        self._posicionar_tarjeta()

    def _carita_de_fondo(self, estado, x, y, r):
        """Dibuja una carita y la marca como parte del fondo (para poder redibujarla)."""
        c = self._lienzo
        antes = set(c.find_all())
        estado.dibujar_carita(c, x, y, r)
        for item in set(c.find_all()) - antes:
            c.addtag_withtag("fondo", item)

    def _ajustar_tarjeta(self):
        """Se llama al terminar de armar una pantalla: recalcula el tamaño de la tarjeta."""
        self.update_idletasks()
        self._posicionar_tarjeta()

    def _posicionar_tarjeta(self):
        c = self._lienzo
        ancho = c.winfo_width()
        if ancho < 50:
            return
        c.coords(self._ventana_tarjeta, ancho / 2, TOPE_TARJETA)
        c.delete("marco")
        w, h = self._tarjeta.winfo_reqwidth(), self._tarjeta.winfo_reqheight()
        x1, x2 = ancho / 2 - w / 2 - MARGEN_TARJETA, ancho / 2 + w / 2 + MARGEN_TARJETA
        y1, y2 = TOPE_TARJETA - MARGEN_TARJETA, TOPE_TARJETA + h + MARGEN_TARJETA
        rect_redondeado(c, x1 + 2, y1 + 10, x2 + 2, y2 + 10, MARGEN_TARJETA, fill="#0B3D2E",
                        stipple="gray25", outline="", tags="marco")
        rect_redondeado(c, x1, y1, x2, y2, MARGEN_TARJETA, fill=BLANCO, outline="", tags="marco")
        c.tag_raise("marco")
        c.tag_lower("fondo")

    # ----- piezas reutilizables -----
    def _limpiar(self):
        self.unbind("<Return>")
        for widget in self._cuerpo.winfo_children():
            widget.destroy()

    def _titulo_tarjeta(self, titulo, subtitulo=None):
        tk.Label(self._cuerpo, text=titulo, bg=BLANCO, fg=TEXTO,
                 font=(FUENTE, 26, "bold")).pack()
        if subtitulo:
            tk.Label(self._cuerpo, text=subtitulo, bg=BLANCO, fg=GRIS,
                     font=(FUENTE, 13)).pack(pady=(2, 0))

    def _campo(self, etiqueta, variable, secreto=False, valores=None):
        tk.Label(self._cuerpo, text=etiqueta.upper(), bg=BLANCO, fg=GRIS, anchor="w",
                 font=(FUENTE, 9, "bold")).pack(fill="x", pady=(14, 3))
        if valores:
            campo = ttk.Combobox(self._cuerpo, textvariable=variable, values=valores,
                                 font=(FUENTE, 12), width=34)
            campo.pack(fill="x")
        else:
            campo = tk.Entry(self._cuerpo, textvariable=variable, font=(FUENTE, 12),
                             relief="flat", bg=CLARO, fg=TEXTO, width=36,
                             show="•" if secreto else "", highlightthickness=2,
                             highlightbackground=BORDE, highlightcolor=VERDE)
            campo.pack(fill="x", ipady=8)
        return campo

    # ---------- Pantalla de inicio: elegir el tipo de usuario ----------
    def mostrar_inicio(self):
        self._limpiar()
        self._titulo_tarjeta("Bienvenido(a)", "¿Cómo desea ingresar?")
        fila = tk.Frame(self._cuerpo, bg=BLANCO)
        fila.pack(pady=(24, 10))
        TarjetaRol(fila, "Empleado", "Registrar cómo me siento hoy",
                   self.mostrar_identificacion, "carita", VERDE).pack(side="left", padx=16)
        TarjetaRol(fila, "Administrador", "Ver los reportes estadísticos",
                   self.mostrar_login_admin, "grafico", AZUL).pack(side="left", padx=16)
        tk.Label(self._cuerpo, text="Tu bienestar también es parte del trabajo.",
                 bg=BLANCO, fg=GRIS, font=(FUENTE, 11)).pack(pady=(6, 0))
        self._ajustar_tarjeta()

    # ---------- Empleado: identificación ----------
    def mostrar_identificacion(self):
        self._limpiar()
        self._titulo_tarjeta("Identifíquese", "Para empezar su jornada")
        self._var_codigo = tk.StringVar()
        self._var_nombre = tk.StringVar()
        self._var_area = tk.StringVar(value=AREAS[0])
        self._campo("Documento o código", self._var_codigo)
        self._campo("Nombre completo", self._var_nombre)
        self._campo("Área", self._var_area, valores=AREAS)
        Boton(self._cuerpo, "Continuar", self._continuar, ancho=380).pack(pady=(26, 10))
        BotonSecundario(self._cuerpo, "Volver", self.mostrar_inicio, ancho=380).pack()
        self.bind("<Return>", lambda _e: self._continuar())
        self._ajustar_tarjeta()

    def _continuar(self):
        codigo = self._var_codigo.get().strip()
        nombre = self._var_nombre.get().strip()
        area = self._var_area.get().strip()
        if not (codigo and nombre and area):
            messagebox.showwarning("Faltan datos", "Complete todos los campos para continuar.")
            return
        empleado = Empleado(codigo, nombre, area)
        try:
            self._repositorio.guardar_empleado(empleado)
        except sqlite3.Error as error:
            messagebox.showerror("Base de datos", f"No se pudo guardar el empleado:\n{error}")
            return
        self.mostrar_seleccion(Sesion(empleado, self._repositorio))

    # ---------- Empleado: selección de la carita ----------
    def mostrar_seleccion(self, sesion):
        self._limpiar()
        self._titulo_tarjeta(f"Hola, {sesion.empleado.nombre}",
                             "Seleccione cómo se encuentra el día de hoy")
        fila = tk.Frame(self._cuerpo, bg=BLANCO)
        fila.pack(pady=(24, 14))
        for estado in EstadoAnimo.todos():
            CaritaOpcion(fila, estado, lambda est=estado: self._elegir(sesion, est)).pack(
                side="left", padx=8)
        tk.Label(self._cuerpo,
                 text="Con esta información la empresa puede mejorar la calidad de vida del trabajador.",
                 bg=BLANCO, fg=GRIS, font=(FUENTE, 11)).pack()
        self._ajustar_tarjeta()

    def _elegir(self, sesion, estado):
        try:
            registro = sesion.registrar_estado(estado)
        except sqlite3.Error as error:
            messagebox.showerror("Base de datos", f"No se pudo guardar su respuesta:\n{error}")
            return
        self.mostrar_resultado(sesion, registro)

    # ---------- Empleado: la carita de la emoción elegida ----------
    def mostrar_resultado(self, sesion, registro):
        self._limpiar()
        estado = registro.estado
        self._titulo_tarjeta(f"Hoy te sientes {estado.nombre.lower()}")

        lienzo = tk.Canvas(self._cuerpo, width=230, height=230, bg=BLANCO, highlightthickness=0)
        lienzo.pack(pady=(10, 4))
        lienzo.create_oval(6, 6, 224, 224, fill=mezclar(estado.color, BLANCO, 0.65), outline="")
        lienzo.create_oval(26, 26, 204, 204, fill=mezclar(estado.color, BLANCO, 0.35), outline="")
        estado.dibujar_carita(lienzo, 115, 115, 74)

        tk.Label(self._cuerpo, text=estado.recomendacion(), bg=BLANCO, fg=TEXTO,
                 font=(FUENTE, 14), wraplength=560, justify="center").pack(pady=(6, 4))
        tk.Label(self._cuerpo,
                 text=f"Guardado en la base de datos · registro n.º {registro.id} · "
                      f"{registro.fecha_hora:%d/%m/%Y %H:%M}",
                 bg=BLANCO, fg=GRIS, font=(FUENTE, 10)).pack()

        boton = Boton(self._cuerpo, "Entrar al software de trabajo",
                      lambda: self._abrir_software(sesion), ancho=380)
        boton.pack(pady=(16, 8))
        if not sesion.permitir_acceso():
            boton.desactivar()
        BotonSecundario(self._cuerpo, "Salir (siguiente empleado)", self.mostrar_inicio,
                        ancho=380).pack()
        self._ajustar_tarjeta()

    def _abrir_software(self, sesion):
        ventana = tk.Toplevel(self)
        ventana.title("Software de trabajo")
        ventana.geometry("520x240")
        ventana.configure(bg=CLARO)
        tk.Label(ventana, text=f"Bienvenido(a), {sesion.empleado.nombre}", bg=CLARO,
                 fg=TEXTO, font=(FUENTE, 18, "bold")).pack(pady=(50, 10))
        tk.Label(ventana, text="Aquí se abriría el software de trabajo de la empresa.",
                 bg=CLARO, fg=GRIS, font=(FUENTE, 12)).pack()

    # ---------- Administrador: inicio de sesión y panel ----------
    def mostrar_login_admin(self):
        self._limpiar()
        self._titulo_tarjeta("Administrador", "Solo el administrador puede ver los reportes")
        self._var_usuario = tk.StringVar()
        self._var_clave = tk.StringVar()
        self._campo("Usuario", self._var_usuario)
        self._campo("Contraseña", self._var_clave, secreto=True)
        Boton(self._cuerpo, "Ingresar", self._ingresar_admin, color=AZUL,
              color_hover=AZUL_OSCURO, ancho=380).pack(pady=(26, 10))
        BotonSecundario(self._cuerpo, "Volver", self.mostrar_inicio, ancho=380).pack()
        self.bind("<Return>", lambda _e: self._ingresar_admin())
        self._ajustar_tarjeta()

    def _ingresar_admin(self):
        usuario = self._var_usuario.get().strip()
        try:
            admin = self._repositorio.verificar_administrador(usuario, self._var_clave.get())
        except sqlite3.Error as error:
            messagebox.showerror("Base de datos", f"No se pudo verificar el usuario:\n{error}")
            return
        if admin is None:
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.")
            self._var_clave.set("")
            return
        self.mostrar_panel_admin(admin)
        VentanaReportes(self, self._repositorio)

    def mostrar_panel_admin(self, admin):
        self._limpiar()
        avatar = tk.Canvas(self._cuerpo, width=96, height=96, bg=BLANCO, highlightthickness=0)
        avatar.pack()
        avatar.create_oval(4, 4, 92, 92, fill=AZUL, outline="")
        avatar.create_text(48, 48, text=admin.nombre[:1].upper(), fill=BLANCO,
                           font=(FUENTE, 36, "bold"))
        self._titulo_tarjeta("Panel del administrador", f"Hola, {admin.nombre}")
        Boton(self._cuerpo, "Abrir reportes estadísticos",
              lambda: VentanaReportes(self, self._repositorio), color=AZUL,
              color_hover=AZUL_OSCURO, ancho=380).pack(pady=(26, 10))
        BotonSecundario(self._cuerpo, "Cerrar sesión", self.mostrar_inicio, ancho=380).pack()
        self._ajustar_tarjeta()


class VentanaReportes(tk.Toplevel):
    """Reportes estadísticos. Solo se abre después de iniciar sesión como administrador."""

    def __init__(self, maestro, repositorio):
        super().__init__(maestro)
        self.title("Reportes estadísticos del estado de ánimo")
        self.geometry("1120x820")
        self.configure(bg=FONDO)
        self._repositorio = repositorio

        encabezado = tk.Frame(self, bg=DEGRADADO_ARRIBA)
        encabezado.pack(fill="x")
        tk.Label(encabezado, text="Reportes estadísticos", bg=DEGRADADO_ARRIBA, fg=BLANCO,
                 font=(FUENTE, 22, "bold")).pack(side="left", padx=(24, 14), pady=14)
        tk.Label(encabezado, text="Estado de ánimo de los empleados", bg=DEGRADADO_ARRIBA,
                 fg="#D9F0E6", font=(FUENTE, 12)).pack(side="left")
        self._construir_filtros()

        pestanas = ttk.Notebook(self)
        pestanas.pack(fill="both", expand=True, padx=14, pady=(4, 14))
        self._tab_resumen = tk.Frame(pestanas, bg=FONDO)
        self._tab_areas = tk.Frame(pestanas, bg=FONDO)
        self._tab_empleados = tk.Frame(pestanas, bg=FONDO)
        self._tab_registros = tk.Frame(pestanas, bg=FONDO)
        pestanas.add(self._tab_resumen, text="Resumen")
        pestanas.add(self._tab_areas, text="Por área y tendencia")
        pestanas.add(self._tab_empleados, text="Empleados")
        pestanas.add(self._tab_registros, text="Registros")

        self._construir_resumen()
        self._lienzo_areas = self._nuevo_lienzo(self._tab_areas, 1060, 330)
        self._lienzo_tendencia = self._nuevo_lienzo(self._tab_areas, 1060, 300)
        self._tabla_empleados = self._crear_tabla(self._tab_empleados, (
            ("documento", "Documento", 130), ("nombre", "Nombre", 240), ("area", "Área", 150),
            ("registros", "Registros", 100), ("estado", "Último estado", 140),
            ("fecha", "Último registro", 170)))
        self._tabla = self._crear_tabla(self._tab_registros, (
            ("empleado", "Empleado", 260), ("area", "Área", 170),
            ("estado", "Estado", 130), ("fecha", "Fecha y hora", 190)))
        self.actualizar()

    # ----- construcción de la ventana -----
    def _construir_filtros(self):
        filtros = tk.Frame(self, bg=FONDO)
        filtros.pack(pady=12)
        self._var_area = tk.StringVar(value="Todas")
        self._var_periodo = tk.StringVar(value="Todo")
        tk.Label(filtros, text="Área", bg=FONDO, fg=GRIS,
                 font=(FUENTE, 11, "bold")).pack(side="left", padx=4)
        ttk.Combobox(filtros, textvariable=self._var_area, width=18, state="readonly",
                     values=["Todas"] + self._repositorio.listar_areas()).pack(side="left")
        tk.Label(filtros, text="Periodo", bg=FONDO, fg=GRIS,
                 font=(FUENTE, 11, "bold")).pack(side="left", padx=(18, 4))
        ttk.Combobox(filtros, textvariable=self._var_periodo, width=14, state="readonly",
                     values=list(PERIODOS)).pack(side="left")
        Boton(filtros, "Actualizar", self.actualizar, ancho=130, alto=38, tamano=11,
              fondo=FONDO).pack(side="left", padx=(18, 8))
        Boton(filtros, "Exportar a Excel (CSV)", self._exportar_csv, color=AZUL,
              color_hover=AZUL_OSCURO, ancho=210, alto=38, tamano=11, fondo=FONDO).pack(side="left")

    @staticmethod
    def _nuevo_lienzo(padre, ancho, alto, **empaque):
        lienzo = tk.Canvas(padre, width=ancho, height=alto, bg=BLANCO,
                           highlightthickness=1, highlightbackground=BORDE)
        lienzo.pack(**({"pady": 6} | empaque))
        return lienzo

    def _construir_resumen(self):
        indicadores = tk.Frame(self._tab_resumen, bg=FONDO)
        indicadores.pack(fill="x", pady=12)
        self._valores = {}
        for clave, titulo, color in (("total", "Registros", VERDE),
                                     ("empleados", "Empleados", AZUL),
                                     ("frecuente", "Estado más frecuente", NARANJA),
                                     ("positivo", "Ánimo positivo", POSITIVO)):
            tarjeta = tk.Frame(indicadores, bg=BLANCO, highlightbackground=BORDE,
                               highlightthickness=1)
            tarjeta.pack(side="left", expand=True, fill="x", padx=8)
            tk.Frame(tarjeta, bg=color, width=7).pack(side="left", fill="y")
            interior = tk.Frame(tarjeta, bg=BLANCO)
            interior.pack(side="left", fill="both", expand=True, padx=18, pady=10)
            tk.Label(interior, text=titulo, bg=BLANCO, fg=GRIS, font=(FUENTE, 11)).pack()
            valor = tk.Label(interior, bg=BLANCO, fg=TEXTO, font=(FUENTE, 24, "bold"))
            valor.pack()
            self._valores[clave] = valor

        graficos = tk.Frame(self._tab_resumen, bg=FONDO)
        graficos.pack()
        self._lienzo_barras = self._nuevo_lienzo(graficos, 540, 360, side="left", padx=8)
        self._lienzo_dona = self._nuevo_lienzo(graficos, 500, 360, side="left", padx=8)

    @staticmethod
    def _crear_tabla(padre, columnas):
        marco = tk.Frame(padre, bg=FONDO)
        marco.pack(fill="both", expand=True, padx=10, pady=10)
        tabla = ttk.Treeview(marco, columns=[c[0] for c in columnas], show="headings")
        for clave, titulo, ancho in columnas:
            tabla.heading(clave, text=titulo)
            tabla.column(clave, width=ancho)
        barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        return tabla

    # ----- actualización de los datos -----
    def actualizar(self):
        area = None if self._var_area.get() == "Todas" else self._var_area.get()
        reporte = ReporteAnimo(self._repositorio, area, PERIODOS[self._var_periodo.get()])
        conteo = reporte.contar_por_estado()
        total = reporte.total()

        self._valores["total"].config(text=str(total))
        self._valores["empleados"].config(text=str(reporte.empleados_distintos()))
        self._valores["frecuente"].config(text=reporte.estado_mas_frecuente() or "—")
        self._valores["positivo"].config(text=f"{reporte.porcentaje_positivo():.0f} %")

        self._dibujar_barras(conteo, total)
        self._dibujar_dona(conteo, total)
        self._dibujar_areas(reporte.conteo_por_area())
        tendencia = ReporteAnimo(self._repositorio, area, "todo").registros_por_dia(7)
        self._dibujar_tendencia(tendencia)

        self._tabla_empleados.delete(*self._tabla_empleados.get_children())
        for documento, nombre, area_emp, cantidad, ultimo, fecha in self._repositorio.resumen_empleados():
            if area is None or area_emp == area:
                self._tabla_empleados.insert("", "end", values=(
                    documento, nombre, area_emp, cantidad, ultimo or "—",
                    fecha[:16] if fecha else "—"))

        self._tabla.delete(*self._tabla.get_children())
        for registro in reversed(reporte.registros()[-200:]):
            self._tabla.insert("", "end", values=(
                registro.empleado.nombre, registro.empleado.area, registro.estado.nombre,
                f"{registro.fecha_hora:%d/%m/%Y %H:%M}"))

    def _exportar_csv(self):
        """Guarda en un archivo CSV (se abre con Excel) los registros del filtro actual."""
        area = None if self._var_area.get() == "Todas" else self._var_area.get()
        reporte = ReporteAnimo(self._repositorio, area, PERIODOS[self._var_periodo.get()])
        ruta = filedialog.asksaveasfilename(
            parent=self, defaultextension=".csv", initialfile="registros_estado_animo.csv",
            filetypes=[("Archivo CSV", "*.csv")])
        if not ruta:
            return
        try:
            with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
                escritor = csv.writer(archivo, delimiter=";")
                escritor.writerow(["Registro", "Documento", "Empleado", "Área", "Estado", "Fecha y hora"])
                for r in reporte.registros():
                    escritor.writerow([r.id, r.empleado.id, r.empleado.nombre, r.empleado.area,
                                       r.estado.nombre, f"{r.fecha_hora:%d/%m/%Y %H:%M}"])
        except OSError as error:
            messagebox.showerror("Exportar", f"No se pudo guardar el archivo:\n{error}")
            return
        messagebox.showinfo("Exportar", f"Se guardaron {reporte.total()} registros en:\n{ruta}")

    # ----- gráficos -----
    @staticmethod
    def _escala(maximo):
        """Devuelve (paso, tope) para marcar el eje con números enteros."""
        paso = max(1, ceil(maximo / 5))
        return paso, ceil(maximo / paso) * paso

    def _dibujar_barras(self, conteo, total):
        c = self._lienzo_barras
        c.delete("all")
        c.create_text(270, 22, text="Registros por estado de ánimo",
                      font=(FUENTE, 13, "bold"), fill=TEXTO)
        x0, x1, y_base, y_top = 60, 520, 270, 60
        paso, tope = self._escala(max(max(conteo.values()), 1))
        escala = (y_base - y_top) / tope
        for valor in range(0, tope + 1, paso):
            y = y_base - valor * escala
            c.create_line(x0, y, x1, y, fill="#e3e3e3")
            c.create_text(x0 - 8, y, text=str(valor), anchor="e",
                          font=(FUENTE, 10), fill=GRIS)
        c.create_line(x0, y_top, x0, y_base, fill=TEXTO)
        c.create_line(x0, y_base, x1, y_base, fill=TEXTO)

        celda = (x1 - x0) / 5
        for i, estado in enumerate(EstadoAnimo.todos()):
            cx = x0 + celda * (i + 0.5)
            n = conteo[estado.nombre]
            alto = n * escala
            c.create_rectangle(cx - 28, y_base - alto, cx + 28, y_base,
                               fill=estado.color, outline=TEXTO)
            porcentaje = 100 * n / total if total else 0
            c.create_text(cx, y_base - alto - 12, text=f"{n} ({porcentaje:.0f}%)",
                          font=(FUENTE, 10, "bold"), fill=TEXTO)
            estado.dibujar_carita(c, cx, y_base + 30, 16)
            c.create_text(cx, y_base + 60, text=estado.nombre,
                          font=(FUENTE, 10), fill=TEXTO)
        if total == 0:
            c.create_text(270, 160, text="Sin registros para este filtro",
                          font=(FUENTE, 12), fill="#888888")

    def _dibujar_dona(self, conteo, total):
        c = self._lienzo_dona
        c.delete("all")
        c.create_text(250, 22, text="Distribución porcentual",
                      font=(FUENTE, 13, "bold"), fill=TEXTO)
        cx, cy, r = 160, 190, 120
        if total == 0:
            c.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#cccccc", width=2)
            c.create_text(cx, cy, text="Sin datos", font=(FUENTE, 12), fill="#888888")
        else:
            inicio = 90
            for estado in EstadoAnimo.todos():
                n = conteo[estado.nombre]
                if n == 0:
                    continue
                extension = -min(360 * n / total, 359.99)
                c.create_arc(cx - r, cy - r, cx + r, cy + r, start=inicio, extent=extension,
                             fill=estado.color, outline="white", width=2, style="pieslice")
                inicio += extension
            c.create_oval(cx - 62, cy - 62, cx + 62, cy + 62, fill=BLANCO, outline="")
            c.create_text(cx, cy - 8, text=str(total), font=(FUENTE, 24, "bold"), fill=TEXTO)
            c.create_text(cx, cy + 18, text="registros", font=(FUENTE, 10), fill=GRIS)

        for i, estado in enumerate(EstadoAnimo.todos()):
            y = 100 + i * 52
            n = conteo[estado.nombre]
            porcentaje = 100 * n / total if total else 0
            c.create_rectangle(322, y - 8, 338, y + 8, fill=estado.color, outline=TEXTO)
            c.create_text(348, y - 2, text=estado.nombre, anchor="w",
                          font=(FUENTE, 12, "bold"), fill=TEXTO)
            c.create_text(348, y + 16, text=f"{n} registros · {porcentaje:.0f} %", anchor="w",
                          font=(FUENTE, 10), fill=GRIS)

    def _dibujar_areas(self, datos):
        c = self._lienzo_areas
        c.delete("all")
        c.create_text(530, 22, text="Estados de ánimo por área (número de registros)",
                      font=(FUENTE, 13, "bold"), fill=TEXTO)
        for i, estado in enumerate(EstadoAnimo.todos()):
            x = 190 + i * 150
            c.create_rectangle(x, 44, x + 14, 58, fill=estado.color, outline=TEXTO)
            c.create_text(x + 22, 51, text=estado.nombre, anchor="w",
                          font=(FUENTE, 10), fill=TEXTO)
        if not datos:
            c.create_text(530, 170, text="Sin registros para este filtro",
                          font=(FUENTE, 12), fill="#888888")
            return
        maximo = max(sum(estados.values()) for estados in datos.values())
        for i, (area, estados) in enumerate(sorted(datos.items())):
            y = 100 + i * 40
            c.create_text(20, y, text=area, anchor="w", font=(FUENTE, 11, "bold"), fill=TEXTO)
            x = 190
            for estado in EstadoAnimo.todos():
                n = estados[estado.nombre]
                if n == 0:
                    continue
                largo = 700 * n / maximo
                c.create_rectangle(x, y - 14, x + largo, y + 14, fill=estado.color, outline=TEXTO)
                if largo >= 22:
                    c.create_text(x + largo / 2, y, text=str(n),
                                  font=(FUENTE, 10, "bold"), fill=TEXTO)
                x += largo
            c.create_text(x + 10, y, text=f"Total: {sum(estados.values())}", anchor="w",
                          font=(FUENTE, 10), fill=GRIS)

    def _dibujar_tendencia(self, serie):
        c = self._lienzo_tendencia
        c.delete("all")
        c.create_text(530, 22, text="Tendencia de los últimos 7 días (registros por día)",
                      font=(FUENTE, 13, "bold"), fill=TEXTO)
        for x, color, texto in ((70, POSITIVO, "Ánimo positivo (feliz, tranquilo)"),
                                (390, ATENCION, "Requiere atención (triste, enojado, ansioso)")):
            c.create_rectangle(x, 42, x + 14, 56, fill=color, outline="")
            c.create_text(x + 22, 49, text=texto, anchor="w", font=(FUENTE, 10), fill=TEXTO)

        x0, x1, y_base, y_top = 70, 980, 245, 80
        paso, tope = self._escala(max([max(p, n) for _, p, n in serie] + [1]))
        escala = (y_base - y_top) / tope
        for valor in range(0, tope + 1, paso):
            y = y_base - valor * escala
            c.create_line(x0, y, x1, y, fill="#e3e3e3")
            c.create_text(x0 - 8, y, text=str(valor), anchor="e",
                          font=(FUENTE, 10), fill=GRIS)
        c.create_line(x0, y_base, x1, y_base, fill=TEXTO)

        separacion = (x1 - x0) / (len(serie) - 1)
        puntos_positivos, puntos_atencion = [], []
        for i, (dia, positivos, atencion) in enumerate(serie):
            x = x0 + i * separacion
            c.create_text(x, y_base + 18, text=f"{dia:%d/%m}", font=(FUENTE, 10), fill=TEXTO)
            puntos_positivos.append((x, y_base - positivos * escala, positivos))
            puntos_atencion.append((x, y_base - atencion * escala, atencion))

        for puntos, color, desplazamiento in ((puntos_positivos, POSITIVO, -14),
                                              (puntos_atencion, ATENCION, 14)):
            coordenadas = []
            for x, y, _valor in puntos:
                coordenadas += [x, y]
            c.create_line(*coordenadas, fill=color, width=3)
            for x, y, valor in puntos:
                c.create_oval(x - 5, y - 5, x + 5, y + 5, fill=color, outline="white")
                c.create_text(x, y + desplazamiento, text=str(valor),
                              font=(FUENTE, 10, "bold"), fill=color)
