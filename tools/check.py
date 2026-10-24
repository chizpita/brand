#!/usr/bin/env python3
"""Sanity checks run by `make check` (and before every release tag):
every path in brand.json exists, masters are clean vector SVG, and the
version strings agree."""
import glob
import json
import os
import re
import sys
import xml.dom.minidom

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []

brand = json.load(open(os.path.join(ROOT, 'brand.json')))
version = open(os.path.join(ROOT, 'VERSION')).read().strip()
if brand['version'] != version:
    errors.append(f'brand.json version {brand["version"]} != VERSION {version}')
if f'@v{version}/' not in brand['base_urls']['cdn']:
    errors.append('brand.json base_urls do not point at the current version tag')


def paths(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str) and re.match(r'^(logo|mascot|exports|tokens|social)/[^<>]*\.\w+$', v):
                yield v
            else:
                yield from paths(v)


for p in paths(brand['use_cases']):
    if not os.path.exists(os.path.join(ROOT, p)):
        errors.append(f'brand.json points at missing file: {p}')
for p in brand['tokens'].values():
    if not os.path.exists(os.path.join(ROOT, p)):
        errors.append(f'missing token file: {p}')

for svg in glob.glob(os.path.join(ROOT, '*', '**', '*.svg'), recursive=True):
    if '/exports/' in svg or '/.git/' in svg:
        continue
    text = open(svg).read()
    try:
        xml.dom.minidom.parseString(text)
    except Exception as e:
        errors.append(f'{svg}: not well-formed XML ({e})')
    for bad in ('<image', '<text', 'font-family', '<script', 'href="http'):
        if bad in text:
            errors.append(f'{os.path.relpath(svg, ROOT)}: contains {bad}')

# privacy: no phone numbers or personal emails anywhere in the tree. Names
# to block are kept OUT of this public repo: put one term per line in the
# file named by $CHIZPITA_PRIVATE_TERMS (e.g. in the shared notes folder).
import subprocess as _sp
pat = r'\b[0-9]{3}[ .-][0-9]{3}[ .-][0-9]{4}\b|@gmail\.|@icloud\.|@yahoo\.|@hotmail\.'
terms_file = os.environ.get('CHIZPITA_PRIVATE_TERMS')
if terms_file and os.path.exists(terms_file):
    terms = [t.strip() for t in open(terms_file) if t.strip()]
    pat += '|' + '|'.join(re.escape(t) for t in terms)
hits = _sp.run(['grep', '-rniElI', pat, '--exclude-dir=.git', '--exclude-dir=exports', ROOT],
               capture_output=True, text=True).stdout.strip()
if hits:
    errors.append('personal information found in: ' + hits.replace(ROOT + '/', ''))

if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'ok: brand.json paths resolve, masters are clean vector, version {version}')
