"""Fig. 4(a): torsion FEM effective stress.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.
Panel titles stay plain text (no mathtext).

Usage:  python3 scripts/figures/fig4a.py
"""

import _bootstrap  # noqa: F401

from _fem import fig4a


if __name__ == "__main__":
    fig4a()
