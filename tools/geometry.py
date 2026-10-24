"""Shared drawing primitives for the Chizpita brand masters.

Everything here produces plain SVG path data. Text is converted to outlines
with fontTools so the published masters never depend on an installed font.
"""
import math
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.varLib import instancer

_fonts = {}


def font(path, **axes):
    key = (path, tuple(sorted(axes.items())))
    if key not in _fonts:
        f = TTFont(path)
        if axes and 'fvar' in f:
            f = instancer.instantiateVariableFont(f, axes)
        _fonts[key] = f
    return _fonts[key]


def f2(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.')


def glyph_path(fnt, glyph, size, x, y, rot=0.0, ys=1.0, ybase=None):
    """Outline of one glyph. (x, y) is the centre of the glyph's advance on
    the baseline; rot rotates around that point (degrees, clockwise).
    ys stretches the result vertically about ybase (custom lettering)."""
    gs = fnt.getGlyphSet()
    upm = fnt['head'].unitsPerEm
    adv = fnt['hmtx'][glyph][0]
    k = size / upm
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    cx = adv / 2
    xx, xy, yx, yy = ca * k, sa * k, sa * k, -ca * k
    dx, dy = x - xx * cx, y - xy * cx
    if ys != 1.0:
        yb = y if ybase is None else ybase
        xy, yy, dy = xy * ys, yy * ys, yb + (dy - yb) * ys
    pen = SVGPathPen(gs, ntos=f2)
    gs[glyph].draw(TransformPen(pen, (xx, xy, yx, yy, dx, dy)))
    return pen.getCommands(), adv * k


def advance(fnt, glyph, size):
    return fnt['hmtx'][glyph][0] * size / fnt['head'].unitsPerEm


def kern(fnt, a, b, size):
    """Pair kerning from a legacy 'kern' table if present (GPOS ignored)."""
    if 'kern' not in fnt:
        return 0
    for t in fnt['kern'].kernTables:
        v = t.kernTable.get((a, b))
        if v:
            return v * size / fnt['head'].unitsPerEm
    return 0


def glyph_name(fnt, ch):
    return fnt.getBestCmap()[ord(ch)]


def text_run(fnt, text, size, tracking=0.0, glyphs=None):
    """Lay out text on a straight baseline. Returns list of
    (glyph, centre_x, advance) and total width. tracking in em."""
    names = glyphs or [glyph_name(fnt, c) for c in text]
    out, x = [], 0.0
    for i, g in enumerate(names):
        adv = advance(fnt, g, size)
        if i:
            x += kern(fnt, names[i - 1], g, size) + tracking * size
        out.append((g, x + adv / 2, adv))
        x += adv
    return out, x


def text_path(fnt, text, size, x, y, tracking=0.0, anchor='start'):
    run, w = text_run(fnt, text, size, tracking)
    x0 = x - (w / 2 if anchor == 'middle' else w if anchor == 'end' else 0)
    return ''.join(glyph_path(fnt, g, size, x0 + cx, y)[0] for g, cx, _ in run), w


def arc_text(fnt, text, size, cx, cy, r, centre_deg, tracking=0.0, outside=True):
    """Text on a circle. centre_deg: angle of the text centre (0 = top,
    clockwise). outside=True reads clockwise along the top (baseline on r);
    False reads counter-clockwise along the bottom (cap tops toward centre)."""
    run, w = text_run(fnt, text, size, tracking)
    d = []
    for g, gx, _ in run:
        s = gx - w / 2                      # arc length from centre
        if outside:
            ang = centre_deg + math.degrees(s / r)
            t = math.radians(ang)
            px, py = cx + r * math.sin(t), cy - r * math.cos(t)
            d.append(glyph_path(fnt, g, size, px, py, ang)[0])
        else:
            ang = centre_deg - math.degrees(s / r)
            t = math.radians(ang)
            px, py = cx + r * math.sin(t), cy - r * math.cos(t)
            d.append(glyph_path(fnt, g, size, px, py, ang + 180)[0])
    return ''.join(d)


# ---------------------------------------------------------------- geometry

def ellipse_pt(cx, cy, rx, ry, t):
    return cx + rx * math.cos(t), cy + ry * math.sin(t)


def circle_ellipse_hits(cx, cy, rx, ry, bx, by, r):
    """Parameters t where the ellipse meets circle (bx, by, r)."""
    def f(t):
        x, y = ellipse_pt(cx, cy, rx, ry, t)
        return math.hypot(x - bx, y - by) - r
    n, hits = 2000, []
    prev = f(0)
    for i in range(1, n + 1):
        t = 2 * math.pi * i / n
        cur = f(t)
        if prev * cur < 0:
            lo, hi = 2 * math.pi * (i - 1) / n, t
            for _ in range(60):
                mid = (lo + hi) / 2
                if f(lo) * f(mid) <= 0:
                    hi = mid
                else:
                    lo = mid
            hits.append((lo + hi) / 2)
        prev = cur
    return hits


def circle_hits(a, b):
    (x0, y0, r0), (x1, y1, r1) = a, b
    d = math.hypot(x1 - x0, y1 - y0)
    l = (r0 * r0 - r1 * r1 + d * d) / (2 * d)
    h = math.sqrt(max(r0 * r0 - l * l, 0))
    mx, my = x0 + l * (x1 - x0) / d, y0 + l * (y1 - y0) / d
    return ((mx + h * (y1 - y0) / d, my - h * (x1 - x0) / d),
            (mx - h * (y1 - y0) / d, my + h * (x1 - x0) / d))
