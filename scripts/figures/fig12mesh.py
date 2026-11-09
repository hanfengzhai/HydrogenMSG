"""Fig. 12 mesh: tip-graded Q9 mode-I slit mesh (SI).

Math labels use matplotlib mathtext: wrap symbols in `$...$`.
Do not use `$$`. Panel titles stay plain text.

Usage:  python3 scripts/figures/fig12mesh.py
"""

import _bootstrap  # noqa: F401

from _fem import fig12mesh


if __name__ == "__main__":
    fig12mesh()
