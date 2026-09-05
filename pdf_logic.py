"""
Módulo de lógica para la combinación de PDFs.

Contiene la clase PDFLogic que maneja la lógica de negocio
para agregar, remover, reordenar y combinar archivos PDF, además
de utilidades para detectar duplicados y agrupar por serie.
"""

import os
import re
from collections import Counter
from collections.abc import Iterable

from PyPDF2 import PdfMerger

# (éxito, mensaje) o (éxito, lista_de_fallos)
ResultadoEliminado = tuple[bool, str] | tuple[bool, list[tuple[str, str]]]


def _es_pdf(ruta: str) -> bool:
    """True si la ruta termina en .pdf (sin distinguir mayúsculas)."""
    return ruta.lower().endswith(".pdf")


def _clave_serie(nombre_base: str) -> str:
    """
    Devuelve la clave de 'serie' de un nombre de archivo: el nombre base
    sin la parte numérica final y sin separadores alrededor de ella.
    """
    base = re.sub(r"[\s._()\[\]-]*\d+[\s._()\[\]-]*$", "", nombre_base)
    return base.lower().strip()


def _clave_natural(texto: str) -> list[object]:
    """Ordena naturalmente (1, 2, 10 en lugar de 1, 10, 2)."""
    return [
        int(p) if p.isdigit() else p.lower()
        for p in re.split(r"(\d+)", texto)
        if p != ""
    ]


class PDFLogic:
    """
    Clase que maneja la lógica de combinación de PDFs.
    """

    def __init__(self) -> None:
        """
        Inicializa la lista de PDFs.
        """
        self.pdf_files: list[str] = []

    # ------------------------------------------------------------------
    # Gestión de la lista
    # ------------------------------------------------------------------

    def add_pdf(self, pdf_path: str) -> bool:
        """
        Agrega un archivo PDF a la lista si no está ya presente.

        Args:
            pdf_path (str): Ruta del archivo PDF a agregar.

        Returns:
            bool: True si se agregó, False si ya estaba en la lista.

        Raises:
            ValueError: Si la ruta no termina en .pdf.
            FileNotFoundError: Si el archivo no existe.
        """
        if not _es_pdf(pdf_path):
            raise ValueError(f"No es un archivo PDF: {pdf_path}")
        if not os.path.isfile(pdf_path):
            raise FileNotFoundError(f"No existe el archivo: {pdf_path}")
        if pdf_path not in self.pdf_files:
            self.pdf_files.append(pdf_path)
            return True
        return False

    def add_pdfs(self, rutas: Iterable[str]) -> tuple[int, int, list[str]]:
        """
        Agrega varias rutas de una vez, validando cada una.

        Args:
            rutas (Iterable[str]): Rutas a agregar.

        Returns:
            tuple[int, int, list[str]]: (agregados, ya_presentes, errores).
        """
        agregados = 0
        ya_presentes = 0
        errores: list[str] = []
        for ruta in rutas:
            try:
                if self.add_pdf(ruta):
                    agregados += 1
                else:
                    ya_presentes += 1
            except (ValueError, FileNotFoundError) as exc:
                errores.append(str(exc))
        return agregados, ya_presentes, errores

    def add_pdfs_de_carpeta(self, carpeta: str) -> tuple[int, int, list[str]]:
        """
        Agrega todos los PDF de una carpeta (solo nivel superior) ordenados
        por nombre.

        Args:
            carpeta (str): Ruta de la carpeta a escanear.

        Returns:
            tuple[int, int, list[str]]: (agregados, ya_presentes, errores).

        Raises:
            NotADirectoryError: Si la carpeta no existe o no es un directorio.
        """
        if not os.path.isdir(carpeta):
            raise NotADirectoryError(f"No es una carpeta válida: {carpeta}")
        rutas = sorted(
            os.path.join(carpeta, nombre)
            for nombre in os.listdir(carpeta)
            if _es_pdf(nombre)
        )
        return self.add_pdfs(rutas)

    def remove_indices(self, indices: Iterable[int]) -> None:
        """
        Remueve varios archivos de la lista por índice.

        Los índices inválidos se ignoran silenciosamente.

        Args:
            indices (Iterable[int]): Índices a remover.
        """
        for idx in sorted(set(indices), reverse=True):
            if 0 <= idx < len(self.pdf_files):
                self.pdf_files.pop(idx)

    def clear(self) -> None:
        """Vacía la lista de archivos PDF."""
        self.pdf_files.clear()

    def move_block_to(self, indices: Iterable[int], target_first: int) -> list[int]:
        """
        Coloca el bloque formado por `indices` de modo que el primero
        quede en `target_first`, preservando el orden relativo interno.

        Args:
            indices (Iterable[int]): Índices actuales del bloque.
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
        resto = [ruta for i, ruta in enumerate(self.pdf_files) if i not in set(sel)]
        resto[target_first:target_first] = seleccionados
        self.pdf_files[:] = resto
        return list(range(target_first, target_first + k))

    def move(self, indices: Iterable[int], delta: int) -> list[int]:
        """
        Mueve el bloque seleccionado delta posiciones (delta -1 = subir,
        +1 = bajar). Si el bloque ya está en el borde correspondiente no
        hace nada.

        Args:
            indices (Iterable[int]): Índices actuales del bloque.
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

    def get_pdf_list(self) -> list[str]:
        """
        Devuelve la lista actual de archivos PDF.

        Returns:
            list[str]: Lista de rutas de archivos PDF.
        """
        return self.pdf_files.copy()

    def indices_duplicados(self) -> list[int]:
        """
        Devuelve los índices de la lista cuyo nombre de archivo base
        (sin distinguir mayúsculas) aparece más de una vez.
        """
        if not self.pdf_files:
            return []
        nombres = [os.path.basename(r).lower() for r in self.pdf_files]
        repetidos = {
            nombre for nombre, cantidad in Counter(nombres).items() if cantidad > 1
        }
        return [i for i, nombre in enumerate(nombres) if nombre in repetidos]

    def organizar_por_serie(self) -> None:
        """
        Reordena la lista agrupando por 'serie' (prefijo del nombre de
        archivo hasta la parte numérica final) y, dentro de cada serie,
        ordena por número de forma natural.
        """
        self.pdf_files.sort(
            key=lambda r: (
                _clave_serie(os.path.basename(r)),
                _clave_natural(os.path.basename(r)),
            )
        )

    # ------------------------------------------------------------------
    # Combinación
    # ------------------------------------------------------------------

    def combine_pdfs(self, output_path: str) -> None:
        """
        Combina los PDFs en la lista y guarda el resultado.

        Args:
            output_path (str): Ruta donde guardar el PDF combinado.

        Raises:
            ValueError: Si la lista está vacía.
            Exception: Si ocurre un error durante la combinación.
        """
        if not self.pdf_files:
            raise ValueError("No hay PDFs en la lista para combinar.")
        merger = PdfMerger()
        try:
            for pdf in self.pdf_files:
                with open(pdf, "rb") as f:
                    merger.append(f)
            merger.write(output_path)
        finally:
            merger.close()

    @staticmethod
    def is_admin() -> bool:
        """
        Verifica si el usuario tiene privilegios de administrador.

        Returns:
            bool: True si es administrador, False en caso contrario.
        """
        if os.name == "nt":
            try:
                import ctypes

                return bool(ctypes.windll.shell32.IsUserAnAdmin())  # type: ignore[attr-defined]
            except Exception:
                return False
        try:
            return os.geteuid() == 0
        except AttributeError:
            return False

    def combine_and_delete_originals(self, output_path: str) -> ResultadoEliminado:
        """
        Combina los PDFs y elimina los archivos originales (requiere permisos).

        Args:
            output_path (str): Ruta donde guardar el PDF combinado.

        Returns:
            tuple: (bool, str o list) - (éxito, mensaje o lista de fallos).

        Raises:
            Exception: Si ocurre un error durante la combinación.
        """
        if not self.pdf_files:
            raise ValueError("No hay PDFs en la lista para combinar.")
        if not self.is_admin():
            return (
                False,
                "Se requieren permisos de administrador para eliminar archivos.",
            )

        # Primero combinar
        self.combine_pdfs(output_path)

        # Luego intentar eliminar los originales
        failed_deletions: list[tuple[str, str]] = []
        for pdf in self.pdf_files:
            try:
                os.remove(pdf)
            except OSError as exc:
                failed_deletions.append((pdf, str(exc)))

        if failed_deletions:
            return False, failed_deletions
        return (
            True,
            f"PDFs combinados y originales eliminados exitosamente en:\n{output_path}",
        )
