"""Fig. 6(d): average uptake vs beam thickness.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.

Usage:  python3 scripts/figures/fig6d.py
"""

import _bootstrap  # noqa: F401

from _analytical import draw_fig6d
from _style import new_axes, save
from msg_hydrogen import Params


def main():
    fig, ax = new_axes(figsize=(4.5, 4.68))
    draw_fig6d(ax, Params())
    fig.tight_layout()
    save(fig, "fig6d.pdf")


if __name__ == "__main__":
    main()
