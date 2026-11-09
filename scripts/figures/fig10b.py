"""Fig. 10(b): hydrogen knockdown map.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.

Usage:  python3 scripts/figures/fig10b.py
"""

import _bootstrap  # noqa: F401

from _analytical import draw_fig10b
from _style import new_axes, save
from msg_hydrogen import Params


def main():
    fig, ax = new_axes(figsize=(4.96, 4.32))
    draw_fig10b(ax, Params())
    fig.tight_layout()
    save(fig, "fig10b.pdf")


if __name__ == "__main__":
    main()
