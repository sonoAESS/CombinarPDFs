"""
Tests unitarios de la lógica de negocio (pdf_logic.py).
"""

import os
from pathlib import Path

import pytest
from conftest import paginas_de

from pdf_logic import PDFLogic


def test_agregar_pdf_valido(crear_pdf):
    logic = PDFLogic()
    ruta = crear_pdf("a.pdf")
    assert logic.add_pdf(ruta) is True
    assert logic.get_pdf_list() == [ruta]


def test_agregar_pdf_duplicado(crear_pdf):
    logic = PDFLogic()
    ruta = crear_pdf("a.pdf")
    logic.add_pdf(ruta)
    assert logic.add_pdf(ruta) is False
    assert len(logic.get_pdf_list()) == 1


def test_agregar_pdf_con_extension_invalida(crear_pdf):
    logic = PDFLogic()
    ruta = crear_pdf("a.txt")
    with pytest.raises(ValueError):
        logic.add_pdf(ruta)
    assert logic.get_pdf_list() == []


def test_agregar_pdf_inexistente(tmp_path: Path):
    logic = PDFLogic()
    with pytest.raises(FileNotFoundError):
        logic.add_pdf(str(tmp_path / "no_existe.pdf"))


def test_add_pdfs_lote(crear_pdf):
    logic = PDFLogic()
    a = crear_pdf("a.pdf")
    b = crear_pdf("b.txt")
    agregados, ya_presentes, errores = logic.add_pdfs([a, b, a])
    assert agregados == 1
    assert ya_presentes == 1
    assert len(errores) == 1
    assert logic.get_pdf_list() == [a]


def test_add_pdfs_de_carpeta(tmp_path: Path, crear_pdf):
    logic = PDFLogic()
    crear_pdf("b.pdf")
    crear_pdf("a.pdf")
    crear_pdf("nota.txt")
    agregados, ya_presentes, errores = logic.add_pdfs_de_carpeta(str(tmp_path))
    assert agregados == 2
    assert ya_presentes == 0
    assert errores == []
    # ordenada por nombre
    assert logic.get_pdf_list() == sorted(logic.pdf_files)


def test_add_pdfs_de_carpeta_invalida(tmp_path: Path):
    logic = PDFLogic()
    with pytest.raises(NotADirectoryError):
        logic.add_pdfs_de_carpeta(str(tmp_path / "no_existe"))


def test_remove_indices(crear_pdf):
    logic = PDFLogic()
    rutas = [crear_pdf(f"{n}.pdf") for n in "abcde"]
    logic.add_pdfs(rutas)
    logic.remove_indices([1, 3, 99])
    assert logic.get_pdf_list() == [rutas[0], rutas[2], rutas[4]]


def test_clear(crear_pdf):
    logic = PDFLogic()
    logic.add_pdfs([crear_pdf("a.pdf"), crear_pdf("b.pdf")])
    logic.clear()
    assert logic.get_pdf_list() == []


def test_move_block_to(crear_pdf):
    logic = PDFLogic()
    rutas = [crear_pdf(f"{n}.pdf") for n in "abcdef"]
    logic.add_pdfs(rutas)
    nuevos = logic.move_block_to([0, 2], 3)
    assert nuevos == [3, 4]
    assert logic.get_pdf_list() == [
        rutas[1],
        rutas[3],
        rutas[4],
        rutas[0],
        rutas[2],
        rutas[5],
    ]


def test_move_subir_y_bajar(crear_pdf):
    logic = PDFLogic()
    rutas = [crear_pdf(f"{n}.pdf") for n in "abc"]
    logic.add_pdfs(rutas)
    assert logic.move([1], -1) == [0]
    assert logic.get_pdf_list() == [rutas[1], rutas[0], rutas[2]]
    assert logic.move([0], -1) == [0]  # borde superior: no cambia
    assert logic.get_pdf_list() == [rutas[1], rutas[0], rutas[2]]
    assert logic.move([0], +1) == [1]
    assert logic.get_pdf_list() == [rutas[0], rutas[1], rutas[2]]
    assert logic.move([2], +1) == [2]  # borde inferior: no cambia


def test_indices_duplicados(tmp_path: Path, crear_pdf):
    logic = PDFLogic()
    a = crear_pdf("comun.pdf")
    b = str(tmp_path / "sub" / "comun.pdf")
    os.makedirs(os.path.dirname(b))
    with open(a, "rb") as origen, open(b, "wb") as destino:
        destino.write(origen.read())
    c = crear_pdf("otro.pdf")
    logic.add_pdfs([a, b, c])
    assert logic.indices_duplicados() == [0, 1]


def test_organizar_por_serie(crear_pdf):
    logic = PDFLogic()
    nombres = ["Zeta 5.pdf", "Alfa 10.pdf", "Zeta 1.pdf", "Alfa 2.pdf"]
    logic.add_pdfs([crear_pdf(n) for n in nombres])
    logic.organizar_por_serie()
    bases = [os.path.basename(p) for p in logic.get_pdf_list()]
    assert bases == ["Alfa 2.pdf", "Alfa 10.pdf", "Zeta 1.pdf", "Zeta 5.pdf"]


def test_combine_pdfs(crear_pdf):
    logic = PDFLogic()
    logic.add_pdfs([crear_pdf("a.pdf", 2), crear_pdf("b.pdf", 3)])
    salida = crear_pdf("resultado.pdf")
    logic.combine_pdfs(salida)
    assert paginas_de(salida) == 5


def test_combine_pdfs_vacio():
    logic = PDFLogic()
    with pytest.raises(ValueError):
        logic.combine_pdfs("/tmp/salida.pdf")


def test_is_admin_posix(monkeypatch):
    logic = PDFLogic()
    monkeypatch.setattr(os, "name", "posix")
    monkeypatch.setattr(os, "geteuid", lambda: 1000)
    assert logic.is_admin() is False
    monkeypatch.setattr(os, "geteuid", lambda: 0)
    assert logic.is_admin() is True


def test_is_admin_windows_sin_ctypes(monkeypatch):
    logic = PDFLogic()
    monkeypatch.setattr(os, "name", "nt")
    # En Linux no existe ctypes.windll: la rama debe devolver False
    assert logic.is_admin() is False


def test_combine_and_delete_originals_sin_permisos(crear_pdf, monkeypatch):
    logic = PDFLogic()
    logic.add_pdfs([crear_pdf("a.pdf"), crear_pdf("b.pdf")])
    monkeypatch.setattr(PDFLogic, "is_admin", staticmethod(lambda: False))
    exito, resultado = logic.combine_and_delete_originals(crear_pdf("out.pdf"))
    assert exito is False
    assert isinstance(resultado, str)


def test_combine_and_delete_originals_ok(crear_pdf, monkeypatch):
    logic = PDFLogic()
    rutas = [crear_pdf("a.pdf"), crear_pdf("b.pdf")]
    logic.add_pdfs(rutas)
    monkeypatch.setattr(PDFLogic, "is_admin", staticmethod(lambda: True))
    salida = crear_pdf("out.pdf")
    exito, resultado = logic.combine_and_delete_originals(salida)
    assert exito is True
    assert isinstance(resultado, str)
    for ruta in rutas:
        assert not os.path.exists(ruta)
    assert paginas_de(salida) == 2


def test_combine_and_delete_originals_con_fallos(crear_pdf, monkeypatch):
    logic = PDFLogic()
    rutas = [crear_pdf("a.pdf"), crear_pdf("b.pdf")]
    logic.add_pdfs(rutas)

    def _remove_que_falla(ruta):
        raise OSError("permiso denegado")

    monkeypatch.setattr(PDFLogic, "is_admin", staticmethod(lambda: True))
    monkeypatch.setattr(os, "remove", _remove_que_falla)
    salida = crear_pdf("out.pdf")
    exito, resultado = logic.combine_and_delete_originals(salida)
    assert exito is False
    assert isinstance(resultado, list)
    assert len(resultado) == 2
    for ruta in rutas:
        assert os.path.exists(ruta)
