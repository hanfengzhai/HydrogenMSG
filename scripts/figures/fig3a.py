"""Fig. 3(a): normalized torque vs twist.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.

Usage:  python3 scripts/figures/fig3a.py
"""

import _bootstrap  # noqa: F401

from _analytical import draw_fig3a
from _style import new_axes, save
from msg_hydrogen import Params


def main():
    fig, ax = new_axes(figsize=(4.48, 4.0))
    draw_fig3a(ax, Params())
    fig.tight_layout()
    save(fig, "fig3a.pdf")


if __name__ == "__main__":
    main()
