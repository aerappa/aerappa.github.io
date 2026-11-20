# Personal site — Quarto, EN/FR

## Build and preview

Requires Quarto and Python 3. Build both languages, then serve at http://localhost:8000:

```bash
bash build.sh
python3 -m http.server -d _site 8000
```

## Publications

Edit `mypapers.bib`, then run `python3 generate_publications.py` (also run by `build.sh`).
This overwrites `publications.qmd` and `fr/publications.qmd`; don't edit those directly.
Use `@article` for journal articles and `@unpublished` for preprints; `preprint = {...}` adds a HAL/arXiv link.

## Adding a page

Create an English `.qmd` at the root and its French counterpart in `fr/`.
Add each to the render list and navbar in `_quarto-en.yml` / `_quarto-fr.yml`, respectively.

Pushing to `main` builds both languages and deploys to https://aerappa.github.io via GitHub Actions.
