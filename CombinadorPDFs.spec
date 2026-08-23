# -*- mode: python ; coding: utf-8 -*-
"""
Spec de PyInstaller multiplataforma para CombinadorPDFs.

Genera un ejecutable único (onefile) sin consola:
  - Windows: dist/CombinadorPDFs.exe (con assets/icon.ico embebido)
  - Linux:   dist/CombinadorPDFs

Uso:
    pyinstaller --noconfirm --clean CombinadorPDFs.spec
"""

import glob
import os
import sys

from PyInstaller.utils.hooks import collect_all

sv_datas, sv_binaries, sv_hiddenimports = collect_all("sv_ttk")

icono = "assets/icon.ico" if sys.platform == "win32" else None

# ------------------------------------------------------------------
# Tcl/Tk 9: algunos intérpretes (p. ej. python-build-standalone/uv)
# traen Tcl/Tk 9 en sys.prefix/lib que el hook estándar de PyInstaller
# no detecta. Se empaquetan manualmente solo en ese caso; con Tk 8.6
# el hook por defecto ya lo hace bien.
# ------------------------------------------------------------------
binaries_tcltk = []
datas_tcltk = []

for prefijo in dict.fromkeys([getattr(sys, "base_prefix", sys.prefix), sys.prefix]):
    libdir = os.path.join(prefijo, "lib")
    if glob.glob(os.path.join(libdir, "libtcl9*.so*")):
        for patron in ("libtcl*.so*", "libtk*.so*"):
            binaries_tcltk += [(ruta, ".") for ruta in glob.glob(os.path.join(libdir, patron))]
        for nombre in ("tcl9.0", "tk9.0"):
            ruta = os.path.join(libdir, nombre)
            if os.path.isdir(ruta):
                datas_tcltk.append((ruta, nombre))
        break

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=sv_binaries + binaries_tcltk,
    datas=[("assets/icon.png", "assets")] + sv_datas + datas_tcltk,
    hiddenimports=sv_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["tools/pyi_rth_tcltk9.py"],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="CombinadorPDFs",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icono,
)
