"""Fig. 4(c): torsion FEM vs closed form.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.
Panel titles stay plain text (no mathtext).

Usage:  python3 scripts/figures/fig4c.py
"""

import _bootstrap  # noqa: F401

from _fem import fig4c


if __name__ == "__main__":
    fig4c()
