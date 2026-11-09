"""Fig. 5(c): lattice and trapped H schematic.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.
Panel titles stay plain text (no mathtext).

Usage:  python3 scripts/figures/fig5c.py
"""

import _bootstrap  # noqa: F401

from _schematics import make_fig5c


def main():
    make_fig5c()


if __name__ == "__main__":
    main()
