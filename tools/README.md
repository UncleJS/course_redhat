# Tooling

## Markdown audit / fix

Requires **Node.js 18+** (or Bun):

```bash
node tools/md_audit.js .
node tools/md_fix.js . --write    # only with --write
```

Checks intra-file `#` anchors against GitHub heading slugs and TOC completeness.

## Slide decks

```bash
pip install -r requirements.txt    # odfpy
python3 slides/generate_slides.py
```

Writes flat `slides/NNN-<slug>.odp` for each chapter in `README_ORDER`. H2 and H3 sections become content slides.
