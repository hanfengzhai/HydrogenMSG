"""Generate every standalone manuscript subfigure.

Usage:  python3 scripts/make_figures.py

Delegates to ``scripts/figures/make_all_panels.py``. Outputs go to ``figures/``.
"""

import os
import runpy
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PANEL = os.path.join(_HERE, "figures", "make_all_panels.py")

if __name__ == "__main__":
    sys.path.insert(0, os.path.join(_HERE, "figures"))
    sys.path.insert(0, _HERE)
    runpy.run_path(_PANEL, run_name="__main__")
