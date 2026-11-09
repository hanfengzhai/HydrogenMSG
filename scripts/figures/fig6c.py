"""Fig. 6(c): trapped hydrogen through the beam thickness.

Same figure *height* and vertical axes box as fig6a.py so side-by-side
panels align, but a tight left margin (no y-label / tick labels). Manuscript
includes both at equal display height so the axes line up.

Usage:  python3 scripts/figures/fig6c.py
"""

import _bootstrap  # noqa: F401

import matplotlib.pyplot as plt

from _analytical import draw_fig6c
from _style import apply_style, save
from msg_hydrogen import Params

# Match fig6a vertical layout (bottom, height); tighter left (no ylabel).
# Axes data width ≈ fig6a: 0.70*4.4 = 3.08 in → width = 3.08/0.90 ≈ 3.42
FIGSIZE = (3.42, 4.4)
AXES_RECT = [0.06, 0.22, 0.90, 0.74]


def main():
    apply_style()
    fig = plt.figure(figsize=FIGSIZE)
    ax = fig.add_axes(AXES_RECT)
    draw_fig6c(ax, Params())
    save(fig, "fig6c.pdf", fixed_canvas=True, crop=False)


if __name__ == "__main__":
    main()
