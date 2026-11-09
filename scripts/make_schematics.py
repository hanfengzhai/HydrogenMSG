"""Generate schematic subfigures (fig1*, fig2*, fig5*, fig8*).

Usage:  python3 scripts/make_schematics.py

Outputs go to ``figures/``.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figures"))
sys.path.insert(0, _HERE)

import _bootstrap  # noqa: F401
from _schematics import (make_fig1a, make_fig1b, make_fig2a, make_fig2b,
                         make_fig2c, make_fig5a, make_fig5b, make_fig5c,
                         make_fig8a, make_fig8b, make_fig8c)


if __name__ == "__main__":
    for fn in (make_fig1a, make_fig1b, make_fig2a, make_fig2b, make_fig2c,
               make_fig5a, make_fig5b, make_fig5c, make_fig8a, make_fig8b,
               make_fig8c):
        fn()
    print("done")
