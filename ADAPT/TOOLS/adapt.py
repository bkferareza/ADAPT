"""ADAPT read-only operator entry point."""
import sys
sys.dont_write_bytecode = True
from supporting_modules.operator import main

if __name__ == "__main__":
    sys.exit(main())
