"""Fig. 8(c): cavitation and traps schematic.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.
Panel titles stay plain text (no mathtext).

Usage:  python3 scripts/figures/fig8c.py
"""

import _bootstrap  # noqa: F401

from _schematics import make_fig8c


def main():
    make_fig8c()


if __name__ == "__main__":
    main()
