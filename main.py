"""
Punto de entrada principal de la aplicación de combinación de PDFs.

Este archivo inicia la aplicación gráfica.
"""

from ttkthemes import ThemedTk
from pdf_gui import PDFCombinerApp


if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = PDFCombinerApp(root)
    root.mainloop()
