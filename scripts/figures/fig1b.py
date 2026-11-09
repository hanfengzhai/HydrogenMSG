"""Fig. 1(b): three canonical problems.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.
Panel titles stay plain text (no mathtext).

Usage:  python3 scripts/figures/fig1b.py
"""

import _bootstrap  # noqa: F401

from _schematics import make_fig1b


def main():
    make_fig1b()


if __name__ == "__main__":
    main()
