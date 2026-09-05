"""
Módulo para la interfaz gráfica de la aplicación de combinación de PDFs.

Este módulo contiene la clase PDFCombinerApp que maneja la interfaz de usuario.
"""

from __future__ import annotations

import os
import tkinter as tk
import tkinter.font as tkfont
from collections.abc import Iterable
from dataclasses import dataclass
from tkinter import filedialog, messagebox, ttk
from typing import Protocol

from pdf_logic import PDFLogic

try:
    from tkinterdnd2 import DND_FILES
except ImportError:
    DND_FILES = ""

# Máscara de modificadores (Shift / Ctrl) que desactivan el arrastre
_MOD_SHIFT = 0x0001
_MOD_CTRL = 0x0004

# Color de las filas cuyo nombre de archivo se repite (duplicados)
COLOR_DUPLICADO = "#e8a33d"


@dataclass
class _Arrastre:
    """Estado del arrastre para reordenar filas de la lista."""

    y: int
    indice: int
    activo: bool
    desplazamiento: int


class _EventoDrop(Protocol):
    """Evento de tkdnd; las rutas arrastradas viajan en ``.data``."""

    data: str


class PDFCombinerApp:
    """
    Clase principal de la aplicación para combinar PDFs con interfaz gráfica.
    """

    UMBRAL_ARRASTRE = 5  # píxeles mínimos para distinguir clic de arrastre

    def __init__(self, root: tk.Tk) -> None:
        """
        Inicializa la aplicación.

        Args:
            root: La ventana raíz de Tkinter.
        """
        self.root = root
        self.root.title("Combinador de PDFs")
        self.root.geometry("640x500")
        self.root.minsize(520, 430)
        self.logic = PDFLogic()
        self._drag: _Arrastre | None = None
        self._msg_token = 0
        self._duplicados: set[int] = set()
        self._dnd_activo = False

        # Marco principal
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill="both", expand=True)

        # Etiqueta título
        title_label = ttk.Label(main_frame, text="Lista de PDFs a combinar:")
        title_label.pack(anchor="w", pady=(0, 10))

        # Listbox con scroll (selección múltiple con Ctrl y Shift)
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill="both", expand=True)

        mono_font = tkfont.nametofont("TkFixedFont").copy()
        mono_font.configure(size=11)

        self.listbox = tk.Listbox(
            list_frame,
            selectmode=tk.EXTENDED,
            font=mono_font,
            height=12,
            bd=2,
            relief="ridge",
            activestyle="none",
            exportselection=False,
        )
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.listbox.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Eventos de la lista
        self.listbox.bind("<<ListboxSelect>>", self.actualizar_estado)
        self.listbox.bind("<Delete>", lambda e: self.eliminar_seleccionados())
        self.listbox.bind("<KP_Delete>", lambda e: self.eliminar_seleccionados())
        self.listbox.bind("<ButtonPress-1>", self._arrastre_inicio)
        self.listbox.bind("<B1-Motion>", self._arrastre_movimiento)
        self.listbox.bind("<ButtonRelease-1>", self._arrastre_fin)
        self.listbox.bind("<Button-3>", self._menu_contextual)

        # Arrastrar y soltar desde el gestor de archivos (tkinterdnd2)
        if DND_FILES and hasattr(self.root, "drop_target_register"):
            self.listbox.drop_target_register(DND_FILES)  # type: ignore[attr-defined]
            self.listbox.dnd_bind("<<Drop>>", self._on_drop)  # type: ignore[attr-defined]
            self._dnd_activo = True

        # Menú contextual (clic derecho)
        self.menu_ctx = tk.Menu(self.root, tearoff=0)
        self.menu_ctx.add_command(
            label="Subir", command=self.mover_arriba, accelerator="Ctrl+Up"
        )
        self.menu_ctx.add_command(
            label="Bajar", command=self.mover_abajo, accelerator="Ctrl+Down"
        )
        self.menu_ctx.add_separator()
        self.menu_ctx.add_command(
            label="Eliminar seleccionados",
            command=self.eliminar_seleccionados,
            accelerator="Supr",
        )
        self.menu_ctx.add_separator()
        self.menu_ctx.add_command(label="Vaciar lista", command=self.vaciar_lista)

        # Atajos de teclado
        self.root.bind("<Control-Up>", lambda e: self.mover_arriba())
        self.root.bind("<Control-Down>", lambda e: self.mover_abajo())

        # Frame botones
        btn_frame = ttk.Frame(main_frame, padding=(0, 10, 0, 0))
        btn_frame.pack(fill="x")

        self.btn_agregar = ttk.Button(
            btn_frame, text="Agregar PDFs", command=self.agregar_pdfs
        )
        self.btn_agregar_carpeta = ttk.Button(
            btn_frame, text="Agregar Carpeta", command=self.agregar_carpeta
        )
        self.btn_eliminar = ttk.Button(
            btn_frame, text="Eliminar Sel.", command=self.eliminar_seleccionados
        )
        self.btn_subir = ttk.Button(btn_frame, text="Subir", command=self.mover_arriba)
        self.btn_bajar = ttk.Button(btn_frame, text="Bajar", command=self.mover_abajo)
        self.btn_vaciar = ttk.Button(
            btn_frame, text="Vaciar", command=self.vaciar_lista
        )

        botones = (
            self.btn_agregar,
            self.btn_agregar_carpeta,
            self.btn_eliminar,
            self.btn_subir,
            self.btn_bajar,
            self.btn_vaciar,
        )
        for columna, boton in enumerate(botones):
            boton.grid(row=0, column=columna, padx=(0, 5), sticky="ew")
            btn_frame.columnconfigure(columna, weight=1)

        self.btn_combinar = ttk.Button(
            btn_frame, text="Combinar PDFs", command=self.combinar_pdfs
        )
        self.btn_combinar.grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0), padx=(0, 5)
        )

        self.btn_combinar_eliminar = ttk.Button(
            btn_frame,
            text="Combinar y eliminar originales",
            command=self.combinar_y_eliminar,
        )
        self.btn_combinar_eliminar.grid(
            row=1, column=2, columnspan=3, sticky="ew", pady=(10, 0)
        )

        # Barra de estado
        self.status_var = tk.StringVar(value="0 PDFs en lista")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, anchor="w")
        status_bar.pack(fill="x", pady=(10, 0))

        self.refrescar_lista()

    # ------------------------------------------------------------------
    # Gestión de la lista
    # ------------------------------------------------------------------

    def agregar_pdfs(self) -> None:
        """Abre un diálogo para seleccionar archivos PDF y los agrega a la lista."""
        archivos = filedialog.askopenfilenames(
            title="Selecciona archivos PDF", filetypes=[("Archivos PDF", "*.pdf")]
        )
        if not archivos:
            return
        self.agregar_rutas(archivos)

    def agregar_rutas(self, rutas: Iterable[str]) -> None:
        """
        Agrega un conjunto de rutas a la lista y muestra un resumen.

        Args:
            rutas (Iterable[str]): Rutas a agregar.
        """
        agregados, ya_presentes, errores = self.logic.add_pdfs(rutas)
        mensaje = (
            f"{agregados} PDF{'s' if agregados != 1 else ''} "
            f"agregado{'s' if agregados != 1 else ''}"
        )
        if ya_presentes:
            mensaje += (
                f" · {ya_presentes} ya "
                f"{'estaban' if ya_presentes != 1 else 'estaba'} en la lista"
            )
        if errores:
            mensaje += (
                f" · {len(errores)} {'error' if len(errores) == 1 else 'errores'}"
            )
            messagebox.showwarning(
                "Archivos no válidos",
                "Los siguientes archivos no se agregaron:\n\n" + "\n".join(errores),
            )
        self.refrescar_lista()
        self.mostrar_mensaje(mensaje)

    def agregar_carpeta(self) -> None:
        """
        Abre un diálogo para elegir una carpeta y agrega sus PDFs,
        organizando la lista por serie.
        """
        carpeta = filedialog.askdirectory(title="Selecciona una carpeta con PDFs")
        if not carpeta:
            return
        self.agregar_carpeta_ruta(carpeta)

    def agregar_carpeta_ruta(self, carpeta: str) -> None:
        """
        Agrega los PDFs de una carpeta y los agrupa por serie.

        Args:
            carpeta (str): Ruta de la carpeta a añadir.
        """
        try:
            agregados, ya_presentes, errores = self.logic.add_pdfs_de_carpeta(carpeta)
        except NotADirectoryError as exc:
            messagebox.showerror("Error", str(exc))
            return
        if agregados:
            self.logic.organizar_por_serie()
        self.refrescar_lista()
        mensaje = (
            f"{agregados} PDF{'s' if agregados != 1 else ''} de la carpeta "
            f"agregado{'s' if agregados != 1 else ''}"
        )
        if ya_presentes:
            mensaje += f" · {ya_presentes} ya estaban en la lista"
        if errores:
            messagebox.showwarning(
                "Archivos no válidos",
                "Algunos archivos de la carpeta no se agregaron:\n\n"
                + "\n".join(errores),
            )
        self.mostrar_mensaje(mensaje + " · agrupado por serie")

    def _on_drop(self, evento: _EventoDrop) -> None:
        """
        Maneja archivos y carpetas soltados desde el gestor de archivos.
        """
        if not self._dnd_activo:
            return
        rutas = list(self.root.tk.splitlist(evento.data))
        archivos = [
            r for r in rutas if os.path.isfile(r) and r.lower().endswith(".pdf")
        ]
        carpetas = [r for r in rutas if os.path.isdir(r)]
        if archivos:
            self.agregar_rutas(archivos)
        for carpeta in carpetas:
            self.agregar_carpeta_ruta(carpeta)

    def eliminar_seleccionados(self) -> None:
        """Elimina todos los archivos PDF seleccionados de la lista."""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning(
                "Advertencia", "Debes seleccionar al menos un archivo para eliminar."
            )
            return
        primero = sel[0]
        self.logic.remove_indices(sel)
        self.refrescar_lista()
        # Deja seleccionado el elemento que quedó en esa posición
        total = self.listbox.size()
        if total:
            nuevo = min(primero, total - 1)
            self.listbox.selection_set(nuevo)
            self.listbox.see(nuevo)
        plural = len(sel) != 1
        self.mostrar_mensaje(
            f"{len(sel)} archivo{'s' if plural else ''}"
            f" eliminado{'s' if plural else ''}"
        )

    def vaciar_lista(self) -> None:
        """Elimina todos los archivos de la lista previa confirmación."""
        if not self.listbox.size():
            return
        confirmar = messagebox.askyesno(
            "Vaciar lista",
            f"Se quitarán los {self.listbox.size()} archivos de la lista.\n\n"
            "¿Deseas continuar?",
        )
        if not confirmar:
            return
        self.logic.clear()
        self.refrescar_lista()

    def mover_arriba(self) -> None:
        """Mueve el bloque seleccionado una posición hacia arriba."""
        sel = self.listbox.curselection()
        if not sel or sel[0] == 0:
            return
        nuevos = self.logic.move(sel, -1)
        self.refrescar_lista(seleccion=nuevos)

    def mover_abajo(self) -> None:
        """Mueve el bloque seleccionado una posición hacia abajo."""
        sel = self.listbox.curselection()
        if not sel or sel[-1] == self.listbox.size() - 1:
            return
        nuevos = self.logic.move(sel, +1)
        self.refrescar_lista(seleccion=nuevos)

    def refrescar_lista(self, seleccion: list[int] | None = None) -> None:
        """
        Actualiza la listbox con la lista actual de PDFs.

        Args:
            seleccion (list[int], opcional): Índices a marcar como seleccionados.
        """
        self.listbox.delete(0, tk.END)
        self._duplicados = set(self.logic.indices_duplicados())
        for archivo in self.logic.get_pdf_list():
            self.listbox.insert(tk.END, archivo)
        for indice in self._duplicados:
            self.listbox.itemconfig(indice, foreground=COLOR_DUPLICADO)
        if seleccion:
            for indice in seleccion:
                self.listbox.selection_set(indice)
            self.listbox.see(seleccion[0])
        self.actualizar_estado()

    # ------------------------------------------------------------------
    # Barra de estado y estado de botones
    # ------------------------------------------------------------------

    def actualizar_estado(self, *_: object) -> None:
        """Actualiza el texto de la barra de estado y el estado de los botones."""
        total = self.listbox.size()
        marcados = len(self.listbox.curselection())

        hay_sel = "normal" if marcados else "disabled"
        self.btn_eliminar.configure(state=hay_sel)
        self.btn_subir.configure(state=hay_sel)
        self.btn_bajar.configure(state=hay_sel)
        self.btn_vaciar.configure(state="normal" if total else "disabled")
        self.btn_combinar.configure(state="normal" if total >= 2 else "disabled")
        self.btn_combinar_eliminar.configure(
            state="normal" if total >= 2 else "disabled"
        )

        texto = f"{total} PDF{'s' if total != 1 else ''} en lista"
        if self._duplicados:
            plural = len(self._duplicados) != 1
            texto += f" · {len(self._duplicados)} duplicado{'s' if plural else ''}"
        if marcados:
            texto += f" · {marcados} seleccionado{'s' if marcados != 1 else ''}"
        self.status_var.set(texto)

    def mostrar_mensaje(self, texto: str, milisegundos: int = 4000) -> None:
        """
        Muestra un mensaje transitorio en la barra de estado.

        Args:
            texto (str): Mensaje a mostrar.
            milisegundos (int): Tiempo antes de volver al estado normal.
        """
        self._msg_token += 1
        token = self._msg_token
        self.status_var.set(texto)
        self.root.after(milisegundos, lambda: self._restaurar_estado(token))

    def _restaurar_estado(self, token: int) -> None:
        """Restaura la barra de estado si el mensaje sigue vigente."""
        if token == self._msg_token:
            self.actualizar_estado()

    # ------------------------------------------------------------------
    # Arrastrar y soltar interno para reordenar
    # ------------------------------------------------------------------

    def _arrastre_inicio(self, evento: tk.Event[tk.Misc]) -> None:
        """Prepara los datos del posible arrastre al pulsar sobre la lista."""
        self._drag = None
        if int(evento.state) & (_MOD_SHIFT | _MOD_CTRL):
            return  # clic extendido de selección, no arrastre
        indice = self.listbox.nearest(evento.y)
        if indice < 0 or indice >= self.listbox.size():
            return
        self._drag = _Arrastre(
            y=evento.y,
            indice=indice,
            activo=False,
            desplazamiento=0,
        )

    def _arrastre_movimiento(self, evento: tk.Event[tk.Misc]) -> None:
        """Reordena en vivo el bloque seleccionado mientras se arrastra."""
        datos = self._drag
        if datos is None:
            return

        if not datos.activo:
            if abs(evento.y - datos.y) < self.UMBRAL_ARRASTRE:
                return
            sel = list(self.listbox.curselection())
            if datos.indice in sel:
                datos.desplazamiento = datos.indice - min(sel)
            else:
                datos.desplazamiento = 0
            datos.activo = True

        destino = self.listbox.nearest(evento.y)
        total = self.listbox.size()
        if destino < 0 or destino >= total:
            return

        sel = sorted(self.listbox.curselection())
        if not sel:
            return
        bloque = len(sel)
        objetivo = max(0, min(destino - datos.desplazamiento, total - bloque))
        if objetivo != sel[0]:
            nuevos = self.logic.move_block_to(sel, objetivo)
            self.refrescar_lista(seleccion=nuevos)

    def _arrastre_fin(self, *_: object) -> None:
        """Finaliza el arrastre."""
        self._drag = None

    # ------------------------------------------------------------------
    # Menú contextual
    # ------------------------------------------------------------------

    def _menu_contextual(self, evento: tk.Event[tk.Misc]) -> None:
        """Muestra el menú contextual de la lista en la posición del cursor."""
        indice = self.listbox.nearest(evento.y)
        dentro = 0 <= indice < self.listbox.size()
        if dentro and indice not in self.listbox.curselection():
            # Clic derecho fuera de la selección: selecciona solo esa fila
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(indice)
            self.actualizar_estado()

        sel = self.listbox.curselection()
        hay_sel = bool(sel)
        estado_sel = "normal" if hay_sel else "disabled"
        self.menu_ctx.entryconfig(
            "Subir", state="normal" if hay_sel and sel[0] > 0 else "disabled"
        )
        self.menu_ctx.entryconfig(
            "Bajar",
            state="normal"
            if hay_sel and sel[-1] < self.listbox.size() - 1
            else "disabled",
        )
        self.menu_ctx.entryconfig("Eliminar seleccionados", state=estado_sel)
        self.menu_ctx.entryconfig(
            "Vaciar lista", state="normal" if self.listbox.size() else "disabled"
        )

        try:
            self.menu_ctx.tk_popup(evento.x_root, evento.y_root)
        finally:
            self.menu_ctx.grab_release()

    # ------------------------------------------------------------------
    # Acciones principales
    # ------------------------------------------------------------------

    def combinar_pdfs(self) -> None:
        """Combina los PDFs seleccionados y guarda el resultado."""
        if len(self.logic.get_pdf_list()) < 2:
            messagebox.showwarning(
                "Advertencia", "Debes agregar al menos dos PDFs para combinar."
            )
            return
        output_file = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            title="Guardar PDF combinado como",
        )
        if not output_file:
            return
        try:
            self.logic.combine_pdfs(output_file)
            messagebox.showinfo(
                "Éxito", f"PDFs combinados exitosamente en:\n{output_file}"
            )
        except Exception as exc:
            messagebox.showerror(
                "Error", f"Ocurrió un error al combinar los PDFs:\n{exc}"
            )

    def combinar_y_eliminar(self) -> None:
        """
        Combina los PDFs y elimina los originales (requiere permisos de administrador).
        """
        if len(self.logic.get_pdf_list()) < 2:
            messagebox.showwarning(
                "Advertencia", "Debes agregar al menos dos PDFs para combinar."
            )
            return

        confirm = messagebox.askyesno(
            "Confirmar eliminación",
            "Esta acción combinará los PDFs y eliminará los archivos originales.\n"
            "Se requieren permisos de administrador.\n\n¿Deseas continuar?",
        )
        if not confirm:
            return

        output_file = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            title="Guardar PDF combinado como",
        )
        if not output_file:
            return

        try:
            success, result = self.logic.combine_and_delete_originals(output_file)
            if isinstance(result, str):
                if success:
                    messagebox.showinfo("Éxito", result)
                else:
                    messagebox.showerror("Error", result)
            else:
                failed_list = "\n".join([f"{pdf}: {error}" for pdf, error in result])
                messagebox.showwarning(
                    "Advertencia",
                    "PDFs combinados, pero algunos archivos no pudieron ser "
                    f"eliminados:\n\n{failed_list}",
                )
        except Exception as exc:
            messagebox.showerror(
                "Error", f"Ocurrió un error al procesar los PDFs:\n{exc}"
            )
