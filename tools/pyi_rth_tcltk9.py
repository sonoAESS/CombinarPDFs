"""
Runtime hook de PyInstaller para Tcl/Tk 9.

Cuando Tcl/Tk se empaqueta manualmente (caso de intérpretes que traen
Tcl/Tk 9 no detectados por el hook estándar), este hook apunta las
variables TCL_LIBRARY y TK_LIBRARY a las carpetas incluidas en el
ejecutable. En otros entornos es un no-op.
"""

import os
import sys

base = getattr(sys, "_MEIPASS", None)
if base:
    for variable, carpeta in (("TCL_LIBRARY", "tcl9.0"), ("TK_LIBRARY", "tk9.0")):
        ruta = os.path.join(base, carpeta)
        if os.path.isdir(ruta):
            os.environ[variable] = ruta
