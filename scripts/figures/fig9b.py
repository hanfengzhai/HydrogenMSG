"""Fig. 9(b): mean stress around a void.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.

Usage:  python3 scripts/figures/fig9b.py
"""

import _bootstrap  # noqa: F401

from _analytical import draw_fig9b
from _style import new_axes, save
from msg_hydrogen import Params


def main():
    fig, ax = new_axes(figsize=(5.0, 5.2))
    draw_fig9b(ax, Params())
    fig.tight_layout()
    save(fig, "fig9b.pdf")


if __name__ == "__main__":
    main()
