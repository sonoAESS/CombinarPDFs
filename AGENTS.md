# AGENTS.md

Guía para agentes de IA que trabajan en **CombinadorPDFs**.

## Proyecto

Aplicación de escritorio en Python/tkinter que combina varios PDFs en uno solo,
con tema oscuro Sun Valley (`sv-ttk`), arrastrar y soltar interno y desde el
gestor de archivos (`tkinterdnd2`), detección de duplicados y agrupación por
serie. Se empaqueta con PyInstaller y publica ejecutables para Windows y Linux
vía GitHub Actions.

- Python `>=3.10`, Tk 8.6 o 9.x.
- Runtime: `PyPDF2`, `sv-ttk`, `tkinterdnd2`.
- Desarrollo: `ruff`, `mypy` (strict), `pre-commit`, `pytest`, `pyinstaller`.

## Comandos

El entorno virtual vive en `entorno/` (no tocar ni commitear; ya está en
`.gitignore`).

```bash
# Instalar el paquete + extras de desarrollo
entorno/bin/pip install ".[dev]"

# Ejecutar la aplicación (requiere una sesión gráfica)
entorno/bin/python main.py

# Lint y formato
entorno/bin/ruff check .
entorno/bin/ruff format --check .

# Tipos (usa stubs/; mypy_path está en pyproject.toml)
entorno/bin/mypy .

# Tests
entro/bin/python -m pytest -q            # en una sesión con pantalla
env DISPLAY=:1 entorno/bin/python -m pytest -q          # con display conocido
xvfb-run -a entorno/bin/python -m pytest -q             # headless (Linux)

# Hooks de pre-commit
entorno/bin/pre-commit run --all-files
```

Regla de oro: **los tests de GUI necesitan una ventana**. En Linux/BSD requieren
una pantalla X/Wayland: si no hay `DISPLAY`, la fixture `tk` de
`tests/conftest.py` salta esos tests automáticamente; para ejecutarlos en un
entorno sin gráficos usa `xvfb-run -a`. En Windows y macOS se ejecutan de forma
nativa (sin `DISPLAY`). Ejecuta la suite completa (34 tests) antes de cada commit.

## Estructura

```
main.py                 Punto de entrada: crear_ventana() y main()
pdf_gui.py              Interfaz gráfica (PDFCombinerApp)
pdf_logic.py            Lógica de negocio (PDFLogic y utilidades)
tests/                  pytest (conftest.py con fixtures tk/app/crear_pdf/paginas_de)
stubs/                  Stubs de tipos para tkinterdnd2 (para mypy)
tools/                  Generación del icono y runtime hooks de PyInstaller
assets/                 Icono (icon.png e icon.ico)
CombinadorPDFs.spec     Spec de PyInstaller
.github/workflows/      CI: job test (ruff + pytest) y job build/release
```

## Convenciones

- Documentación, mensajes de usuario, comentarios y commits en **español**.
- Type hints completos en todo el código; pasan `ruff` (reglas
  E/F/I/UP/B/SIM/W) y `mypy --strict`.
- No añadir comentarios de relleno; solo cuando aclaran una decisión.
- `pdf_logic.py` expone resultados explícitos (tuplas `(bool, str)` o conteos),
  no excepciones internas para flujos esperados. La GUI traduce esos resultados
  a `messagebox`/estado.
- El resaltado de duplicados usa `COLOR_DUPLICADO = "#e8a33d"`.
- Cambios relevantes se anotan en `CHANGELOG.md` (sección "No publicado").

## Cambios en el empaquetado

- `CombinadorPDFs.spec`: con Tk 9.x hay que empaquetar la subcarpeta de tkdnd
  `-tcl9` (el hook automático solo recoge la de Tcl 8). Ver la función
  `_recoleccion_tkdnd()` en el spec.
- Para generar el ejecutable: `entorno/bin/pyinstaller --noconfirm --clean CombinadorPDFs.spec`

## Git

- Ramas y tags en `main`; los tags `v*.*.*` disparan la release automática
  (ejecutables en GitHub Releases).
- No subir nunca `entorno/`, cachés ni ficheros de build (están en `.gitignore`).
- Mensajes de commit concisos en español siguiendo el estilo del historial
  (p. ej. "fase 4: drag-and-drop ...").