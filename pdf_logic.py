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

        Returns:
            bool: True si se agregó, False si ya estaba en la lista.
        """
        if pdf_path not in self.pdf_files:
            self.pdf_files.append(pdf_path)
            return True
        return False

    def remove_indices(self, indices):
        """
        Remueve varios archivos de la lista por índice.

        Los índices inválidos se ignoran silenciosamente.

        Args:
            indices (iterable de int): Índices a remover.
        """
        for idx in sorted(set(indices), reverse=True):
            if 0 <= idx < len(self.pdf_files):
                self.pdf_files.pop(idx)

    def clear(self):
        """Vacía la lista de archivos PDF."""
        self.pdf_files.clear()

    def move_block_to(self, indices, target_first):
        """
        Coloca el bloque formado por `indices` de modo que el primero
        quede en `target_first`, preservando el orden relativo interno.

        Args:
            indices (iterable de int): Índices actuales del bloque.
            target_first (int): Posición destino para el primer elemento.

        Returns:
            list[int]: Nuevos índices que ocupa el bloque tras el movimiento.
        """
        sel = sorted(set(indices))
        total = len(self.pdf_files)
        if not sel or not all(0 <= i < total for i in sel):
            return []
        k = len(sel)
        target_first = max(0, min(target_first, total - k))

        seleccionados = [self.pdf_files[i] for i in sel]
        resto = [
            ruta for i, ruta in enumerate(self.pdf_files) if i not in set(sel)
        ]
        resto[target_first:target_first] = seleccionados
        self.pdf_files[:] = resto
        return list(range(target_first, target_first + k))

    def move(self, indices, delta):
        """
        Mueve el bloque seleccionado delta posiciones (delta -1 = subir,
        +1 = bajar). Si el bloque ya está en el borde correspondiente no
        hace nada.

        Args:
            indices (iterable de int): Índices actuales del bloque.
            delta (int): Desplazamiento (-1 o +1).

        Returns:
            list[int]: Nuevos índices del bloque tras el movimiento.
        """
        sel = sorted(set(indices))
        if not sel:
            return []
        total = len(self.pdf_files)
        if delta < 0 and sel[0] == 0:
            return sel
        if delta > 0 and sel[-1] == total - 1:
            return sel
        return self.move_block_to(sel, sel[0] + delta)

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
