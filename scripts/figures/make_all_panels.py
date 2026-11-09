"""Regenerate every standalone subfigure PDF (fig1a … fig12f).

Usage:  python3 scripts/figures/make_all_panels.py
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

import fig3b as _fig3b
import fig3c as _fig3c
import fig6a as _fig6a
import fig6c as _fig6c
import fig6_fields as _fig6_fields
from _analytical import (draw_fig3a, draw_fig6b, draw_fig6d, draw_fig9a,
                         draw_fig9b, draw_fig9c, draw_fig9d, draw_fig10a,
                         draw_fig10b)
from _fem import (fig4a, fig4b, fig4c, fig7a, fig7b, fig7c, fig11a, fig11b,
                  fig11c, fig11d, fig11e, fig11f, fig12mesh, fig12conv,
                  fig12a, fig12b, fig12c, fig12d, fig12e, fig12f)
from _schematics import (make_fig1a, make_fig1b, make_fig2a, make_fig2b,
                         make_fig2c, make_fig5a, make_fig5b, make_fig5c,
                         make_fig8a, make_fig8b, make_fig8c)
from _style import new_axes, save
from msg_hydrogen import Params
import fig_mechanism as _fig_mechanism


def _run_analytical(stem, drawer, figsize):
    fig, ax = new_axes(figsize=figsize)
    drawer(ax, Params())
    fig.tight_layout()
    save(fig, f"{stem}.pdf")


def main():
    print("=== schematics ===")
    _fig_mechanism.main()
    for fn in (make_fig1a, make_fig1b, make_fig2a, make_fig2b, make_fig2c,
               make_fig5a, make_fig5b, make_fig5c, make_fig8a, make_fig8b,
               make_fig8c):
        fn()

    print("=== analytical ===")
    # fig3b/fig3c share a fixed canvas; fig6_fields is the paired bending panel.
    _fig3b.main()
    _fig3c.main()
    _fig6a.main()
    _fig6c.main()
    _fig6_fields.main()
    for stem, drawer, fs in (
            ("fig3a", draw_fig3a, (4.48, 4.0)),
            ("fig6b", draw_fig6b, (5.0, 5.2)),
            ("fig6d", draw_fig6d, (4.5, 4.68)),
            ("fig9a", draw_fig9a, (5.0, 5.2)),
            ("fig9b", draw_fig9b, (5.0, 5.2)),
            ("fig9c", draw_fig9c, (5.0, 5.2)),
            ("fig9d", draw_fig9d, (5.0, 5.2)),
            ("fig10a", draw_fig10a, (4.96, 4.32)),
            ("fig10b", draw_fig10b, (4.96, 4.32)),
    ):
        _run_analytical(stem, drawer, fs)

    print("=== FEM (slow) ===")
    for fn in (fig4a, fig4b, fig4c, fig7a, fig7b, fig7c,
               fig11a, fig11b, fig11c, fig11d, fig11e, fig11f,
               fig12mesh, fig12conv,
               fig12a, fig12b, fig12c, fig12d, fig12e, fig12f):
        fn()

    print("done")


if __name__ == "__main__":
    main()
