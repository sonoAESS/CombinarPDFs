# Combinador de PDFs

Esta aplicación permite combinar múltiples archivos PDF en uno solo mediante una interfaz gráfica intuitiva.

## Características

- Seleccionar y agregar archivos PDF desde el explorador de archivos.
- Multiselección en la lista (Ctrl+clic, Shift+clic o arrastrando el ratón).
- Reordenar los PDFs antes de combinarlos: botones Subir/Bajar, menú contextual
  (clic derecho) o arrastrando y soltando las filas directamente.
- Eliminar uno o varios archivos a la vez (botón, clic derecho o tecla Supr),
  o vaciar toda la lista con confirmación.
- Barra de estado con contador de archivos y selección actual.
- Combinar los PDFs y guardar el resultado en un archivo nuevo.
- Interfaz oscura moderna (tema Sun Valley) compatible con Linux, Windows y macOS.

## Requisitos

- Python 3.8+ (compatible también con Tk 9.x)
- Bibliotecas: tkinter, sv-ttk, PyPDF2

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
2. Haz clic en "Agregar PDFs" para seleccionar archivos (los duplicados se omiten).
3. Selecciona uno o varios archivos con Ctrl+clic, Shift+clic o arrastrando.
4. Reordénalos con "Subir"/"Bajar", con el menú contextual (clic derecho)
   o arrastrando las filas a su posición.
5. Elimina lo seleccionado con "Eliminar Seleccionados" o la tecla Supr;
   usa "Vaciar Lista" para empezar de cero.
6. Haz clic en "Combinar PDFs" y selecciona dónde guardar el archivo resultante.

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
