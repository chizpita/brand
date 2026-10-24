# Illustration sources

`art/source/` holds the canonical illustrations exactly as generated. Everything else (cutouts, the one-color trace, every lockup and export) is derived from them by `make`.

They reconstruct the brand's original concept art: the "Love at first bite" badge (a pita pocket torn open with a cheese pull) and the flyer mascot (a round toasted pita with a crown). The reconstruction fixes the originals' problems: low resolution, screenshot overlays, the misspelled name on the flyer, and inconsistent rendering between pieces. No text is generated inside the images; all lettering is vector, set by `tools/`.

- Generator: Google Gemini image model ("Nano Banana 2 Lite"), 1024×1024, 2026-10-23, via Composio.
- Each pose was generated from the same character description, below, with only the pose sentence changed.

## Pita (`pita-cheese-pull.jpg`)

> Bakery logo illustration, eye-level side view: a crispy golden-orange pita pocket being pulled apart into two halves left and right, like a calzone torn open. Both halves lie horizontally with rounded puffy domes on top and a flat, crimped, rolled edge along the bottom, torn open edges facing each other in the middle and tilted slightly up. Deep toasted crust with dark orange-brown griddle char spots. Between them, a thick stretchy pull of rich golden-yellow melted cheese with many glossy strings, and a long drip falling down from the middle. Wide horizontal composition, about twice as wide as tall. Hand-painted vector-style illustration, thin dark brown outline, vivid warm colors, glossy cheese highlights. Isolated on plain pure white background, no shadow, no text, no plate.

## Mascot (`mascot-<pose>.jpg`)

Character description used for every pose:

> Cute cartoon mascot for a cheese pita bakery: a round, puffy, toasted pita bread character, pale golden dough with big orange-brown griddle toast patches and speckled texture. Big friendly brown eyes with eyelashes and white highlights, rosy pink cheeks, open happy smile with tongue. A small spiky golden-yellow crown tilted on its head with a four-point gold sparkle on the crown. Thin brown arms and legs, white four-finger cartoon gloves, yellow high-top sneakers with white toe caps and laces. 3D-style cartoon render, soft lighting, crisp clean edges. Full body, centered, isolated on plain pure white background, no shadow, no text.

Pose sentences:
- **thumbs-up:** giving a thumbs-up with the right hand, walking pose
- **front:** standing straight facing the viewer, both arms relaxed at its sides, feet apart, friendly
- **waving:** waving hello with its right hand raised high, open palm, left arm relaxed, standing
- **celebrating:** eyes squeezed shut with joy, huge open happy smile; jumping for joy, both arms raised high in celebration, feet off the ground, a few small golden four-point sparkles around it
- **sleepy:** eyes peacefully closed with eyelashes, small relaxed smile, a little drowsy, crown slipping sideways; sitting down, hands resting on its lap, dozing off

To add a pose: reuse the character description, change only the pose sentence, generate on a plain white background, save as `mascot-<pose>.jpg`, add the pose to `POSES` in `tools/build.py`, and compare it with the existing five before releasing.
