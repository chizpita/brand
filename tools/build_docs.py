#!/usr/bin/env python3
"""Render the reference sheets in docs/ that BRAND.md shows.

    python3 tools/build_docs.py
"""
import io
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
FIG = os.path.join(ROOT, 'tools', 'fonts', 'Figtree-VF.ttf')
VERSION = open(os.path.join(ROOT, 'VERSION')).read().strip()

PAPER, CREAM, ROAST, GOLD, KRAFT, ACCENT = '#FFFCF6', '#FFF3DC', '#2A1A0F', '#F2A230', '#C8A27A', '#D9482B'


def load(rel, w):
    path = os.path.join(ROOT, rel)
    if path.endswith('.svg'):
        png = subprocess.run(['rsvg-convert', '-w', str(w), path], capture_output=True, check=True).stdout
        return Image.open(io.BytesIO(png)).convert('RGBA')
    im = Image.open(path).convert('RGBA')
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def font(size, weight=600):
    f = ImageFont.truetype(FIG, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def label(img, xy, text, size=22, color=ROAST, weight=600):
    ImageDraw.Draw(img).text(xy, text, fill=color, font=font(size, weight))


def canvas(w, h, bg=PAPER):
    return Image.new('RGBA', (w, h), bg)


def paste(c, im, x, y):
    c.alpha_composite(im, (int(x), int(y)))


def overview():
    c = canvas(1800, 1060)
    label(c, (40, 28), f'Chizpita logo system v{VERSION}', 40, weight=800)
    paste(c, load('logo/badge/chizpita-badge-color.png', 560), 30, 100)
    label(c, (40, 672), 'Primary: badge   logo/badge/', 20)
    paste(c, load('logo/horizontal/chizpita-horizontal-color.png', 900), 640, 110)
    label(c, (640, 330), 'Horizontal   logo/horizontal/', 20)
    paste(c, load('logo/stacked/chizpita-stacked-color.png', 400), 640, 400)
    label(c, (640, 860), 'Stacked   logo/stacked/', 20)
    paste(c, load('logo/mark/chizpita-mark-color.png', 360), 1100, 420)
    label(c, (1100, 660), 'Mark   logo/mark/', 20)
    paste(c, load('logo/wordmark/chizpita-wordmark-color.svg', 520), 1100, 730)
    label(c, (1100, 880), 'Wordmark   logo/wordmark/', 20)
    paste(c, load('logo/icon/chizpita-icon-color.png', 170), 1590, 110)
    paste(c, load('logo/icon/chizpita-icon-dark.png', 170), 1590, 300)
    label(c, (1590, 480), 'App icon / avatar', 20)
    kr = canvas(300, 300, KRAFT)
    paste(kr, load('logo/badge/chizpita-badge-mono-dark.svg', 270), 15, 15)
    paste(c, kr, 30, 730)
    label(c, (350, 1000), 'One color (stamp)', 20)
    c.save(os.path.join(DOCS, 'overview.png'))


def sizes():
    c = canvas(1800, 620)
    label(c, (40, 24), 'Small-size test (actual pixels, then 4x nearest-neighbour)', 28, weight=800)
    x = 40
    for rel, bg in (('logo/icon/chizpita-icon-color.png', '#FFFFFF'), ('logo/icon/chizpita-icon-dark.png', '#202124')):
        for w in (16, 32, 48):
            tile = Image.new('RGBA', (w + 8, w + 8), bg)
            tile.alpha_composite(load(rel, w), (4, 4))
            paste(c, tile, x, 90)
            big = tile.resize((tile.width * 4, tile.height * 4), Image.NEAREST)
            paste(c, big, x, 150)
            label(c, (x, 150 + big.height + 8), f'{w}px', 18)
            x += big.width + 24
    for i, s in enumerate((200, 56, 40)):
        im = load('exports/social/avatar-640.png', s)
        m = Image.new('L', (s, s), 0)
        ImageDraw.Draw(m).ellipse((0, 0, s - 1, s - 1), fill=255)
        im.putalpha(m)
        paste(c, im, 40 + [0, 230, 310][i], 380 if i == 0 else 450)
    label(c, (40, 590), 'WhatsApp avatar circle crop: 200 / 56 / 40px', 18)
    for j, w in enumerate((160, 240, 360)):
        paste(c, load('logo/horizontal/chizpita-horizontal-color.png', w), 1100, 360 + j * 70)
    label(c, (1100, 590), 'Horizontal at 160 / 240 / 360px wide (min 160px)', 18)
    c.save(os.path.join(DOCS, 'sizes.png'))


def backgrounds():
    c = canvas(1800, 720)
    label(c, (40, 24), 'Backgrounds: which version goes where', 28, weight=800)
    tiles = [
        (PAPER, 'logo/horizontal/chizpita-horizontal-color.png', 'Paper / white: color'),
        (CREAM, 'logo/horizontal/chizpita-horizontal-color.png', 'Cream: color'),
        (ROAST, 'logo/horizontal/chizpita-horizontal-color-reversed.png', 'Roast / dark: color-reversed'),
        (KRAFT, 'logo/horizontal/chizpita-horizontal-mono-dark.svg', 'Kraft box: mono-dark (stamp)'),
        (GOLD, 'logo/horizontal/chizpita-horizontal-mono-dark.svg', 'Gold: mono-dark'),
        (ROAST, 'logo/horizontal/chizpita-horizontal-mono-light.svg', 'Dark one-color print: mono-light'),
    ]
    for i, (bg, rel, text) in enumerate(tiles):
        x, y = 40 + (i % 3) * 580, 90 + (i // 3) * 310
        t = Image.new('RGBA', (560, 290), bg)
        t.alpha_composite(load(rel, 470), (45, 60))
        paste(c, t, x, y)
        label(c, (x + 16, y + 252), text, 20, color=CREAM if bg == ROAST else ROAST)
    c.save(os.path.join(DOCS, 'backgrounds.png'))


def clearspace():
    c = canvas(1500, 560)
    label(c, (40, 24), 'Clear space = X on every side. X = 1/4 of the logo height (badge: 1/10 of its width)', 26, weight=800)
    im = load('logo/horizontal/chizpita-horizontal-color.png', 800)
    x0, y0 = 300, 160
    X = im.height // 4
    d = ImageDraw.Draw(c)
    d.rectangle((x0 - X, y0 - X, x0 + im.width + X, y0 + im.height + X), outline=ACCENT, width=3)
    d.rectangle((x0, y0, x0 + im.width, y0 + im.height), outline='#C2AE99', width=1)
    d.line((x0 - X, y0 + im.height // 2, x0, y0 + im.height // 2), fill=ACCENT, width=3)
    label(c, (x0 - X + 4, y0 + im.height // 2 + 8), 'X', 26, ACCENT, 800)
    paste(c, im, x0, y0)
    c.save(os.path.join(DOCS, 'clearspace.png'))


def mascot():
    c = canvas(1800, 620)
    label(c, (40, 24), f'Chizpita, the mascot  v{VERSION}', 34, weight=800)
    poses = ('front', 'waving', 'thumbs-up', 'celebrating', 'sleepy')
    use = ('canonical', 'hello, welcome', 'got it, confirmed', 'order placed', 'orders closed')
    for i, (pz, u) in enumerate(zip(poses, use)):
        im = load(f'mascot/chizpita-mascot-{pz}.png', 270)
        if im.height > 380:
            im = im.resize((round(im.width * 380 / im.height), 380), Image.LANCZOS)
        paste(c, im, 30 + i * 300, 100 + (380 - im.height) // 2)
        label(c, (40 + i * 300, 500), pz, 22, weight=800)
        label(c, (40 + i * 300, 530), u, 18, color='#6E5A49')
    paste(c, load('mascot/chizpita-mascot-head.png', 140), 1560, 170)
    paste(c, load('mascot/chizpita-mascot-head.png', 48), 1720, 340)
    label(c, (1560, 500), 'head', 22, weight=800)
    label(c, (1560, 530), 'avatars, icons', 18, color='#6E5A49')
    c.save(os.path.join(DOCS, 'mascot.png'))


def donts():
    c = canvas(1800, 700)
    label(c, (40, 24), "Don't", 34, ACCENT, 800)
    hz = load('logo/horizontal/chizpita-horizontal-color.png', 440)
    cells = [(hz.resize((520, int(hz.height * 1.6))), 'Stretch or squash'),
             (hz.rotate(12, expand=True, resample=Image.BICUBIC), 'Rotate or tilt'),
             (hz.convert('LA').convert('RGBA'), 'Recolor or desaturate')]
    dark = Image.new('RGBA', (460, 180), ROAST)
    dark.alpha_composite(load('logo/horizontal/chizpita-horizontal-color.png', 420), (20, 30))
    cells.append((dark, 'Dark wordmark on dark grounds'))
    sh = Image.new('RGBA', (470, 200), (0, 0, 0, 0))
    shadow = Image.merge('RGBA', [Image.new('L', hz.size, 0)] * 3 + [hz.getchannel('A').point(lambda a: int(a * .45))])
    sh.alpha_composite(shadow, (14, 18))
    sh.alpha_composite(hz, (0, 0))
    cells.append((sh, 'Add shadows, glows or bevels'))
    sp = Image.new('RGBA', (460, 140), PAPER)
    ImageDraw.Draw(sp).text((10, 20), 'Chizpita', fill=ROAST, font=font(90, 400))
    cells.append((sp, 'Retype the wordmark in another font'))
    for i, (im, text) in enumerate(cells):
        x, y = 40 + (i % 3) * 580, 100 + (i // 3) * 300
        paste(c, im, x, y)
        ImageDraw.Draw(c).line((x, y + 250, x + 30, y + 250), fill=ACCENT, width=4)
        label(c, (x + 40, y + 236), text, 20)
    c.save(os.path.join(DOCS, 'donts.png'))


def main():
    os.makedirs(DOCS, exist_ok=True)
    overview()
    sizes()
    backgrounds()
    clearspace()
    mascot()
    donts()
    print('docs/ sheets rendered')


if __name__ == '__main__':
    main()
