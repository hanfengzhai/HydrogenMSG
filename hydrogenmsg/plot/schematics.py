"""Problem-setup schematics for the MSG-hydrogen paper.

Standalone panel makers write ``fig{N}{letter}.pdf``; compose functions
assemble the multi-panel PDFs used in the paper:

  compose_fig_overview()            -> fig_overview.pdf
  compose_fig_schematic_torsion()   -> fig_schematic_torsion.pdf
  compose_fig_schematic_bending() -> fig_schematic_bending.pdf
  compose_fig_schematic_void()      -> fig_schematic_void.pdf

Layout convention: composed figures are authored at printed width
(``FIGW`` inches, included at ``width=\\textwidth``).  Geometry panels
use inches as their data unit so circles stay round without
``set_aspect``.  Panel titles are plain text; axis labels and
annotations use ``$...$`` mathtext.
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import (Circle, Ellipse, FancyBboxPatch, Rectangle,
                                Wedge)

from hydrogenmsg.plot.style import (EDGE, FEED, FIGW, FILL, FILL2, FONT_SIZE, HYDR, MECH, OUT,
                    apply_style, fit_geom_panel, regular_font, save, title_font)

TITLE_FS = FONT_SIZE
LABEL_FS = FONT_SIZE
SMALL_FS = FONT_SIZE
TINY_FS = FONT_SIZE


def _apply_schematic_style():
    """Schematic figures: legends off-frame, slightly finer spines."""
    apply_style(**{
        "legend.frameon": False,
        "axes.linewidth": 0.7,
        "lines.linewidth": 1.2,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
    })


# ----------------------------------------------------------------------
# layout helpers
# ----------------------------------------------------------------------

def title(fig, xc, tag, text, y):
    """Panel title at a fixed figure height, so all panels align.

    Plain Libertinus Serif Regular only. No mathtext in titles (CM looks
    bold in Overleaf/pdf.js).
    """
    full = f"({tag}) {text}"
    if "$" in full:
        raise ValueError(f"panel titles must be plain text, got: {full!r}")
    fig.text(xc, y, full,
             ha="center", va="bottom", fontproperties=title_font(),
             fontweight="normal")


def geom_panel(fig, rect, figsize, tag=None, text=None, title_y=None,
               title_xc=None):
    """Axes whose data unit is one inch, for drawings that must stay round."""
    ax = fig.add_axes(rect)
    ax.set_xlim(0, rect[2] * figsize[0])
    ax.set_ylim(0, rect[3] * figsize[1])
    ax.axis("off")
    if tag is not None:
        title(fig, title_xc if title_xc is not None else rect[0] + rect[2] / 2,
              tag, text, title_y)
    return ax


def plot_panel(fig, rect, tag=None, text=None, title_y=None, title_xc=None):
    ax = fig.add_axes(rect)
    ax.tick_params(length=2.5, pad=2)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    if tag is not None:
        title(fig, title_xc if title_xc is not None else rect[0] + rect[2] / 2,
              tag, text, title_y)
    return ax


def note(ax, x, y, s, **kw):
    """Caption anchored in axes fractions, so it can never leave the panel."""
    kw.setdefault("ha", "center")
    kw.setdefault("va", "bottom")
    kw.setdefault("fontsize", SMALL_FS)
    kw.setdefault("color", "0.25")
    ax.text(x, y, s, transform=ax.transAxes, **kw)


def tbox(ax, xc, yc, w, h, title, equation=None, fc=FILL, fs=TINY_FS,
         weight="normal", *, edgecolor="black", lw=0.9, rounding=0.08):
    """Rounded box with a plain-text title and an optional mathtext equation.

    ``equation`` must be a full mathtext string wrapped in ``$...$``, e.g.
    ``r"$\\theta_{\\mathrm{T}}$"``. Title and equation are drawn as separate
    artists so a newline never enters the mathtext parser.
    """
    ax.add_patch(FancyBboxPatch(
        (xc - w / 2, yc - h / 2), w, h,
        boxstyle=f"round,pad=0.03,rounding_size={rounding}",
        facecolor=fc, edgecolor=edgecolor, linewidth=lw))
    if equation is None:
        ax.text(xc, yc, title, ha="center", va="center", fontsize=fs,
                fontweight=weight, color="black")
        return
    if "$" not in equation:
        raise ValueError(
            f"equation must use mathtext $...$, got: {equation!r}")
    # Title slightly above center; equation slightly below.
    ax.text(xc, yc + 0.18 * h, title, ha="center", va="center", fontsize=fs,
            fontweight=weight, color="black")
    ax.text(xc, yc - 0.22 * h, equation, ha="center", va="center",
            fontsize=fs, color="black")


def arrow(ax, p0, p1, color=EDGE, lw=0.9, ls="-", rad=0.0, scale=8,
          zorder=None):
    kw = {}
    if zorder is not None:
        kw["zorder"] = zorder
    ax.annotate("", xy=p1, xytext=p0,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                linestyle=ls, mutation_scale=scale,
                                shrinkA=0, shrinkB=0,
                                connectionstyle=f"arc3,rad={rad}"),
                **kw)


def arc_arrow(ax, center, rx, ry, th0, th1, color=MECH, lw=1.2, scale=9,
              zorder=None):
    """Elliptical arc terminated by an arrowhead: a readable torque symbol."""
    th = np.linspace(np.deg2rad(th0), np.deg2rad(th1), 60)
    x = center[0] + rx * np.cos(th)
    y = center[1] + ry * np.sin(th)
    plot_kw = {}
    if zorder is not None:
        plot_kw["zorder"] = zorder
    ax.plot(x[:-1], y[:-1], color=color, lw=lw, solid_capstyle="round",
            **plot_kw)
    arrow(ax, (x[-2], y[-2]), (x[-1], y[-1]), color=color, lw=lw, scale=scale,
          zorder=zorder)
    return x[-1], y[-1]


def dim(ax, p0, p1, color=EDGE, lw=0.7):
    ax.annotate("", xy=p1, xytext=p0,
                arrowprops=dict(arrowstyle="<->", color=color, lw=lw,
                                mutation_scale=6, shrinkA=0, shrinkB=0))


def bending_moment_arcs(ax, xL, yL, xR, yR, half, *,
                        gap=0.10, lw=1.2, scale=8, label=True,
                        label_fs=LABEL_FS, label_dx=0.04):
    """End moments drawn as arcs strictly *outside* the beam end faces.

    Beam is drawn hogging (center up, ∩). That deformation has tension on
    the top (extrados) and compression on the bottom (intrados), so the
    left end moment is counter-clockwise and the right end moment is
    clockwise in the plane of the figure.
    """
    r = 0.85 * half
    # Sweep almost the full half-circle so the terminating arrowhead points
    # clearly along the circulation and the two couples read as opposite.
    th = np.linspace(-0.92 * np.pi / 2, 0.92 * np.pi / 2, 60)
    # Left: bottom -> top through the west (CCW), entirely left of the face.
    cxL = xL - gap
    xLarc = cxL - r * np.cos(th)
    yLarc = yL + r * np.sin(th)
    ax.plot(xLarc[:-1], yLarc[:-1], color=MECH, lw=lw, solid_capstyle="round",
            zorder=5)
    arrow(ax, (xLarc[-2], yLarc[-2]), (xLarc[-1], yLarc[-1]),
          color=MECH, lw=lw, scale=scale, zorder=6)
    # Right: top -> bottom through the east (CW), entirely right of the face.
    thR = th[::-1]
    cxR = xR + gap
    xRarc = cxR + r * np.cos(thR)
    yRarc = yR + r * np.sin(thR)
    ax.plot(xRarc[:-1], yRarc[:-1], color=MECH, lw=lw, solid_capstyle="round",
            zorder=5)
    arrow(ax, (xRarc[-2], yRarc[-2]), (xRarc[-1], yRarc[-1]),
          color=MECH, lw=lw, scale=scale, zorder=6)
    if label:
        # Equal and opposite end couples: M on the left, -M on the right.
        ax.text(float(np.min(xLarc)) - label_dx, yL, r"$+M$", color=MECH,
                fontsize=label_fs, ha="right", va="center")
        ax.text(float(np.max(xRarc)) + label_dx, yR, r"$-M$", color=MECH,
                fontsize=label_fs, ha="left", va="center")


# ----------------------------------------------------------------------
# small reusable sketches (used by the overview thumbnails)
# ----------------------------------------------------------------------

def sketch_torsion(ax, cx, cy, r):
    """Short cylinder: equal-and-opposite end torques (not rigid-body spin)."""
    a = 0.55 * r
    y_bot, y_top = cy - 0.95 * r, cy + 0.95 * r
    ry = 0.28 * r
    ax.add_patch(Ellipse((cx, y_bot), 2 * a, 2 * ry, facecolor=FILL,
                         edgecolor=EDGE, lw=0.8, zorder=1))
    ax.add_patch(Rectangle((cx - a, y_bot), 2 * a, y_top - y_bot,
                           facecolor=FILL, edgecolor="none", zorder=2))
    ax.plot([cx - a, cx - a], [y_bot, y_top], color=EDGE, lw=0.8, zorder=3)
    ax.plot([cx + a, cx + a], [y_bot, y_top], color=EDGE, lw=0.8, zorder=3)
    ax.add_patch(Ellipse((cx, y_top), 2 * a, 2 * ry, facecolor="0.96",
                         edgecolor=EDGE, lw=0.8, zorder=4))
    # Equal and opposite end torques.
    arc_arrow(ax, (cx, y_top + 0.05 * r), 0.85 * a, 1.1 * ry, 200, 340,
              color=MECH, lw=0.8, scale=5, zorder=5)
    arc_arrow(ax, (cx, y_bot - 0.05 * r), 0.85 * a, 1.1 * ry, 20, 160,
              color=MECH, lw=0.8, scale=5, zorder=5)
    ax.text(cx + 1.15 * a, y_top + 0.15 * r, r"$T$", color=MECH,
            fontsize=TINY_FS, ha="left", va="bottom")
    ax.text(cx + 1.15 * a, y_bot - 0.15 * r, r"$-T$", color=MECH,
            fontsize=TINY_FS, ha="left", va="top")
    dim(ax, (cx, y_bot), (cx + a, y_bot))
    ax.text(cx + 0.5 * a, y_bot - 0.42 * r, r"$a$", fontsize=TINY_FS,
            ha="center", va="top", color=MECH)


def sketch_bending(ax, cx, cy, w, h):
    xs = np.linspace(cx - w / 2, cx + w / 2, 60)
    # Hogging (∩): mid high at center, lower at the ends.
    mid = cy - 0.55 * ((xs - cx) / (w / 2)) ** 2 * (h / 2)
    ax.fill_between(xs, mid - h / 2, mid + h / 2, facecolor=FILL,
                    edgecolor=EDGE, lw=0.9)
    ax.plot(xs, mid, ls=(0, (3, 2)), color="0.45", lw=0.6)
    bending_moment_arcs(ax, xs[0], mid[0], xs[-1], mid[-1], 0.42 * h,
                        gap=0.05, lw=1.0, scale=9, label=True,
                        label_fs=TINY_FS, label_dx=0.02)
    # Thickness dimension.
    xh = cx - 0.18 * w
    ym = float(np.interp(xh, xs, mid))
    dim(ax, (xh, ym - h / 2), (xh, ym + h / 2))
    ax.text(xh - 0.04 * w, ym, r"$h$", fontsize=TINY_FS, ha="right",
            va="center", color=MECH)
    ax.text(cx, cy - 1.35 * h, r"$\kappa$", ha="center", va="top",
            fontsize=TINY_FS, color=MECH)


def sketch_void(ax, cx, cy, r):
    """Remote hydrostatic tension on a large outer boundary; free void wall."""
    R0 = r
    Rout = 2.1 * r
    Rg = 1.3 * r
    ax.add_patch(Circle((cx, cy), Rout, facecolor="0.965", edgecolor=EDGE,
                        lw=0.7))
    ax.add_patch(Wedge((cx, cy), Rg, 0, 360, width=Rg - R0,
                       facecolor=FILL2, edgecolor="none"))
    ax.add_patch(Circle((cx, cy), R0, facecolor="white", edgecolor=EDGE,
                        lw=0.9))
    for ang in np.arange(22.5, 360, 45):
        th = np.deg2rad(ang)
        arrow(ax,
              (cx + 1.02 * Rout * np.cos(th), cy + 1.02 * Rout * np.sin(th)),
              (cx + 1.22 * Rout * np.cos(th), cy + 1.22 * Rout * np.sin(th)),
              color=MECH, lw=0.75, scale=4.5)
    ax.text(cx, cy - 1.30 * Rout, r"$\sigma^{\infty}$", ha="center",
            va="top", fontsize=TINY_FS, color=MECH)
    ax.text(cx, cy + 0.15 * R0, "Free", ha="center", va="bottom",
            fontsize=TINY_FS, color="0.4")
    dim(ax, (cx, cy), (cx + R0, cy))
    ax.text(cx + 0.55 * R0, cy - 0.22 * R0, r"$R_0$", fontsize=TINY_FS,
            ha="center", va="top", color=MECH)


# ----------------------------------------------------------------------
# shared panel drawers
# ----------------------------------------------------------------------

def draw_coupling_chain(ax, W, H):
    """Overview panel (a): MSG-hydrogen causal chain.

    TikZ-matched style (see ``paper/figures/fig1a.tikz``): white rounded
    boxes, ``gray!10`` key nodes, black ``Latex`` arrows, serif mathtext.

    Sequence: kinematics -> (eps_e, eta) -> MSG/Taylor -> (rho_T, sigma_e)/N_T.
    Mean stress comes from higher-order equilibrium and BCs (Eq. 6).
    HELP is a phenomenological amplitude loop only (Formulation A); the
    trap-density identity is not updated under that loop.
    """
    white, key = "white", "0.94"  # gray!10
    lw, arr_scale = 0.9, 10
    lx, rx = 0.26 * W, 0.74 * W
    bw, bh = 0.42 * W, 0.095 * H
    tw = 0.60 * W
    gap = 0.028 * H
    step = bh + gap
    # Eight rows: kinematics, (eps,eta), Taylor, (flow|NT),
    # higher-order eq/BCs, mean stress, theta_L, (theta_T|c_T).
    n_row = 8
    chain_h = (n_row - 1) * step + bh
    top = 0.50 * (H + chain_h) - 0.5 * bh
    lvl = [top - step * k for k in range(n_row)]
    cx = 0.5 * (lx + rx)

    def box(xc, yc, w, title, equation, fc=white):
        tbox(ax, xc, yc, w, bh, title, equation, fc=fc, weight="bold",
             edgecolor="black", lw=lw, rounding=0.09)

    box(cx, lvl[0], tw,
        "Kinematics and geometry",
        r"$u_i,\ \varepsilon_{ij}$")
    box(cx, lvl[1], tw,
        "Effective measures",
        r"$\varepsilon_{\mathrm{e}},\ \eta$")
    box(cx, lvl[2], tw,
        "MSG / Taylor identity",
        r"$\rho_{\mathrm{T}}=\rho_{\mathrm{S}}+\rho_{\mathrm{G}}$",
        fc=key)

    box(lx, lvl[3], bw,
        "Flow stress",
        r"$\sigma_{\mathrm{e}}=\sigma_{\mathrm{Y}}\sqrt{f^{2}+l\,\eta}$")
    box(rx, lvl[3], bw,
        "Trap-site density",
        r"$N_{\mathrm{T}}=\chi\rho_{\mathrm{T}}/b$")

    box(lx, lvl[4], bw,
        "Higher-order equilibrium and BCs",
        r"$\sigma'_{ik,i}-\tau'_{ijk,ij}+H_{,k}=0$")

    box(lx, lvl[5], bw,
        "Mean stress",
        r"$\sigma_{\mathrm{m}}$")

    box(lx, lvl[6], bw,
        "Lattice occupancy",
        r"$\theta_{\mathrm{L}}\propto e^{\sigma_{\mathrm{m}}"
        r"\bar{V}_{\mathrm{H}}/RT}$")

    box(lx, lvl[7], bw,
        "Oriani / Trap occupancy",
        r"$\theta_{\mathrm{T}}(\theta_{\mathrm{L}},K_{\mathrm{T}})$")
    box(rx, lvl[7], bw,
        "Trapped H",
        r"$c_{\mathrm{T}}=N_{\mathrm{T}}\,\theta_{\mathrm{T}}$",
        fc=key)

    # Vertical spine.
    arrow(ax, (cx, lvl[0] - bh / 2), (cx, lvl[1] + bh / 2),
          color="black", lw=lw, scale=arr_scale)
    arrow(ax, (cx, lvl[1] - bh / 2), (cx, lvl[2] + bh / 2),
          color="black", lw=lw, scale=arr_scale)

    # Split: down from Taylor, then left/right (TikZ |- style).
    y_split = lvl[2] - bh / 2 - 0.35 * gap
    ax.plot([cx, cx], [lvl[2] - bh / 2, y_split], color="black", lw=lw)
    arrow(ax, (cx, y_split), (lx, lvl[3] + bh / 2),
          color="black", lw=lw, scale=arr_scale)
    arrow(ax, (cx, y_split), (rx, lvl[3] + bh / 2),
          color="black", lw=lw, scale=arr_scale)

    # Left column: flow -> equilibrium -> mean -> occupancy -> Oriani.
    for i in (3, 4, 5, 6):
        arrow(ax, (lx, lvl[i] - bh / 2), (lx, lvl[i + 1] + bh / 2),
              color="black", lw=lw, scale=arr_scale)

    # Right column: N_T feeds only the trapped concentration.
    arrow(ax, (rx, lvl[3] - bh / 2), (rx, lvl[7] + bh / 2),
          color="black", lw=lw, scale=arr_scale)

    # theta_T -> c_T (no floating edge label; both boxes already show θ_T).
    arrow(ax, (lx + bw / 2 + 0.01 * W, lvl[7]),
          (rx - bw / 2 - 0.01 * W, lvl[7]),
          color="black", lw=lw, scale=arr_scale)

    # HELP: phenomenological amplitude correction only (Formulation A).
    # Dashed feedback loop only — no side label; the figure caption names it.
    chan = lx - 0.5 * bw - 0.08 * W
    feed = "0.45"
    ax.plot([lx - bw / 2, chan], [lvl[7], lvl[7]], ls=(0, (3, 2.5)),
            color=feed, lw=lw)
    ax.plot([chan, chan], [lvl[7], lvl[3]], ls=(0, (3, 2.5)), color=feed,
            lw=lw)
    arrow(ax, (chan, lvl[3]), (lx - bw / 2, lvl[3]), color=feed, lw=lw,
          ls=(0, (3, 2.5)), scale=arr_scale)
    ax.set_xlim(-0.02 * W, W)
    ax.set_ylim(0, H)


def draw_problems_thumbnails(ax, W, H):
    """Overview panel (b): torsion, bending, void thumbnails."""
    rows = [
        (2 * H / 3, "I. Torsion", "torsion"),
        (H / 3, "II. Bending", "bending"),
        (0.0, "III. Microvoid", "void"),
    ]

    for y0, head, kind in rows:
        h = H / 3
        ax.add_patch(FancyBboxPatch(
            (0.03 * W, y0 + 0.03 * h), 0.94 * W, 0.94 * h,
            boxstyle="round,pad=0.008,rounding_size=0.03",
            facecolor="0.975", edgecolor="0.6", linewidth=0.7))
        ax.text(0.07 * W, y0 + 0.90 * h, head, fontsize=SMALL_FS,
                fontweight="normal", va="center", ha="left")

        gx = 0.52 * W
        # Glyphs sit a bit high so bottom math labels clear the card edge.
        if kind == "torsion":
            sketch_torsion(ax, gx, y0 + 0.52 * h, 0.24 * h)
        elif kind == "bending":
            sketch_bending(ax, gx, y0 + 0.54 * h, 0.56 * W, 0.20 * h)
        else:
            sketch_void(ax, gx, y0 + 0.50 * h, 0.120 * h)

    ax.set_xlim(0, W)
    ax.set_ylim(0, H)


def draw_torsion_geometry(ax, W, H):
    """Torsion schematic panel (a): wire geometry."""
    cx = W / 2
    # Tall short-wire: height ~2.2 diameters, modest end ellipses.
    a = 0.42
    y_bot, y_top = 0.48, 1.72
    ry = 0.14

    ax.add_patch(Ellipse((cx, y_bot), 2 * a, 2 * ry, facecolor=FILL,
                         edgecolor=EDGE, lw=1.0, zorder=1))
    ax.add_patch(Rectangle((cx - a, y_bot), 2 * a, y_top - y_bot,
                           facecolor=FILL, edgecolor="none", zorder=2))
    ax.plot([cx - a, cx - a], [y_bot, y_top], color=EDGE, lw=1.0, zorder=3)
    ax.plot([cx + a, cx + a], [y_bot, y_top], color=EDGE, lw=1.0, zorder=3)
    ax.add_patch(Ellipse((cx, y_top), 2 * a, 2 * ry, facecolor="0.96",
                         edgecolor=EDGE, lw=1.0, zorder=4))

    ax.plot([cx, cx], [y_bot - 0.22, y_bot], color="0.45", lw=0.8, zorder=5)
    ax.plot([cx, cx], [y_bot, y_top], color="0.45", lw=0.8,
            ls=(0, (4, 3)), zorder=5)
    arrow(ax, (cx, y_top), (cx, y_top + 0.38), color="0.45", lw=0.8,
          zorder=5)
    ax.text(cx + 0.09, y_top + 0.36, r"$x_3$", fontsize=SMALL_FS,
            va="bottom", color="0.35")

    xh, yh = arc_arrow(ax, (cx, y_top + 0.18), 0.88 * a, 1.20 * ry, 200, 348,
                        zorder=5)
    ax.text(xh + 0.06, yh + 0.03, r"$T$", color=MECH, fontsize=LABEL_FS,
            ha="left", va="center", zorder=5)
    # Equal and opposite bottom torque for static equilibrium.
    xb, yb = arc_arrow(ax, (cx, y_bot - 0.16), 0.88 * a, 1.20 * ry, 20, 160,
                        zorder=5)
    ax.text(xb + 0.06, yb - 0.02, r"$-T$", color=MECH, fontsize=LABEL_FS,
            ha="left", va="top", zorder=5)

    dim(ax, (cx, y_bot), (cx + a, y_bot))
    ax.text(cx + a / 2, y_bot - 0.10, r"$a$", fontsize=SMALL_FS,
            ha="center", va="top")

    ax.set_xlim(0, W)
    ax.set_ylim(0, H)


def draw_torsion_kinematics(ax, W, H):
    """Torsion schematic panel (b): cross-section shear."""
    cx, cy, R = W / 2, 0.55 * H, 0.52

    ax.add_patch(Circle((cx, cy), R, facecolor=FILL, edgecolor=EDGE, lw=1.0))
    ax.add_patch(Circle((cx, cy), 0.02, color=EDGE))

    th = np.deg2rad(38)
    ax.plot([cx, cx + R * np.cos(th)], [cy, cy + R * np.sin(th)],
            color="0.35", lw=0.7)
    ax.text(cx + 0.52 * R * np.cos(th) + 0.05,
            cy + 0.52 * R * np.sin(th) - 0.11, r"$r$", fontsize=SMALL_FS)

    tdir = np.array([-np.sin(th), np.cos(th)])
    for frac in (0.35, 0.65, 0.95):
        p = np.array([cx + frac * R * np.cos(th), cy + frac * R * np.sin(th)])
        arrow(ax, tuple(p), tuple(p + 0.42 * frac * R * tdir),
              color=HYDR, lw=1.0, scale=7)
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)


def draw_torsion_trap_inventory(ax):
    """Torsion schematic panel (c): trap density vs radius."""
    r = np.linspace(0, 1, 200)
    N = 0.2
    gnd = np.full_like(r, 0.45)
    ssd = r ** (2 * N)
    ax.fill_between(r, 0, gnd, facecolor=MECH, alpha=0.30, lw=0,
                    label="GND")
    ax.fill_between(r, gnd, gnd + ssd, facecolor=HYDR, alpha=0.30, lw=0,
                    label="SSD")
    ax.plot(r, gnd + ssd, color="0.15", lw=1.2)
    ax.axhline(0.45, color=MECH, lw=0.8, ls=(0, (3, 2)))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.95)
    ax.set_xlabel(r"$r/a$", fontsize=SMALL_FS, labelpad=1)
    ax.set_ylabel(r"$c_{\mathrm{T}}$", fontsize=SMALL_FS, labelpad=2)
    ax.set_yticks([])
    ax.legend(fontsize=TINY_FS, loc="upper center",
              bbox_to_anchor=(0.5, -0.14), ncol=2, handlelength=1.1,
              borderpad=0.2, labelspacing=0.3, columnspacing=1.0)


def _bending_profiles():
    """Through-thickness fields for the schematic (sigma_Y = 1)."""
    z = np.linspace(-0.5, 0.5, 401)
    t = np.abs(z) / 0.5
    eps_s, E, N, lk = 0.02, 300.0, 0.2, 0.5
    f = (E * eps_s * t) ** N
    sm_cl = np.sign(z) * f / np.sqrt(3.0)
    sm_msg = np.sign(z) * np.sqrt(f ** 2 + lk) / np.sqrt(3.0)
    varsigma = 0.55
    cL = np.exp(varsigma * sm_msg)
    cT = (f ** 2 + lk) * cL
    cL_n = cL / cL.max()
    cT_n = cT / cT.max()
    return z, sm_cl, sm_msg, cL_n, cT_n


def draw_bending_geometry(ax, W, H):
    """Bending schematic panel (a): plane-strain beam."""
    xs = np.linspace(0.32, W - 0.32, 80)
    xc = 0.5 * (xs[0] + xs[-1])
    h = 0.40
    # Hogging (∩): mid high at center.
    mid = 0.54 * H - 0.28 * ((xs - xc) / ((xs[-1] - xs[0]) / 2)) ** 2
    ax.fill_between(xs, mid - h / 2, mid + h / 2, facecolor=FILL,
                    edgecolor=EDGE, lw=1.0)
    ax.plot(xs, mid, ls=(0, (3, 2)), color="0.45", lw=0.7)

    bending_moment_arcs(ax, xs[0], mid[0], xs[-1], mid[-1], 0.34,
                        gap=0.12, lw=1.3, scale=12, label=True,
                        label_fs=LABEL_FS)

    ym = mid[len(xs) // 2]

    def mid_at(x):
        return 0.54 * H - 0.28 * ((x - xc) / ((xs[-1] - xs[0]) / 2)) ** 2

    # Labels sit in the whitespace above / below the beam, not on the fill.
    x_h = xc - 0.34
    y_h = mid_at(x_h)
    dim(ax, (x_h, y_h - h / 2), (x_h, y_h + h / 2))
    ax.text(x_h, y_h + h / 2 + 0.07, r"$h$", fontsize=SMALL_FS,
            va="bottom", ha="center")

    arrow(ax, (xc, ym), (xc, ym + 0.58), color="0.45", lw=0.8, scale=6)
    ax.text(xc + 0.06, ym + 0.60, r"$x_2$", fontsize=SMALL_FS, color="0.35",
            ha="left", va="bottom")
    x_a = xc + 0.40
    arrow(ax, (xc, ym), (x_a, ym), color="0.45", lw=0.8, scale=6)
    ax.text(x_a, mid_at(x_a) - h / 2 - 0.07, r"$x_1$", fontsize=SMALL_FS,
            color="0.35", ha="center", va="top")

    ax.set_xlim(0, W)
    ax.set_ylim(0, H)


def _draw_bending_strip(ax_s):
    ax_s.add_patch(Rectangle((0, -0.5), 1, 1, facecolor=FILL,
                             edgecolor=EDGE, lw=0.9))
    ax_s.axhline(0, color="0.45", lw=0.7, ls=(0, (3, 2)))
    ax_s.set_xlim(0, 1)
    ax_s.set_ylim(-0.5, 0.5)
    ax_s.set_xticks([])
    ax_s.set_yticks([-0.5, 0, 0.5])
    ax_s.set_yticklabels([r"$-h/2$", "N.A.", r"$+h/2$"], fontsize=TINY_FS)
    ax_s.tick_params(length=0, pad=1.5)
    for side in ("top", "right", "bottom", "left"):
        ax_s.spines[side].set_visible(False)


def draw_bending_mean_stress(ax, z, sm_cl, sm_msg):
    """Bending schematic panel (b): mean-stress profile."""
    mask_lo, mask_hi = z < 0, z > 0
    ax.plot(sm_msg[mask_lo], z[mask_lo], color=MECH, lw=1.3, label="MSG")
    ax.plot(sm_msg[mask_hi], z[mask_hi], color=MECH, lw=1.3)
    ax.plot(sm_cl, z, color="0.45", lw=1.0, ls=(0, (3, 2)),
            label="SSD-only")
    ax.axvline(0, color="0.8", lw=0.6)
    jump = np.sqrt(0.5) / np.sqrt(3.0)
    dim(ax, (-jump, 0.0), (jump, 0.0), color=HYDR, lw=0.9)
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-0.5, 0.5)
    ax.set_yticks([])
    ax.set_xticks([-1, 0, 1])
    ax.set_xlabel(r"$\sigma_{\mathrm{m}}/\sigma_{\mathrm{Y}}$",
                  fontsize=SMALL_FS, labelpad=1)
    ax.legend(fontsize=TINY_FS, loc="upper center",
              bbox_to_anchor=(0.5, -0.14), ncol=2, handlelength=1.2,
              borderpad=0.2, labelspacing=0.3, columnspacing=1.0)
    ax.spines["left"].set_visible(False)


def draw_bending_hydrogen(ax, z, cL, cT):
    """Bending schematic panel (c): lattice and trapped H."""
    mask_lo, mask_hi = z < 0, z > 0
    ax.plot(cL[mask_lo], z[mask_lo], color=MECH, lw=1.3,
            label=r"$c_{\mathrm{L}}$")
    ax.plot(cL[mask_hi], z[mask_hi], color=MECH, lw=1.3)
    ax.plot(cT[mask_lo], z[mask_lo], color=HYDR, lw=1.3,
            label=r"$c_{\mathrm{T}}$")
    ax.plot(cT[mask_hi], z[mask_hi], color=HYDR, lw=1.3)
    ax.axhline(0, color="0.45", lw=0.7, ls=(0, (3, 2)))
    ax.set_xlim(0, 1.15)
    ax.set_ylim(-0.5, 0.5)
    ax.set_yticks([-0.5, 0, 0.5])
    ax.set_yticklabels([r"$-h/2$", "0", r"$+h/2$"], fontsize=TINY_FS)
    ax.set_xticks([])
    ax.set_xlabel("Normalized", fontsize=SMALL_FS, labelpad=1)
    ax.set_ylabel(r"$x_2$", fontsize=SMALL_FS, labelpad=1)
    ax.legend(fontsize=TINY_FS, loc="upper center",
              bbox_to_anchor=(0.5, -0.14), ncol=2, handlelength=1.2,
              borderpad=0.2, labelspacing=0.3, columnspacing=1.0)


def draw_void_geometry(ax, W, H):
    """Void schematic panel (a): remote hydrostatic tension, free wall, GND shell."""
    cx, cy = W / 2, 0.52 * H
    # Larger radii so size-15 labels fit without overlapping.
    R0, Rg, Rout = 0.45, 0.80, 1.30

    ax.add_patch(Circle((cx, cy), Rout, facecolor="0.965", edgecolor=EDGE,
                        lw=0.9))
    ax.add_patch(Wedge((cx, cy), Rg, 0, 360, width=Rg - R0,
                       facecolor=FILL2, edgecolor="none"))
    ax.add_patch(Circle((cx, cy), R0, facecolor="white", edgecolor=EDGE,
                        lw=1.1))

    # Remote tractions on the outer boundary (not near the void wall).
    for ang in (15, 60, 105, 150, 195, 240, 285, 330):
        th = np.deg2rad(ang)
        arrow(ax, (cx + 1.02 * Rout * np.cos(th), cy + 1.02 * Rout * np.sin(th)),
              (cx + 1.16 * Rout * np.cos(th), cy + 1.16 * Rout * np.sin(th)),
              color=MECH, lw=0.9, scale=7)
    th = np.deg2rad(125)
    ax.text(cx + 1.28 * Rout * np.cos(th), cy + 1.28 * Rout * np.sin(th),
            r"$\sigma^{\infty}$", ha="center", va="center",
            fontsize=LABEL_FS, color=MECH)

    # Stacked Free / GND at 12 o'clock: Free on the traction-free wall,
    # GND in the near-surface shell directly above it.
    ax.text(cx, cy + 0.42 * R0, "Free", ha="center", va="center",
            fontsize=TINY_FS, color="0.45")
    Rm = 0.55 * R0 + 0.45 * Rg
    ax.text(cx, cy + Rm, "GND", ha="center", va="center",
            fontsize=TINY_FS, color="0.30")

    dim(ax, (cx, cy), (cx, cy - R0))
    ax.text(cx - 0.16, cy - 0.72 * R0, r"$R_0$", fontsize=TINY_FS,
            ha="right", va="center")
    # Wall displacement u_0: radial at the equator (3 o'clock).
    arrow(ax, (cx + R0, cy), (cx + R0 + 0.40, cy),
          color=HYDR, lw=0.8, scale=6)
    ax.text(cx + R0 + 0.44, cy, r"$u_0$", fontsize=TINY_FS,
            ha="left", va="center", color=HYDR)
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)


def draw_void_radial_decay(ax):
    """Void schematic panel (b): field decay vs R/R0."""
    R = np.logspace(0, 1, 200)
    # Blue tint denotes the physical near-wall GND layer, not extrapolation.
    ax.axvspan(1.0, 1.5, color="#DCEAF4", alpha=0.8, lw=0)
    ax.loglog(R, R ** -3.0, color=MECH, lw=1.3,
              label=r"$\varepsilon_{\mathrm{e}}$")
    ax.loglog(R, R ** -4.0, color=HYDR, lw=1.3,
              label=r"$\eta$")
    ax.set_xlim(1, 10)
    ax.set_ylim(1e-4, 2)
    ax.set_xticks([1, 3, 10])
    ax.set_xticklabels([r"$1$", r"$3$", r"$10$"])
    ax.xaxis.set_minor_formatter(plt.NullFormatter())
    ax.yaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_xlabel(r"$R/R_0$", fontsize=SMALL_FS, labelpad=1)
    ax.set_ylabel("Amplitude", fontsize=SMALL_FS, labelpad=1)
    ax.legend(fontsize=TINY_FS, loc="upper center",
              bbox_to_anchor=(0.5, -0.14), ncol=2, handlelength=1.2,
              borderpad=0.2, labelspacing=0.3, columnspacing=1.0)


def draw_void_cavitation(ax):
    """Void schematic panel (c): cavitation stress vs trap density."""
    s = np.linspace(0, 5, 200)
    ax.plot(s, np.sqrt(1 + 0.55 * s), color=MECH, lw=1.3)
    ax.set_xlim(0, 5)
    ax.set_ylim(0.9, 2.3)
    ax.set_xlabel(r"$l/R_0$", fontsize=SMALL_FS, labelpad=1)
    ax.set_ylabel(r"$\sigma_{\mathrm{c}}/\sigma_{\mathrm{c}}^{\,\mathrm{cl}}$",
                  fontsize=SMALL_FS, color=MECH, labelpad=2)
    ax.tick_params(axis="y", colors=MECH)
    ax.set_yticks([1, 2])

    ax2 = ax.twinx()
    ax2.plot(s, 0.15 + 0.62 * s, color=HYDR, lw=1.3, ls=(0, (4, 2)))
    ax2.set_ylim(0, 3.6)
    ax2.set_yticks([0, 3])
    ax2.set_ylabel(r"$c_{\mathrm{T}}(R_0)$", fontsize=SMALL_FS,
                   color=HYDR, labelpad=2)
    ax2.tick_params(axis="y", colors=HYDR, length=2.5, pad=2)
    ax2.spines["top"].set_visible(False)
    ax2.spines["left"].set_visible(False)


# ----------------------------------------------------------------------
# standalone panel makers
# ----------------------------------------------------------------------

def make_fig1a():
    _apply_schematic_style()
    figsize = (9.0, 11.5)  # room for size-15 labels inside boxes
    fig = plt.figure(figsize=figsize)
    rect = [0.03, 0.02, 0.94, 0.96]
    ax = geom_panel(fig, rect, figsize)
    draw_coupling_chain(ax, rect[2] * figsize[0], rect[3] * figsize[1])
    fit_geom_panel(fig, ax, pad=0.06, min_size=None, equal=False)
    save(fig, "fig1a.pdf")


def make_fig1b():
    _apply_schematic_style()
    # Larger cards so size-15 labels fit without overlapping glyphs.
    figsize = (5.25, 7.65)
    fig = plt.figure(figsize=figsize)
    rect = [0.02, 0.02, 0.96, 0.96]
    ax = geom_panel(fig, rect, figsize)
    draw_problems_thumbnails(ax, rect[2] * figsize[0], rect[3] * figsize[1])
    fit_geom_panel(fig, ax, pad=0.03, min_size=None, equal=False)
    save(fig, "fig1b.pdf")


def make_fig2a():
    _apply_schematic_style()
    figsize = (2.8, 4.6)
    fig = plt.figure(figsize=figsize)
    ty = 0.920
    rect = [0.08, 0.12, 0.84, 0.78]
    ax = geom_panel(fig, rect, figsize)
    draw_torsion_geometry(ax, rect[2] * figsize[0], rect[3] * figsize[1])
    fit_geom_panel(fig, ax, pad=0.06, min_size=3.0)
    save(fig, "fig2a.pdf")


def make_fig2b():
    _apply_schematic_style()
    figsize = (2.56, 3.36)
    fig = plt.figure(figsize=figsize)
    ty = 0.920
    rect = [0.08, 0.12, 0.84, 0.78]
    ax = geom_panel(fig, rect, figsize)
    draw_torsion_kinematics(ax, rect[2] * figsize[0], rect[3] * figsize[1])
    fit_geom_panel(fig, ax, pad=0.06, min_size=2.0)
    save(fig, "fig2b.pdf")


def make_fig2c():
    _apply_schematic_style()
    figsize = (3.2, 3.36)
    fig = plt.figure(figsize=figsize)
    ty = 0.920
    ax = plot_panel(fig, [0.12, 0.18, 0.76, 0.68])
    draw_torsion_trap_inventory(ax)
    save(fig, "fig2c.pdf")


def make_fig5a():
    _apply_schematic_style()
    figsize = (3.4, 4.2)
    fig = plt.figure(figsize=figsize)
    ty = 0.920
    rect = [0.08, 0.12, 0.84, 0.78]
    ax = geom_panel(fig, rect, figsize)
    draw_bending_geometry(ax, rect[2] * figsize[0], rect[3] * figsize[1])
    fit_geom_panel(fig, ax, pad=0.06, min_size=2.0)
    save(fig, "fig5a.pdf")


def make_fig5b():
    _apply_schematic_style()
    figsize = (4.2, 4.2)
    fig = plt.figure(figsize=figsize)
    ty = 0.920
    z, sm_cl, sm_msg, _, _ = _bending_profiles()
    ax_s = fig.add_axes([0.12, 0.18, 0.08, 0.68])
    _draw_bending_strip(ax_s)
    ax = plot_panel(fig, [0.24, 0.18, 0.64, 0.68])
    draw_bending_mean_stress(ax, z, sm_cl, sm_msg)
    save(fig, "fig5b.pdf")


def make_fig5c():
    _apply_schematic_style()
    figsize = (3.6, 4.2)
    fig = plt.figure(figsize=figsize)
    ty = 0.920
    z, _, _, cL, cT = _bending_profiles()
    ax = plot_panel(fig, [0.14, 0.18, 0.72, 0.68])
    draw_bending_hydrogen(ax, z, cL, cT)
    save(fig, "fig5c.pdf")


def make_fig8a():
    _apply_schematic_style()
    figsize = (6.2, 7.4)
    fig = plt.figure(figsize=figsize)
    ty = 0.920
    rect = [0.08, 0.12, 0.84, 0.78]
    ax = geom_panel(fig, rect, figsize)
    draw_void_geometry(ax, rect[2] * figsize[0], rect[3] * figsize[1])
    fit_geom_panel(fig, ax, pad=0.08, min_size=4.2)
    save(fig, "fig8a.pdf")


def make_fig8b():
    _apply_schematic_style()
    figsize = (3.4, 4.2)
    fig = plt.figure(figsize=figsize)
    ty = 0.920
    ax = plot_panel(fig, [0.14, 0.18, 0.72, 0.68])
    draw_void_radial_decay(ax)
    save(fig, "fig8b.pdf")


def make_fig8c():
    _apply_schematic_style()
    figsize = (3.2, 4.2)
    fig = plt.figure(figsize=figsize)
    ty = 0.920
    ax = plot_panel(fig, [0.14, 0.18, 0.72, 0.68])
    draw_void_cavitation(ax)
    save(fig, "fig8c.pdf")


def draw_cavitation_geometry(ax, W, H):
    """Finite-strain cavitation geometry: $R_0\\to r_0$, far-field $\\sigma^\\infty$.

    Matches the manuscript caption: initial void radius $R_0$, current wall
    $r_0$, material map $R\\to r$, dashed outer arcs for the unbounded far field.
    """
    cx, cy = 0.50 * W, 0.52 * H
    R0 = 0.38
    r0 = 0.62
    Rout = 1.35

    # Far-field disk (unbounded domain cue).
    ax.add_patch(Circle((cx, cy), Rout, facecolor="0.965", edgecolor="none"))
    th = np.linspace(0, 2 * np.pi, 120)
    for frac in (0.92, 1.0):
        ax.plot(
            cx + frac * Rout * np.cos(th),
            cy + frac * Rout * np.sin(th),
            color=EDGE, lw=0.8, ls=(0, (2.5, 2.0)), solid_capstyle="round",
        )

    # Current void wall (solid) and initial wall (dashed).
    ax.add_patch(Circle((cx, cy), r0, facecolor="white", edgecolor=EDGE, lw=1.15))
    ax.plot(
        cx + R0 * np.cos(th), cy + R0 * np.sin(th),
        color="0.45", lw=0.9, ls=(0, (3, 2)),
    )

    # Remote hydrostatic tension.
    for ang in (20, 70, 110, 160, 200, 250, 290, 340):
        a = np.deg2rad(ang)
        arrow(
            ax,
            (cx + 1.02 * Rout * np.cos(a), cy + 1.02 * Rout * np.sin(a)),
            (cx + 1.16 * Rout * np.cos(a), cy + 1.16 * Rout * np.sin(a)),
            color=MECH, lw=0.9, scale=7,
        )
    ax.text(
        cx - 1.22 * Rout, cy + 1.05 * Rout, r"$\sigma^{\infty}$",
        ha="center", va="center", fontsize=LABEL_FS, color=MECH,
    )

    # Radii at the equator.
    arrow(ax, (cx, cy), (cx + R0, cy), color=EDGE, lw=0.7, scale=5)
    ax.text(cx + 0.52 * R0, cy - 0.12, r"$R_0$", fontsize=TINY_FS,
            ha="center", va="top")
    arrow(ax, (cx, cy), (cx + r0, cy), color=EDGE, lw=0.7, scale=5)
    ax.text(cx + 0.72 * r0, cy + 0.10, r"$r_0$", fontsize=TINY_FS,
            ha="center", va="bottom")

    # Material map R → r in the solid.
    ang = np.deg2rad(-35)
    p0 = (cx + 0.78 * r0 * np.cos(ang), cy + 0.78 * r0 * np.sin(ang))
    p1 = (cx + 1.05 * Rout * np.cos(ang), cy + 1.05 * Rout * np.sin(ang))
    arrow(ax, p0, p1, color=EDGE, lw=0.8, scale=6)
    ax.text(
        cx + 1.18 * Rout * np.cos(ang), cy + 1.18 * Rout * np.sin(ang),
        r"$R\rightarrow r$", fontsize=TINY_FS, ha="left", va="center",
    )

    ax.set_xlim(0, W)
    ax.set_ylim(0, H)


def make_fig_cavitation_geom():
    """Manuscript Fig. cavitation geometry (finite-strain void expansion)."""
    _apply_schematic_style()
    figsize = (4.6, 4.8)
    fig = plt.figure(figsize=figsize)
    rect = [0.06, 0.06, 0.88, 0.88]
    ax = geom_panel(fig, rect, figsize)
    draw_cavitation_geometry(ax, rect[2] * figsize[0], rect[3] * figsize[1])
    fit_geom_panel(fig, ax, pad=0.08, min_size=3.5)
    save(fig, "fig_cavitation_geom.pdf")


# ----------------------------------------------------------------------
# multi-panel compose functions
# ----------------------------------------------------------------------

def compose_fig_overview():
    _apply_schematic_style()
    figsize = (FIGW, 8.2)
    fig = plt.figure(figsize=figsize)
    ty = 0.945

    rect_a = [0.030, 0.030, 0.420, 0.870]
    ax = geom_panel(fig, rect_a, figsize, "a",
                    "Coupled MSG-hydrogen chain", ty)
    draw_coupling_chain(ax, rect_a[2] * figsize[0], rect_a[3] * figsize[1])

    rect_b = [0.530, 0.030, 0.445, 0.870]
    ax = geom_panel(fig, rect_b, figsize, "b", "Problems", ty)
    draw_problems_thumbnails(ax, rect_b[2] * figsize[0],
                             rect_b[3] * figsize[1])

    save(fig, "fig_overview.pdf")


def compose_fig_schematic_torsion():
    _apply_schematic_style()
    figsize = (FIGW, 5.6)
    fig = plt.figure(figsize=figsize)
    ty = 0.920

    rect = [0.025, 0.175, 0.245, 0.690]
    ax = geom_panel(fig, rect, figsize, "a", "Geometry", ty)
    draw_torsion_geometry(ax, rect[2] * figsize[0], rect[3] * figsize[1])

    rect = [0.305, 0.175, 0.245, 0.690]
    ax = geom_panel(fig, rect, figsize, "b", "Kinematics", ty)
    draw_torsion_kinematics(ax, rect[2] * figsize[0], rect[3] * figsize[1])

    ax = plot_panel(fig, [0.665, 0.255, 0.305, 0.615], "c",
                    "trap inventory", ty)
    draw_torsion_trap_inventory(ax)

    save(fig, "fig_schematic_torsion.pdf")


def compose_fig_schematic_bending():
    _apply_schematic_style()
    figsize = (FIGW, 5.6)
    fig = plt.figure(figsize=figsize)
    ty = 0.920

    rect = [0.020, 0.175, 0.265, 0.690]
    ax = geom_panel(fig, rect, figsize, "a", "Plane-strain bending", ty)
    draw_bending_geometry(ax, rect[2] * figsize[0], rect[3] * figsize[1])

    z, sm_cl, sm_msg, cL, cT = _bending_profiles()

    ax_s = fig.add_axes([0.365, 0.255, 0.028, 0.610])
    _draw_bending_strip(ax_s)

    ax = plot_panel(fig, [0.415, 0.255, 0.175, 0.610], "b",
                    "Mean stress", ty, title_xc=0.475)
    draw_bending_mean_stress(ax, z, sm_cl, sm_msg)

    ax = plot_panel(fig, [0.715, 0.255, 0.245, 0.610], "c",
                    "lattice and trapped H", ty)
    draw_bending_hydrogen(ax, z, cL, cT)

    save(fig, "fig_schematic_bending.pdf")


def compose_fig_schematic_void():
    _apply_schematic_style()
    figsize = (FIGW, 5.6)
    fig = plt.figure(figsize=figsize)
    ty = 0.920

    rect = [0.015, 0.175, 0.265, 0.690]
    ax = geom_panel(fig, rect, figsize, "a", "Geometry", ty)
    draw_void_geometry(ax, rect[2] * figsize[0], rect[3] * figsize[1])

    ax = plot_panel(fig, [0.375, 0.255, 0.235, 0.610], "b",
                    "Radial decay", ty)
    draw_void_radial_decay(ax)

    ax = plot_panel(fig, [0.700, 0.255, 0.220, 0.610], "c",
                    "cavitation and traps", ty)
    draw_void_cavitation(ax)

    save(fig, "fig_schematic_void.pdf")


if __name__ == "__main__":
    compose_fig_overview()
    compose_fig_schematic_torsion()
    compose_fig_schematic_bending()
    compose_fig_schematic_void()
