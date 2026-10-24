"""Brand colors and the spark (chispita) shape shared by the vector parts of
the system: the wordmark, the type on the lockups and the one-color art."""
from geometry import f2

INK = '#2A1A0F'           # roast: wordmark, outlines, text
CREAM = '#FFF3DC'         # badge and icon ground
LIGHT = CREAM             # light ink on dark grounds
GOLD = '#F2A230'          # the spark, rays and heart (as in the original badge)
CHEESE = '#F2B53A'        # the cheese drip off the A
PAPER = '#FFFCF6'


def spark_path(cx, cy, r, pinch=0.22, wide=0.8):
    """Four-point spark (the chispita) with concave sides; taller than wide."""
    k = r * pinch
    w = r * wide
    return (f'M{f2(cx)} {f2(cy - r)}'
            f'C{f2(cx + k * .35)} {f2(cy - k)} {f2(cx + k)} {f2(cy - k * .35)} {f2(cx + w)} {f2(cy)}'
            f'C{f2(cx + k)} {f2(cy + k * .35)} {f2(cx + k * .35)} {f2(cy + k)} {f2(cx)} {f2(cy + r)}'
            f'C{f2(cx - k * .35)} {f2(cy + k)} {f2(cx - k)} {f2(cy + k * .35)} {f2(cx - w)} {f2(cy)}'
            f'C{f2(cx - k)} {f2(cy - k * .35)} {f2(cx - k * .35)} {f2(cy - k)} {f2(cx)} {f2(cy - r)}Z')


def heart(cx, cy, s):
    return (f'M{f2(cx)} {f2(cy + s * .9)}C{f2(cx - s * 1.3)} {f2(cy)} {f2(cx - s * 1.1)} {f2(cy - s * .9)} '
            f'{f2(cx - s * .5)} {f2(cy - s * .9)}C{f2(cx - s * .2)} {f2(cy - s * .9)} {f2(cx)} {f2(cy - s * .6)} '
            f'{f2(cx)} {f2(cy - s * .4)}C{f2(cx)} {f2(cy - s * .6)} {f2(cx + s * .2)} {f2(cy - s * .9)} '
            f'{f2(cx + s * .5)} {f2(cy - s * .9)}C{f2(cx + s * 1.1)} {f2(cy - s * .9)} {f2(cx + s * 1.3)} {f2(cy)} '
            f'{f2(cx)} {f2(cy + s * .9)}Z')
