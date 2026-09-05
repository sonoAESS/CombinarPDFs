---
name: test-gui-headless
description: Use when running the pytest suite of CombinadorPDFs, especially the GUI tests that need a display. Covers DISPLAY/xvfb-run, the automatic skip logic in tests/conftest.py, running subsets, and avoiding blocking Tk messagebox dialogs in tests.
---

# Ejecutar los tests (incluidos los de GUI) de CombinadorPDFs

## Cuándo usar esta skill

- Para ejecutar la suite de pytest o un subconjunto de tests.
- Cuando los tests de GUI fallan o se cuelgan por falta de pantalla o por
  diálogos de `messagebox` que bloquean.

## Regla de oro

Los tests de GUI necesitan un servidor X/Wayland. Si no hay `DISPLAY`, la
fixture `tk` de `tests/conftest.py` hace `pytest.skip("No hay display...")` y
esos tests no se ejecutan (quedan "skip", no "pass"), por lo que el recuento de
pasados bajará. Usa siempre un display para verificar la suite completa.

## Comandos

```bash
# Con display conocido (p. ej. :1)
env DISPLAY=:1 entorno/bin/python -m pytest -q

# Headless en Linux (más fiable en CI o sin sesión gráfica)
xvfb-run -a entorno/bin/python -m pytest -q

# Subconjunto (un fichero, un test, o excluyendo)
env DISPLAY=:1 entorno/bin/python -m pytest tests/test_pdf_gui.py -q
env DISPLAY=:1 entorno/bin/python -m pytest tests/test_pdf_logic.py::test_organizar_por_serie -q
env DISPLAY=:1 entorno/bin/python -m pytest tests/ -q -k "not drop"
```

## Contar los tests y verificar la suite

- La suite completa debe dar 34 passed, 1 warning (cierre de la advertencia de
  deprecación de PyPDF2; es esperada y no se debe silenciar).
- Antes de cada commit: `ruff check .`, `mypy .` y la suite completa con
  `DISPLAY=:1` o `xvfb-run -a`.

## Fixtures disponibles (tests/conftest.py)

- `crear_pdf`: fabrica un PDF real en `tmp_path`. Uso: `ruta = crear_pdf("a.pdf", paginas=3)`.
- `tk`: raíz Tk oculta; se salta el test si no hay display.
- `app`: instancia de `PDFCombinerApp` sobre la raíz `tk`.
- `paginas_de(ruta)`: número de páginas de un PDF.

## Errores comunes

### Tests que se cuelgan (sin salida, timeout)

Suele ser un `messagebox` real abriéndose en mitad de un test. Los diálogos
bloquean el bucle de Tk esperando clic del usuario. Solución: parchear el
`messagebox` con `monkeypatch`:

```python
monkeypatch.setattr("pdf_gui.messagebox.showwarning", lambda *a, **k: None)
monkeypatch.setattr("pdf_gui.messagebox.showinfo", lambda *a, **k: None)
```

Aplica también `askyesno`/`showerror` si el test los dispara. La marca de
duplicados (test_duplicados_marcados_en_naranja) sobrescribe `status_var` con
un mensaje transitorio; llama a `app.actualizar_estado()` antes de comprobar la
barra de estado.

### Test "skipped" que debería correr

El test no se ejecuta porque no hay `DISPLAY`. Ejecútalo con `DISPLAY=:1` o
`xvfb-run -a`; nunca lo "arregles" quitando el display.