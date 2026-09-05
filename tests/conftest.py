"""
Fixtures compartidos de pytest.

Proporciona generación de PDFs reales mínimos y una ventana Tk para
los tests de GUI (a modo del plugin externo 'pytest-tk', que no está
disponible en PyPI).
"""

import contextlib
import os
import sys
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from PyPDF2 import PdfReader, PdfWriter


def _hay_display() -> bool:
    """True si Tk puede abrir ventanas en esta sesión.

    En Windows y macOS Tk crea la ventana de forma nativa; en Linux/BSD
    hace falta un servidor X/Wayland (variable DISPLAY o WAYLAND_DISPLAY).
    """
    if sys.platform == "darwin" or os.name != "posix":
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


@pytest.fixture
def crear_pdf(tmp_path: Path) -> Callable[..., str]:
    """
    Devuelve una fabrica que crea un PDF real con N paginas en tmp_path.

    Uso: `ruta = crear_pdf("archivo.pdf", paginas=3)`.
    """

    def _crear(nombre: str, paginas: int = 1) -> str:
        ruta = tmp_path / nombre
        writer = PdfWriter()
        for _ in range(paginas):
            writer.add_blank_page(width=200, height=200)
        with open(ruta, "wb") as fh:
            writer.write(fh)
        return str(ruta)

    return _crear


@pytest.fixture
def tk() -> Iterator:
    """
    Crea una ventana Tk raíz. Se omite el test si no hay pantalla.
    """
    import tkinter as tk

    if not _hay_display():
        pytest.skip("No hay display disponible para los tests de GUI")
    root = tk.Tk()
    root.withdraw()
    try:
        yield root
    finally:
        with contextlib.suppress(tk.TclError):
            root.destroy()


@pytest.fixture
def app(tk):
    """Crea una instancia de la aplicación GUI sobre la ventana raíz."""
    from pdf_gui import PDFCombinerApp

    ui = PDFCombinerApp(tk)
    tk.update_idletasks()
    return ui


@pytest.fixture
def app_dnd():
    """
    Como `app`, pero sobre una raíz con soporte de arrastrar y soltar
    (`TkinterDnD.Tk`). Se omite el test si no hay pantalla o tkinterdnd2.
    """
    try:
        from tkinterdnd2 import TkinterDnD
    except ImportError:
        pytest.skip("tkinterdnd2 no está instalado")

    if not _hay_display():
        pytest.skip("No hay display disponible para los tests de GUI")
    import tkinter as tk

    from pdf_gui import PDFCombinerApp

    root = TkinterDnD.Tk()
    root.withdraw()
    try:
        ui = PDFCombinerApp(root)
        root.update_idletasks()
        yield ui
    finally:
        with contextlib.suppress(tk.TclError):
            root.destroy()


def paginas_de(ruta: str) -> int:
    """Número de páginas de un PDF."""
    with open(ruta, "rb") as fh:
        return len(PdfReader(fh).pages)
