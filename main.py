"""
Punto de entrada principal de la aplicación de combinación de PDFs.

Este archivo inicia la aplicación gráfica.
"""

import os
import sys
import tkinter as tk

import sv_ttk

from pdf_gui import PDFCombinerApp


def resource_path(ruta_relativa: str) -> str:
    """
    Resuelve rutas a recursos tanto en desarrollo como dentro del
    ejecutable generado con PyInstaller (carpeta temporal _MEIPASS).
    """
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, ruta_relativa)


def main() -> None:
    """Crea la ventana principal y arranca el bucle de eventos de Tk."""
    root = tk.Tk()
    app = PDFCombinerApp(root)
    try:
        _icono = tk.PhotoImage(file=resource_path(os.path.join("assets", "icon.png")))
        root.iconphoto(True, _icono)
    except tk.TclError:
        pass  # icono no disponible; la app funciona igualmente
    sv_ttk.set_theme("dark")
    root.mainloop()


if __name__ == "__main__":
    main()