"""Fig. 3(b): trapped hydrogen profiles at fixed Gamma.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.

Usage:  python3 scripts/figures/fig3b.py
"""

import _bootstrap  # noqa: F401

import matplotlib.pyplot as plt

from _analytical import draw_fig3b
from _style import apply_style, save
from msg_hydrogen import Params

# Same fixed canvas and axes box as fig3c so the two panels match exactly.
# Leave room on the right so the r/a = 1.0 tick is not clipped in the PDF.
FIGSIZE = (4.48, 4.0)
AXES_RECT = [0.18, 0.16, 0.74, 0.78]


def main():
    apply_style()
    fig = plt.figure(figsize=FIGSIZE)
    ax = fig.add_axes(AXES_RECT)
    draw_fig3b(ax, Params())
    save(fig, "fig3b.pdf", fixed_canvas=True)


if __name__ == "__main__":
    main()
