"""
Punto de entrada principal de la aplicación de combinación de PDFs.

Este archivo inicia la aplicación gráfica.
"""

import tkinter as tk
import sv_ttk

from pdf_gui import PDFCombinerApp


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFCombinerApp(root)
    sv_ttk.set_theme("dark")
    root.mainloop()
