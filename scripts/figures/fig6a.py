"""Fig. 6(a): mean stress through the beam thickness.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.

Usage:  python3 scripts/figures/fig6a.py
"""

import _bootstrap  # noqa: F401

import matplotlib.pyplot as plt

from _analytical import draw_fig6a
from _style import apply_style, save
from msg_hydrogen import Params

# Shared with fig6c so the manuscript panels (b) and (c) have identical axes.
# Left/bottom margins sized so the rotated $x_2/h$ and math x-labels stay
# inside the fixed canvas at FONT_SIZE=15 (no post-crop).
FIGSIZE = (4.4, 4.4)
AXES_RECT = [0.24, 0.22, 0.70, 0.74]


def main():
    apply_style()
    fig = plt.figure(figsize=FIGSIZE)
    ax = fig.add_axes(AXES_RECT)
    draw_fig6a(ax, Params())
    save(fig, "fig6a.pdf", fixed_canvas=True, crop=False)


if __name__ == "__main__":
    main()
