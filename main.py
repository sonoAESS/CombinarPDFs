"""Lanzador que ejecuta la aplicación sin instalar el paquete."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from combinadorpdfs.main import main  # noqa: E402

if __name__ == "__main__":
    main()
