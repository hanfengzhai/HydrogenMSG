"""Fig. 12(e): mode-I slit FEM + HELP softening panel.

Math labels use matplotlib mathtext: wrap symbols in `$...$`.
Do not use `$$`. Panel titles stay plain text.

Usage:  python3 scripts/figures/fig12e.py
"""

import _bootstrap  # noqa: F401

from _fem import fig12e


if __name__ == "__main__":
    fig12e()
