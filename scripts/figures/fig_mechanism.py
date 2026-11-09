"""Fig. mechanism: two-panel one-way MSG–hydrogen trapping schematic.

(a) Stress-assisted redistribution: σ_m gradient → lattice H enrichment
(b) Dislocation trapping: ρ_T → N_T; reversed-T sites with fractional occupancy
Synthesis: c_T = N_T θ_T

Deterministic matplotlib (no AI, no RNG). Style matches other paper figures.

Usage:  python3 scripts/figures/fig_mechanism.py
"""

from __future__ import annotations

import os

import _bootstrap  # noqa: F401

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgb
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyArrowPatch, PathPatch, Rectangle
from matplotlib.path import Path as MplPath

from _style import FONT_SIZE, OUT, apply_style

_FS = FONT_SIZE
_COLOR = "#1a1a1a"
_DISL = "#2a2a2a"
_H_FREE_EDGE = "black"
_H_FREE_BLUE = "#7EB8E8"  # shallow blue (rim)
_H_FREE_WHITE = "#FFFFFF"  # white (center)
_H_TRAP = "#1B3A6B"
_ARROW = "#2F4A56"
_EDGE = "#404040"
_FIELD_EDGE = "#B0B0B0"

_CMAP_A = "coolwarm"
_CMAP_B = "BuPu"

# Panel A / B field boxes (data coords on a shared 0–1 canvas).
# Leave a clear gap above the slabs so the N_T label does not sit on panel (b).
_A = dict(x0=0.04, x1=0.46, y0=0.30, y1=0.74)
_B = dict(x0=0.54, x1=0.96, y0=0.30, y1=0.74)

# Shared vertical stack (figure-fraction coords)
_CBAR_LABEL_Y = 0.955
_CBAR_Y0, _CBAR_Y1 = 0.900, 0.930
_CBAR_TICK_Y = 0.885
_EQ_B_Y = 0.805
_PANEL_LABEL_Y = 0.235


def _draw_cbar(ax, x0, x1, cmap, label):
    bx0, bx1 = x0 + 0.04, x1 - 0.04
    grad = np.linspace(0.0, 1.0, 200)[None, :]
    ax.imshow(
        grad, extent=(bx0, bx1, _CBAR_Y0, _CBAR_Y1), origin="lower",
        aspect="auto", cmap=cmap, vmin=0, vmax=1, interpolation="bilinear",
        zorder=9, alpha=0.85,
    )
    ax.add_patch(Rectangle(
        (bx0, _CBAR_Y0), bx1 - bx0, _CBAR_Y1 - _CBAR_Y0,
        fill=False, edgecolor=_EDGE, linewidth=0.7, zorder=10,
    ))
    ax.text(
        0.5 * (bx0 + bx1), _CBAR_LABEL_Y, label,
        ha="center", va="center", fontsize=_FS, color=_COLOR, zorder=10,
    )
    ax.text(bx0, _CBAR_TICK_Y, "Lower", ha="left", va="top",
            fontsize=_FS, color=_COLOR, zorder=10)
    ax.text(bx1, _CBAR_TICK_Y, "Higher", ha="right", va="top",
            fontsize=_FS, color=_COLOR, zorder=10)


def _wavy_field_path(x0, x1, y0, y1, n_per_side=40, amp=0.012, n_waves=2.5):
    """Closed wavy boundary for an unbounded-field excerpt."""
    segs = []
    t = np.linspace(0.0, 1.0, n_per_side, endpoint=False)
    # bottom L→R
    segs.append(np.column_stack([
        x0 + t * (x1 - x0),
        y0 - amp * np.sin(2.0 * np.pi * n_waves * t),
    ]))
    # right B→T
    segs.append(np.column_stack([
        x1 + amp * np.sin(2.0 * np.pi * n_waves * t + 0.4),
        y0 + t * (y1 - y0),
    ]))
    # top R→L
    segs.append(np.column_stack([
        x1 - t * (x1 - x0),
        y1 + amp * np.sin(2.0 * np.pi * n_waves * t + 0.8),
    ]))
    # left T→B
    segs.append(np.column_stack([
        x0 - amp * np.sin(2.0 * np.pi * n_waves * t + 1.2),
        y1 - t * (y1 - y0),
    ]))
    pts = np.vstack(segs)
    verts = np.vstack([pts, pts[0:1]])
    codes = np.full(len(verts), MplPath.LINETO, dtype=np.uint8)
    codes[0] = MplPath.MOVETO
    codes[-1] = MplPath.CLOSEPOLY
    return MplPath(verts, codes)


def _draw_field_border(ax, x0, x1, y0, y1):
    path = _wavy_field_path(x0, x1, y0, y1)
    patch = PathPatch(
        path, facecolor="none", edgecolor=_FIELD_EDGE,
        linewidth=1.0, linestyle=(0, (4.0, 2.8)), alpha=0.55, zorder=8,
    )
    ax.add_patch(patch)
    return path


def _draw_lattice_h(ax, x, y, *, r=0.008, lw=1.05, zorder=4, n=48):
    """Lattice H: black outline, shallow-blue → white radial fill."""
    blue = np.asarray(to_rgb(_H_FREE_BLUE))
    white = np.asarray(to_rgb(_H_FREE_WHITE))
    yy, xx = np.mgrid[-1:1:n * 1j, -1:1:n * 1j]
    rho = np.sqrt(xx * xx + yy * yy)
    # rim = shallow blue (rho=1), interior = white (rho=0);
    # soft power keeps a visible blue ring at small glyph sizes
    t = np.clip(rho, 0.0, 1.0) ** 0.65
    t = t[..., None]
    rgba = np.empty((n, n, 4))
    rgba[..., :3] = (1.0 - t) * white + t * blue
    rgba[..., 3] = (rho <= 1.0).astype(float)
    ax.imshow(
        rgba, extent=(x - r, x + r, y - r, y + r), origin="lower",
        aspect="auto", interpolation="bilinear", zorder=zorder,
    )
    ax.add_patch(Circle(
        (x, y), r, facecolor="none", edgecolor=_H_FREE_EDGE,
        linewidth=lw, zorder=zorder + 1,
    ))


def _draw_perp(ax, x, y, angle_deg=0.0, *, size=0.024, lw=1.1, zorder=5):
    ang = np.deg2rad(angle_deg)
    e1 = np.array([np.cos(ang), np.sin(ang)])
    e2 = np.array([-np.sin(ang), np.cos(ang)])
    half = 0.45 * size
    stem = 0.80 * size
    p_l = np.array([x, y]) - half * e1
    p_r = np.array([x, y]) + half * e1
    p_tip = np.array([x, y]) + stem * e2
    ax.add_line(Line2D(
        [p_l[0], p_r[0]], [p_l[1], p_r[1]],
        color=_DISL, lw=lw, solid_capstyle="butt", zorder=zorder,
    ))
    ax.add_line(Line2D(
        [x, p_tip[0]], [y, p_tip[1]],
        color=_DISL, lw=lw, solid_capstyle="butt", zorder=zorder,
    ))
    return x, y


def _draw_panel_a(ax):
    """(a) Stress-assisted redistribution."""
    x0, x1, y0, y1 = _A["x0"], _A["x1"], _A["y0"], _A["y1"]
    _draw_cbar(ax, x0, x1, _CMAP_A, r"Mean stress $\sigma_{\mathrm{m}}$")
    ax.text(
        0.5 * (x0 + x1), _PANEL_LABEL_Y, "(a)",
        ha="center", va="top", fontsize=_FS, color=_COLOR, zorder=10,
    )
    pad = 0.015
    path = _draw_field_border(ax, x0, x1, y0, y1)
    im = ax.imshow(
        np.linspace(0.0, 1.0, 300)[None, :],
        extent=(x0 - pad, x1 + pad, y0 - pad, y1 + pad),
        origin="lower", aspect="auto", cmap=_CMAP_A, vmin=0, vmax=1,
        interpolation="bilinear", zorder=0, alpha=0.48,
    )
    im.set_clip_path(path, transform=ax.transData)

    # Lattice H: sparse left → denser right
    left = [
        (0.10, 0.70), (0.14, 0.58), (0.12, 0.46),
        (0.16, 0.64), (0.11, 0.38),
    ]
    mid = [
        (0.22, 0.72), (0.26, 0.62), (0.30, 0.70),
        (0.24, 0.52), (0.28, 0.44), (0.32, 0.56),
        (0.25, 0.36), (0.31, 0.48),
    ]
    right = [
        (0.36, 0.72), (0.40, 0.66), (0.42, 0.74),
        (0.38, 0.58), (0.42, 0.52), (0.40, 0.44),
        (0.36, 0.40), (0.42, 0.36), (0.38, 0.68),
        (0.41, 0.60), (0.37, 0.50), (0.43, 0.48),
    ]
    for x, y in left + mid + right:
        _draw_lattice_h(ax, x, y)

    for x0a, y0a, x1a, y1a, rad in (
        (0.14, 0.62, 0.38, 0.62, 0.05),
        (0.15, 0.48, 0.39, 0.48, 0.04),
    ):
        ax.add_patch(FancyArrowPatch(
            (x0a, y0a), (x1a, y1a),
            connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>", mutation_scale=7,
            color=_ARROW, lw=0.70, alpha=0.75, zorder=3,
        ))


def _draw_panel_b(ax):
    """(b) Dislocation trapping."""
    x0, x1, y0, y1 = _B["x0"], _B["x1"], _B["y0"], _B["y1"]
    _draw_cbar(
        ax, x0, x1, _CMAP_B,
        r"Dislocation density $\rho_{\mathrm{T}}$",
    )
    ax.text(
        0.5 * (x0 + x1), _PANEL_LABEL_Y, "(b)",
        ha="center", va="top", fontsize=_FS, color=_COLOR, zorder=10,
    )

    pad = 0.015
    path = _draw_field_border(ax, x0, x1, y0, y1)
    im = ax.imshow(
        np.linspace(0.0, 1.0, 300)[None, :],
        extent=(x0 - pad, x1 + pad, y0 - pad, y1 + pad),
        origin="lower", aspect="auto", cmap=_CMAP_B, vmin=0, vmax=1,
        interpolation="bilinear", zorder=0, alpha=0.48,
    )
    im.set_clip_path(path, transform=ax.transData)

    # Plain text above the slab (no bbox) so nothing overlaps the schematic.
    ax.text(
        0.5 * (x0 + x1), _EQ_B_Y,
        r"$N_{\mathrm{T}}=\chi\rho_{\mathrm{T}}/b$",
        ha="center", va="center", fontsize=_FS, color=_COLOR, zorder=10,
        clip_on=False,
    )

    sparse = [
        (0.60, 0.62, -2, False),
        (0.64, 0.48, 3, False),
        (0.58, 0.40, -4, True),
        (0.66, 0.68, 2, False),
    ]
    dense = [
        (0.74, 0.70, -3, False),
        (0.78, 0.66, 2, True),
        (0.84, 0.70, -2, True),
        (0.90, 0.66, 4, True),
        (0.74, 0.58, 1, False),
        (0.80, 0.54, -4, True),
        (0.86, 0.58, 3, True),
        (0.92, 0.52, -1, True),
        (0.76, 0.44, 2, False),
        (0.82, 0.42, -5, True),
        (0.88, 0.46, 1, True),
        (0.78, 0.36, -2, True),
        (0.86, 0.34, 3, True),
    ]
    for x, y, ang, occupied in sparse + dense:
        jx, jy = _draw_perp(ax, x, y, ang)
        if occupied:
            ax.add_patch(Circle(
                (jx, jy), 0.0075, facecolor=_H_TRAP, edgecolor="white",
                linewidth=0.35, zorder=6,
            ))


def _draw_synthesis_and_legend(ax):
    ax.text(
        0.50, 0.155,
        r"$c_{\mathrm{T}}=N_{\mathrm{T}}\,\theta_{\mathrm{T}}$",
        ha="center", va="center", fontsize=_FS, color=_COLOR, zorder=10,
    )

    y = 0.055
    entries = [
        (0.06, 0.10, "free", r"Lattice $H$"),
        (0.30, 0.34, "trap", r"Trapped $H$"),
        (0.56, 0.60, "perp", "Trap site"),
        (0.78, 0.82, "arrow", "Redistribution"),
    ]
    for xs, xt, kind, label in entries:
        if kind == "free":
            _draw_lattice_h(ax, xs, y, r=0.009, zorder=21)
        elif kind == "perp":
            _draw_perp(ax, xs, y + 0.004, 0.0, size=0.022, lw=1.1, zorder=21)
        elif kind == "trap":
            _draw_perp(ax, xs, y + 0.004, 0.0, size=0.022, lw=1.1, zorder=21)
            ax.add_patch(Circle(
                (xs, y + 0.004), 0.007, facecolor=_H_TRAP,
                edgecolor="white", linewidth=0.3, zorder=22,
            ))
        elif kind == "arrow":
            ax.add_patch(FancyArrowPatch(
                (xs - 0.016, y), (xs + 0.016, y),
                arrowstyle="-|>", mutation_scale=6,
                color=_ARROW, lw=0.70, alpha=0.85, zorder=21,
            ))
        ax.text(
            xt, y, label, ha="left", va="center",
            fontsize=_FS, color=_COLOR, zorder=21,
        )


def make_fig_mechanism():
    apply_style()

    fig_w, fig_h = 7.4, 3.8
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)

    _draw_panel_a(ax)
    _draw_panel_b(ax)
    _draw_synthesis_and_legend(ax)

    path = os.path.join(OUT, "fig_mechanism.pdf")
    png = path.replace(".pdf", ".png")
    meta = {"CreationDate": None}
    fig.savefig(path, metadata=meta)
    fig.savefig(png, dpi=220, metadata=meta)
    plt.close(fig)
    print(f"wrote {os.path.relpath(path)}")
    return path


def main():
    make_fig_mechanism()


if __name__ == "__main__":
    main()
