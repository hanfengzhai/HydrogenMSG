"""Fig. 12(f): mode-I slit FEM + HELP softening panel.

Math labels use matplotlib mathtext: wrap symbols in `$...$`.
Do not use `$$`. Panel titles stay plain text.

Usage:  python3 scripts/figures/fig12f.py
"""

import _bootstrap  # noqa: F401

from _fem import fig12f


if __name__ == "__main__":
    fig12f()
