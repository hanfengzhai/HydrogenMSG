"""Panel drawers for analytical result figures (Figs. 3, 6, 9, 10)."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from msg_hydrogen import (Params, bending_average_uptake, bending_fields,
                          cavitation_stress, f_power, torsion_Q, torsion_cT_profile,
                          torsion_torque, void_fields)
from _style import COLORS, COLORS_THREE, FONT_SIZE, LINE_LW, LINESTYLES_THREE, MECH, panel_title


# ----------------------------------------------------------------------
# Fig. 3 — torsion closed forms
# ----------------------------------------------------------------------

def draw_fig3a(ax, p: Params, *, show_title=False):
    """Normalized torque vs twist."""
    ka = np.linspace(0.005, 0.5, 80)
    for c, la in zip(COLORS, [0.0, 1.0, 2.0, 5.0]):
        T = [torsion_torque(k, la, p) for k in ka]
        lbl = "SSD-only" if la == 0 else rf"$l/a={la:g}$"
        ax.plot(ka, T, color=c, lw=LINE_LW, label=lbl)
    ax.set_xlabel(r"$\kappa a$")
    ax.set_ylabel(r"$T/(\sigma_{\mathrm{Y}} a^3)$")
    if show_title:
        panel_title(ax, "(a)")
    ax.legend(loc="best", fontsize=FONT_SIZE)


def draw_fig3b(ax, p: Params, *, show_title=False):
    """Trapped hydrogen profiles at fixed surface strain (linear r/a)."""
    Gamma = 0.05
    r = np.linspace(0.0, 1.0, 400)
    for c, la in zip(COLORS, [0.0, 1.0, 5.0, 10.0]):
        cT = torsion_cT_profile(r, Gamma, la, p)
        style = dict(color=c, lw=LINE_LW)
        if la == 0.0:
            style["ls"] = "--"
            lbl = "SSD-only"
        else:
            lbl = rf"$l/a={la:g}$"
        ax.plot(r, cT, label=lbl, **style)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, None)
    ax.set_xlabel(r"$r/a$")
    ax.set_ylabel(
        r"$c_{\mathrm{T}}(r)\,/\,[\chi\,\theta_{\mathrm{T}}/(l\,b^{2})]$")
    if show_title:
        panel_title(ax, r"(b) $\Gamma=0.05$")
    ax.legend(loc="upper left", fontsize=FONT_SIZE)


def draw_fig3c(ax, p: Params, *, show_title=False):
    """Uptake enhancement vs wire radius."""
    # Physical a with l = p.l (~4.8 um).
    a_min, a_max = 0.05e-6, 50e-6
    a = np.logspace(np.log10(a_min), np.log10(a_max), 120)
    curves = []
    for c, ls, G in zip(COLORS_THREE, LINESTYLES_THREE, [0.05, 0.1, 0.2]):
        Q = torsion_Q(a, G, p)
        curves.append(Q)
        ax.plot(a * 1e6, Q, color=c, ls=ls, lw=LINE_LW, label=rf"$\Gamma={G:g}$")
    ax.axhline(1.0, color="0.5", lw=0.7, ls=":")
    ymax = float(np.nanmax(curves)) * 1.05
    ax.set_ylim(0.9, ymax)
    ax.set_xscale("log")
    ax.set_xlim(a_min * 1e6, a_max * 1e6)
    ax.set_xlabel(r"Wire radius $a$ [$\mu\mathrm{m}$]")
    ax.set_ylabel(
        r"$Q(a)=\bar{c}_{\mathrm{T}}/\bar{c}_{\mathrm{T}}^{\,\mathrm{SSD}}$")
    if show_title:
        panel_title(ax, "(c)")
    ax.legend(loc="best", fontsize=FONT_SIZE)
    # Intrinsic length is already in the figure caption; keep the x-label short
    # so side-by-side panels do not collide.


# ----------------------------------------------------------------------
# Fig. 6 — bending closed forms
# ----------------------------------------------------------------------

def _bending_z(gap=0.04):
    """Through-thickness stations with a visible gap about the neutral axis.

    The outer MSG mean stress is discontinuous at x2=0. The gap stands in
    for the unresolved O(l_eps) higher-order layer.
    """
    z_neg = np.linspace(-0.5, -gap, 400)
    z_pos = np.linspace(gap, 0.5, 400)
    return np.concatenate([z_neg, [np.nan], z_pos])


def _shade_neutral_layer(ax, gap=0.08):
    # Warm tint for the unresolved local neutral-axis layer (not a
    # structural-size continuum cutoff).
    ax.axhspan(-gap, gap, color="#F3E6D3", zorder=0, lw=0)
    # Compact in-band label at the right edge (size 15); avoids the legend.
    ax.text(0.99, 0.0, r"$|x_2|=\mathcal{O}(l_{\varepsilon})$",
            transform=ax.get_yaxis_transform(),
            ha="right", va="center", fontsize=FONT_SIZE, color="0.35",
            clip_on=True)


def _mark_outer_limits(ax, x_left, x_right, gap=0.04, color="0.25"):
    """Open markers at the one-sided outer limits x2 = 0+/-."""
    ax.plot([x_left], [-gap], "o", color=color, ms=5.0, mfc="none",
            mew=1.1, zorder=5)
    ax.plot([x_right], [gap], "o", color=color, ms=5.0, mfc="none",
            mew=1.1, zorder=5)


def draw_fig6a(ax, p: Params, eps_s=0.05, *, show_title=False):
    gap = 0.08
    z = _bending_z(gap=gap)
    _shade_neutral_layer(ax, gap=gap)
    for c, lh in zip(COLORS, [0.0, 2.0, 5.0, 10.0]):
        F = bending_fields(z, eps_s, lh, p)
        lbl = "SSD-only" if lh == 0 else rf"$l/h={lh:g}$"
        ls = "--" if lh == 0 else "-"
        ax.plot(F["sig_m_hat"], z, color=c, ls=ls, lw=LINE_LW, label=lbl)
        # One-sided outer limits for the MSG cases.
        if lh > 0:
            F_lim = bending_fields(np.array([-gap, gap]), eps_s, lh, p)
            _mark_outer_limits(ax, F_lim["sig_m_hat"][0],
                               F_lim["sig_m_hat"][1], gap=gap, color=c)
    ax.set_xlabel(r"$\sigma_{\mathrm{m}}/\sigma_{\mathrm{Y}}$")
    ax.set_ylabel(r"$x_2/h$")
    if show_title:
        panel_title(ax, r"(a) $\sigma_{\mathrm{m}}$")
    ax.legend(loc="best", fontsize=FONT_SIZE)


def draw_fig6b(ax, p: Params, eps_s=0.05, *, show_title=False):
    gap = 0.08
    z = _bending_z(gap=gap)
    _shade_neutral_layer(ax, gap=gap)
    for c, lh in zip(COLORS, [0.0, 2.0, 5.0, 10.0]):
        F = bending_fields(z, eps_s, lh, p)
        lbl = "SSD-only" if lh == 0 else rf"$l/h={lh:g}$"
        ls = "--" if lh == 0 else "-"
        ax.plot(F["cL_rel"], z, color=c, ls=ls, lw=LINE_LW, label=lbl)
    ax.set_xlabel(r"$c_{\mathrm{L}}/c_{\mathrm{L}}^0$")
    ax.set_ylabel(r"$x_2/h$")
    if show_title:
        panel_title(ax, r"(b) $c_{\mathrm{L}}$")
    ax.legend(loc="best", fontsize=FONT_SIZE)


def draw_fig6c(ax, p: Params, eps_s=0.05, *, show_title=False):
    # Panel (c) sits beside panel (b) in the manuscript figure, so the shared
    # $x_2/h$ label/ticks and the $l/h$ legend are omitted here.
    gap = 0.08
    z = _bending_z(gap=gap)
    _shade_neutral_layer(ax, gap=gap)
    for c, lh in zip(COLORS, [0.0, 2.0, 5.0, 10.0]):
        F = bending_fields(z, eps_s, lh, p)
        ls = "--" if lh == 0 else "-"
        ax.plot(F["cT_norm"], z, color=c, ls=ls, lw=LINE_LW)
        if lh > 0:
            F_lim = bending_fields(np.array([-gap, gap]), eps_s, lh, p)
            _mark_outer_limits(ax, F_lim["cT_norm"][0],
                               F_lim["cT_norm"][1], gap=gap, color=c)
    ax.set_xlabel(r"$c_{\mathrm{T}}\,/\,[\chi\,\theta_{\mathrm{T}}^{0}/(l\,b^{2})]$")
    ax.tick_params(axis="y", labelleft=False)
    if show_title:
        panel_title(ax, r"(c) $c_{\mathrm{T}}$")


def draw_fig6d(ax, p: Params, eps_s=0.05, *, show_title=False):
    h_min, h_max = 0.2e-6, 50e-6
    h = np.logspace(np.log10(h_min), np.log10(h_max), 60)
    cL_avg, cT_avg = zip(*[bending_average_uptake(hh, eps_s, p) for hh in h])
    cL_avg = np.asarray(cL_avg)
    cT_avg = np.asarray(cT_avg)
    ax.plot(h * 1e6, cL_avg / cL_avg[-1], color=COLORS_THREE[0], ls=LINESTYLES_THREE[0],
            lw=LINE_LW, label=r"$\bar{c}_{\mathrm{L}}/\bar{c}_{\mathrm{L}}^{\mathrm{thick}}$")
    ax.plot(h * 1e6, cT_avg / cT_avg[-1], color=COLORS_THREE[1], ls=LINESTYLES_THREE[1],
            lw=LINE_LW, label=r"$\bar{c}_{\mathrm{T}}/\bar{c}_{\mathrm{T}}^{\mathrm{thick}}$")
    ax.axhline(1.0, color="0.5", lw=0.7, ls=":")
    ax.set_xscale("log")
    ax.set_xlabel(r"Beam thickness $h$ [$\mu\mathrm{m}$]")
    ax.set_ylabel("Normalized average concentration")
    if show_title:
        panel_title(ax, "(d)")
    ax.legend(loc="best", fontsize=FONT_SIZE)


# ----------------------------------------------------------------------
# Fig. 9 — void closed forms
# ----------------------------------------------------------------------

def draw_fig9a(ax, p: Params, delta=0.2, *, show_title=False):
    """Wall GND trap-site density vs void radius: the 1/R0 scaling."""
    # N_T^GND(R0) / [chi/(l b^2)] = 3 sqrt(5/2) l delta / R0
    # so N_T^GND ∝ 1/R0 at fixed delta.
    R0 = np.logspace(np.log10(0.05e-6), np.log10(20e-6), 80)
    pref = 3.0 * np.sqrt(2.5) * p.l * delta
    NT_gnd = pref / R0   # in units of chi/(l b^2)  [since NT = chi/(l b^2) * l_eta]
    # Guide with the same slope, vertically offset so it is not hidden
    # under the exact 1/R0 data curve.
    R_ref = 1.0e-6
    NT_ref = pref / R_ref
    ax.loglog(R0 * 1e6, 2.0 * NT_ref * (R_ref / R0), color="black", lw=1.4,
              ls="-.", label=r"$\propto 1/R_0$", zorder=1)
    ax.loglog(R0 * 1e6, NT_gnd, color="blue", lw=LINE_LW,
              label=r"$N_{\mathrm{T}}^{\mathrm{GND}}(R_0)$", zorder=2)
    # SSD–GND wall crossover from eq:void:crossover at this delta.
    R_cross = (3.0 * np.sqrt(2.5) * p.l * delta
               / f_power(2.0 * delta, p) ** 2)
    ax.axvline(R_cross * 1e6, color="0.2", lw=1.1, ls="--", zorder=0)
    ax.text(R_cross * 1e6 * 0.45, 0.42,
            r"GND-dominated",
            transform=ax.get_xaxis_transform(),
            ha="center", va="center", fontsize=FONT_SIZE, color="0.2",
            rotation=90)
    ax.annotate(
        rf"$R_0\approx{R_cross*1e6:.2f}\,\mu\mathrm{{m}}$",
        xy=(R_cross * 1e6, NT_gnd[np.argmin(np.abs(R0 - R_cross))]),
        xytext=(R_cross * 1e6 * 2.2, NT_gnd[np.argmin(np.abs(R0 - R_cross))] * 3.0),
        fontsize=FONT_SIZE, color="0.2",
        arrowprops=dict(arrowstyle="-", color="0.35", lw=0.8),
        ha="left", va="bottom")
    ax.set_xlabel(r"Void radius $R_0$ [$\mu\mathrm{m}$]")
    ax.set_ylabel(
        r"$N_{\mathrm{T}}^{\mathrm{GND}}(R_0)\,/\,[\chi/(l\,b^{2})]$")
    if show_title:
        panel_title(ax, r"(a) Wall $N_{\mathrm{T}}^{\mathrm{GND}}$")
    ax.legend(loc="upper right", fontsize=FONT_SIZE)


def draw_fig9b(ax, p: Params, delta=0.2, *, show_title=False):
    s = np.linspace(1.0, 5.0, 800)
    for c, lr in zip(COLORS, [0.0, 1.0, 5.0, 10.0]):
        F = void_fields(s, delta, lr, p)
        lbl = "SSD-only" if lr == 0 else rf"$l/R_0={lr:g}$"
        ls = "--" if lr == 0 else "-"
        ax.plot(s, F["sig_m_hat"], color=c, ls=ls, lw=LINE_LW, label=lbl)
    ax.set_xlabel(r"$R/R_0$")
    ax.set_ylabel(r"$\sigma_{\mathrm{m}}/\sigma_{\mathrm{Y}}$")
    if show_title:
        panel_title(ax, r"(b) $\sigma_{\mathrm{m}}$")
    ax.legend(loc="best", fontsize=FONT_SIZE)


def draw_fig9c(ax, p: Params, delta=0.2, *, show_title=False):
    s = np.linspace(1.0, 5.0, 800)
    for c, lr in zip(COLORS, [0.0, 1.0, 5.0, 10.0]):
        F = void_fields(s, delta, lr, p)
        lbl = "SSD-only" if lr == 0 else rf"$l/R_0={lr:g}$"
        ls = "--" if lr == 0 else "-"
        ax.plot(s, F["cL_rel"], color=c, ls=ls, lw=LINE_LW, label=lbl)
    ax.set_xlabel(r"$R/R_0$")
    ax.set_ylabel(r"$c_{\mathrm{L}}/c_{\mathrm{L}}^0$")
    if show_title:
        panel_title(ax, r"(c) $c_{\mathrm{L}}$")
    ax.legend(loc="best", fontsize=FONT_SIZE)


def draw_fig9d(ax, p: Params, delta=0.2, *, show_title=False):
    s = np.linspace(1.0, 5.0, 800)
    for c, lr in zip(COLORS, [0.0, 1.0, 5.0, 10.0]):
        F = void_fields(s, delta, lr, p)
        lbl = "SSD-only" if lr == 0 else rf"$l/R_0={lr:g}$"
        ls = "--" if lr == 0 else "-"
        ax.plot(s, F["cT_norm"], color=c, ls=ls, lw=LINE_LW, label=lbl)
    ax.set_xlabel(r"$R/R_0$")
    ax.set_ylabel(r"$c_{\mathrm{T}}\,/\,[\chi\,\theta_{\mathrm{T}}^{0}/(l\,b^{2})]$")
    ax.set_yscale("log")
    if show_title:
        panel_title(ax, r"(d) $c_{\mathrm{T}}$")
    ax.legend(loc="best", fontsize=FONT_SIZE)


# ----------------------------------------------------------------------
# Fig. 10 — cavitation
# ----------------------------------------------------------------------

def draw_fig10a(ax, p: Params, xi=0.3, *, show_title=False):
    lr_grid = np.logspace(np.log10(0.1), np.log10(20.0), 16)
    activities = [0.0, 1e-6, 1e-5, 1e-4]
    labels = ["Hydrogen-free", r"$\theta_{\mathrm{L}}^0=10^{-6}$",
              r"$\theta_{\mathrm{L}}^0=10^{-5}$", r"$\theta_{\mathrm{L}}^0=10^{-4}$"]
    for c, th0, lbl in zip(COLORS, activities, labels):
        q = Params(**{**p.__dict__})
        q.xi = 0.0 if th0 == 0.0 else xi
        q.thetaL0 = max(th0, 1e-12)
        sigc = np.array([cavitation_stress(lr, q) for lr in lr_grid])
        ax.plot(lr_grid, sigc, color=c, lw=LINE_LW, label=lbl)
    ax.set_xscale("log")
    ax.set_xlabel(r"$l/R_0$")
    ax.set_ylabel(r"$\sigma_{\mathrm{c}}/\sigma_{\mathrm{Y}}^{\,0}$")
    if show_title:
        panel_title(ax, r"(a) $\xi=0.3$")
    ax.legend(loc="upper left", fontsize=FONT_SIZE)


def draw_fig10b(ax, p: Params, xi=0.3, *, show_title=False):
    lr_grid = np.logspace(np.log10(0.1), np.log10(20.0), 16)
    th_grid = np.logspace(-8, -4, 13)
    # reference: hydrogen-free cavitation stress
    q0 = Params(**{**p.__dict__})
    q0.xi = 0.0
    q0.thetaL0 = 1e-12
    sigc_ref = np.array([cavitation_stress(lr, q0) for lr in lr_grid])
    knock = np.zeros((len(th_grid), len(lr_grid)))
    for i, th0 in enumerate(th_grid):
        q = Params(**{**p.__dict__})
        q.xi = xi
        q.thetaL0 = th0
        for j, lr in enumerate(lr_grid):
            knock[i, j] = 1.0 - cavitation_stress(lr, q) / sigc_ref[j]
    X, Y = np.meshgrid(lr_grid, th_grid)
    cf = ax.contourf(X, Y, knock, levels=12, cmap="coolwarm")
    cs = ax.contour(X, Y, knock, levels=[0.05, 0.10, 0.15, 0.20, 0.25],
                    colors="0.15", linewidths=0.8)
    ax.clabel(cs, fontsize=FONT_SIZE, fmt="%.2f", inline=True, inline_spacing=8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"$l/R_0$")
    ax.set_ylabel(r"$\theta_{\mathrm{L}}^0$")
    if show_title:
        panel_title(ax, r"(b) Knockdown")
    cbar = ax.figure.colorbar(cf, ax=ax, shrink=0.9, pad=0.02)
    cbar.set_label(
        r"$1-\sigma_{\mathrm{c}}(\theta_{\mathrm{L}}^{0})"
        r"/\sigma_{\mathrm{c}}(0)$",
        fontsize=FONT_SIZE)
    cbar.ax.tick_params(labelsize=FONT_SIZE)
    return cf


def compose_fig_torsion(p: Params):
    """Multi-panel PDF used by the paper (fig_torsion.pdf)."""
    from _style import apply_style, save
    apply_style()
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 5.6))
    draw_fig3a(axes[0], p, show_title=True)
    draw_fig3b(axes[1], p, show_title=True)
    draw_fig3c(axes[2], p, show_title=True)
    # legends already on axes; tighten for paper layout
    for ax in axes:
        leg = ax.get_legend()
        if leg is not None:
            leg.remove()
    h_a = axes[0].get_lines()
    h_b = axes[1].get_lines()
    h_c = axes[2].get_lines()
    fig.tight_layout(rect=[0, 0.16, 1, 1], w_pad=2.4)
    axes[0].legend(h_a, [h.get_label() for h in h_a],
                   loc="upper center", bbox_to_anchor=(0.5, -0.24),
                   ncol=2, fontsize=FONT_SIZE)
    axes[1].legend(h_b, [h.get_label() for h in h_b],
                   loc="upper center", bbox_to_anchor=(0.5, -0.24),
                   ncol=2, fontsize=FONT_SIZE)
    axes[2].legend(h_c, [h.get_label() for h in h_c],
                   loc="upper center", bbox_to_anchor=(0.5, -0.24),
                   ncol=3, fontsize=FONT_SIZE)
    save(fig, "fig_torsion.pdf")


def compose_fig_bending(p: Params):
    from _style import apply_style, save
    apply_style()
    fig, axes = plt.subplots(1, 4, figsize=(18.0, 5.2))
    draw_fig6a(axes[0], p, show_title=True)
    draw_fig6b(axes[1], p, show_title=True)
    draw_fig6c(axes[2], p, show_title=True)
    draw_fig6d(axes[3], p, show_title=True)
    for ax in axes:
        leg = ax.get_legend()
        if leg is not None:
            leg.remove()
    handles, labels = axes[0].get_legend_handles_labels()
    h_d, l_d = axes[3].get_legend_handles_labels()
    fig.tight_layout(rect=[0, 0.14, 1, 1], w_pad=2.0)
    fig.legend(handles, labels, loc="lower left", ncol=4,
               bbox_to_anchor=(0.02, 0.0), frameon=True,
               fontsize=FONT_SIZE)
    fig.legend(h_d, l_d, loc="lower right", ncol=2,
               bbox_to_anchor=(0.98, 0.0), frameon=True,
               fontsize=FONT_SIZE)
    save(fig, "fig_bending.pdf")


def compose_fig_void(p: Params):
    from _style import apply_style, save
    apply_style()
    fig, axes = plt.subplots(1, 4, figsize=(18.0, 5.2))
    draw_fig9a(axes[0], p, show_title=True)
    draw_fig9b(axes[1], p, show_title=True)
    draw_fig9c(axes[2], p, show_title=True)
    draw_fig9d(axes[3], p, show_title=True)
    for ax in axes:
        leg = ax.get_legend()
        if leg is not None:
            leg.remove()
    handles, labels = axes[0].get_legend_handles_labels()
    fig.tight_layout(rect=[0, 0.12, 1, 1], w_pad=2.2)
    fig.legend(handles, labels, loc="lower center", ncol=4,
               bbox_to_anchor=(0.5, 0.0), frameon=True,
               fontsize=FONT_SIZE)
    save(fig, "fig_void.pdf")


def compose_fig_cavitation(p: Params):
    from _style import apply_style, save
    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 5.4))
    draw_fig10a(axes[0], p, show_title=True)
    draw_fig10b(axes[1], p, show_title=True)
    fig.tight_layout()
    save(fig, "fig_cavitation.pdf")
