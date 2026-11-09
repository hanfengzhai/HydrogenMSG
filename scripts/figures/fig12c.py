"""Fig. 12(c): mode-I slit FEM + HELP softening panel.

Math labels use matplotlib mathtext: wrap symbols in `$...$`.
Do not use `$$`. Panel titles stay plain text.

Usage:  python3 scripts/figures/fig12c.py
"""

import _bootstrap  # noqa: F401

from _fem import fig12c


if __name__ == "__main__":
    fig12c()
