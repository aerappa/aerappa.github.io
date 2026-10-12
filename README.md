# Personal academic site — Quarto, bilingual EN/FR

## Layout

- `index.qmd`, `research.qmd`, `publications.qmd`, `teaching.qmd` — English pages
- `fr/` — French pages (`index`, `recherche`, `publications`, `enseignement`)
- `_quarto.yml` — shared config (theme, footer, fonts)
- `_quarto-en.yml` / `_quarto-fr.yml` — per-language navbar + render list
- `theme.scss` — palette, typography, the damped-wave title divider
- `mypapers.bib` — source of truth for the publication list (see below)
- `generate_publications.py` — regenerates `publications.qmd` / `fr/publications.qmd` from `mypapers.bib`
- `build.sh` — regenerates the publication pages, renders both profiles, merges into `_site/`
- `.github/workflows/publish.yml` — CI: render + deploy to GitHub Pages

## Local preview

```bash
bash build.sh
python3 -m http.server -d _site 8000   # http://localhost:8000
```

(`quarto preview` works too, but only per-profile: `quarto preview --profile fr`.)

## First deployment

1. Push this directory to `main` of the `aerappa.github.io` repo
   (served at https://aerappa.github.io).
2. Repo → Settings → Pages → Source: **GitHub Actions**.

### Optional: custom domain

3. Set `site-url` in `_quarto.yml` and `\homepage` in `cv_en.tex` to the
   domain, and add a step writing it to `_site/CNAME` in
   `.github/workflows/publish.yml`.
4. At your registrar, add DNS records:
   - apex domain: 4 × `A` records → `185.199.108.153`, `.109.153`, `.110.153`, `.111.153`
     (or `ALIAS`/`ANAME` → `aerappa.github.io`)
   - `www` (optional): `CNAME` → `aerappa.github.io`
5. Repo → Settings → Pages → Custom domain: enter the domain, enable
   **Enforce HTTPS** once the certificate is issued.

## Remaining TODOs (search the source for `TODO`)

- Copy `buste.jpg` and the research figures from the old Inria site into `assets/`
  (the current `assets/buste.jpg` is a gray placeholder).
- ERC project name + link on both home pages.
- Current LJLL email address.
- Any Sorbonne/LJLL teaching.
- Consider a redirect note or link on the old Inria page pointing here.

## Updating publications

Edit `mypapers.bib` (add an entry, fill in volume/pages once a preprint is
accepted, or add/update a `preprint = {...}` field with the HAL/arXiv link).
Journal entries (`@article`) go under "Journal articles"; anything else
(`@unpublished`, etc.) goes under "Preprints". Then run:

```bash
python3 generate_publications.py
```

to regenerate `publications.qmd` and `fr/publications.qmd` (both are
overwritten — don't hand-edit them). `build.sh` runs this automatically
before rendering, so a normal build always stays in sync with the `.bib`.

## Adding content later

New page: create `something.qmd`, add it to the `render` list and navbar in
`_quarto-en.yml`; mirror it under `fr/` and `_quarto-fr.yml`. Everything else
is Markdown.
