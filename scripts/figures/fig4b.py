"""Fig. 4(b): torsion FEM trapped hydrogen.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.
Panel titles stay plain text (no mathtext).

Usage:  python3 scripts/figures/fig4b.py
"""

import _bootstrap  # noqa: F401

from _fem import fig4b


if __name__ == "__main__":
    fig4b()
