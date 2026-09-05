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


def test_agregar_pdfs_omite_duplicados_y_errores(app, crear_pdf):
    a = crear_pdf("a.pdf")
    invalido = str(Path(a).with_suffix(".txt"))
    with open(invalido, "w") as fh:
        fh.write("no es pdf")
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
