"""Fig. 10(a): cavitation stress vs l/R0.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.

Usage:  python3 scripts/figures/fig10a.py
"""

import _bootstrap  # noqa: F401

from _analytical import draw_fig10a
from _style import new_axes, save
from msg_hydrogen import Params


def main():
    fig, ax = new_axes(figsize=(4.96, 4.32))
    draw_fig10a(ax, Params())
    fig.tight_layout()
    save(fig, "fig10a.pdf")


if __name__ == "__main__":
    main()
