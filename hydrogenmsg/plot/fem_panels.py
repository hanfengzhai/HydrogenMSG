"""FEM panel drawers and compose functions for Figs. 4, 7, 11, and 12.

Panel titles stay plain text (no ``$...$``). Axis labels, legends, headers,
and annotations use matplotlib mathtext (``$...$`` only — never ``$$...$$``).

Usage::

    python3 -m hydrogenmsg.plot fig4a
"""

from __future__ import annotations

import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import Circle
from matplotlib.tri import Triangulation

from hydrogenmsg.analytics import (Params, bending_fields, torsion_cT_profile,
                                   torsion_torque, void_fields)
from hydrogenmsg.fem.canonical import solve_bending, solve_torsion
from hydrogenmsg.fem.slit import (run_mesh_convergence, solve as solve_slit)
from hydrogenmsg.fem.void import Load, radial_profile, solve
from hydrogenmsg.plot.style import (FONT_SIZE, FIGW, GREY, HYDR, MECH, OUT,
                                    apply_style, panel_title, save, title_font)

# FEM-specific layout constants (shared style lives in style.py).
FIGH = 7.6
L_OVER_R0 = 10.0
LOAD = Load(S_z=3.6, S_r=2.2)
ZOOM = 3.0
MESH = dict(n_rho=48, n_th=14, Rout_over_R0=30.0)

# Mode-I slit + HELP softening (SI Fig. 12).
SLIT_L_OVER_A = 5.0
SLIT_S = 1.0
SLIT_XI = 0.3
SLIT_ZOOM = 1.0  # tip-centred square of side 2a (matches fig12mesh)
# Uniform fine Cartesian mesh over the tip window |x-a|<=a, |y|<=a
# (tip_box=1); mild geometric grading only outside that window to the
# remote boundary.
SLIT_MESH = dict(nx_c=40, nx_l=12, ny=40, nx_box=80, ny_box=40, tip_box=1.0,
                 W_over_a=14.0, H_over_a=14.0, ratio=1.12,
                 itmax=600, relax=0.35, tol=1e-6)

_torsion_data = None
_bending_data = None
_void_data = None
_slit_data = None


def get_torsion_sol():
    """Cached torsion FEM solutions (MSG + classical)."""
    global _torsion_data
    if _torsion_data is None:
        print("FEM torsion ...")
        Gamma, la = 0.05, 2.0
        sol = solve_torsion(Gamma=Gamma, l_over_a=la, n_r=20, n_th=16)
        cla = solve_torsion(Gamma=Gamma, l_over_a=0.0, n_r=20, n_th=16)
        _torsion_data = dict(Gamma=Gamma, la=la, sol=sol, cla=cla)
    return _torsion_data


def get_bending_sol():
    """Cached bending FEM solution."""
    global _bending_data
    if _bending_data is None:
        print("FEM bending ...")
        eps_s, lh = 0.05, 2.0
        sol = solve_bending(eps_s=eps_s, l_over_h=lh, n_x=8, n_y=28)
        _bending_data = dict(eps_s=eps_s, lh=lh, sol=sol)
    return _bending_data


def get_void_sols():
    """Cached void FEM solutions (MSG, classical, hydrostatic verification)."""
    global _void_data
    if _void_data is None:
        p = Params()
        print("solving: triaxial MSG ...")
        msg = solve(l_over_R0=L_OVER_R0, load=LOAD, **MESH)
        print("solving: triaxial classical ...")
        cla = solve(l_over_R0=0.0, load=LOAD, **MESH)
        print("solving: hydrostatic MSG (verification) ...")
        hyd = solve(l_over_R0=L_OVER_R0, load=Load(2.6, 2.6), **MESH)
        print(f"  delta: MSG {msg['delta']:.4f}, classical {cla['delta']:.4f}, "
              f"hydrostatic {hyd['delta']:.4f}")
        _void_data = dict(p=p, msg=msg, cla=cla, hyd=hyd)
    return _void_data


def get_slit_sol():
    """Cached plane-strain mode-I slit solution with HELP softening."""
    global _slit_data
    if _slit_data is None:
        p = Params(xi=SLIT_XI)
        print(f"solving: mode-I slit MSG + HELP (xi={SLIT_XI}, "
              f"l/a={SLIT_L_OVER_A}, S={SLIT_S}) ...")
        sol = solve_slit(l_over_a=SLIT_L_OVER_A, S=SLIT_S, p=p, **SLIT_MESH)
        print(f"  iters={sol['iters']}, resid={sol['resid']:.2e}, "
              f"COD/a={sol['cod']:.4e}, soft_min={sol['soft'].min():.3f}")
        _slit_data = dict(p=p, sol=sol)
    return _slit_data


# ----------------------------------------------------------------------
# Meridian contours (void)
# ----------------------------------------------------------------------

def meridian(sol, key, zoom=ZOOM):
    """Nodal field on the full meridian plane, mirrored from the quadrant."""
    mesh = sol["mesh"]
    nr, nt = 2 * mesh.n_rho + 1, 2 * mesh.n_th + 1
    F = sol["kin"].project(sol[key])[:, 0].reshape(nr, nt)

    rho = np.hypot(mesh.coords[:, 0], mesh.coords[:, 1]).reshape(nr, nt)[:, -1]
    th = np.arctan2(mesh.coords[:, 0], mesh.coords[:, 1]).reshape(nr, nt)[0]
    keep = rho <= zoom * mesh.R0 * 1.02
    rho, F = rho[keep], F[keep]

    th_full = np.concatenate([th, np.pi - th[::-1][1:],
                              np.pi + th[1:], 2.0 * np.pi - th[::-1][1:]])
    F_full = np.concatenate([F, F[:, ::-1][:, 1:],
                             F[:, 1:], F[:, ::-1][:, 1:]], axis=1)
    s = rho[:, None] / mesh.R0
    return s * np.sin(th_full), s * np.cos(th_full), F_full


def _add_colorbar(fig, ax, cf, cticks, clabels, label=None, *, mode="absolute"):
    """Attach a colorbar.

    ``mode="absolute"`` uses a fixed figure-fraction strip (paper panels).
    ``mode="axes"`` uses an axes-relative colorbar (multi-panel rows).
    """
    if mode == "axes":
        cb = fig.colorbar(cf, ax=ax, fraction=0.045, pad=0.08, aspect=16)
        tick_fs = max(8, FONT_SIZE - 4)
        label_fs = max(8, FONT_SIZE - 3)
    else:
        pos = ax.get_position()
        cax = fig.add_axes([pos.x1 + 0.012, pos.y0 + 0.045,
                            0.012, pos.height - 0.09])
        cb = fig.colorbar(cf, cax=cax)
        tick_fs = FONT_SIZE
        label_fs = FONT_SIZE
    cb.set_ticks(cticks)
    cb.set_ticklabels(clabels)
    cb.outline.set_linewidth(0.6)
    cb.ax.tick_params(width=0.6, labelsize=tick_fs)
    if label is not None:
        cb.set_label(label, fontsize=label_fs)
    return cb


def draw_meridian_contour(ax, fig, sol, key, tag, label, cmap, *,
                          log=False, nlev=13, cbar=True, show_title=False,
                          cbar_label=None, cbar_mode="absolute"):
    """Contour map on the void meridian plane."""
    r, z, F = meridian(sol, key)
    if log:
        lev = np.logspace(np.log10(F.min()), np.log10(F.max()), nlev)
        cf = ax.contourf(r, z, F, levels=lev, norm=LogNorm(), cmap=cmap)
        lo, hi = np.ceil(np.log10(F.min())), np.floor(np.log10(F.max()))
        cticks = 10.0 ** np.arange(lo, hi + 1)
        clabels = [rf"$10^{{{int(k)}}}$" for k in np.arange(lo, hi + 1)]
    else:
        lev = np.linspace(F.min(), F.max(), nlev)
        cf = ax.contourf(r, z, F, levels=lev, cmap=cmap)
        vmin, vmax = F.min(), F.max()
        cticks = [vmin, 0.5 * (vmin + vmax), vmax]
        clabels = [f"{t:.2f}" for t in cticks]
    ax.contour(r, z, F, levels=lev, colors="w", linewidths=0.25, alpha=0.6)
    ax.add_patch(Circle((0, 0), 1.0, facecolor="w", edgecolor="0.15", lw=0.9,
                        zorder=5))
    ax.set_aspect("equal")
    ax.set_xlim(-ZOOM, ZOOM)
    ax.set_ylim(-ZOOM, ZOOM)
    if show_title:
        panel_title(ax, f"({tag})  {label}", allow_math=False)
    ax.set_xlabel(r"$\rho/R_0$", labelpad=1)
    ax.set_ylabel(r"$z/R_0$", labelpad=0)
    ax.set_xticks([-3, 0, 3])
    ax.set_yticks([-3, 0, 3])
    if cbar:
        _add_colorbar(fig, ax, cf, cticks, clabels, label=cbar_label,
                      mode=cbar_mode)
    return cf


def draw_fig11e(ax, sol=None, p=None):
    """FEM against the closed-form void solution at the same expansion."""
    data = get_void_sols()
    sol = sol if sol is not None else data["hyd"]
    p = p if p is not None else data["p"]

    R, se = radial_profile(sol, "sig_e_hat")
    _, sm = radial_profile(sol, "sig_m_hat")
    _, le = radial_profile(sol, "l_eta")
    _, ee = radial_profile(sol, "eps_e")
    an = void_fields(R, sol["delta"], sol["l_over_R0"], p)

    l_eta_exact = (3.0 * np.sqrt(2.5) * sol["delta"] * sol["l_over_R0"]
                   / R ** 4)
    m = R <= 4.0
    k = slice(1, int(m.sum()), 5)
    for exact, fem, col, mk, ms in (
            (an["sig_m_hat"], sm, MECH, "o", 4.5),
            (an["sig_e_hat"], se, GREY, "s", 4.0),
            (l_eta_exact, le, HYDR, "^", 4.5)):
        ax.plot(R[m], exact[m], "-", color=col, lw=1.4, zorder=2)
        ax.plot(R[m][k], fem[m][k], mk, color=col, ms=ms, mfc="none", mew=1.0,
                zorder=3)

    eY = 1.0 / p.E_over_sigY
    Rp = R[np.argmax(ee < eY)] if np.any(ee < eY) else R[-1]
    # Blue tint denotes the elastic field region, not extrapolation.
    ax.axvspan(Rp, 4.0, color="#DCEAF4", zorder=0, lw=0)
    ax.text(3.92, 4.3, "Elastic", color="0.40", fontsize=FONT_SIZE,
            ha="right", va="top")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1.0, 4.0)
    ax.set_ylim(2e-2, 5.0)
    ax.set_xlabel(r"$R/R_0$", labelpad=1)
    ax.set_xticks([1, 1.5, 2, 3, 4])
    ax.set_xticklabels(["1", "1.5", "2", "3", "4"])
    ax.set_yticks([0.1, 1.0])
    ax.set_yticklabels(["0.1", "1"])
    ax.text(1.16, 2.7, r"$\sigma_{\mathrm{m}}/\sigma_{\mathrm{Y}}$",
            color=MECH, fontsize=FONT_SIZE, va="bottom")
    ax.text(1.42, 0.55, r"$\sigma_{\mathrm{e}}/\sigma_{\mathrm{Y}}$",
            color=GREY, fontsize=FONT_SIZE, va="top")
    ax.text(1.03, 0.19, r"$l\,\eta$",
            color=HYDR, fontsize=FONT_SIZE, va="bottom")
    ax.plot([], [], "k-", lw=1.4, label="Closed form")
    ax.plot([], [], "k^", ms=4.5, mfc="none", mew=1.0, label="FEM")
    ax.legend(loc="lower right", handlelength=1.4, borderaxespad=0.4,
              labelspacing=0.25, fontsize=FONT_SIZE)


def draw_fig11f(ax, msg=None, cla=None):
    """Gradient hardening raises the trap population at the void surface."""
    data = get_void_sols()
    msg = msg if msg is not None else data["msg"]
    cla = cla if cla is not None else data["cla"]

    for sol, c, ls, lab in ((cla, "tab:red", "--", "SSD-only"),
                            (msg, "blue", "-", r"MSG ($l/R_0=10$)")):
        R, ct = radial_profile(sol, "cT_norm")
        m = R <= 3.0
        ax.plot(R[m], ct[m], ls, color=c, lw=1.9, label=lab)
    ax.set_xlim(1.0, 3.0)
    ax.set_ylim(0.0, None)
    ax.set_xlabel(r"$\rho/R_0$", labelpad=1)
    ax.set_ylabel(r"$c_{\mathrm{T}}/c_{T0}$", labelpad=2)
    ax.legend(loc="lower left", handlelength=1.6, borderaxespad=0.3,
              labelspacing=0.25, fontsize=FONT_SIZE)

    cm = radial_profile(msg, "cT_norm")[1][0]
    cc = radial_profile(cla, "cT_norm")[1][0]
    ax.annotate("", xy=(1.06, cm), xytext=(1.06, cc),
                arrowprops=dict(arrowstyle="<->", color="0.25", lw=0.8,
                                shrinkA=0, shrinkB=0))
    ax.text(1.09, 0.5 * (cm + cc), r"$+%.0f\%%$" % (100 * (cm / cc - 1)),
            color="0.25", fontsize=FONT_SIZE, va="center", ha="left")


# ----------------------------------------------------------------------
# Torsion / bending scatter contours
# ----------------------------------------------------------------------

def _scatter_contour(ax, x, y, f, cmap, nlev=12):
    tri = Triangulation(x, y)
    lev = np.linspace(np.nanmin(f), np.nanmax(f), nlev)
    cf = ax.tricontourf(tri, f, levels=lev, cmap=cmap)
    ax.tricontour(tri, f, levels=lev, colors="w", linewidths=0.2, alpha=0.5)
    return cf, lev


def _torsion_full_disk(sol):
    xq = sol["xy"][..., 0].ravel() / sol["a"]
    yq = sol["xy"][..., 1].ravel() / sol["a"]
    parts = []
    for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        parts.append((sx * xq, sy * yq))
    x = np.concatenate([p[0] for p in parts])
    y = np.concatenate([p[1] for p in parts])
    return x, y


def _mirror_field(field):
    v = field.ravel()
    return np.concatenate([v, v, v, v])


def _scatter_colorbar(fig, ax, cf, label=None):
    pos = ax.get_position()
    h = max(0.55 * pos.height, min(pos.height - 0.04, 0.70))
    y0 = pos.y0 + 0.5 * (pos.height - h)
    cax = fig.add_axes([min(pos.x1 + 0.02, 0.92), y0, 0.025, h])
    cb = fig.colorbar(cf, cax=cax)
    vmin, vmax = cf.levels[0], cf.levels[-1]
    ticks = [vmin, 0.5 * (vmin + vmax), vmax]
    cb.set_ticks(ticks)
    cb.set_ticklabels([f"{v:.2f}" for v in ticks])
    cb.ax.tick_params(labelsize=FONT_SIZE)
    if label is not None:
        cb.set_label(label, fontsize=FONT_SIZE)
    return cb


def draw_fig4a(ax, fig=None, *, cbar=True):
    data = get_torsion_sol()
    sol = data["sol"]
    x, y = _torsion_full_disk(sol)
    cf, _ = _scatter_contour(ax, x, y, _mirror_field(sol["sig_e_hat"]), "viridis")
    ax.add_patch(Circle((0, 0), 1.0, fill=False, edgecolor="0.2", lw=0.9))
    ax.set_aspect("equal")
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-1.15, 1.15)
    ax.set_xlabel(r"$x/a$", labelpad=1)
    ax.set_ylabel(r"$y/a$", labelpad=0)
    if cbar and fig is not None:
        _scatter_colorbar(fig, ax, cf, label=r"$\sigma_{\mathrm{e}}/\sigma_{\mathrm{Y}}$")


def draw_fig4b(ax, fig=None, *, cbar=True):
    data = get_torsion_sol()
    sol = data["sol"]
    x, y = _torsion_full_disk(sol)
    cf, _ = _scatter_contour(ax, x, y, _mirror_field(sol["cT_norm"]), "YlOrRd")
    ax.add_patch(Circle((0, 0), 1.0, fill=False, edgecolor="0.2", lw=0.9))
    ax.set_aspect("equal")
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-1.15, 1.15)
    ax.set_xlabel(r"$x/a$", labelpad=1)
    ax.set_ylabel(r"$y/a$", labelpad=0)
    if cbar and fig is not None:
        _scatter_colorbar(fig, ax, cf, label=r"$c_{\mathrm{T}}$ (norm.)")


def draw_fig4c(ax):
    data = get_torsion_sol()
    sol, cla = data["sol"], data["cla"]
    Gamma, la = data["Gamma"], data["la"]

    r = np.linspace(0, 1, 200)
    exact = torsion_cT_profile(r, Gamma, la, sol["p"])
    exact0 = torsion_cT_profile(r, Gamma, 0.0, sol["p"])
    ax.plot(r, exact, "-", color="blue", lw=1.9, label="MSG Closed form")
    ax.plot(r, exact0, "--", color="tab:red", lw=1.9, label="SSD-only")

    rp, cp = sol["r_prof"], sol["cT_prof"]
    k = np.linspace(0, len(rp) - 1, 25).astype(int)
    ax.plot(rp[k], cp[k], "o", color="blue", ms=5, mfc="none", mew=1.0,
            label="MSG FEM")
    rpc, cpc = cla["r_prof"], cla["cT_prof"]
    kc = np.linspace(0, len(rpc) - 1, 20).astype(int)
    ax.plot(rpc[kc], cpc[kc], "s", color="tab:red", ms=4, mfc="none",
            mew=1.0, label="SSD-only FEM")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, None)
    ax.set_xlabel(r"$r/a$", labelpad=1)
    ax.set_ylabel(r"$c_{\mathrm{T}}$ (norm.)", labelpad=2)
    ax.legend(loc="upper left", fontsize=FONT_SIZE, handlelength=1.3,
              borderaxespad=0.3, labelspacing=0.25)


def draw_fig7a(ax, fig=None, *, cbar=True):
    data = get_bending_sol()
    sol = data["sol"]
    h = sol["h"]
    x = sol["xy"][..., 0].ravel() / h
    y = sol["xy"][..., 1].ravel() / h
    cf, _ = _scatter_contour(ax, x, y, sol["sig_m_hat"].ravel(), "coolwarm")
    ax.set_aspect("equal")
    ax.set_xlabel(r"$x_1/h$", labelpad=1)
    ax.set_ylabel(r"$x_2/h$", labelpad=0)
    if cbar and fig is not None:
        _scatter_colorbar(fig, ax, cf, label=r"$\sigma_{\mathrm{m}}/\sigma_{\mathrm{Y}}$")


def draw_fig7b(ax, fig=None, *, cbar=True):
    data = get_bending_sol()
    sol = data["sol"]
    h = sol["h"]
    x = sol["xy"][..., 0].ravel() / h
    y = sol["xy"][..., 1].ravel() / h
    cf, _ = _scatter_contour(ax, x, y, sol["cT_norm"].ravel(), "YlOrRd")
    ax.set_aspect("equal")
    ax.set_xlabel(r"$x_1/h$", labelpad=1)
    ax.set_ylabel(r"$x_2/h$", labelpad=0)
    if cbar and fig is not None:
        _scatter_colorbar(fig, ax, cf, label=r"$c_{\mathrm{T}}$ (norm.)")


def draw_fig7c(ax):
    data = get_bending_sol()
    sol = data["sol"]
    eps_s, lh = data["eps_s"], data["lh"]

    z = np.linspace(-0.5, 0.5, 401)
    an = bending_fields(z, eps_s, lh, sol["p"])
    ax.plot(an["sig_m_hat"], z, "-", color="darkblue", lw=1.4, label="Closed form")
    zp, smp = sol["z_prof"], sol["sm_prof"]
    k = np.linspace(0, len(zp) - 1, 30).astype(int)
    ax.plot(smp[k], zp[k], "o", color="darkblue", ms=4.5, mfc="none", mew=1.0,
            label="FEM")
    ax.axhline(0, color="0.6", lw=0.6, ls=":")
    ax.set_ylim(-0.5, 0.5)
    ax.set_xlabel(r"$\sigma_{\mathrm{m}}/\sigma_{\mathrm{Y}}$", labelpad=1)
    ax.set_ylabel(r"$x_2/h$", labelpad=1)
    ax.legend(loc="lower right", fontsize=FONT_SIZE, handlelength=1.3,
              borderaxespad=0.3, labelspacing=0.25)


# Void contour panels (Fig. 11a–d)
def draw_fig11a(ax, fig, sol=None):
    sol = sol if sol is not None else get_void_sols()["msg"]
    draw_meridian_contour(ax, fig, sol, "sig_m_hat", "a", "mean stress",
                          "viridis",
                          cbar_label=r"$\sigma_{\mathrm{m}}/\sigma_{\mathrm{Y}}$")


def draw_fig11b(ax, fig, sol=None):
    sol = sol if sol is not None else get_void_sols()["msg"]
    draw_meridian_contour(ax, fig, sol, "sig_e_hat", "b", "effective stress",
                          "viridis",
                          cbar_label=r"$\sigma_{\mathrm{e}}/\sigma_{\mathrm{Y}}$")


def draw_fig11c(ax, fig, sol=None):
    sol = sol if sol is not None else get_void_sols()["msg"]
    draw_meridian_contour(ax, fig, sol, "l_eta", "c", "strain gradient",
                          "cividis", log=True,
                          cbar_label=r"$l\,\eta$")


def draw_fig11d(ax, fig, sol=None):
    sol = sol if sol is not None else get_void_sols()["msg"]
    draw_meridian_contour(ax, fig, sol, "cT_norm", "d", "trapped hydrogen",
                          "YlOrRd",
                          cbar_label=r"$c_{\mathrm{T}}/c_{\mathrm{T}0}$")


# ----------------------------------------------------------------------
# Standalone panel makers (fig{N}{letter}.pdf)
# ----------------------------------------------------------------------

def fig4a():
    apply_style()
    fig = plt.figure(figsize=(4.64, 4.0))
    ax = fig.add_axes([0.12, 0.12, 0.62, 0.78])
    draw_fig4a(ax, fig)
    save(fig, "fig4a.pdf")


def fig4b():
    apply_style()
    fig = plt.figure(figsize=(4.64, 4.0))
    ax = fig.add_axes([0.12, 0.12, 0.62, 0.78])
    draw_fig4b(ax, fig)
    save(fig, "fig4b.pdf")


def fig4c():
    apply_style()
    fig = plt.figure(figsize=(4.48, 4.0))
    ax = fig.add_axes([0.14, 0.14, 0.78, 0.78])
    draw_fig4c(ax)
    save(fig, "fig4c.pdf")


def fig7a():
    apply_style()
    # Wide, short canvas: bending strip is short in x2.
    fig = plt.figure(figsize=(6.8, 2.8))
    ax = fig.add_axes([0.10, 0.22, 0.68, 0.62])
    draw_fig7a(ax, fig)
    save(fig, "fig7a.pdf")


def fig7b():
    apply_style()
    fig = plt.figure(figsize=(5.8, 2.8))
    ax = fig.add_axes([0.12, 0.22, 0.58, 0.62])
    draw_fig7b(ax, fig)
    save(fig, "fig7b.pdf")


def fig7c():
    apply_style()
    fig = plt.figure(figsize=(4.8, 5.0))
    ax = fig.add_axes([0.18, 0.14, 0.74, 0.74])
    draw_fig7c(ax)
    save(fig, "fig7c.pdf")


def fig11a():
    apply_style()
    fig = plt.figure(figsize=(4.8, 4.0))
    ax = fig.add_axes([0.12, 0.12, 0.62, 0.78])
    draw_fig11a(ax, fig)
    save(fig, "fig11a.pdf")


def fig11b():
    apply_style()
    fig = plt.figure(figsize=(4.8, 4.0))
    ax = fig.add_axes([0.12, 0.12, 0.62, 0.78])
    draw_fig11b(ax, fig)
    save(fig, "fig11b.pdf")


def fig11c():
    apply_style()
    fig = plt.figure(figsize=(4.8, 4.0))
    ax = fig.add_axes([0.12, 0.12, 0.62, 0.78])
    draw_fig11c(ax, fig)
    save(fig, "fig11c.pdf")


def fig11d():
    apply_style()
    fig = plt.figure(figsize=(4.8, 4.0))
    ax = fig.add_axes([0.12, 0.12, 0.62, 0.78])
    draw_fig11d(ax, fig)
    save(fig, "fig11d.pdf")


def fig11e():
    apply_style()
    fig = plt.figure(figsize=(4.48, 4.0))
    ax = fig.add_axes([0.16, 0.14, 0.76, 0.78])
    draw_fig11e(ax)
    save(fig, "fig11e.pdf", fixed_canvas=True)


def fig11f():
    apply_style()
    fig = plt.figure(figsize=(4.48, 4.0))
    ax = fig.add_axes([0.16, 0.14, 0.76, 0.78])
    draw_fig11f(ax)
    save(fig, "fig11f.pdf", fixed_canvas=True)


# ----------------------------------------------------------------------
# Mode-I slit + HELP softening (Fig. 12)
# ----------------------------------------------------------------------

def _slit_window_mask(sol, zoom=SLIT_ZOOM):
    """Gauss points inside the tip-centred plotting window."""
    a = sol["mesh"].a
    x = sol["kin"].x.ravel() / a
    y = sol["kin"].y.ravel() / a
    xt = x - 1.0
    # Quarter model only has x >= 0, so (x-a)/a >= -1.
    m = (xt >= -1.02) & (xt <= zoom) & (y <= zoom) & (y >= -1e-12)
    return xt[m], y[m], m


def _slit_structured_field(sol, key, zoom=SLIT_ZOOM, n=560, smooth=2.5,
                           clip_pct=(5.0, 95.0)):
    """Tip-window field on a uniform Cartesian grid from Gauss points.

    Clips rare tip outliers before interpolation so singular Gauss values
    cannot paint a vertical tip seam, then lightly blurs for clean iso-lines.
    """
    from scipy.interpolate import griddata
    from scipy.ndimage import gaussian_filter

    xt, y, m = _slit_window_mask(sol, zoom)
    f = sol[key].ravel()[m]
    upper = y > 1e-12
    x_u, y_u, f_u = xt[upper], y[upper], f[upper]
    x_all = np.concatenate([xt, x_u])
    y_all = np.concatenate([y, -y_u])
    if key in ("uy_a",):
        f_all = np.concatenate([f, -f_u])
    else:
        f_all = np.concatenate([f, f_u])

    # Keep raw samples for interpolation. Percentile clipping is applied only
    # as display colour limits in ``draw_slit_contour`` (saturation), not here.
    del clip_pct

    xi = np.linspace(-1.05, zoom, n)
    yi = np.linspace(-zoom, zoom, n)
    Xi, Yi = np.meshgrid(xi, yi)
    pts = np.column_stack([x_all, y_all])
    Fi = griddata(pts, f_all, (Xi, Yi), method="linear")
    # Open slit: do not nearest-fill across the crack face.
    slit = (Xi < -1e-3) & (np.abs(Yi) < 0.03)
    miss = ~np.isfinite(Fi) & ~slit
    if miss.any():
        Fi[miss] = griddata(pts, f_all, (Xi[miss], Yi[miss]), method="nearest")
    Fi = np.where(slit, np.nan, Fi)
    valid = np.isfinite(Fi)
    weights = gaussian_filter(valid.astype(float), sigma=smooth, mode="nearest")
    blur = gaussian_filter(np.where(valid, Fi, 0.0), sigma=smooth, mode="nearest")
    Fi = np.divide(blur, np.maximum(weights, 1e-8))
    Fi = np.where(slit | ~valid, np.nan, Fi)
    Fi = np.ma.array(Fi, mask=~np.isfinite(Fi) | slit)
    return Xi, Yi, Fi, xi, yi


def _slit_axes_frame(ax, zoom=SLIT_ZOOM):
    ax.set_aspect("equal")
    # Compact tip square: mouth at -1, ligament to +zoom (zoom=1 → side 2a).
    ax.set_xlim(-1.05, max(zoom, 1.0) + 0.05)
    ax.set_ylim(-zoom - 0.05, zoom + 0.05)
    ax.set_xlabel(r"$(x-a)/a$", labelpad=1)
    ax.set_ylabel(r"$y/a$", labelpad=0)
    ax.set_xticks([-1, 0, 1] if zoom <= 1.0 + 1e-9 else [-1, 0, 1, 2])
    ax.set_yticks([-1, 0, 1] if zoom <= 1.0 + 1e-9 else [-2, 0, 2])
    ax.plot([-1.0, 0.0], [0.0, 0.0], color="0.15", lw=1.6, zorder=5)
    ax.plot([0.0], [0.0], "o", color="0.15", ms=3.5, zorder=6)


def slit_raw_extrema(sol, key, zoom=SLIT_ZOOM):
    """Min/max of the raw Gauss field inside the tip plotting window.

    Contour colour limits use percentile saturation; these extrema are the
    unsmoothed sample extremes for quantitative captions.
    """
    _xt, _y, m = _slit_window_mask(sol, zoom)
    vals = np.asarray(sol[key]).ravel()[m]
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return np.nan, np.nan
    return float(vals.min()), float(vals.max())


def draw_slit_contour(ax, fig, sol, key, cmap, *, label=None, nlev=12,
                      cbar=True, zoom=SLIT_ZOOM, pct=(5.0, 95.0),
                      cbar_mode="absolute"):
    """Smooth tip-window raster with light white iso-lines.

    The Gauss field is interpolated and lightly smoothed without clipping.
    Colour limits use the ``pct`` percentiles so tip extrema saturate rather
    than rewrite the field.
    """
    Xi, Yi, Fi, xi, yi = _slit_structured_field(
        sol, key, zoom=zoom, clip_pct=pct)
    vals = np.asarray(Fi[~np.ma.getmaskarray(Fi)]).ravel()
    lo, hi = np.percentile(vals, pct)
    if key in ("uy_a",):
        lim = max(abs(lo), abs(hi), 1e-14)
        lo, hi = -lim, lim
    elif abs(hi - lo) < 1e-14:
        hi = lo + 1e-14
    lev = np.linspace(lo, hi, nlev)
    cf = ax.imshow(
        Fi, origin="lower", aspect="equal", cmap=cmap,
        extent=(xi[0], xi[-1], yi[0], yi[-1]),
        vmin=lo, vmax=hi, interpolation="bilinear",
        rasterized=True)
    cf.set_clim(lo, hi)
    ax.contour(Xi, Yi, Fi, levels=lev, colors="w", linewidths=0.2, alpha=0.35)
    _slit_axes_frame(ax, zoom=zoom)
    if cbar and fig is not None:
        cticks = [lo, 0.5 * (lo + hi), hi]
        clabels = [f"{t:.3g}" for t in cticks]
        _add_colorbar(fig, ax, cf, cticks, clabels, label=label,
                      mode=cbar_mode)
    return cf


def draw_slit_schematic(ax):
    """Mode-I notched-plate schematic (tip-centred square of side 2a)."""
    from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

    fs = FONT_SIZE
    # Unit square in tip-centred coords: tip at (0,0), mouth at (-1,0).
    ax.add_patch(Rectangle((-1, -1), 2, 2, fill=False, ec="0.15", lw=1.4,
                           zorder=3))
    # Notch (open slit).
    ax.plot([-1.0, 0.0], [0.0, 0.0], color="0.15", lw=2.2, solid_capstyle="butt",
            zorder=4)
    ax.plot([0.0], [0.0], "o", color="0.15", ms=4.0, zorder=5)
    ax.text(-0.52, 0.10, "Notch", fontsize=fs, color="0.2", ha="center")

    # Dimension ticks: a left (notch), a right (ligament), a above/below.
    def _dim_h(y, x0, x1, label, label_y):
        ax.plot([x0, x1], [y, y], color="0.25", lw=0.7)
        ax.plot([x0, x0], [y - 0.04, y + 0.04], color="0.25", lw=0.7)
        ax.plot([x1, x1], [y - 0.04, y + 0.04], color="0.25", lw=0.7)
        ax.text(0.5 * (x0 + x1), label_y, label, ha="center", va="center",
                fontsize=fs)

    def _dim_v(x, y0, y1, label, label_x):
        ax.plot([x, x], [y0, y1], color="0.25", lw=0.7)
        ax.plot([x - 0.04, x + 0.04], [y0, y0], color="0.25", lw=0.7)
        ax.plot([x - 0.04, x + 0.04], [y1, y1], color="0.25", lw=0.7)
        ax.text(label_x, 0.5 * (y0 + y1), label, ha="center", va="center",
                fontsize=fs)

    _dim_h(-1.12, -1.0, 0.0, r"$a$", -1.24)
    _dim_h(-1.12, 0.0, 1.0, r"$a$", -1.24)
    _dim_v(-1.12, 0.0, 1.0, r"$a$", -1.26)
    _dim_v(-1.12, -1.0, 0.0, r"$a$", -1.26)

    # Remote tension on top (matches FEM traction loading).
    for x in np.linspace(-0.85, 0.85, 7):
        ax.add_patch(FancyArrowPatch(
            (x, 1.02), (x, 1.16), arrowstyle="-|>", mutation_scale=9,
            lw=0.9, color="0.15", shrinkA=0, shrinkB=0))
    ax.text(0.0, 1.22, r"$\sigma^{\infty}$", ha="center", va="bottom",
            fontsize=fs)

    # Bottom rollers (uy = 0) and one side roller (ux = 0).
    for x in np.linspace(-0.75, 0.75, 5):
        ax.add_patch(Circle((x, -1.07), 0.04, facecolor="w", edgecolor="0.15",
                            lw=0.7, zorder=4))
        ax.plot([x - 0.055, x + 0.055], [-1.12, -1.12], color="0.15", lw=0.7)
    ax.add_patch(Circle((1.07, -1.0), 0.04, facecolor="w", edgecolor="0.15",
                        lw=0.7, zorder=4))
    ax.plot([1.12, 1.12], [-1.055, -0.945], color="0.15", lw=0.7)

    # Fixed data window (no aspect box resize) matches the mesh panel.
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.35, 1.35)
    ax.set_aspect("auto")
    ax.axis("off")


def draw_slit_mesh(ax, sol=None, *, half=1.0):
    """Tip-centred square filled with the uniform fine Q9 mesh (mirrored)."""
    if sol is None:
        from hydrogenmsg.fem.slit import make_mesh
        kw = {k: v for k, v in SLIT_MESH.items()
              if k in ("nx_c", "nx_l", "ny", "ratio", "tip_box",
                       "nx_box", "ny_box")}
        a = 1.0
        mesh = make_mesh(a=a, W=SLIT_MESH.get("W_over_a", 14.0) * a,
                         H=SLIT_MESH.get("H_over_a", 14.0) * a, **kw)
    else:
        mesh = sol["mesh"]
        a = mesh.a
    xy = mesh.coords / a
    # Teal edges like the reference notched-plate mesh figure.
    edge = "#3db8b0"
    corners = (0, 2, 8, 6, 0)
    for e in range(mesh.conn.shape[0]):
        nodes = mesh.conn[e, list(corners)]
        xe = xy[nodes, 0] - 1.0
        ye = xy[nodes, 1]
        # Keep elements fully inside the tip-centred square.
        if (xe.min() < -half - 1e-9 or xe.max() > half + 1e-9
                or ye.min() < -1e-9 or ye.max() > half + 1e-9):
            continue
        ax.plot(xe, ye, color=edge, lw=0.35, solid_capstyle="round",
                solid_joinstyle="round")
        ax.plot(xe, -ye, color=edge, lw=0.35, solid_capstyle="round",
                solid_joinstyle="round")
    # Outer square + notch.
    ax.plot([-half, half, half, -half, -half],
            [-half, -half, half, half, -half],
            color="0.15", lw=1.35, zorder=3)
    ax.plot([-half, 0.0], [0.0, 0.0], color="0.15", lw=1.8, zorder=4)
    ax.plot([0.0], [0.0], "o", color="0.15", ms=3.5, zorder=5)

    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlabel("")
    ax.set_ylabel("")
    # Tick numbers + axis labels in the same outer margin as panel (a).
    for v, s in ((-1, r"$-1$"), (0, r"$0$"), (1, r"$1$")):
        ax.text(v, -1.08, s, ha="center", va="top", fontsize=FONT_SIZE)
        ax.text(-1.08, v, s, ha="right", va="center", fontsize=FONT_SIZE)
    ax.text(0.0, -1.24, r"$(x-a)/a$", ha="center", va="center",
            fontsize=FONT_SIZE)
    ax.text(-1.26, 0.0, r"$y/a$", ha="center", va="center", rotation=90,
            fontsize=FONT_SIZE)

    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.35, 1.35)
    ax.set_aspect("auto")


def draw_fig12a(ax, fig, sol=None):
    sol = sol if sol is not None else get_slit_sol()["sol"]
    draw_slit_contour(ax, fig, sol, "uy_a", "coolwarm",
                      label=r"$u_y/a$")


def draw_fig12b(ax, fig, sol=None):
    sol = sol if sol is not None else get_slit_sol()["sol"]
    draw_slit_contour(ax, fig, sol, "eps_e", "viridis",
                      label=r"$\varepsilon_{\mathrm{e}}$")


def draw_fig12c(ax, fig, sol=None):
    sol = sol if sol is not None else get_slit_sol()["sol"]
    draw_slit_contour(ax, fig, sol, "sig_m_hat", "coolwarm",
                      label=r"$\sigma_{\mathrm{m}}/\sigma_{\mathrm{Y}}$")


def draw_fig12d(ax, fig, sol=None):
    sol = sol if sol is not None else get_slit_sol()["sol"]
    draw_slit_contour(ax, fig, sol, "sig_e_hat", "viridis",
                      label=r"$\sigma_{\mathrm{e}}/\sigma_{\mathrm{Y}}$")


def draw_fig12e(ax, fig, sol=None):
    sol = sol if sol is not None else get_slit_sol()["sol"]
    draw_slit_contour(ax, fig, sol, "soft", "cividis",
                      label=r"$1-\xi\,\theta_{\mathrm{T}}$")


def draw_fig12f(ax, fig, sol=None):
    sol = sol if sol is not None else get_slit_sol()["sol"]
    draw_slit_contour(ax, fig, sol, "cT_norm", "YlOrRd",
                      label=r"$c_{\mathrm{T}}/c_{\mathrm{T}0}$",
                      pct=(10.0, 90.0))


def fig12mesh():
    """Notched-plate schematic + tip-centred Q9 mesh (SI)."""
    apply_style()
    # Identical axes boxes → identical panel heights (keep with fixed_canvas).
    fig = plt.figure(figsize=(8.4, 4.2))
    y0, h, w = 0.04, 0.92, 0.46
    ax0 = fig.add_axes([0.03, y0, w, h])
    ax1 = fig.add_axes([0.51, y0, w, h])
    draw_slit_schematic(ax0)
    draw_slit_mesh(ax1)
    for ax, lab in ((ax0, "(a)"), (ax1, "(b)")):
        ax.text(0.02, 0.98, lab, transform=ax.transAxes, ha="left", va="top",
                fontsize=FONT_SIZE)
    save(fig, "fig12mesh.pdf", fixed_canvas=True, crop=False)  # equal panel boxes


def fig12a():
    apply_style()
    fig = plt.figure(figsize=(5.4, 4.0))
    ax = fig.add_axes([0.10, 0.12, 0.68, 0.78])
    draw_fig12a(ax, fig)
    save(fig, "fig12a.pdf")


def fig12b():
    apply_style()
    fig = plt.figure(figsize=(5.4, 4.0))
    ax = fig.add_axes([0.10, 0.12, 0.68, 0.78])
    draw_fig12b(ax, fig)
    save(fig, "fig12b.pdf")


def fig12c():
    apply_style()
    fig = plt.figure(figsize=(5.4, 4.0))
    ax = fig.add_axes([0.10, 0.12, 0.68, 0.78])
    draw_fig12c(ax, fig)
    save(fig, "fig12c.pdf")


def fig12d():
    apply_style()
    fig = plt.figure(figsize=(5.4, 4.0))
    ax = fig.add_axes([0.10, 0.12, 0.68, 0.78])
    draw_fig12d(ax, fig)
    save(fig, "fig12d.pdf")


def fig12e():
    apply_style()
    fig = plt.figure(figsize=(5.4, 4.0))
    ax = fig.add_axes([0.10, 0.12, 0.68, 0.78])
    draw_fig12e(ax, fig)
    save(fig, "fig12e.pdf")


def fig12f():
    apply_style()
    fig = plt.figure(figsize=(5.4, 4.0))
    ax = fig.add_axes([0.10, 0.12, 0.68, 0.78])
    draw_fig12f(ax, fig)
    save(fig, "fig12f.pdf")


_slit_conv_rows = None


def get_slit_convergence():
    """Cached mesh-refinement ladder for the SI slit study."""
    global _slit_conv_rows
    if _slit_conv_rows is None:
        cache = os.path.join(OUT, "fig12conv_metrics.json")
        if os.path.isfile(cache):
            import json
            with open(cache) as f:
                rows = json.load(f)
            # Require L2 keys + tip_box=1 uniform-window hierarchy.
            if (rows and "L2_uy_a" in rows[0] and "h" in rows[0]
                    and rows[0].get("tip_box") == 1.0
                    and rows[0].get("nx_box") == 20):
                _slit_conv_rows = rows
                print(f"loaded slit convergence metrics from {cache}")
                return _slit_conv_rows
        print("solving: mode-I slit mesh-convergence ladder ...", flush=True)
        _slit_conv_rows = run_mesh_convergence(
            l_over_a=SLIT_L_OVER_A, S=SLIT_S, xi=SLIT_XI,
            W_over_a=SLIT_MESH["W_over_a"], H_over_a=SLIT_MESH["H_over_a"],
            ratio=SLIT_MESH.get("ratio", 1.12),
            tip_box=1.0,
            itmax=SLIT_MESH.get("itmax", 600),
            relax=SLIT_MESH.get("relax", 0.35),
            tol=SLIT_MESH.get("tol", 1e-6),
        )
        import json
        with open(cache, "w") as f:
            json.dump(_slit_conv_rows, f, indent=2)
        print(f"wrote {cache}")
    return _slit_conv_rows


def draw_fig12conv(ax, rows=None):
    """Single-panel tip-window relative L2 errors vs h, with rate estimates."""
    rows = rows if rows is not None else get_slit_convergence()
    h = np.array([r["h"] for r in rows], dtype=float)
    series = (
        ("L2_uy_a", "uy_a", r"$u_y$", "o", MECH),
        ("L2_eps_e", "eps_e", r"$\varepsilon_{\mathrm{e}}$", "s", HYDR),
        ("L2_sig_m_hat", "sig_m_hat", r"$\sigma_{\mathrm{m}}$", "D", "#009E73"),
        ("L2_cT_norm", "cT_norm", r"$c_{\mathrm{T}}$", "^", GREY),
    )
    for key, kraw, lab, mk, c in series:
        err = np.array([r[key] for r in rows], dtype=float)
        p_fit = rows[0].get(f"p_fit_{kraw}")
        if p_fit is not None and np.isfinite(p_fit):
            lab = rf"{lab} ($p\approx{p_fit:.2f}$)"
        ax.loglog(h[:-1], np.maximum(err[:-1], 1e-16), mk + "-",
                  color=c, ms=7, lw=1.7, label=lab)

    e0 = max(rows[0]["L2_uy_a"], 1e-16)
    h0, h1 = h[0], h[-2]
    href = np.array([h0, h1])
    ax.loglog(href, e0 * (href / h0) ** 1, ":", color="0.45", lw=1.1,
              label=r"$\mathcal{O}(h)$")
    ax.loglog(href, e0 * (href / h0) ** 2, "--", color="0.45", lw=1.1,
              label=r"$\mathcal{O}(h^{2})$")

    # Mark production mesh (M3).
    ax.axvline(rows[2]["h"], color="0.7", ls="--", lw=0.9, zorder=0)
    ax.set_xlabel(r"tip-window element size $h/a$")
    ax.set_ylabel(
        r"$\|q_h-q_{\mathrm{M4}}\|_{L^2}/\|q_{\mathrm{M4}}\|_{L^2}$")
    ax.legend(loc="best", fontsize=FONT_SIZE - 2, frameon=True)
    return rows


def fig12conv():
    """Single-panel L2 mesh-convergence figure for the SI slit study."""
    apply_style()
    rows = get_slit_convergence()
    fig = plt.figure(figsize=(5.6, 4.4))
    ax = fig.add_axes([0.16, 0.14, 0.78, 0.78])
    draw_fig12conv(ax, rows)
    save(fig, "fig12conv.pdf")
    print("slit tip-window L2 convergence (vs M4):")
    print(f"{'mesh':>4} {'h/a':>9} {'L2 uy':>10} {'L2 eps':>10} "
          f"{'L2 sigm':>10} {'L2 cT':>10}")
    for r in rows:
        mark = " *" if r["label"] == "M3" else ""
        print(f"{r['label']:>4}{mark} {r['h']:9.4e} "
              f"{r['L2_uy_a']:10.3e} {r['L2_eps_e']:10.3e} "
              f"{r['L2_sig_m_hat']:10.3e} {r['L2_cT_norm']:10.3e}")
    pkeys = ("uy_a", "eps_e", "sig_m_hat", "cT_norm")
    print("least-squares rates p:",
          ", ".join(f"{k}={rows[0].get(f'p_fit_{k}')}" for k in pkeys))
    return rows


# ----------------------------------------------------------------------
# Composed paper figures
# ----------------------------------------------------------------------

def compose_fig_fem_torsion():
    apply_style()
    data = get_torsion_sol()
    sol = data["sol"]
    Gamma, la = data["Gamma"], data["la"]

    fig = plt.figure(figsize=(FIGW, 4.8))
    draw_fig4a(fig.add_axes([0.06, 0.18, 0.24, 0.68]), fig)
    draw_fig4b(fig.add_axes([0.36, 0.18, 0.24, 0.68]), fig)
    draw_fig4c(fig.add_axes([0.70, 0.18, 0.26, 0.68]))

    T_an = torsion_torque(Gamma, la, sol["p"])
    fig.text(0.50, 0.96,
             r"Wire torsion FEM, $\Gamma=%g$, $l/a=%g$  "
             r"($T_{\mathrm{FEM}}/T_{\mathrm{an}}=%.3f$)"
             % (Gamma, la, sol["T_hat"] / T_an),
             ha="center", va="top", fontproperties=title_font(),
             fontweight="normal")
    save(fig, "fig_fem_torsion.pdf")


def compose_fig_fem_bending():
    apply_style()
    data = get_bending_sol()
    eps_s, lh = data["eps_s"], data["lh"]

    fig = plt.figure(figsize=(FIGW, 4.8))
    draw_fig7a(fig.add_axes([0.06, 0.20, 0.36, 0.62]), fig)
    draw_fig7b(fig.add_axes([0.50, 0.20, 0.20, 0.62]), fig)
    draw_fig7c(fig.add_axes([0.78, 0.20, 0.18, 0.62]))

    fig.text(0.50, 0.96,
             r"Beam bending FEM, $\varepsilon_s=%g$, $l/h=%g$" % (eps_s, lh),
             ha="center", va="top", fontproperties=title_font(),
             fontweight="normal")
    save(fig, "fig_fem_bending.pdf")


def compose_fig_fem_void():
    apply_style()
    data = get_void_sols()
    msg = data["msg"]

    fig = plt.figure(figsize=(FIGW, FIGH))
    w, h = 0.207, 0.352
    xs = [0.050, 0.375, 0.700]
    y_top, y_bot = 0.575, 0.085

    draw_fig11a(fig.add_axes([xs[0], y_top, w, h]), fig)
    draw_fig11b(fig.add_axes([xs[1], y_top, w, h]), fig)
    draw_fig11c(fig.add_axes([xs[2], y_top, w, h]), fig)
    draw_fig11d(fig.add_axes([xs[0], y_bot, w, h]), fig)
    draw_fig11e(fig.add_axes([xs[1], y_bot + 0.015, w, h - 0.015]))
    draw_fig11f(fig.add_axes([xs[2], y_bot + 0.015, w, h - 0.015]))

    header = (
        r"Submicron void, $l/R_0=%g$ ($R_0=%.2f\,\mu\mathrm{m}$), remote "
        r"$S_{zz}/\sigma_{\mathrm{Y}}=%.1f$, $S_{rr}/\sigma_{\mathrm{Y}}=%.1f$"
        % (L_OVER_R0, msg["R0"] * 1e6, LOAD.S_z, LOAD.S_r)
    )
    fig.text(0.50, 0.985, header,
             ha="center", va="top", fontproperties=title_font(),
             fontweight="normal")
    save(fig, "fig_fem_void.pdf")


def compose_fig_fem_slit():
    apply_style()
    sol = get_slit_sol()["sol"]

    fig = plt.figure(figsize=(FIGW, FIGH))
    w, h = 0.207, 0.352
    xs = [0.050, 0.375, 0.700]
    y_top, y_bot = 0.575, 0.085

    draw_fig12a(fig.add_axes([xs[0], y_top, w, h]), fig)
    draw_fig12b(fig.add_axes([xs[1], y_top, w, h]), fig)
    draw_fig12c(fig.add_axes([xs[2], y_top, w, h]), fig)
    draw_fig12d(fig.add_axes([xs[0], y_bot, w, h]), fig)
    draw_fig12e(fig.add_axes([xs[1], y_bot, w, h]), fig)
    draw_fig12f(fig.add_axes([xs[2], y_bot, w, h]), fig)

    header = (
        r"Mode-I slit + HELP, $l/a=%g$, $\xi=%g$, "
        r"$\sigma_{yy}^{\infty}/\sigma_{\mathrm{Y}}=%g$"
        % (sol["l_over_a"], sol["p"].xi, sol["S"])
    )
    fig.text(0.50, 0.985, header,
             ha="center", va="top", fontproperties=title_font(),
             fontweight="normal")
    save(fig, "fig_fem_slit.pdf")


if __name__ == "__main__":
    compose_fig_fem_torsion()
    compose_fig_fem_bending()
    compose_fig_fem_void()
    compose_fig_fem_slit()