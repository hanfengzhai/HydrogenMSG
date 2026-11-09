"""Fig. 11(c): void FEM strain gradient contour.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.
Panel titles stay plain text (no mathtext).

Usage:  python3 scripts/figures/fig11c.py
"""

import _bootstrap  # noqa: F401

from _fem import fig11c


if __name__ == "__main__":
    fig11c()
