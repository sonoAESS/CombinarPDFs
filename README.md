# Combinador de PDFs

[![Builds](https://github.com/sonoAESS/CombinarPDFs/actions/workflows/release.yml/badge.svg)](https://github.com/sonoAESS/CombinarPDFs/actions/workflows/release.yml)
[![Release](https://img.shields.io/github/v/release/sonoAESS/CombinarPDFs)](https://github.com/sonoAESS/CombinarPDFs/releases/latest)

Esta aplicación permite combinar múltiples archivos PDF en uno solo mediante una interfaz gráfica intuitiva.

## Descargas

Ejecutables listos para usar en la página de
[Releases](https://github.com/sonoAESS/CombinarPDFs/releases):

- **Windows**: `CombinadorPDFs-windows-x64.exe` — doble clic y listo.
- **Linux**: `CombinadorPDFs-linux-x64.bin` — dale permisos de ejecución y ábrelo:
  ```bash
  chmod +x CombinadorPDFs-linux-x64.bin
  ./CombinadorPDFs-linux-x64.bin
  ```

## Características

- Seleccionar y agregar archivos PDF desde el explorador de archivos.
- Agregar una carpeta completa (los archivos se agrupan por serie, es decir,
  se ordenan por su nombre base y número, p. ej. `capitulo1.pdf`, `capitulo2.pdf`...).
- Arrastrar y soltar archivos PDF desde el gestor de archivos a la ventana.
- Los archivos duplicados se omiten y se marcan en naranja si ya están en la lista.
- Multiselección en la lista (Ctrl+clic, Shift+clic o arrastrando el ratón).
- Reordenar los PDFs antes de combinarlos: botones Subir/Bajar, menú contextual
  (clic derecho) o arrastrando y soltando las filas directamente.
- Eliminar uno o varios archivos a la vez (botón, clic derecho o tecla Supr),
  o vaciar toda la lista con confirmación.
- Barra de estado con contador de archivos, selección actual y duplicados.
- Combinar los PDFs y guardar el resultado en un archivo nuevo, o combinarlos
  y eliminar los originales en un solo paso.
- Interfaz oscura moderna (tema Sun Valley) compatible con Linux, Windows y macOS.

## Requisitos

- Python 3.10+ (compatible también con Tk 9.x)
- Bibliotecas: tkinter, sv-ttk, PyPDF2, tkinterdnd2

## Instalación

El proyecto es un paquete de Python gestionado con `pyproject.toml`:

1. Clona o descarga este repositorio.
2. (Opcional) Crea un entorno virtual.
3. Instala el paquete con sus extras de desarrollo (incluye las herramientas
   de calidad y los tests):
   ```
   pip install ".[dev]"
   ```
   Para instalarlo solo como dependencia de ejecución: `pip install .`
4. Ejecuta la aplicación:
   ```
   python main.py
   ```
   o, instalada globalmente: `combinador-pdfs`

### Tests

```
pytest
```

Los tests de interfaz requieren un fichero de pantalla; en un entorno sin
pantalla usa `xvfb-run -a pytest`.

### Construir el ejecutable

Con las dependencias de desarrollo instaladas, genera el binario de tu
plataforma con:

```
pyinstaller --noconfirm --clean CombinadorPDFs.spec
```

El resultado queda en `dist/`. Para generar los ejecutables de Windows y Linux
automáticamente, basta con crear un tag `v*.*.*` y subirlo: GitHub Actions
compila ambos y los adjunta a la release.

## Uso

1. Ejecuta `main.py`.
2. Haz clic en "Agregar PDFs" para seleccionar archivos (los duplicados se omiten),
   en "Agregar Carpeta" para cargar una carpeta (agrupada por serie),
   o arrastra y suelta archivos desde el gestor de archivos.
3. Selecciona uno o varios archivos con Ctrl+clic, Shift+clic o arrastrando.
4. Reordénalos con "Subir"/"Bajar", con el menú contextual (clic derecho)
   o arrastrando las filas a su posición.
5. Elimina lo seleccionado con "Eliminar Seleccionados" o la tecla Supr;
   usa "Vaciar Lista" para empezar de cero.
6. Haz clic en "Combinar PDFs" y selecciona dónde guardar el archivo resultante.
   Con "Combinar y eliminar originales" además se borran los archivos de origen
   tras combinar.

## Estructura del Proyecto

- `main.py`: Punto de entrada de la aplicación.
- `pdf_gui.py`: Interfaz gráfica de usuario.
- `pdf_logic.py`: Lógica para combinar PDFs.
- `pyproject.toml`: Configuración del paquete, dependencias y herramientas (ruff, mypy, pytest).
- `assets/`: Icono de la aplicación (PNG e ICO).
- `tools/`: Scripts auxiliares (generación del icono, hooks de PyInstaller).
- `stubs/`: Stubs de tipos para tkinterdnd2.
- `tests/`: Tests unitarios, de interfaz e integración (pytest).
- `CombinadorPDFs.spec`: Configuración de PyInstaller para los ejecutables.
- `.github/workflows/release.yml`: CI que ejecuta los tests y publica releases.
- `CHANGELOG.md`: Historial de cambios.
- `README.md`: Este archivo de documentación.

## Contribuciones

Si deseas contribuir, por favor crea un issue o envía un pull request.

## Licencia

Este proyecto está bajo la Licencia MIT.