"""Permite ejecutar la aplicación con `python -m filepilot`."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
