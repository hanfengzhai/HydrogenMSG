"""Fig. 9(a): effective stress around a void.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.

Usage:  python3 scripts/figures/fig9a.py
"""

import _bootstrap  # noqa: F401

from _analytical import draw_fig9a
from _style import new_axes, save
from msg_hydrogen import Params


def main():
    fig, ax = new_axes(figsize=(5.0, 5.2))
    draw_fig9a(ax, Params())
    fig.tight_layout()
    save(fig, "fig9a.pdf")


if __name__ == "__main__":
    main()
