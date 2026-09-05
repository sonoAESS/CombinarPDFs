# MEJORAS.md — Plan de Mejoras para CombinarPDFs

## Fase 1: Limpieza y Configuración Base
| # | Tarea | Archivos |
|---|---|---|
| 1.1 | Crear `pyproject.toml` con metadata, dependencias y scripts | `pyproject.toml` |
| 1.2 | Configurar `ruff` (linter + formatter) | `pyproject.toml` |
| 1.3 | Configurar `mypy` para type hints | `pyproject.toml` |
| 1.4 | Agregar `pre-commit` hooks | `.pre-commit-config.yaml` |
| 1.5 | Eliminar `requirements.txt` y `requirements-dev.txt` | — |
| 1.6 | Eliminar directorio `anteriores/` | — |
| 1.7 | Eliminar `llm_translator.py` | — |
| 1.8 | Agregar archivo `LICENSE` (MIT) | `LICENSE` |

## Fase 2: Calidad de Código
| # | Tarea | Archivos |
|---|---|---|
| 2.1 | Corregir bare `except` → `except Exception:` | `pdf_logic.py:145` |
| 2.2 | Hacer import de `ctypes` lazy (solo Windows) | `pdf_logic.py` |
| 2.3 | Agregar validación de existencia y extensión `.pdf` en `add_pdf()` | `pdf_logic.py` |
| 2.4 | Conectar botón "Combinar y eliminar originales" en GUI | `pdf_gui.py` |
| 2.5 | Agregar type hints a funciones públicas | `pdf_logic.py`, `pdf_gui.py` |
| 2.6 | Ejecutar `ruff format` y `ruff check --fix` | Todos los `.py` |

## Fase 3: Tests
| # | Tarea | Archivos |
|---|---|---|
| 3.1 | Configurar `pytest` y `pytest-tk` | `pyproject.toml` |
| 3.2 | Crear estructura `tests/` | `tests/` |
| 3.3 | Tests unitarios para `pdf_logic.py` | `tests/test_pdf_logic.py` |
| 3.4 | Tests de GUI básicos | `tests/test_pdf_gui.py` |
| 3.5 | Test de integración completo | `tests/test_integration.py` |

## Fase 4: Completar TODO
| # | Tarea | Archivos |
|---|---|---|
| 4.1 | Drag-and-drop desde gestor de archivos (tkinterdnd2) | `pdf_gui.py`, `pyproject.toml` |
| 4.2 | Resaltar duplicados en naranja | `pdf_gui.py` |
| 4.3 | Organizar PDFs por extensión al seleccionar carpeta | `pdf_gui.py`, `pdf_logic.py` |

## Fase 5: CI/CD y Release
| # | Tarea | Archivos |
|---|---|---|
| 5.1 | Actualizar workflow para usar `pyproject.toml` | `release.yml` |
| 5.2 | Agregar job de linting en CI | `release.yml` |
| 5.3 | Agregar job de tests en CI | `release.yml` |
| 5.4 | Agregar `CHANGELOG.md` | `CHANGELOG.md` |
