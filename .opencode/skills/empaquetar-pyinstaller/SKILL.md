---
name: empaquetar-pyinstaller
description: Use when building the executable of CombinadorPDFs with PyInstaller from CombinadorPDFs.spec, editing the spec, or debugging tkinterdnd2/Tk 9 bundling failures in the frozen binary.
---

# Empaquetar CombinadorPDFs con PyInstaller

## Cuándo usar esta skill

- Para generar el ejecutable (Windows/Linux) con `CombinadorPDFs.spec`.
- Para tocar el spec o diagnosticar un binario que crashea al arrancar por
  fallos de tkinterdnd2, sv-ttk o Tcl/Tk 9.

## Comando de build

```bash
entorno/bin/pyinstaller --noconfirm --clean CombinadorPDFs.spec
```

El resultado queda en `dist/CombinadorPDFs` (Linux) o `dist/CombinadorPDFs.exe`
(Windows). No commitear `build/` ni `dist/` (están en `.gitignore`).

## Partes del spec que se tocan con frecuencia

### tkinterdnd2 y Tk 9 (trampa conocida)

- tkinterdnd2 busca su librería tkdnd en `tkinterdnd2/tkdnd/<plataforma>-tcl9`
  cuando el intérprete usa Tcl 9.x (Tk 9.0).
- El hook automático de `pyinstaller-hooks-contrib` aún solo recoge la subcarpeta
  compilada para Tcl 8 (`linux-x64`, `win-x64`, ...). Si el hueco se omitese, el
  binario crashea al arrancar con:

  ```
  RuntimeError: Unable to load tkdnd library.
  _tkinter.TclError: this extension is compiled for Tcl 8.x
  ```

- Por eso el spec llama a `_recoleccion_tkdnd()`, que empaqueta la subcarpeta
  `-tcl9` correspondiente a la plataforma (`win-x64-tcl9`, `linux-x64-tcl9`, ...).
  Mantener esta función si se actualiza el spec.

### Tcl/Tk 9 en intérpretes "build-standalone"

- Si el intérprete trae Tcl/Tk 9 en `sys.prefix/lib` (p. ej. python-build-standalone
  o uv), el hook estándar no lo detecta: el spec añade manualmente
  `libtcl9*.so`/`libtk9*.so` y las carpetas `tcl9.0`/`tk9.0` en `binaries_tcltk`/
  `datas_tcltk`. Con Tk 8.6 no se activa.

### sv-ttk e icono

- `collect_all("sv_ttk")` empaqueta temas y binarios del tema Sun Valley.
- El icono se empaqueta con `assets/icon.png` (datas) y, en Windows, se embebe
  `assets/icon.ico` en el EXE.

## Verificar el binario tras compilar

1. Ejecutarlo en una sesión gráfica durante unos segundos y comprobar que se
   queda activo (si sale solo con traceback, falló al arrancar):

   ```bash
   timeout 30 env DISPLAY=:1 ./dist/CombinadorPDFs & BGPID=$!; sleep 12
   kill -0 $BGPID && echo "OK, activo" && kill $BGPID
   ```

2. En la app en vivo: arrastrar un PDF desde el gestor de archivos a la lista
   (valida que tkdnd se cargó) y probar "Combinar PDFs".

## CI (GitHub Actions)

- El job `build` compila con `pip install . pyinstaller` y el mismo spec.
- Los tags `v*.*.*` publican los artefactos en la GitHub Release. Para probar
  el spec sin hacer release, usar `workflow_dispatch`.