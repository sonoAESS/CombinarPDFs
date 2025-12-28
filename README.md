# Combinador de PDFs

Esta aplicación permite combinar múltiples archivos PDF en uno solo mediante una interfaz gráfica intuitiva.

## Características

- Seleccionar y agregar archivos PDF desde el explorador de archivos.
- Reordenar los PDFs en la lista antes de combinarlos.
- Eliminar PDFs de la lista.
- Combinar los PDFs y guardar el resultado en un archivo nuevo.

## Requisitos

- Python 3.x
- Bibliotecas: tkinter, ttkthemes, PyPDF2

## Instalación

1. Clona o descarga este repositorio.
2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Ejecuta la aplicación:
   ```
   python main.py
   ```

## Uso

1. Ejecuta `main.py`.
2. Haz clic en "Agregar PDFs" para seleccionar archivos.
3. Reordena si es necesario usando "Subir" y "Bajar".
4. Elimina archivos seleccionados con "Eliminar Seleccionado".
5. Haz clic en "Combinar PDFs" y selecciona dónde guardar el archivo resultante.

## Estructura del Proyecto

- `main.py`: Punto de entrada de la aplicación.
- `pdf_gui.py`: Interfaz gráfica de usuario.
- `pdf_logic.py`: Lógica para combinar PDFs.
- `requirements.txt`: Dependencias del proyecto.
- `README.md`: Este archivo de documentación.

## Contribuciones

Si deseas contribuir, por favor crea un issue o envía un pull request.

## Licencia

Este proyecto está bajo la Licencia MIT.
