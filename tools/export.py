#!/usr/bin/env python3
"""Regenerate exports/ from the masters. Never edit exports by hand.

    python3 tools/export.py

Needs rsvg-convert (brew install librsvg) and Pillow.
"""
import glob
import io
import os
import shutil
import subprocess

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'exports')
CREAM = '#FFF3DC'

# logical widths; each also gets an @2x file
WIDTHS = {
    'badge': (256, 512, 1024),
    'horizontal': (256, 512, 1024),
    'stacked': (256, 512, 1024),
    'mark': (128, 256, 512),
    'wordmark': (256, 512, 1024),
    'icon': (64, 128, 256, 512),
}
MASCOT_WIDTHS = (128, 256, 512)


def load(path, w):
    """Master at width w: SVGs are rendered, PNGs resampled (never upscaled
    past the master: a request beyond it returns the master size)."""
    if path.endswith('.svg'):
        png = subprocess.run(['rsvg-convert', '-w', str(w), path], capture_output=True, check=True).stdout
        return Image.open(io.BytesIO(png)).convert('RGBA')
    im = Image.open(path).convert('RGBA')
    w = min(w, im.width)
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def save(img, rel, flatten=None):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if flatten:
        bg = Image.new('RGBA', img.size, flatten)
        bg.alpha_composite(img)
        img = bg.convert('RGB')
    img.save(path, optimize=True)


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    n = 0
    for folder, widths in WIDTHS.items():
        for src in sorted(glob.glob(os.path.join(ROOT, 'logo', folder, '*.*'))):
            name = os.path.splitext(os.path.basename(src))[0]
            for w in widths:
                save(load(src, w), f'logo/{folder}/{name}-{w}.png')
                save(load(src, w * 2), f'logo/{folder}/{name}-{w}@2x.png')
                n += 2
    for src in sorted(glob.glob(os.path.join(ROOT, 'mascot', '*.png'))):
        name = os.path.splitext(os.path.basename(src))[0]
        ws = (32, 64, 128, 256) if name.endswith('head') else MASCOT_WIDTHS
        for w in ws:
            save(load(src, w), f'mascot/{name}-{w}.png')
            save(load(src, w * 2), f'mascot/{name}-{w}@2x.png')
            n += 2

    icon = os.path.join(ROOT, 'logo', 'icon')
    color = os.path.join(icon, 'chizpita-icon-color.png')
    dark = os.path.join(icon, 'chizpita-icon-dark.png')
    mask = os.path.join(icon, 'chizpita-icon-maskable.png')
    for s in (16, 32, 48):
        save(load(color, s), f'web/favicon-{s}.png')
    ico = [load(color, s) for s in (16, 32, 48)]
    ico[2].save(os.path.join(OUT, 'web', 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)], append_images=ico[:2])
    save(load(color, 180), 'web/apple-touch-icon.png', flatten=CREAM)
    save(load(color, 192), 'web/icon-192.png')
    save(load(color, 512), 'web/icon-512.png')
    save(load(mask, 512), 'web/icon-maskable-512.png')
    with open(os.path.join(OUT, 'web', 'site.webmanifest'), 'w') as f:
        f.write('''{
  "name": "Chizpita",
  "short_name": "Chizpita",
  "icons": [
    { "src": "icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ],
  "theme_color": "#F2A230",
  "background_color": "#FFF3DC",
  "display": "standalone"
}
''')
    save(load(color, 640), 'social/avatar-640.png', flatten=CREAM)
    save(load(dark, 640), 'social/avatar-dark-640.png', flatten='#2A1A0F')
    save(load(os.path.join(ROOT, 'logo', 'badge', 'chizpita-badge-color.png'), 640), 'social/avatar-badge-640.png', flatten=CREAM)
    og = os.path.join(ROOT, 'social', 'chizpita-og-image.png')
    save(load(og, 1200), 'social/og-image-1200x630.png', flatten=CREAM)
    save(load(og, 2400), 'social/og-image-1200x630@2x.png', flatten=CREAM)
    print(f'exported {n} logo/mascot PNGs + web, PWA and social files to exports/')


if __name__ == '__main__':
    main()
