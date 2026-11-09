"""Visualize the Q9 FEM meshes used for torsion, bending, and void.

Produces ``output/fig_fem_mesh_*.pdf``.

Usage:  python3 -m hydrogenmsg.plot.meshes
"""

import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.collections import LineCollection

from hydrogenmsg.analytics import Params
from hydrogenmsg.fem.canonical import mesh_disk, mesh_strip
from hydrogenmsg.fem.void import make_mesh as make_void_mesh
from hydrogenmsg.plot.fem_panels import L_OVER_R0, MESH as VOID_MESH_KW
from hydrogenmsg.plot.style import OUT

os.makedirs(OUT, exist_ok=True)

FONT_SIZE = 15
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Libertinus Serif", "Times New Roman", "DejaVu Serif"],
    "font.weight": "normal",
    "mathtext.fontset": "cm",
    "mathtext.default": "regular",
    "font.size": FONT_SIZE,
    "axes.titleweight": "normal",
    "figure.titleweight": "normal",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

_TITLE_FONT = None
for cand in font_manager.fontManager.ttflist:
    if (cand.name == "Libertinus Serif" and int(cand.weight) == 400
            and cand.style == "normal"
            and "Regular" in os.path.basename(cand.fname)):
        _TITLE_FONT = font_manager.FontProperties(fname=cand.fname,
                                                  size=FONT_SIZE)
        break
if _TITLE_FONT is None:
    _TITLE_FONT = font_manager.FontProperties(
        family="Libertinus Serif", weight="regular", size=FONT_SIZE)


def q9_corner_edges(conn):
    """Corner-to-corner edges of each Q9 (layout j*3+i)."""
    corners = [0, 2, 8, 6, 0]
    edges = []
    for e in conn:
        for a, b in zip(corners[:-1], corners[1:]):
            edges.append((e[a], e[b]))
    edges = np.asarray(edges, dtype=int)
    key = np.sort(edges, axis=1)
    _, uniq = np.unique(key, axis=0, return_index=True)
    return edges[uniq]


def draw_mesh(ax, coords, conn, title, lw=0.35):
    edges = q9_corner_edges(conn)
    segs = coords[edges]
    ax.add_collection(LineCollection(segs, colors="0.30", linewidths=lw))
    ax.plot(coords[:, 0], coords[:, 1], ".", color="#0072B2", ms=1.6,
            zorder=3)
    ax.set_title(title, fontproperties=_TITLE_FONT, fontweight="normal")
    ax.set_aspect("equal")


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, bbox_inches="tight")
    fig.savefig(path.replace(".pdf", ".png"), bbox_inches="tight", dpi=300)
    plt.close(fig)
    print(f"wrote {os.path.relpath(path)}")


def fig_all():
    p = Params()
    R0 = p.l / L_OVER_R0
    void = make_void_mesh(R0, VOID_MESH_KW["Rout_over_R0"] * R0,
                          VOID_MESH_KW["n_rho"], VOID_MESH_KW["n_th"])
    disk = mesh_disk(a=1.0, n_r=20, n_th=16)
    strip = mesh_strip(h=1.0, n_x=8, n_y=28)

    fig, axes = plt.subplots(1, 3, figsize=(12.0, 4.4))

    ax = axes[0]
    c = void.coords / R0
    draw_mesh(ax, c, void.conn,
              f"(a)  void sector\n{void.n_rho}x{void.n_th} Q9, "
              f"Rout/R0={VOID_MESH_KW['Rout_over_R0']:g}",
              lw=0.22)
    th = np.linspace(0, 0.5 * np.pi, 100)
    ax.plot(np.sin(th), np.cos(th), color="#D55E00", lw=1.3, zorder=4)
    ax.set_xlabel(r"$r/R_0$")
    ax.set_ylabel(r"$z/R_0$")

    ax = axes[1]
    draw_mesh(ax, disk["coords"], disk["conn"],
              f"(b)  torsion quarter-disk\n{disk['n_r']}x{disk['n_th']} Q9",
              lw=0.35)
    ax.plot(np.cos(th), np.sin(th), color="#D55E00", lw=1.3, zorder=4)
    ax.set_xlabel(r"$x/a$")
    ax.set_ylabel(r"$y/a$")

    ax = axes[2]
    draw_mesh(ax, strip["coords"] / strip["h"], strip["conn"],
              f"(c)  bending strip\n{strip['n_x']}x{strip['n_y']} Q9, "
              f"L/h={strip['L']/strip['h']:g}",
              lw=0.28)
    ax.set_xlabel(r"$x_1/h$")
    ax.set_ylabel(r"$x_2/h$")

    fig.text(0.5, 1.01, "FEM meshes (Q9)", ha="center", va="bottom",
             fontproperties=_TITLE_FONT, fontweight="normal")
    fig.tight_layout()
    save(fig, "fig_fem_meshes.pdf")


def fig_one(name, coords, conn, title, xlabel, ylabel, highlight=None,
            lw=0.35):
    fig, ax = plt.subplots(figsize=(5.6, 5.2))
    draw_mesh(ax, coords, conn, title, lw=lw)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if highlight is not None:
        ax.plot(highlight[0], highlight[1], color="#D55E00", lw=1.4,
                zorder=4)
    fig.tight_layout()
    save(fig, name)


def main():
    p = Params()
    R0 = p.l / L_OVER_R0
    void = make_void_mesh(R0, VOID_MESH_KW["Rout_over_R0"] * R0,
                          VOID_MESH_KW["n_rho"], VOID_MESH_KW["n_th"])
    disk = mesh_disk(a=1.0, n_r=20, n_th=16)
    strip = mesh_strip(h=1.0, n_x=8, n_y=28)
    th = np.linspace(0, 0.5 * np.pi, 120)

    fig_all()
    fig_one("fig_fem_mesh_void.pdf", void.coords / R0, void.conn,
            f"Void mesh: {void.n_rho} x {void.n_th} Q9",
            r"$r/R_0$", r"$z/R_0$",
            highlight=(np.sin(th), np.cos(th)), lw=0.2)
    fig_one("fig_fem_mesh_torsion.pdf", disk["coords"], disk["conn"],
            f"Torsion mesh: {disk['n_r']} x {disk['n_th']} Q9",
            r"$x/a$", r"$y/a$",
            highlight=(np.cos(th), np.sin(th)))
    fig_one("fig_fem_mesh_bending.pdf", strip["coords"] / strip["h"],
            strip["conn"],
            f"Bending mesh: {strip['n_x']} x {strip['n_y']} Q9",
            r"$x_1/h$", r"$x_2/h$", lw=0.25)
    print("done")


if __name__ == "__main__":
    main()
