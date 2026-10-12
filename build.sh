#!/usr/bin/env bash
# Render both language profiles and merge into _site/
set -euo pipefail

python3 generate_publications.py

quarto render --profile en
quarto render --profile fr
rm -rf _site/fr
cp -r _site-fr/fr _site/fr
# Merge FR-rendered libs (harmless if identical; needed if theme hashes diverge)
cp -rn _site-fr/site_libs/. _site/site_libs/ 2>/dev/null || true
echo "Done. Full site in _site/"
