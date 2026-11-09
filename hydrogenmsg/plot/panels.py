"""Registry of manuscript panel builders.

Each entry writes one or more PDFs under ``output/``.
"""

from __future__ import annotations

from collections.abc import Callable

import matplotlib.pyplot as plt

from hydrogenmsg.analytics import Params
from hydrogenmsg.plot import analytical as A
from hydrogenmsg.plot import fem_panels as F
from hydrogenmsg.plot import mechanism as M
from hydrogenmsg.plot import schematics as S
from hydrogenmsg.plot.style import apply_style, new_axes, save


def _analytical(stem: str, drawer, figsize) -> Callable[[], None]:
    def _run():
        fig, ax = new_axes(figsize=figsize)
        drawer(ax, Params())
        fig.tight_layout()
        save(fig, f"{stem}.pdf")

    _run.__name__ = stem
    _run.__doc__ = f"Write output/{stem}.pdf"
    return _run


def _fixed(stem: str, drawer, figsize, axes_rect, *, crop=False) -> Callable[[], None]:
    def _run():
        apply_style()
        fig = plt.figure(figsize=figsize)
        ax = fig.add_axes(axes_rect)
        drawer(ax, Params())
        save(fig, f"{stem}.pdf", fixed_canvas=True, crop=crop)

    _run.__name__ = stem
    return _run


def _fig6_fields() -> None:
    apply_style()
    fig, (ax_a, ax_b) = plt.subplots(
        1, 2, figsize=(9.2, 4.4), sharey=True,
        gridspec_kw={"wspace": 0.10},
    )
    A.draw_fig6a(ax_a, Params())
    A.draw_fig6c(ax_b, Params())
    ax_b.tick_params(axis="y", labelleft=False)
    ax_b.set_ylabel("")
    fig.subplots_adjust(left=0.09, right=0.995, bottom=0.15, top=0.97, wspace=0.12)
    save(fig, "fig6_fields.pdf", fixed_canvas=True, crop=True)


PANELS: dict[str, Callable[[], None]] = {
    # Schematics
    "fig_mechanism": M.main,
    "fig1a": S.make_fig1a,
    "fig1b": S.make_fig1b,
    "fig2a": S.make_fig2a,
    "fig2b": S.make_fig2b,
    "fig2c": S.make_fig2c,
    "fig5a": S.make_fig5a,
    "fig5b": S.make_fig5b,
    "fig5c": S.make_fig5c,
    "fig8a": S.make_fig8a,
    "fig8b": S.make_fig8b,
    "fig8c": S.make_fig8c,
    # Analytical (fixed canvas where the manuscript needs matched boxes)
    "fig3a": _analytical("fig3a", A.draw_fig3a, (4.48, 4.0)),
    "fig3b": _fixed("fig3b", A.draw_fig3b, (4.48, 4.0), [0.18, 0.16, 0.74, 0.78]),
    "fig3c": _fixed("fig3c", A.draw_fig3c, (4.48, 4.0), [0.18, 0.16, 0.74, 0.78]),
    "fig6a": _fixed("fig6a", A.draw_fig6a, (4.4, 4.4), [0.24, 0.22, 0.70, 0.74]),
    "fig6b": _analytical("fig6b", A.draw_fig6b, (5.0, 5.2)),
    "fig6c": _fixed("fig6c", A.draw_fig6c, (3.42, 4.4), [0.06, 0.22, 0.90, 0.74]),
    "fig6d": _analytical("fig6d", A.draw_fig6d, (4.5, 4.68)),
    "fig6_fields": _fig6_fields,
    "fig9a": _analytical("fig9a", A.draw_fig9a, (5.0, 5.2)),
    "fig9b": _analytical("fig9b", A.draw_fig9b, (5.0, 5.2)),
    "fig9c": _analytical("fig9c", A.draw_fig9c, (5.0, 5.2)),
    "fig9d": _analytical("fig9d", A.draw_fig9d, (5.0, 5.2)),
    "fig10a": _analytical("fig10a", A.draw_fig10a, (4.96, 4.32)),
    "fig10b": _analytical("fig10b", A.draw_fig10b, (4.96, 4.32)),
    # FEM
    "fig4a": F.fig4a,
    "fig4b": F.fig4b,
    "fig4c": F.fig4c,
    "fig7a": F.fig7a,
    "fig7b": F.fig7b,
    "fig7c": F.fig7c,
    "fig11a": F.fig11a,
    "fig11b": F.fig11b,
    "fig11c": F.fig11c,
    "fig11d": F.fig11d,
    "fig11e": F.fig11e,
    "fig11f": F.fig11f,
    "fig12mesh": F.fig12mesh,
    "fig12conv": F.fig12conv,
    "fig12a": F.fig12a,
    "fig12b": F.fig12b,
    "fig12c": F.fig12c,
    "fig12d": F.fig12d,
    "fig12e": F.fig12e,
    "fig12f": F.fig12f,
}

# Manuscript build order (schematics → analytical → FEM).
DEFAULT_ORDER: tuple[str, ...] = (
    "fig_mechanism",
    "fig1a", "fig1b",
    "fig2a", "fig2b", "fig2c",
    "fig5a", "fig5b", "fig5c",
    "fig8a", "fig8b", "fig8c",
    "fig3a", "fig3b", "fig3c",
    "fig6a", "fig6b", "fig6c", "fig6d", "fig6_fields",
    "fig9a", "fig9b", "fig9c", "fig9d",
    "fig10a", "fig10b",
    "fig4a", "fig4b", "fig4c",
    "fig7a", "fig7b", "fig7c",
    "fig11a", "fig11b", "fig11c", "fig11d", "fig11e", "fig11f",
    "fig12mesh", "fig12conv",
    "fig12a", "fig12b", "fig12c", "fig12d", "fig12e", "fig12f",
)


def run_panels(names: list[str] | None = None) -> None:
    todo = list(DEFAULT_ORDER if not names else names)
    unknown = [n for n in todo if n not in PANELS]
    if unknown:
        raise SystemExit(f"Unknown panel(s): {', '.join(unknown)}")
    for name in todo:
        print(f"=== {name} ===")
        PANELS[name]()
    print("done")
