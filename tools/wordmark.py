"""The CHiZPiTA™ wordmark: Titan One (OFL) outlines with lowercase dotless
i's, a gentle hand-made bounce, the first i dotted with the spark
(chispa -> chispita) and the second with a round cheese dot."""
import os
from geometry import font, glyph_path, advance, kern, f2, text_path
from palette import spark_path, INK, GOLD as SPARK, LIGHT, CHEESE as CHEESE_LINE

HERE = os.path.dirname(os.path.abspath(__file__))
TITAN = os.path.join(HERE, 'fonts', 'TitanOne-Regular.ttf')
FIGTREE = os.path.join(HERE, 'fonts', 'Figtree-VF.ttf')

LETTERS = ['C', 'H', 'dotlessi', 'Z', 'P', 'dotlessi', 'T', 'A']
# per letter: (baseline shift, rotation deg) - the bounce
BOUNCE = [(0, -3), (-6, 1), (2, 0), (-4, 3), (2, -2), (-2, 0), (-6, 2), (2, -2)]
TRACK = -0.005        # em: letters nearly touching, like the concept
YSCALE = 1.24         # custom lettering: Titan One drawn taller and narrower-looking
SIZE = 200            # cap height ~ 142 at this size


def layout(size=SIZE):
    f = font(TITAN)
    k = size / SIZE
    x, items = 0.0, []
    for i, g in enumerate(LETTERS):
        adv = advance(f, g, size)
        if i:
            x += kern(f, LETTERS[i - 1], g, size) + TRACK * size
        dy, rot = BOUNCE[i]
        items.append((g, x + adv / 2, dy * k, rot, adv))
        x += adv
    return f, items, x


def wordmark_parts(size=SIZE, x0=0, y0=0):
    """Return dict with 'letters' path, 'dots' list of (kind, path), the
    width, cap height and bounds. (x0, y0) = left end of the baseline."""
    f, items, w = layout(size)
    d = []
    dots = []
    xh = 0.58 * size * YSCALE        # Titan One x-height, stretched
    for g, cx, dy, rot, adv in items:
        d.append(glyph_path(f, g, size, x0 + cx, y0 + dy, rot, YSCALE, y0)[0])
        if g == 'dotlessi':
            dx = cx + x0 + 2
            dyy = y0 + dy - xh - 0.20 * size
            if not dots:
                dots.append(('spark', spark_path(dx + 2, dyy + 4, 0.19 * size)))
            else:
                r = 0.08 * size
                dots.append(('dot', f'M{f2(dx - r)} {f2(dyy)}a{f2(r)} {f2(r)} 0 1 0 {f2(2 * r)} 0'
                                    f'a{f2(r)} {f2(r)} 0 1 0 {f2(-2 * r)} 0Z'))
    # trademark: small TM hanging at cap height after the A. width stays the
    # letters' width so lockups centre on the name, not on the symbol.
    ts = 0.17 * size
    tm, _ = text_path(font(FIGTREE, wght=800), 'TM', ts, x0 + w + 0.035 * size,
                      y0 - 0.71 * size * YSCALE + 0.72 * ts, tracking=0.02)
    # cheese dripping off the A's right foot, as in the concept
    g, cx, dy, rot, adv = items[-1]
    fx = x0 + cx + adv * 0.30
    fy = y0 + dy - 0.02 * size
    dw = 0.05 * size
    # one connected teardrop (a separate drop read as an exclamation mark)
    L = 0.24 * size
    drip = (f'M{f2(fx - dw)} {f2(fy - 0.06 * size)}C{f2(fx - dw)} {f2(fy + L * 0.45)} {f2(fx - dw * 1.25)} {f2(fy + L * 0.75)} {f2(fx - dw * 1.25)} {f2(fy + L)}'
            f'A{f2(dw * 1.25)} {f2(dw * 1.25)} 0 0 0 {f2(fx + dw * 1.25)} {f2(fy + L)}'
            f'C{f2(fx + dw * 1.25)} {f2(fy + L * 0.75)} {f2(fx + dw)} {f2(fy + L * 0.45)} {f2(fx + dw)} {f2(fy - 0.06 * size)}Z')
    return dict(letters=''.join(d), dots=dots, tm=tm, drip=drip, width=w, cap=0.71 * size * YSCALE,
                top=y0 - 0.71 * size * YSCALE - 0.12 * size, bottom=y0 + 0.06 * size)


def wordmark_g(variant='color', size=SIZE, x0=0, y0=0, tm=True):
    parts = wordmark_parts(size, x0, y0)
    if variant == 'color':
        ink, spark, dot = INK, SPARK, INK
    elif variant == 'color-reversed':
        ink, spark, dot = LIGHT, SPARK, LIGHT
    elif variant == 'mono-dark':
        ink = spark = dot = INK
    else:
        ink = spark = dot = LIGHT
    out = [f'<path d="{parts["letters"]}" fill="{ink}"/>']
    if tm:
        out.append(f'<path d="{parts["tm"]}" fill="{ink}"/>')
    out.append(f'<path d="{parts["drip"]}" fill="{ink if variant.startswith("mono") else CHEESE_LINE}"/>')
    for kind, d in parts['dots']:
        c = spark if kind == 'spark' else dot
        stroke = ''
        out.append(f'<path d="{d}" fill="{c}"{stroke}/>')
    return ''.join(out), parts
