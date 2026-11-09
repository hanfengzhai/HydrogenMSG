"""Fig. 7(a): bending FEM mean stress.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.
Panel titles stay plain text (no mathtext).

Usage:  python3 scripts/figures/fig7a.py
"""

import _bootstrap  # noqa: F401

from _fem import fig7a


if __name__ == "__main__":
    fig7a()
