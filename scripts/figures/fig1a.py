"""Fig. 1(a): coupled MSG-hydrogen chain.

Canonical source for Overleaf / the manuscript is TikZ:
  ``scripts/figures/fig1a.tikz`` (standalone wrapper: ``fig1a.tex``).
This script regenerates the tracked PNG / local PDF preview in a matching
white-box / gray-key / Latex-arrow style.

Math labels use matplotlib mathtext: wrap symbols in ``$...$``
(e.g. ``r"$\\sigma_{\\mathrm{m}}$"``). Do not use ``$$``.
Panel titles stay plain text (no mathtext).

Usage:  python3 scripts/figures/fig1a.py
"""

import _bootstrap  # noqa: F401

from _schematics import make_fig1a


def main():
    make_fig1a()


if __name__ == "__main__":
    main()
