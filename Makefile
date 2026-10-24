# Chizpita brand assets. `make` regenerates everything from tools/.
# Needs: python3 with fonttools + pillow (pip install -r tools/requirements.txt)
#        and rsvg-convert (brew install librsvg).
PY ?= python3

all: masters tokens exports docs check

masters:
	$(PY) tools/build.py
tokens:
	$(PY) tools/build_tokens.py
exports: masters
	$(PY) tools/export.py
docs: masters
	$(PY) tools/build_docs.py
check:
	$(PY) tools/check.py

.PHONY: all masters tokens exports docs check
