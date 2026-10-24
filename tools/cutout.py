"""Cut a generated illustration off its plain white background.

mode 'global': every near-white, low-saturation pixel becomes transparent
(right for the pita: the gaps between cheese strands are background).
mode 'flood':  only near-white connected to the border (keeps the mascot's
white gloves, eyes and shoe caps).
The cutout is cropped, upscaled 2x (Lanczos) and lightly sharpened.
"""
from collections import deque

import numpy as np
from PIL import Image, ImageFilter


def cutout(src, dst, mode='global', threshold=232):
    a = np.asarray(Image.open(src).convert('RGB')).astype(np.int16)
    mx, mn = a.max(2), a.min(2)
    white = (mn > threshold) & (mx - mn < 22)
    if mode == 'flood':
        h, w = white.shape
        bg = np.zeros_like(white)
        q = deque([(y, x) for x in range(w) for y in (0, h - 1)] +
                  [(y, x) for y in range(h) for x in (0, w - 1)])
        while q:
            y, x = q.popleft()
            if 0 <= y < h and 0 <= x < w and white[y, x] and not bg[y, x]:
                bg[y, x] = True
                q.extend(((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)))
        white = bg
    # soft edge: pixels next to the background fade by how close to white
    edge = np.asarray(Image.fromarray(white.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(3))) > 0
    soft = np.clip((255 - mn - 2) * 255 / 40, 0, 255)
    alpha = np.where(white, 0, np.where(edge, soft, 255)).astype(np.float32)
    al = alpha[..., None] / 255.0
    rgb = np.where(al > 0.02, (a - 255 * (1 - al)) / np.maximum(al, 0.02), a)   # remove white fringe
    out = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alpha]).astype(np.uint8), 'RGBA')
    out = out.crop(out.getchannel('A').getbbox())
    out = out.resize((out.width * 2, out.height * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
    out.save(dst, optimize=True)
    return out
