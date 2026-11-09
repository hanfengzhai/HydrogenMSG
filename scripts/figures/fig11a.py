"""Fig. 11(a): void FEM mean stress contour.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.
Panel titles stay plain text (no mathtext).

Usage:  python3 scripts/figures/fig11a.py
"""

import _bootstrap  # noqa: F401

from _fem import fig11a


if __name__ == "__main__":
    fig11a()
