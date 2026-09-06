#!/usr/bin/env python3
"""Regenerate publications.qmd and fr/publications.qmd from mypapers.bib.

mypapers.bib is the single source of truth for the publication list. Edit
the .bib (add entries, update volume/pages once a preprint is accepted,
add a `preprint` field for the HAL/arXiv link) and re-run this script
(or `bash build.sh`, which calls it automatically) to refresh both pages.

Stdlib only, no bibtexparser dependency, so it runs unmodified in CI.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BIB_PATH = ROOT / "mypapers.bib"

ACCENTS = [
    (re.compile(r"\\'\{?e\}?"), "é"),
    (re.compile(r"\\'\{?i\}?"), "í"),
    (re.compile(r"\\'\{?a\}?"), "á"),
    (re.compile(r"\\'\{?o\}?"), "ó"),
    (re.compile(r"\\'\{?u\}?"), "ú"),
    (re.compile(r'\\c\s*\{?c\}?'), "ç"),
    (re.compile(r'\\c\s*\{?C\}?'), "Ç"),
    (re.compile(r'\\"\{?o\}?'), "ö"),
    (re.compile(r'\\"\{?u\}?'), "ü"),
]


# ---------------------------------------------------------------------------
# Minimal BibTeX parser (handles the subset of syntax used in mypapers.bib:
# brace-delimited values with possible nesting, mixed field-name casing,
# multi-line values, entries with or without a trailing comma).
# ---------------------------------------------------------------------------

def parse_bib(text):
    entries = []
    for m in re.finditer(r'@(\w+)\s*\{', text):
        entrytype = m.group(1).lower()
        start = m.end()
        depth = 1
        i = start
        while i < len(text) and depth > 0:
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
            i += 1
        body = text[start:i - 1]
        citekey, rest = _split_citekey(body)
        fields = _parse_fields(rest)
        entries.append({"type": entrytype, "key": citekey, **fields})
    return entries


def _split_citekey(body):
    depth = 0
    for idx, ch in enumerate(body):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        elif ch == ',' and depth == 0:
            return body[:idx].strip(), body[idx + 1:]
    return body.strip(), ''


def _parse_fields(s):
    fields = {}
    i, n = 0, len(s)
    while i < n:
        while i < n and (s[i].isspace() or s[i] == ','):
            i += 1
        if i >= n:
            break
        j = i
        while j < n and (s[j].isalnum() or s[j] in '_-'):
            j += 1
        name = s[i:j].strip().lower()
        if not name:
            break
        i = j
        while i < n and s[i].isspace():
            i += 1
        if i < n and s[i] == '=':
            i += 1
        while i < n and s[i].isspace():
            i += 1
        if i < n and s[i] == '{':
            depth = 1
            k = i + 1
            while k < n and depth > 0:
                if s[k] == '{':
                    depth += 1
                elif s[k] == '}':
                    depth -= 1
                k += 1
            value = s[i + 1:k - 1]
            i = k
        else:
            k = i
            depth = 0
            while k < n and not (s[k] == ',' and depth == 0):
                if s[k] == '{':
                    depth += 1
                elif s[k] == '}':
                    depth -= 1
                k += 1
            value = s[i:k]
            i = k
        fields[name] = value.strip()
    return fields


# ---------------------------------------------------------------------------
# Text cleanup helpers
# ---------------------------------------------------------------------------

def _fully_wrapped(s):
    if not (s.startswith('{') and s.endswith('}')):
        return False
    depth = 0
    for idx, ch in enumerate(s):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and idx != len(s) - 1:
                return False
    return True


def clean_text(s):
    s = s.strip()
    while _fully_wrapped(s):
        s = s[1:-1].strip()
    for pat, repl in ACCENTS:
        s = pat.sub(repl, s)
    s = s.replace('{', '').replace('}', '')
    return re.sub(r'\s+', ' ', s).strip()


def clean_pages(pages):
    pages = clean_text(pages)
    m = re.match(r'Paper No\.?\s*(\S+?),?\s*\d*$', pages)
    if m:
        return m.group(1)
    pages = pages.replace('--', '\u2013')
    pages = re.sub(r'(?<=\w)-(?=\w)', '\u2013', pages)
    return pages


def format_authors(raw):
    raw = clean_text(raw)
    formatted = []
    for author in raw.split(' and '):
        parts = [p.strip() for p in author.split(',')]
        if len(parts) == 3:
            last, suffix, first = parts
        elif len(parts) == 2:
            last, first = parts
            suffix = ''
        else:
            tokens = author.split()
            last, first, suffix = tokens[-1], ' '.join(tokens[:-1]), ''
        initials = []
        for tok in first.split():
            initials.append(tok if tok.endswith('.') else tok[0].upper() + '.')
        name = ' '.join(initials) + ' ' + last
        if suffix:
            name += ' ' + suffix
        formatted.append(name)
    return ', '.join(formatted)


def journal_name(entry):
    return clean_text(entry.get('fjournal') or entry.get('journal', ''))


def journal_citation(entry):
    journal = journal_name(entry)
    year = clean_text(entry.get('year', ''))
    volume = clean_text(entry.get('volume', ''))
    number = clean_text(entry.get('number', ''))
    pages = clean_pages(entry.get('pages', '')) if entry.get('pages') else ''

    if volume:
        tail = volume
        if number:
            tail += f", no. {number}"
        tail += f" ({year})"
        if pages:
            tail += f", {pages}"
        return f"*{journal}* {tail}."
    if pages:
        return f"*{journal}*, {pages} ({year})."
    return f"*{journal}* ({year})."


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

LABELS = {
    "en": {
        "journal_heading": "## Journal articles",
        "preprint_heading": "## Preprints",
        "journal_link": "journal",
        "preprint_link": "preprint",
        "hal_link": "HAL",
    },
    "fr": {
        "journal_heading": "## Articles dans des revues internationales",
        "preprint_heading": "## Prépublications et articles soumis",
        "journal_link": "revue",
        "preprint_link": "prépublication",
        "hal_link": "HAL",
    },
}


def render_journal_entry(entry, labels):
    authors = format_authors(entry.get('author', ''))
    title = clean_text(entry.get('title', ''))
    citation = journal_citation(entry)
    line = f"- **{authors}.** {title}, {citation}"
    links = []
    url = entry.get('url') or entry.get('doi')
    if url and not url.startswith('http'):
        url = f"https://doi.org/{url}"
    if url:
        links.append(f"[{labels['journal_link']}]({clean_text(url)})")
    preprint = entry.get('preprint')
    if preprint:
        links.append(f"[{labels['preprint_link']}]({clean_text(preprint)})")
    if links:
        line += " " + " \u00b7 ".join(links)
    return line


def render_preprint_entry(entry, labels):
    authors = format_authors(entry.get('author', ''))
    title = clean_text(entry.get('title', ''))
    year = clean_text(entry.get('year', ''))
    url = clean_text(entry.get('url', ''))
    return f"- **{authors}.** {title}, {year}. [{labels['hal_link']}]({url})"


def render_page(entries, lang):
    labels = LABELS[lang]
    journals = [e for e in entries if e['type'] == 'article']
    preprints = [e for e in entries if e['type'] == 'unpublished']
    journals.sort(key=lambda e: int(clean_text(e.get('year', '0'))), reverse=True)
    preprints.sort(key=lambda e: int(clean_text(e.get('year', '0'))), reverse=True)

    lines = ['---', 'title: "Publications"', '---', '']
    lines.append(labels['journal_heading'])
    lines.append('')
    lines.append('::: {.pub-list}')
    lines.append('')
    for i, e in enumerate(journals):
        lines.append(render_journal_entry(e, labels))
        if i != len(journals) - 1:
            lines.append('')
    lines.append(':::')
    lines.append('')
    lines.append(labels['preprint_heading'])
    lines.append('')
    lines.append('::: {.pub-list}')
    lines.append('')
    for i, e in enumerate(preprints):
        lines.append(render_preprint_entry(e, labels))
        if i != len(preprints) - 1:
            lines.append('')
    lines.append(':::')
    lines.append('')
    return '\n'.join(lines)


def main():
    text = BIB_PATH.read_text(encoding='utf-8')
    entries = parse_bib(text)

    en_path = ROOT / "publications.qmd"
    fr_path = ROOT / "fr" / "publications.qmd"

    en_path.write_text(render_page(entries, "en"), encoding='utf-8')
    fr_path.write_text(render_page(entries, "fr"), encoding='utf-8')
    print(f"Wrote {en_path.relative_to(ROOT)} and {fr_path.relative_to(ROOT)} "
          f"from {len(entries)} bib entries.")


if __name__ == "__main__":
    main()
