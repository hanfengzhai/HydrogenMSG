"""Fig. 12 mesh convergence: tip-window L2 norms with rate estimates (SI).

Solves a nested uniform tip-window hierarchy, samples fields on a common
grid, and writes a single log–log plot of relative L2 errors vs h with
least-squares rate annotations.

Usage:  python3 scripts/figures/fig12conv.py
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

from _fem import fig12conv


if __name__ == "__main__":
    fig12conv()
