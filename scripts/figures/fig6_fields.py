"""Composed bending through-thickness fields: sigma_m | c_T.

One canvas with sharey so the axes boxes align, with no fake left
margin on the right panel. Used by the manuscript as fig6_fields.

Usage:  python3 scripts/figures/fig6_fields.py
"""

import _bootstrap  # noqa: F401

import matplotlib.pyplot as plt

from _analytical import draw_fig6a, draw_fig6c
from _style import apply_style, save
from msg_hydrogen import Params


def main():
    apply_style()
    fig, (ax_a, ax_b) = plt.subplots(
        1, 2, figsize=(9.2, 4.4), sharey=True,
        gridspec_kw={"wspace": 0.10})
    draw_fig6a(ax_a, Params())
    draw_fig6c(ax_b, Params())
    # sharey keeps tick positions; suppress labels on the right panel only.
    ax_b.tick_params(axis="y", labelleft=False)
    ax_b.set_ylabel("")
    fig.subplots_adjust(left=0.09, right=0.995, bottom=0.15, top=0.97,
                        wspace=0.12)
    save(fig, "fig6_fields.pdf", fixed_canvas=True, crop=True)


if __name__ == "__main__":
    main()
