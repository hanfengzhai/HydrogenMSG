"""Shared matplotlib style for per-panel figure scripts.

Math convention (matplotlib mathtext)
-------------------------------------
Wrap every equation / math symbol in single dollar signs so it renders:

    r"$\\sigma_{\\mathrm{m}}/\\sigma_{\\mathrm{Y}}$"
    r"$\\theta_{\\mathrm{T}}$"          # theta, not \\tho
    r"$l/R_0$"
    r"$c_{\\mathrm{T}}$"

Do **not** use LaTeX display math ``$$...$$`` here — that is for Markdown /
GitHub README only. Matplotlib mathtext parses ``$...$``.

Use ``\\mathrm{...}`` for upright multi-letter sub/superscripts (T, L, Y, …).
``mathtext.default`` is italic so variables match paper math; roman subscripts
stay upright via ``\\mathrm``.

Panel titles in schematics / FEM figures stay plain text (no ``$``).
Axis labels, legends, tick numbers, and in-panel annotations use Computer
Modern (``mathtext.fontset = cm`` / ``cmr10``) so all figure fonts match
LaTeX equation style.
"""

from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# scripts/ on sys.path for msg_hydrogen / fem_* imports
_SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

OUT = os.path.join(_SCRIPTS, "..", "figures")
os.makedirs(OUT, exist_ok=True)

FONT_SIZE = 15
# SSD-only / gradient-free (dashed) + three comparison curves.
COLORS = ["#000000", "blue", "tab:red", "tab:green", "#CC79A7"]
COLORS_THREE = ["blue", "tab:red", "tab:green"]
LINESTYLES_THREE = ["-", "--", "-."]
MECH = "#0072B2"
HYDR = "#D55E00"
GREY = "0.45"
FEED = "#7f7f7f"
FILL = "0.90"
FILL2 = "0.80"
EDGE = "0.25"
LINE_LW = 1.9

FIGW = 12.0

_RC = {
    "font.family": "serif",
    "font.serif": ["cmr10", "DejaVu Serif"],
    "font.weight": "normal",
    # Computer Modern: same family as LaTeX equation mode (ticks included).
    "mathtext.fontset": "cm",
    # Italic variables; keep subscripts upright with \\mathrm.
    "mathtext.default": "it",
    "axes.formatter.use_mathtext": True,
    "font.size": FONT_SIZE,
    "axes.titlesize": FONT_SIZE,
    "axes.labelsize": FONT_SIZE,
    "xtick.labelsize": FONT_SIZE,
    "ytick.labelsize": FONT_SIZE,
    "legend.fontsize": FONT_SIZE,
    "figure.titlesize": FONT_SIZE,
    "figure.titleweight": "normal",
    "axes.titleweight": "normal",
    "axes.labelweight": "normal",
    "axes.unicode_minus": False,
    "axes.linewidth": 0.8,
    "lines.linewidth": LINE_LW,
    "figure.dpi": 150,
    "legend.frameon": True,
    "legend.fancybox": False,
    "legend.framealpha": 0.95,
    "legend.edgecolor": "0.7",
    "legend.borderpad": 0.35,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
}


def apply_style(**extra):
    """Apply paper rcParams. Call once at the start of each panel script."""
    cfg = dict(_RC)
    cfg.update(extra)
    plt.rcParams.update(cfg)


def regular_font(size=FONT_SIZE):
    """Computer Modern Roman (cmr10) for LaTeX equation-style plain text."""
    for cand in font_manager.fontManager.ttflist:
        if cand.name == "cmr10" or os.path.basename(cand.fname).lower().startswith(
                "cmr10"):
            return font_manager.FontProperties(fname=cand.fname, size=size)
    return font_manager.FontProperties(family="cmr10", size=size)


TITLE_FONT = None  # set lazily after apply_style / first use


def title_font(size=FONT_SIZE):
    global TITLE_FONT
    if TITLE_FONT is None or TITLE_FONT.get_size() != size:
        TITLE_FONT = regular_font(size)
    return TITLE_FONT


def panel_title(ax, text, *, allow_math=True):
    """Panel title in Computer Modern Roman (cmr10).

    For analytical plots, ``allow_math=True`` permits ``$...$`` in the title.
    For schematics/FEM composed figures, pass ``allow_math=False``.
    """
    if not allow_math and "$" in text:
        raise ValueError(f"panel titles must be plain text, got: {text!r}")
    ax.set_title(text, fontproperties=title_font())


def _crop_png_whitespace(path, *, pad_px=10, thresh=250):
    """Trim near-white margins from a PNG (safety net after savefig)."""
    import numpy as np
    from PIL import Image

    im = Image.open(path)
    arr = np.asarray(im.convert("RGB"))
    ink = (arr < thresh).any(axis=2)
    if not ink.any():
        return
    ys, xs = np.where(ink)
    y0 = max(int(ys.min()) - pad_px, 0)
    y1 = min(int(ys.max()) + pad_px + 1, arr.shape[0])
    x0 = max(int(xs.min()) - pad_px, 0)
    x1 = min(int(xs.max()) + pad_px + 1, arr.shape[1])
    im.crop((x0, y0, x1, y1)).save(path)


def _crop_pdf_whitespace(path, *, pad_pt=8.0, thresh=250, dpi=200):
    """Trim near-white margins from a single-page PDF via PyMuPDF.

    PyMuPDF page coordinates are top-left (y down), same as the pixmap, so
    the content box is applied directly — do not flip Y.  The page is
    rewritten to a new MediaBox so viewers that ignore CropBox still match
    the PNG.
    """
    import numpy as np
    try:
        import fitz
    except ImportError:
        return

    doc = fitz.open(path)
    if doc.page_count < 1:
        doc.close()
        return
    page = doc[0]
    # Always measure against the full media box, not a prior crop.
    page.set_cropbox(page.mediabox)
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72.0, dpi / 72.0), alpha=False)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    ink = (arr < thresh).any(axis=2)
    if not ink.any():
        doc.close()
        return
    ys, xs = np.where(ink)
    scale = 72.0 / dpi
    x0 = max(float(xs.min()) * scale - pad_pt, 0.0)
    y0 = max(float(ys.min()) * scale - pad_pt, 0.0)
    x1 = min(float(xs.max()) * scale + pad_pt, page.mediabox.width)
    y1 = min(float(ys.max()) * scale + pad_pt, page.mediabox.height)
    clip = fitz.Rect(x0, y0, x1, y1)
    if clip.width < 1.0 or clip.height < 1.0:
        doc.close()
        return

    out = fitz.open()
    new_page = out.new_page(width=clip.width, height=clip.height)
    new_page.show_pdf_page(new_page.rect, doc, 0, clip=clip)
    tmp = path + ".tmp.pdf"
    out.save(tmp, deflate=True)
    out.close()
    doc.close()
    os.replace(tmp, path)


def _pad_png_to_size(path, width, height, *, bg=(255, 255, 255)):
    """Pad a PNG with white so it matches ``(width, height)`` (right/bottom bias)."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    if im.size == (width, height):
        return
    canvas = Image.new("RGB", (width, height), bg)
    # Keep right and bottom edges aligned so x-labels line up; pad left/top.
    x0 = width - im.size[0]
    y0 = height - im.size[1]
    canvas.paste(im, (max(x0, 0), max(y0, 0)))
    canvas.save(path)


def _pad_pdf_to_size(path, width_pt, height_pt):
    """Pad a single-page PDF with white to the given MediaBox size."""
    try:
        import fitz
    except ImportError:
        return
    doc = fitz.open(path)
    if doc.page_count < 1:
        doc.close()
        return
    page = doc[0]
    src = page.rect
    if abs(src.width - width_pt) < 0.5 and abs(src.height - height_pt) < 0.5:
        doc.close()
        return
    out = fitz.open()
    new_page = out.new_page(width=width_pt, height=height_pt)
    # Align to bottom-right so shared axes edges coincide after left padding.
    dest = fitz.Rect(width_pt - src.width, height_pt - src.height,
                     width_pt, height_pt)
    new_page.show_pdf_page(dest, doc, 0)
    tmp = path + ".tmp.pdf"
    out.save(tmp, deflate=True)
    out.close()
    doc.close()
    os.replace(tmp, path)


def match_panel_canvases(paths):
    """Pad cropped fixed-canvas panels to a common size (max w x max h)."""
    from PIL import Image
    try:
        import fitz
    except ImportError:
        fitz = None
    sizes = []
    for p in paths:
        png = p if p.endswith(".png") else p.replace(".pdf", ".png")
        im = Image.open(png)
        sizes.append(im.size)
    wt = max(w for w, _ in sizes)
    ht = max(h for _, h in sizes)
    for p in paths:
        png = p if p.endswith(".png") else p.replace(".pdf", ".png")
        pdf = png.replace(".png", ".pdf")
        _pad_png_to_size(png, wt, ht)
        if fitz is not None and os.path.isfile(pdf):
            # Convert px @ 200 dpi used by save() to points.
            _pad_pdf_to_size(pdf, wt * 72.0 / 200.0, ht * 72.0 / 200.0)


def save(fig, name, *, dpi_png=200, tight=True, pad_inches=0.03,
         fixed_canvas=False, crop=None):
    """Write PDF + PNG under ``figures/``.

    By default crops with ``bbox_inches='tight'`` and a content-based trim.
    Pass ``fixed_canvas=True`` to keep the authored figure size (identical
    panel boxes for side-by-side subfigures). Content trim still runs unless
    ``crop=False``; for fixed canvases pass ``crop=True`` to trim shared
    outer whitespace without changing the axes box.
    """
    if not name.endswith(".pdf"):
        name = name + ".pdf"
    path = os.path.join(OUT, name)
    png = path.replace(".pdf", ".png")
    if fixed_canvas:
        kw = {}
    else:
        kw = {"bbox_inches": "tight", "pad_inches": pad_inches}
    fig.savefig(path, **kw)
    fig.savefig(png, dpi=dpi_png, **kw)
    do_crop = (not fixed_canvas) if crop is None else crop
    if do_crop:
        _crop_png_whitespace(png, pad_px=12)
        _crop_pdf_whitespace(path, pad_pt=8.0)
    plt.close(fig)
    print(f"wrote {os.path.relpath(path)}")
    return path


def _artist_data_extents(ax, renderer):
    """Axis-aligned data bbox covering patches, lines, and text on ``ax``."""
    import numpy as np
    from matplotlib.patches import (Circle, Ellipse, FancyBboxPatch, Patch,
                                    Rectangle, Wedge)
    from matplotlib.text import Text, Annotation
    from matplotlib.lines import Line2D
    from matplotlib.collections import Collection

    xs, ys = [], []

    def _add_xy(x, y):
        x = np.atleast_1d(np.asarray(x, dtype=float))
        y = np.atleast_1d(np.asarray(y, dtype=float))
        m = np.isfinite(x) & np.isfinite(y)
        if m.any():
            xs.append(x[m])
            ys.append(y[m])

    def _add_box(x0, x1, y0, y1):
        _add_xy([x0, x1], [y0, y1])

    skip = {ax.patch}
    for art in ax.get_children():
        if art in skip or not art.get_visible():
            continue
        if isinstance(art, Circle):
            c = art.center
            r = art.radius
            _add_box(c[0] - r, c[0] + r, c[1] - r, c[1] + r)
        elif isinstance(art, Ellipse):
            c = art.center
            _add_box(c[0] - art.width / 2, c[0] + art.width / 2,
                     c[1] - art.height / 2, c[1] + art.height / 2)
        elif isinstance(art, Wedge):
            c = art.center
            r = art.r
            _add_box(c[0] - r, c[0] + r, c[1] - r, c[1] + r)
        elif isinstance(art, (Rectangle, FancyBboxPatch)):
            _add_box(art.get_x(), art.get_x() + art.get_width(),
                     art.get_y(), art.get_y() + art.get_height())
        elif isinstance(art, Patch):
            try:
                verts = art.get_path().transformed(
                    art.get_patch_transform()).vertices
                _add_xy(verts[:, 0], verts[:, 1])
            except Exception:
                pass
        elif isinstance(art, Line2D):
            _add_xy(art.get_xdata(), art.get_ydata())
        elif isinstance(art, Annotation):
            try:
                xy = art.xy
                xytext = art.xyann
                _add_xy([xy[0], xytext[0]], [xy[1], xytext[1]])
            except Exception:
                pass
        elif isinstance(art, Text):
            pos = art.get_position()
            # Small pad around the anchor so labels are not clipped.
            _add_box(pos[0] - 0.12, pos[0] + 0.12,
                     pos[1] - 0.10, pos[1] + 0.10)
        elif isinstance(art, Collection):
            try:
                offs = art.get_offsets()
                if offs is not None and len(offs):
                    _add_xy(offs[:, 0], offs[:, 1])
            except Exception:
                pass

    if not xs:
        return None
    x = np.concatenate(xs)
    y = np.concatenate(ys)
    return float(x.min()), float(x.max()), float(y.min()), float(y.max())


def fit_geom_panel(fig, ax, pad=0.08, *, min_size=1.6, equal=True):
    """Crop a geometry axes to its artists and resize the figure to match.

    Figure size matches the content aspect (no square padding). With
    ``equal=True``, ``set_aspect('equal')`` keeps circles round because the
    figure aspect equals the data aspect. Hides the axes patch so empty
    white area cannot expand ``bbox_inches='tight'``.
    """
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    extents = _artist_data_extents(ax, renderer)
    if extents is None:
        return
    x0, x1, y0, y1 = extents
    dx = max(x1 - x0, 1e-6)
    dy = max(y1 - y0, 1e-6)
    p = pad * max(dx, dy)
    x0, x1 = x0 - p, x1 + p
    y0, y1 = y0 - p, y1 + p
    dx, dy = x1 - x0, y1 - y0

    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    if equal:
        ax.set_aspect("equal", adjustable="box")
    ax.patch.set_visible(False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Scale so the longer side is at least min_size inches. ``min_size=None``
    # keeps the authored scale (one data unit = one inch), so text drawn at a
    # fixed point size stays inside boxes sized in inches.
    scale = 1.0 if min_size is None else min_size / max(dx, dy)
    w, h = max(dx * scale, 0.8), max(dy * scale, 0.8)
    fig.set_size_inches(w, h, forward=True)
    ax.set_position([0.02, 0.02, 0.96, 0.96])


def new_axes(figsize=(5.6, 5.0)):
    """Single-panel figure + axes for an ad hoc figXa.py script."""
    apply_style()
    fig, ax = plt.subplots(figsize=figsize)
    return fig, ax
