#!/usr/bin/env python3
"""Build every master in logo/, mascot/ and social/ from art/source/.

    python3 tools/build.py

Pipeline:
1. art/source/*.jpg (the canonical illustrations, see art/README.md) are cut
   off their white background into art/*.png.
2. The pita illustration is traced (potrace) into a one-color vector for
   stamps, embroidery and one-color print.
3. Vector masters (SVG): the wordmark and every one-color lockup.
4. Full-color masters (PNG, 2048px): the illustration composited with the
   vector type (exact spelling, crisp edges, the TM).
"""
import io
import math
import os
import re
import subprocess

import numpy as np
from PIL import Image, ImageFilter

import geometry as G
from cutout import cutout
from palette import INK, CREAM, LIGHT, GOLD, spark_path, heart
from wordmark import wordmark_g, TITAN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, 'art')
VERSION = open(os.path.join(ROOT, 'VERSION')).read().strip()
POSES = ('front', 'waving', 'thumbs-up', 'celebrating', 'sleepy')
TAGLINES = ('LOVE AT FIRST BITE', 'HANDMADE WITH LOVE')     # badge: top, bottom


def p(*a):
    return os.path.join(ROOT, *a)


PITA = p('logo', 'mark', 'chizpita-mark-color.png')   # the illustration, cut out


def write(rel, text):
    os.makedirs(os.path.dirname(p(rel)), exist_ok=True)
    with open(p(rel), 'w') as f:
        f.write(text)
    print('wrote', rel)


def save_png(img, rel):
    os.makedirs(os.path.dirname(p(rel)), exist_ok=True)
    img.save(p(rel), optimize=True)
    print('wrote', rel)


def render(svg, w, h):
    png = subprocess.run(['rsvg-convert', '-w', str(w), '-h', str(h)], input=svg.encode(),
                         capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(png)).convert('RGBA')


def svg_doc(body, vb, title, size=None):
    x, y, w, h = vb
    wh = f' width="{size[0]}" height="{size[1]}"' if size else f' width="{w}" height="{h}"'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}"{wh}>'
            f'<title>{title}</title><desc>Chizpita brand master v{VERSION}. github.com/chizpita/brand</desc>'
            f'{body}</svg>\n')


def trim_vb(body, w, h, margin=6):
    im = render(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>', w, h)
    x0, y0, x1, y1 = im.getchannel('A').getbbox()
    return (x0 - margin, y0 - margin, x1 - x0 + 2 * margin, y1 - y0 + 2 * margin)


# ------------------------------------------------------------ 1. cutouts

def build_cutouts():
    os.makedirs(p('logo', 'mark'), exist_ok=True)
    os.makedirs(p('mascot'), exist_ok=True)
    cutout(os.path.join(ART, 'source', 'pita-cheese-pull.jpg'), PITA, 'global')
    for pose in POSES:
        cutout(os.path.join(ART, 'source', f'mascot-{pose}.jpg'),
               p('mascot', f'chizpita-mascot-{pose}.png'), 'flood', 249)
    print('cut out logo/mark/chizpita-mark-color.png and mascot/*.png')


# --------------------------------------------------------- 2. mono trace

def trace_pita():
    """One-color woodcut of the pita: its dark lines and char plus a solid
    silhouette outline, traced to vector. Returns (path d, width, height)."""
    im = Image.open(PITA).convert('RGBA')
    a = np.asarray(im).astype(np.float32)
    alpha = a[..., 3] / 255
    lum = 0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]
    ink = (lum < 150) & (alpha > 0.5)
    sil = Image.fromarray((alpha > 0.5).astype(np.uint8) * 255)
    outline = (np.asarray(sil.filter(ImageFilter.MaxFilter(9))) > 0) & ~(np.asarray(sil.filter(ImageFilter.MinFilter(9))) > 0)
    mask = ink | outline
    pbm = io.BytesIO()
    Image.fromarray((~mask * 255).astype(np.uint8)).convert('1').save(pbm, 'PPM')
    out = subprocess.run(['potrace', '-s', '-t', '30', '-a', '1.1', '-O', '0.4', '-o', '-', '-'],
                         input=pbm.getvalue(), capture_output=True, check=True).stdout.decode()
    g = re.search(r'<g transform="([^"]+)"[^>]*>(.*?)</g>', out, re.S)
    paths = ''.join(re.findall(r'd="([^"]+)"', g.group(2)))
    return g.group(1), paths, im.width, im.height


def mono_pita_g(color, x, y, width, trace):
    tr, d, w, h = trace
    s = width / w
    return (f'<g transform="translate({G.f2(x)} {G.f2(y)}) scale({G.f2(s)})">'
            f'<g transform="{tr}"><path d="{d}" fill="{color}"/></g></g>'), h * s


# ------------------------------------------------------ 3. layout pieces

def badge_vector(variant, include_ground=True):
    """Everything in the badge except the illustration, 1024 grid."""
    mono = variant.startswith('mono')
    ink = LIGHT if variant == 'mono-light' else INK
    accent = ink if mono else GOLD
    titan = G.font(TITAN)
    cx = cy = 512
    parts = []
    if mono:
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="494" fill="none" stroke="{ink}" stroke-width="12"/>')
    elif include_ground:
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="500" fill="{CREAM}"/>')
    top, bottom = TAGLINES
    parts.append(f'<path d="{G.arc_text(titan, top, 58, cx, cy, 418, 0, 0.05, True)}" fill="{ink}"/>')
    parts.append(f'<path d="{G.arc_text(titan, bottom, 50, cx, cy, 452, 180, 0.05, False)}" fill="{ink}"/>')
    rays = []
    for ang in (-64, -78, -92, 64, 78, 92):
        t = math.radians(ang)
        for r0, r1 in ((392, 438),):
            rays.append(f'M{G.f2(cx + r0 * math.sin(t))} {G.f2(360 - r0 * math.cos(t) * 0.6)}'
                        f'L{G.f2(cx + r1 * math.sin(t))} {G.f2(360 - r1 * math.cos(t) * 0.6)}')
    parts.append(f'<path d="{"".join(rays)}" fill="none" stroke="{accent}" stroke-width="15" stroke-linecap="round"/>')
    w, pr = wordmark_g(variant, 188, 0, 0)
    w, _ = wordmark_g(variant, 188, cx - pr['width'] / 2 - 12, 720)
    parts.append(w)
    parts.append(f'<path d="M356 800H462M562 800H668" stroke="{accent}" stroke-width="10" stroke-linecap="round"/>')
    parts.append(f'<path d="{heart(cx, 800, 21)}" fill="{accent}"/>')
    return ''.join(parts)


BADGE_PITA = (512, 168, 690)      # centre x, top y, width of the illustration on the 1024 grid


def compose(base_svg, vb, scale, overlays):
    """Render base vector art at scale, then paste raster overlays
    [(image, x, y, width)] given in vector-grid units."""
    x0, y0, w, h = vb
    W, H = round(w * scale), round(h * scale)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="{x0} {y0} {w} {h}">{base_svg}</svg>'
    img = render(svg, W, H)
    for art, x, y, width in overlays:
        aw = round(width * scale)
        ah = round(art.height * aw / art.width)
        img.alpha_composite(art.resize((aw, ah), Image.LANCZOS), (round((x - x0) * scale), round((y - y0) * scale)))
    return img


# ----------------------------------------------------------- 4. masters

def build_masters():
    pita = Image.open(PITA).convert('RGBA')
    trace = trace_pita()
    pita_h = lambda width: pita.height * width / pita.width

    # wordmark: vector only
    for v in ('color', 'color-reversed', 'mono-dark', 'mono-light'):
        body, _ = wordmark_g(v, 200, 20, 260)
        vb = trim_vb(body, 1200, 380)
        write(f'logo/wordmark/chizpita-wordmark-{v}.svg', svg_doc(body, vb, f'Chizpita wordmark ({v})'))

    # badge
    cx, top, width = BADGE_PITA
    img = compose(badge_vector('color'), (0, 0, 1024, 1024), 2, [(pita, cx - width / 2, top, width)])
    save_png(img, 'logo/badge/chizpita-badge-color.png')
    for v in ('mono-dark', 'mono-light'):
        ink = LIGHT if v == 'mono-light' else INK
        g, _ = mono_pita_g(ink, cx - width / 2, top, width, trace)
        # one color: the trace goes under a knock-out of the wordmark so letters stay legible
        ko, pr = wordmark_g('mono-dark', 188, 0, 0)
        ko, _ = wordmark_g('mono-dark', 188, cx - pr['width'] / 2 - 12, 720)
        mask = (f'<defs><mask id="ko-{v}"><rect width="1024" height="1024" fill="white"/>'
                f'<g stroke="black" stroke-width="22" stroke-linejoin="round" fill="black">{ko}</g></mask></defs>')
        body = mask + f'<g mask="url(#ko-{v})">{g}</g>' + badge_vector(v)
        write(f'logo/badge/chizpita-badge-{v}.svg', svg_doc(body, (0, 0, 1024, 1024), f'Chizpita badge ({v})'))

    # horizontal: pita left, wordmark right
    pw = 360
    ph = pita_h(pw)
    for v in ('color', 'color-reversed', 'mono-dark', 'mono-light'):
        w, _ = wordmark_g(v, 150, pw + 40, 40 + ph * 0.42 + 50)
        if v.startswith('color'):
            vb = (0, 0, pw + 40 + 1000, max(ph, 260) + 40)
            vb = (0, 0, round(trim_vb(w, 1500, 400)[0] + trim_vb(w, 1500, 400)[2]) + 10, round(ph) + 40)
            img = compose(w, vb, 2, [(pita, 0, 20, pw)])
            save_png(img, f'logo/horizontal/chizpita-horizontal-{v}.png')
        else:
            ink = LIGHT if v == 'mono-light' else INK
            g, _ = mono_pita_g(ink, 0, 20, pw, trace)
            body = g + w
            write(f'logo/horizontal/chizpita-horizontal-{v}.svg', svg_doc(body, trim_vb(body, 1500, 400), f'Chizpita horizontal ({v})'))

    # stacked: pita above, wordmark below (drip runs into the letters)
    pw = 600
    for v in ('color', 'mono-dark', 'mono-light'):
        w, pr = wordmark_g(v, 150, 0, 0)
        w, _ = wordmark_g(v, 150, 450 - pr['width'] / 2, 520)
        if v == 'color':
            img = compose(w, (0, 0, 900, 600), 2, [(pita, 150, 0, pw)])
            img = img.crop(img.getchannel('A').getbbox())
            save_png(img, 'logo/stacked/chizpita-stacked-color.png')
        else:
            ink = LIGHT if v == 'mono-light' else INK
            g, _ = mono_pita_g(ink, 150, 0, pw, trace)
            body = w + g
            write(f'logo/stacked/chizpita-stacked-{v}.svg', svg_doc(body, trim_vb(body, 900, 600), f'Chizpita stacked ({v})'))

    # mark: the illustration itself (cut out in step 1), and its one-color trace
    for v in ('mono-dark', 'mono-light'):
        ink = LIGHT if v == 'mono-light' else INK
        g, h = mono_pita_g(ink, 0, 0, 1000, trace)
        write(f'logo/mark/chizpita-mark-{v}.svg', svg_doc(g, (-10, -10, 1020, round(h) + 20), f'Chizpita mark ({v})'))

    # mascot poses (transparent), head crop, and the icons built from it
    front = Image.open(p('mascot', 'chizpita-mascot-front.png')).convert('RGBA')
    fw, fh = front.size
    # head = the round body plus the crown, without arms and legs
    yy, xx = np.mgrid[0:fh, 0:fw]
    body = (xx - 0.575 * fw) ** 2 + (yy - 0.45 * fh) ** 2 <= (0.335 * fw) ** 2
    crown_box = (xx > 0.60 * fw) & (xx < 0.86 * fw) & (yy < 0.20 * fh)
    keep = Image.fromarray(((body | crown_box) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
    alpha = np.minimum(np.asarray(front.getchannel('A')), np.asarray(keep))
    head = front.copy()
    head.putalpha(Image.fromarray(alpha.astype(np.uint8)))
    head = head.crop(head.getchannel('A').getbbox())
    side = max(head.size)
    sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    sq.alpha_composite(head, ((side - head.width) // 2, side - head.height))
    head = sq
    save_png(head, 'mascot/chizpita-mascot-head.png')
    for name, ground, k in (('color', CREAM, 0.84), ('dark', INK, 0.84), ('maskable', CREAM, 0.66)):
        S = 1024
        icon = Image.new('RGBA', (S, S), ground)
        hs = round(S * k)
        h2 = head.resize((hs, hs), Image.LANCZOS)
        icon.alpha_composite(h2, ((S - hs) // 2, (S - hs) // 2))
        save_png(icon, f'logo/icon/chizpita-icon-{name}.png')

    # link-preview image: badge left, waving mascot right, on cream
    og = Image.new('RGBA', (2400, 1260), CREAM)
    badge = Image.open(p('logo/badge/chizpita-badge-color.png')).resize((1120, 1120), Image.LANCZOS)
    og.alpha_composite(badge, (180, 70))
    wave = Image.open(p('mascot', 'chizpita-mascot-waving.png')).convert('RGBA')
    wave.thumbnail((900, 1000), Image.LANCZOS)
    og.alpha_composite(wave, (1400, (1260 - wave.height) // 2))
    save_png(og.convert('RGB'), 'social/chizpita-og-image.png')


def main():
    build_cutouts()
    build_masters()


if __name__ == '__main__':
    main()
