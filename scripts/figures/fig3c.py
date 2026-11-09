"""Fig. 3(c): uptake enhancement Q(a) vs wire radius.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.

Usage:  python3 scripts/figures/fig3c.py
"""

import _bootstrap  # noqa: F401

import matplotlib.pyplot as plt

from _analytical import draw_fig3c
from _style import apply_style, save
from msg_hydrogen import Params

# Same fixed canvas and axes box as fig3b so the two panels match exactly.
# Leave room for y-label and log-tick labels so panels do not collide in LaTeX.
FIGSIZE = (4.48, 4.0)
AXES_RECT = [0.18, 0.16, 0.74, 0.78]


def main():
    apply_style()
    fig = plt.figure(figsize=FIGSIZE)
    ax = fig.add_axes(AXES_RECT)
    draw_fig3c(ax, Params())
    save(fig, "fig3c.pdf", fixed_canvas=True)


if __name__ == "__main__":
    main()
