"""Compatibility entry point; the active implementation lives in ADAPT/TOOLS."""
import sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "TOOLS"))
from supporting_modules.operator import *

if __name__ == "__main__":
    sys.exit(main())
