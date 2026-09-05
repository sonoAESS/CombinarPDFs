# Historial de cambios

Todas las versiones notables de CombinadorPDFs se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es/1.1.0/) y las versiones siguen [Versionado Semántico](https://semver.org/lang/es/).

## [No publicado]

### Añadido

- Arrastrar y soltar archivos PDF desde el gestor de archivos a la ventana.
- Botón "Agregar Carpeta": carga todos los PDFs de una carpeta agrupados por serie
  (orden natural según su nombre base y número).
- Los archivos duplicados de una carga se detectan y se marcan en naranja en la lista.
- Resaltado de la fila que se arrastra dentro de la lista y selección de destino al soltar.
- Botón "Combinar y eliminar originales": combina los PDFs y borra los originales
  tras confirmarlo.
- Configuración del repositorio con `pyproject.toml`: paquete con entry point
  `combinador-pdfs`, extras de desarrollo, y configuración de ruff, mypy y pytest.
- Pre-commit con hooks de ruff, ruff-format, mypy y trucos básicos de git.
- Licencia MIT para el proyecto.
- Suite de tests (unitarios, de GUI e integración) con pytest.

### Cambiado

- `pdf_logic.py` devuelve tuplas con resultados explícitos (`affected_rows` cambiado
  por conteos detallados) en lugar de lanzar excepciones internas.
- `is_admin()` usa `ctypes.windll` de forma perezosa y solo en Windows.
- `main.py` expone `crear_ventana()` (usa `TkinterDnD.Tk()` con fallback a `tk.Tk()`) y `main()`.
- CI: el job de build instala el paquete desde `pyproject.toml` y añade un job de tests
  (ruff + pytest en Linux headless y Windows) antes de compilar.
- Python mínimo requerido elevado a 3.10.

### Eliminado

- `requirements.txt` y `requirements-dev.txt` (sustituidos por `pyproject.toml`).
- Carpeta `anteriores/` y `llm_translator.py` (prueba de concepto obsoleta).

## [1.1.0] - 2026-08-23

### Añadido

- Icono de la aplicación generado con Pillow e integrado en la ventana.
- Empaquetado con PyInstaller (`CombinadorPDFs.spec`) y releases automáticas
  en GitHub Actions para Windows y Linux.

### Cambiado

- Migrado el tema oscuro de `ttkthemes` a `sv-ttk` (Sun Valley) con soporte
  para Linux y Tk 9.x.
- Separadas las dependencias de ejecución y las de desarrollo.

### Añadido (antes de 1.1.0)

- Manejo avanzado de la lista: multiselección, arrastrar y soltar filas,
  menú contextual y teclas de acceso rápido.

## [1.0.0] - 2025-08-18

### Añadido

- Versión inicial del programa: combina varios PDFs en uno mediante una interfaz
  gráfica con tkinter.