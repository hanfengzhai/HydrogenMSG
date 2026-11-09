"""Fig. 8(a): void geometry schematic.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.
Panel titles stay plain text (no mathtext).

Usage:  python3 scripts/figures/fig8a.py
"""

import _bootstrap  # noqa: F401

from _schematics import make_fig8a


def main():
    make_fig8a()


if __name__ == "__main__":
    main()
