"""
Tests básicos de la interfaz gráfica (pdf_gui.py).

Se ejecutan únicamente si hay display disponible; en caso contrario
el fixture `tk` los omite automáticamente.
"""

import os
from pathlib import Path


def _estado(boton) -> str:
    return str(boton.cget("state"))


def test_estado_inicial(app):
    assert _estado(app.btn_combinar) == "disabled"
    assert _estado(app.btn_combinar_eliminar) == "disabled"
    assert _estado(app.btn_vaciar) == "disabled"
    assert _estado(app.btn_eliminar) == "disabled"
    assert app.listbox.size() == 0
    assert "0 PDFs" in app.status_var.get()


def test_agregar_pdfs_activa_botones(app, crear_pdf):
    app.agregar_rutas([crear_pdf("a.pdf"), crear_pdf("b.pdf")])
    assert app.listbox.size() == 2
    assert _estado(app.btn_combinar) == "normal"
    assert _estado(app.btn_combinar_eliminar) == "normal"
    assert _estado(app.btn_vaciar) == "normal"


def test_agregar_pdfs_omite_duplicados_y_errores(app, crear_pdf, monkeypatch):
    a = crear_pdf("a.pdf")
    invalido = str(Path(a).with_suffix(".txt"))
    with open(invalido, "w") as fh:
        fh.write("no es pdf")
    monkeypatch.setattr("pdf_gui.messagebox.showwarning", lambda *a, **k: None)
    app.agregar_rutas([a, a, invalido])
    assert app.listbox.size() == 1


def test_eliminar_seleccionados(app, crear_pdf):
    rutas = [crear_pdf(f"{n}.pdf") for n in "abc"]
    app.agregar_rutas(rutas)
    app.listbox.selection_set(0)
    app.listbox.selection_set(2)
    app.eliminar_seleccionados()
    assert app.listbox.size() == 1
    assert os.path.basename(app.listbox.get(0)) == "b.pdf"
    assert _estado(app.btn_combinar) == "disabled"


def test_vaciar_lista(app, crear_pdf, monkeypatch):
    app.agregar_rutas([crear_pdf("a.pdf"), crear_pdf("b.pdf")])
    monkeypatch.setattr("pdf_gui.messagebox.askyesno", lambda *a, **k: True)
    app.vaciar_lista()
    assert app.listbox.size() == 0
    assert _estado(app.btn_vaciar) == "disabled"


def test_mover_arriba_y_abajo(app, crear_pdf):
    rutas = [crear_pdf(f"{n}.pdf") for n in "abc"]
    app.agregar_rutas(rutas)
    app.listbox.selection_set(2)
    app.mover_arriba()
    assert os.path.basename(app.listbox.get(1)) == "c.pdf"
    app.listbox.selection_set(1)
    app.mover_abajo()
    assert os.path.basename(app.listbox.get(2)) == "c.pdf"


def test_combinar_pdfs_desde_gui(app, crear_pdf, monkeypatch, tmp_path: Path):
    app.agregar_rutas([crear_pdf("a.pdf", 2), crear_pdf("b.pdf", 3)])
    salida = str(tmp_path / "salida.pdf")
    monkeypatch.setattr("pdf_gui.filedialog.asksaveasfilename", lambda *a, **k: salida)
    monkeypatch.setattr("pdf_gui.messagebox.showinfo", lambda *a, **k: None)
    app.combinar_pdfs()
    assert os.path.exists(salida)


def test_combinar_y_eliminar_sin_permisos(app, crear_pdf, monkeypatch, tmp_path: Path):
    from pdf_logic import PDFLogic

    app.agregar_rutas([crear_pdf("a.pdf"), crear_pdf("b.pdf")])
    salida = str(tmp_path / "salida.pdf")
    monkeypatch.setattr("pdf_gui.filedialog.asksaveasfilename", lambda *a, **k: salida)
    monkeypatch.setattr("pdf_gui.messagebox.askyesno", lambda *a, **k: True)
    monkeypatch.setattr(PDFLogic, "is_admin", staticmethod(lambda: False))
    errores = []

    def _showerror(*a):
        errores.append(a)

    monkeypatch.setattr("pdf_gui.messagebox.showerror", _showerror)
    app.combinar_y_eliminar()
    assert errores  # sin permisos de admin debe mostrarse un error


def test_duplicados_marcados_en_naranja(app, crear_pdf, tmp_path):
    from pdf_gui import COLOR_DUPLICADO

    a = crear_pdf("comun.pdf")
    b = tmp_path / "sub" / "comun.pdf"
    os.makedirs(b.parent)
    with open(a, "rb") as origen, open(b, "wb") as destino:
        destino.write(origen.read())
    app.agregar_rutas([a, crear_pdf("otro.pdf"), str(b)])
    assert app.listbox.size() == 3
    assert app.listbox.itemcget(0, "foreground") == COLOR_DUPLICADO
    assert app.listbox.itemcget(1, "foreground") != COLOR_DUPLICADO
    assert app.listbox.itemcget(2, "foreground") == COLOR_DUPLICADO
    app.actualizar_estado()
    assert "duplicados" in app.status_var.get()


def test_agregar_carpeta_agrupa_por_serie(app, crear_pdf, tmp_path, monkeypatch):
    for nombre in ["Zeta 5.pdf", "Alfa 10.pdf", "Zeta 1.pdf", "Alfa 2.pdf"]:
        crear_pdf(nombre)
    monkeypatch.setattr(
        "pdf_gui.filedialog.askdirectory", lambda *a, **k: str(tmp_path)
    )
    app.agregar_carpeta()
    bases = [app.listbox.get(i) for i in range(app.listbox.size())]
    nombres = [Path(b).name for b in bases]
    assert nombres == ["Alfa 2.pdf", "Alfa 10.pdf", "Zeta 1.pdf", "Zeta 5.pdf"]


def test_drop_archivos_en_lista(crear_pdf, tmp_path, monkeypatch):

    try:
        from tkinterdnd2 import TkinterDnD
    except ImportError:
        return
    from pdf_gui import PDFCombinerApp

    root = TkinterDnD.Tk()
    root.withdraw()
    try:
        app = PDFCombinerApp(root)
        a = crear_pdf("a.pdf")
        b = crear_pdf("b.pdf")
        app._on_drop(type("Ev", (), {"data": f"{{{a}}} {{{b}}}"})())
        assert app.listbox.size() == 2
    finally:
        root.destroy()


def test_drop_sin_soporte_dnd(app, crear_pdf, tmp_path):
    class Evento:
        def __init__(self, data):
            self.data = data

    # Ventana sin tkinterdnd2: el drop no hace nada.
    assert app._dnd_activo is False
    a = crear_pdf("a.pdf")
    nota = str(tmp_path / "nota.txt")
    with open(nota, "w") as fh:
        fh.write("no pdf")
    app._on_drop(Evento(f"{{{a}}} {{{nota}}}"))
    assert app.listbox.size() == 0
