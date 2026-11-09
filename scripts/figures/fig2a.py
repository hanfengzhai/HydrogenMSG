"""Fig. 2(a): torsion geometry schematic.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.
Panel titles stay plain text (no mathtext).

Usage:  python3 scripts/figures/fig2a.py
"""

import _bootstrap  # noqa: F401

from _schematics import make_fig2a


def main():
    make_fig2a()


if __name__ == "__main__":
    main()
