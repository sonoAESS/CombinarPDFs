"""
Tests de integración: flujo completo de la aplicación.

Combina la lógica de negocio con la interfaz, desde agregar archivos
hasta obtener el PDF combinado, sin tocar diálogos reales.
"""

import os
from pathlib import Path

from pdf_logic import PDFLogic


def test_flujo_completo_pdf_logic(crear_pdf, tmp_path: Path):
    logic = PDFLogic()

    # Preparar varios PDFs en una carpeta (con ruido de archivos no PDF)
    for n, pagina in [("Serie 1", 2), ("Serie 2", 3), ("Nota 1", 1)]:
        crear_pdf(f"{n}.pdf", pagina)
    crear_pdf("no_usar.txt")

    # Agregar carpeta: solo captura los .pdf, ordenados por nombre
    agregados, ya_presentes, errores = logic.add_pdfs_de_carpeta(str(tmp_path))
    assert agregados == 3
    assert ya_presentes == 0
    assert errores == []

    # Agrupar por serie y verificar resultado final
    logic.organizar_por_serie()
    bases = [os.path.basename(p) for p in logic.get_pdf_list()]
    assert bases == ["Nota 1.pdf", "Serie 1.pdf", "Serie 2.pdf"]

    # Combinar y validar el total de páginas
    salida = str(tmp_path / "combinado.pdf")
    logic.combine_pdfs(salida)

    from conftest import paginas_de

    assert paginas_de(salida) == 6


def test_mover_bloque_y_combinar(crear_pdf, tmp_path: Path):
    logic = PDFLogic()
    rutas = [crear_pdf(f"{n}.pdf") for n in "abcd"]
    logic.add_pdfs(rutas)

    # Seleccionar dos y moverlos al final
    logic.move_block_to([0, 1], 2)
    lista = logic.get_pdf_list()
    assert lista == [rutas[2], rutas[3], rutas[0], rutas[1]]

    salida = str(tmp_path / "reordenado.pdf")
    logic.combine_pdfs(salida)

    from conftest import paginas_de

    assert paginas_de(salida) == 4
