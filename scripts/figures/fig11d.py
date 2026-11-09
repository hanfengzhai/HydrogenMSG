"""Fig. 11(d): void FEM trapped hydrogen contour.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.
Panel titles stay plain text (no mathtext).

Usage:  python3 scripts/figures/fig11d.py
"""

import _bootstrap  # noqa: F401

from _fem import fig11d


if __name__ == "__main__":
    fig11d()
