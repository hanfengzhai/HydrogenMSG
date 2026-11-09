"""Finite-element evaluation of MSG torsion and bending.

The void problem (scripts/fem_msg.py) is a true two-dimensional BVP.  For the
canonical wire-torsion and beam-bending problems the deformation-theory
kinematics are known a priori (Huang et al. 2000), so the finite-element
role is to evaluate the MSG constitutive response and hydrogen fields on a
Q9 discretisation and to verify them against the closed forms of Sections 3
and 4.

Torsion: quarter-disk mesh in the cross-section; eps_e = kappa r / sqrt(3),
eta^e = kappa, sigma_m = 0.

Bending: plane-strain strip mesh; eps_e = kappa |x2| * 2/sqrt(3) wait
eps_e = kappa_h * |2 z| / sqrt(3) with z = x2/h, eta^e = kappa.

Usage:  python3 scripts/fem_canonical.py
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msg_hydrogen import (Params, bending_fields, f_power, theta_L_local,
                          theta_T, torsion_cT_profile, torsion_torque)


# ----------------------------------------------------------------------
# Q9 meshes
# ----------------------------------------------------------------------

def _q9_shape(xi, et):
    lx = np.array([0.5 * xi * (xi - 1.0), 1.0 - xi * xi, 0.5 * xi * (xi + 1.0)])
    ly = np.array([0.5 * et * (et - 1.0), 1.0 - et * et, 0.5 * et * (et + 1.0)])
    return np.outer(ly, lx).ravel()


def mesh_disk(a=1.0, n_r=16, n_th=12):
    """Quarter-disk Q9 mesh in (x, y), radius a."""
    nr, nt = 2 * n_r + 1, 2 * n_th + 1
    rho = a * np.linspace(0.0, 1.0, nr) ** 1.2
    th = np.linspace(0.0, 0.5 * np.pi, nt)
    RHO, TH = np.meshgrid(rho, th, indexing="ij")
    coords = np.column_stack([(RHO * np.cos(TH)).ravel(),
                              (RHO * np.sin(TH)).ravel()])
    nid = np.arange(nr * nt).reshape(nr, nt)
    conn = np.empty((n_r * n_th, 9), dtype=int)
    e = 0
    for i in range(n_r):
        for j in range(n_th):
            i0, j0 = 2 * i, 2 * j
            conn[e] = [nid[i0 + di, j0 + dj]
                       for di in range(3) for dj in range(3)]
            e += 1
    return dict(coords=coords, conn=conn, a=a, n_r=n_r, n_th=n_th)


def mesh_strip(h=1.0, L=None, n_x=8, n_y=20):
    """Plane-strain strip Q9 mesh, x in [-L/2, L/2], y in [-h/2, h/2]."""
    L = L or 4.0 * h
    nx, ny = 2 * n_x + 1, 2 * n_y + 1
    xs = np.linspace(-0.5 * L, 0.5 * L, nx)
    ys = np.linspace(-0.5 * h, 0.5 * h, ny)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    coords = np.column_stack([X.ravel(), Y.ravel()])
    nid = np.arange(nx * ny).reshape(nx, ny)
    conn = np.empty((n_x * n_y, 9), dtype=int)
    e = 0
    for i in range(n_x):
        for j in range(n_y):
            i0, j0 = 2 * i, 2 * j
            conn[e] = [nid[i0 + di, j0 + dj]
                       for di in range(3) for dj in range(3)]
            e += 1
    return dict(coords=coords, conn=conn, h=h, L=L, n_x=n_x, n_y=n_y)


def _gauss_points(mesh, n_gp=3):
    """Return (nelem, ngp, 2) physical Gauss coordinates and weights."""
    gp, gw = np.polynomial.legendre.leggauss(n_gp)
    ne = mesh["conn"].shape[0]
    xy = np.zeros((ne, n_gp * n_gp, 2))
    w = np.zeros((ne, n_gp * n_gp))
    for e, nodes in enumerate(mesh["conn"]):
        xe = mesh["coords"][nodes]
        k = 0
        for a, wa in enumerate(gp):
            for b, wb in enumerate(gp):
                N = _q9_shape(gp[a], gp[b])
                # parent derivatives for Jacobian
                lx = np.array([0.5 * gp[a] * (gp[a] - 1.0),
                               1.0 - gp[a] * gp[a],
                               0.5 * gp[a] * (gp[a] + 1.0)])
                ly = np.array([0.5 * gp[b] * (gp[b] - 1.0),
                               1.0 - gp[b] * gp[b],
                               0.5 * gp[b] * (gp[b] + 1.0)])
                dx = np.array([gp[a] - 0.5, -2.0 * gp[a], gp[a] + 0.5])
                dy = np.array([gp[b] - 0.5, -2.0 * gp[b], gp[b] + 0.5])
                dN_dxi = np.outer(ly, dx).ravel()
                dN_det = np.outer(dy, lx).ravel()
                J = np.array([dN_dxi @ xe, dN_det @ xe]).T
                detJ = abs(np.linalg.det(J))
                xy[e, k] = N @ xe
                w[e, k] = wa * wb * detJ
                k += 1
    return xy, w


# ----------------------------------------------------------------------
# Solvers (constitutive evaluation on the FE mesh)
# ----------------------------------------------------------------------

def solve_torsion(Gamma=0.05, l_over_a=2.0, p=None, n_r=18, n_th=14):
    """MSG torsion fields on a Q9 quarter-disk mesh.

    Gamma = kappa * a.  Returns Gauss-point fields plus radial profiles.
    """
    p = p or Params()
    a = p.l / l_over_a if l_over_a > 0 else 1.0
    kappa = Gamma / a
    mesh = mesh_disk(a=a, n_r=n_r, n_th=n_th)
    xy, w = _gauss_points(mesh)
    r = np.hypot(xy[..., 0], xy[..., 1])
    s = r / a
    eps_e = kappa * r / np.sqrt(3.0)
    eta = np.full_like(eps_e, kappa)
    sig_e = p.sigY * np.sqrt(f_power(eps_e, p) ** 2 + p.l * eta)
    sig_m = np.zeros_like(sig_e)
    thL = theta_L_local(sig_m / p.sigY, p)
    thT = theta_T(thL, p)
    thT0 = theta_T(p.thetaL0, p)
    cT_norm = (thT / thT0) * (sig_e / p.sigY) ** 2

    # radial profile (sorted Gauss radii)
    rf = r.ravel()
    order = np.argsort(rf)
    r_prof = rf[order] / a
    cT_prof = cT_norm.ravel()[order]
    se_prof = (sig_e / p.sigY).ravel()[order]

    # Torque from the FE radial profile: T = 2 pi ∫ tau(r) r^2 dr
    # Deduplicate nearly coincident radii for a stable trapezoid rule.
    rr = rf[order]
    tau = (sig_e.ravel()[order]) / np.sqrt(3.0)
    keep = np.concatenate([[True], np.diff(rr) > 1e-12 * a])
    T = 2.0 * np.pi * np.trapz(tau[keep] * rr[keep] ** 2, rr[keep])
    T_hat = T / (p.sigY * a ** 3)

    return dict(
        mesh=mesh, p=p, Gamma=Gamma, l_over_a=l_over_a, a=a, kappa=kappa,
        xy=xy, w=w, r=r, s=s,
        eps_e=eps_e, eta=eta, l_eta=p.l * eta,
        sig_e_hat=sig_e / p.sigY, sig_m_hat=sig_m / p.sigY,
        cT_norm=cT_norm, cL_rel=thL / p.thetaL0,
        T_hat=float(T_hat),
        r_prof=r_prof, cT_prof=cT_prof, se_prof=se_prof,
    )


def solve_bending(eps_s=0.05, l_over_h=2.0, p=None, n_x=6, n_y=24):
    """MSG bending fields on a Q9 plane-strain strip mesh.

    eps_s = kappa h / 2 is the axial surface strain (manuscript definition).
    """
    p = p or Params()
    h = p.l / l_over_h if l_over_h > 0 else 1.0
    kappa = 2.0 * eps_s / h
    mesh = mesh_strip(h=h, n_x=n_x, n_y=n_y)
    xy, w = _gauss_points(mesh)
    x2 = xy[..., 1]
    z = x2 / h
    kappa_h = kappa * h
    eps_e = 2.0 * kappa_h * np.abs(z) / np.sqrt(3.0)
    eta = np.full_like(eps_e, kappa)
    sig_e = p.sigY * np.sqrt(f_power(eps_e, p) ** 2 + p.l * eta)
    sig_m = np.sign(z) * sig_e / np.sqrt(3.0)
    # Neutral-axis jump: at z=0 use + side for plotting continuity break
    thL = theta_L_local(sig_m / p.sigY, p)
    thT = theta_T(thL, p)
    thT0 = theta_T(p.thetaL0, p)
    cL_rel = thL / p.thetaL0
    cT_norm = (thT / thT0) * (sig_e / p.sigY) ** 2

    # through-thickness profile at mid-span (bin by x2)
    xf, zf = xy[..., 0].ravel(), xy[..., 1].ravel()
    mid = np.abs(xf) < 0.15 * mesh["L"]
    order = np.argsort(zf[mid])
    z_prof = (zf[mid][order]) / h
    sm_prof = (sig_m / p.sigY).ravel()[mid][order]
    cL_prof = cL_rel.ravel()[mid][order]
    cT_prof = cT_norm.ravel()[mid][order]

    return dict(
        mesh=mesh, p=p, eps_s=eps_s, l_over_h=l_over_h, h=h, kappa=kappa,
        xy=xy, w=w, x2=x2, z=z,
        eps_e=eps_e, eta=eta, l_eta=p.l * eta,
        sig_e_hat=sig_e / p.sigY, sig_m_hat=sig_m / p.sigY,
        cL_rel=cL_rel, cT_norm=cT_norm,
        z_prof=z_prof, sm_prof=sm_prof, cL_prof=cL_prof, cT_prof=cT_prof,
    )


def verify_torsion(Gamma=0.05, l_over_a=2.0):
    sol = solve_torsion(Gamma=Gamma, l_over_a=l_over_a)
    p = sol["p"]
    r = sol["r_prof"]
    # subsample unique-ish radial samples
    idx = np.linspace(0, len(r) - 1, 40).astype(int)
    r_s = r[idx]
    exact = torsion_cT_profile(r_s, Gamma, l_over_a, p)
    # analytical cT_norm uses chi theta_T/(l b^2); our cT_norm uses thT/thT0 * rho
    # With sig_m=0, thT=thT0, so cT_norm = f^2 + l kappa = exact
    fem = sol["cT_prof"][idx]
    err = float(np.max(np.abs(fem - exact) / np.maximum(exact, 1e-12)))
    T_an = torsion_torque(Gamma, l_over_a, p)
    return dict(cT_err=err, T_fem=sol["T_hat"], T_an=float(T_an),
                T_rel=abs(sol["T_hat"] / T_an - 1.0))


def verify_bending(eps_s=0.05, l_over_h=2.0):
    sol = solve_bending(eps_s=eps_s, l_over_h=l_over_h)
    p = sol["p"]
    z = sol["z_prof"]
    idx = np.linspace(0, len(z) - 1, 50).astype(int)
    z_s = z[idx]
    an = bending_fields(z_s, eps_s, l_over_h, p)
    err_m = float(np.max(np.abs(sol["sm_prof"][idx] - an["sig_m_hat"])))
    err_c = float(np.max(np.abs(sol["cT_prof"][idx] - an["cT_norm"])
                         / np.maximum(np.abs(an["cT_norm"]), 1e-12)))
    return dict(sig_m_err=err_m, cT_err=err_c)


if __name__ == "__main__":
    print("torsion:", verify_torsion())
    print("bending:", verify_bending())
