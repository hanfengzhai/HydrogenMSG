"""Fig. 7(b): bending FEM trapped hydrogen.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.
Panel titles stay plain text (no mathtext).

Usage:  python3 scripts/figures/fig7b.py
"""

import _bootstrap  # noqa: F401

from _fem import fig7b


if __name__ == "__main__":
    fig7b()
