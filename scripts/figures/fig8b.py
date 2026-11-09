"""Fig. 8(b): radial decay schematic.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.
Panel titles stay plain text (no mathtext).

Usage:  python3 scripts/figures/fig8b.py
"""

import _bootstrap  # noqa: F401

from _schematics import make_fig8b


def main():
    make_fig8b()


if __name__ == "__main__":
    main()
