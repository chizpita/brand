# Changelog

## v3.0.0 (2026-10-23)

Canonical artwork rebuilt from the original concept badge and flyer mascot, corrected and at production quality. Breaking: most masters changed format and name.

- **Illustrations:** the toasted pita with its cheese pull and five mascot poses were regenerated at full quality from the original concepts (no screenshot artifacts or overlays), with a consistent character. They are kept in `art/source/`.
- **Badge:** follows the original layout (cream disc, Love at first bite / Handmade with love, rays, heart divider) with exact vector type: CHIZPITA spelled correctly, a small ™, the gold spark on the i and the cheese drip off the A.
- **Full-color masters are PNG** (`logo/badge|horizontal|stacked|mark|icon/*.png`, `mascot/*.png`); the wordmark and all one-color versions stay SVG. The one-color pita is a vector trace of the new illustration.
- **App icon and avatars** now use the mascot's face, which reads down to 16 px. The vector favicon (`favicon.svg`) was removed.
- **Removed:** the Spanish badges and Spanish taglines (taglines are English only), the vector mark drawings and the vector mascot.
- **Taglines:** Love at first bite, Handmade with love, Handmade in San Diego.
- **Flavors:** the plain flavor is named El Clásico (brand.json).
- **Palette:** gold spark and crust orange taken from the artwork; tokens updated.

## v2.0.0 (2026-10-23, superseded; tag removed)

- Mascot named Chizpita, like the brand. Mascot files renamed to `mascot/chizpita-mascot-<pose>.*`.
- ™ added to every lockup that shows the wordmark.

## v1.0.0 (2026-10-23, superseded; tag removed)

- First release: vector logo system (badge, horizontal, stacked, wordmark, mark, icons), mascot, exports, tokens, brand.json and BRAND.md.
