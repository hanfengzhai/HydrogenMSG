"""Fig. 11(e): void FEM vs closed form.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.
Panel titles stay plain text (no mathtext).

Usage:  python3 scripts/figures/fig11e.py
"""

import _bootstrap  # noqa: F401

from _fem import fig11e


if __name__ == "__main__":
    fig11e()
