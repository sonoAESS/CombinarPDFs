"""
Módulo para la interfaz gráfica de la aplicación de combinación de PDFs.

Este módulo contiene la clase PDFCombinerApp que maneja la interfaz de usuario.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
from pdf_logic import PDFLogic
import tkdnd2


class PDFCombinerApp:
    """
    Clase principal de la aplicación para combinar PDFs con interfaz gráfica.
    """

    def __init__(self, root):
        """
        Inicializa la aplicación.

        Args:
            root: La ventana raíz de Tkinter.
        """
        self.root = root
        self.root.title("Combinador de PDFs")
        self.root.geometry("600x450")
        self.logic = PDFLogic()

        # Aplicar tema
        self.style = ttk.Style(self.root)

        # Marco principal
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill="both", expand=True)

        # Etiqueta título
        title_label = ttk.Label(main_frame, text="Lista de PDFs a combinar:")
        title_label.pack(pady=(0, 10))

        # Listbox con scroll
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(
            list_frame,
            selectmode=tk.SINGLE,
            font=("Consolas", 11),
            height=12,
            bd=2,
            relief="ridge",
        )
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.listbox.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Frame botones
        btn_frame = ttk.Frame(main_frame, padding=(0, 10, 0, 0))
        btn_frame.pack()

        ttk.Button(btn_frame, text="Agregar PDFs", command=self.agregar_pdfs).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(
            btn_frame, text="Eliminar Seleccionado", command=self.eliminar_seleccionado
        ).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Subir", command=self.mover_arriba).grid(
            row=0, column=2, padx=5
        )
        ttk.Button(btn_frame, text="Bajar", command=self.mover_abajo).grid(
            row=0, column=3, padx=5
        )
        ttk.Button(btn_frame, text="Combinar PDFs", command=self.combinar_pdfs).grid(
            row=0, column=4, padx=5
        )

    def agregar_pdfs(self):
        """
        Abre un diálogo para seleccionar archivos PDF y los agrega a la lista.
        """
        archivos = filedialog.askopenfilenames(
            title="Selecciona archivos PDF", filetypes=[("Archivos PDF", "*.pdf")]
        )
        for archivo in archivos:
            self.logic.add_pdf(archivo)
        self.refrescar_lista()

    def eliminar_seleccionado(self):
        """
        Elimina el archivo PDF seleccionado de la lista.
        """
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning(
                "Advertencia", "Debes seleccionar un archivo para eliminar."
            )
            return
        idx = sel[0]
        self.logic.remove_pdf(idx)
        self.refrescar_lista()

    def mover_arriba(self):
        """
        Mueve el archivo PDF seleccionado hacia arriba en la lista.
        """
        sel = self.listbox.curselection()
        if not sel or sel[0] == 0:
            return
        idx = sel[0]
        self.logic.move_up(idx)
        self.refrescar_lista()
        self.listbox.select_set(idx - 1)

    def mover_abajo(self):
        """
        Mueve el archivo PDF seleccionado hacia abajo en la lista.
        """
        sel = self.listbox.curselection()
        if not sel or sel[0] == len(self.logic.get_pdf_list()) - 1:
            return
        idx = sel[0]
        self.logic.move_down(idx)
        self.refrescar_lista()
        self.listbox.select_set(idx + 1)

    def refrescar_lista(self):
        """
        Actualiza la listbox con la lista actual de PDFs.
        """
        self.listbox.delete(0, tk.END)
        for archivo in self.logic.get_pdf_list():
            self.listbox.insert(tk.END, archivo)

    def combinar_pdfs(self):
        """
        Combina los PDFs seleccionados y guarda el resultado.
        """
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
        except Exception as e:
            messagebox.showerror(
                "Error", f"Ocurrió un error al combinar los PDFs:\n{e}"
            )

    def combinar_y_eliminar(self):
        """
        Combina los PDFs y elimina los originales (requiere permisos de administrador).
        """
        if len(self.logic.get_pdf_list()) < 2:
            messagebox.showwarning(
                "Advertencia", "Debes agregar al menos dos PDFs para combinar."
            )
            return

        # Confirmación de eliminación
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
            if success:
                messagebox.showinfo("Éxito", result)
            else:
                if isinstance(result, str):
                    messagebox.showerror("Error", result)
                else:
                    failed_list = "\n".join(
                        [f"{pdf}: {error}" for pdf, error in result]
                    )
                    messagebox.showwarning(
                        "Advertencia",
                        f"PDFs combinados, pero algunos archivos no pudieron ser eliminados:\n\n{failed_list}",
                    )
        except Exception as e:
            messagebox.showerror(
                "Error", f"Ocurrió un error al procesar los PDFs:\n{e}"
            )
