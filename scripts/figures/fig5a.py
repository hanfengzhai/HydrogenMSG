"""Fig. 5(a): bending geometry schematic.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.
Panel titles stay plain text (no mathtext).

Usage:  python3 scripts/figures/fig5a.py
"""

import _bootstrap  # noqa: F401

from _schematics import make_fig5a


def main():
    make_fig5a()


if __name__ == "__main__":
    main()
