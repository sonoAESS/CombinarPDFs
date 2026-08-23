"""
Módulo de lógica para la combinación de PDFs.

Este módulo contiene la clase PDFLogic que maneja la lógica de negocio
para agregar, remover, reordenar y combinar archivos PDF.
"""

import os
import ctypes
from PyPDF2 import PdfMerger


class PDFLogic:
    """
    Clase que maneja la lógica de combinación de PDFs.
    """

    def __init__(self):
        """
        Inicializa la lista de PDFs.
        """
        self.pdf_files = []

    def add_pdf(self, pdf_path):
        """
        Agrega un archivo PDF a la lista si no está ya presente.

        Args:
            pdf_path (str): Ruta del archivo PDF a agregar.
        """
        if pdf_path not in self.pdf_files:
            self.pdf_files.append(pdf_path)

    def remove_pdf(self, index):
        """
        Remueve un archivo PDF de la lista por índice.

        Args:
            index (int): Índice del archivo a remover.
        """
        if 0 <= index < len(self.pdf_files):
            self.pdf_files.pop(index)

    def move_up(self, index):
        """
        Mueve un archivo PDF hacia arriba en la lista.

        Args:
            index (int): Índice del archivo a mover.
        """
        if index > 0:
            self.pdf_files[index - 1], self.pdf_files[index] = (
                self.pdf_files[index],
                self.pdf_files[index - 1],
            )

    def move_down(self, index):
        """
        Mueve un archivo PDF hacia abajo en la lista.

        Args:
            index (int): Índice del archivo a mover.
        """
        if index < len(self.pdf_files) - 1:
            self.pdf_files[index + 1], self.pdf_files[index] = (
                self.pdf_files[index],
                self.pdf_files[index + 1],
            )

    def get_pdf_list(self):
        """
        Devuelve la lista actual de archivos PDF.

        Returns:
            list: Lista de rutas de archivos PDF.
        """
        return self.pdf_files.copy()

    def combine_pdfs(self, output_path):
        """
        Combina los PDFs en la lista y guarda el resultado.

        Args:
            output_path (str): Ruta donde guardar el PDF combinado.

        Raises:
            Exception: Si ocurre un error durante la combinación.
        """
        merger = PdfMerger()
        try:
            for pdf in self.pdf_files:
                with open(pdf, "rb") as f:
                    merger.append(f)
            merger.write(output_path)
        finally:
            merger.close()

    def is_admin(self):
        """
        Verifica si el usuario tiene privilegios de administrador.

        Returns:
            bool: True si es administrador, False en caso contrario.
        """
        try:
            if os.name == "nt":
                return bool(ctypes.windll.shell32.IsUserAnAdmin())
            return os.geteuid() == 0
        except:
            return False

    def combine_and_delete_originals(self, output_path):
        """
        Combina los PDFs y elimina los archivos originales (requiere permisos de administrador).

        Args:
            output_path (str): Ruta donde guardar el PDF combinado.

        Returns:
            tuple: (bool, str or list) - (éxito, mensaje o lista de fallos)

        Raises:
            Exception: Si ocurre un error durante la combinación.
        """
        if not self.is_admin():
            return (
                False,
                "Se requieren permisos de administrador para eliminar archivos.",
            )

        # Primero combinar
        self.combine_pdfs(output_path)

        # Luego intentar eliminar los originales
        failed_deletions = []
        for pdf in self.pdf_files:
            try:
                os.remove(pdf)
            except OSError as e:
                failed_deletions.append((pdf, str(e)))

        if failed_deletions:
            return False, failed_deletions
        else:
            return (
                True,
                f"PDFs combinados y originales eliminados exitosamente en:\n{output_path}",
            )
