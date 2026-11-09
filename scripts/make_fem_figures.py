"""Generate FEM subfigures (fig4*, fig7*, fig11*).

Usage:  python3 scripts/make_fem_figures.py

Outputs go to ``figures/``.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figures"))
sys.path.insert(0, _HERE)

import _bootstrap  # noqa: F401
from _fem import (L_OVER_R0, MESH,  # noqa: F401 — re-export for mesh scripts
                  fig4a, fig4b, fig4c, fig7a, fig7b, fig7c, fig11a, fig11b,
                  fig11c, fig11d, fig11e, fig11f)


if __name__ == "__main__":
    for fn in (fig4a, fig4b, fig4c, fig7a, fig7b, fig7c,
               fig11a, fig11b, fig11c, fig11d, fig11e, fig11f):
        fn()
    print("done")
