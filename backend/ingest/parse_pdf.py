"""Flatten a VCAA study design PDF into an ordered list of RawBlocks.

PDFs are much "dumber" than Word documents: there's no concept of a
paragraph style, just positioned characters with a font size. So this
parser has to *infer* structure that parse_docx.py gets for free:

  1. Regex patterns for the section labels VCAA study designs always
     use ("Unit 1", "Area of Study 2", "Outcome 3", "Key knowledge",
     "Key skills") — this is the primary, most trustworthy signal.
  2. Font size relative to the page's most common size, as a fallback
     for headings that don't match one of those patterns (e.g. a
     subject-specific subheading the regexes don't know about).

If extraction quality is poor on a real file, start by checking whether
its headings actually match HEADING_PATTERNS in heading_patterns.py —
VCAA's exact wording can vary a little between subjects and years.
"""
from __future__ import annotations

from collections import Counter

import pdfplumber

from .heading_patterns import is_non_glossary_table, looks_like_glossary_row, pattern_level
from .models import RawBlock


def parse_pdf(path: str) -> list[RawBlock]:
    """Read a PDF file and return its text lines (in reading order) as
    RawBlocks, followed by any table rows turned into glossary blocks.
    """
    blocks: list[RawBlock] = []

    with pdfplumber.open(path) as pdf:
        # We need to know the page's "body text" font size before we can
        # decide what counts as a heading, so this has to be a two-pass
        # process: first collect every line + its font size, tally which
        # size is most common (that's the body size), *then* classify.
        sizes = Counter()
        lines_with_size: list[tuple[str, float]] = []

        for page in pdf.pages:
            for line in page.extract_text_lines() or []:
                text = line["text"].strip()
                if not text:
                    continue
                # A line can mix font sizes (e.g. bold run + normal run);
                # take the largest character size on the line as
                # representative, since headings are usually bigger, not
                # smaller, than the surrounding body text.
                char_sizes = [c["size"] for c in line.get("chars", []) if "size" in c]
                size = round(max(char_sizes), 1) if char_sizes else 0
                sizes[size] += 1
                lines_with_size.append((text, size))

        body_size = sizes.most_common(1)[0][0] if sizes else 0

        for text, size in lines_with_size:
            # Regex pattern match is authoritative when it fires. Only
            # fall back to "bigger than body text" when no known pattern
            # matched — this stops random large pull-quotes or footers
            # from being misread as real structural headings.
            level = pattern_level(text)
            if not level and size > body_size + 1:
                level = 4  # unrecognised but visually a heading — treat as minor
            blocks.append(RawBlock(text=text, level=level))

        # Glossary tables (e.g. command terms) get the same level=5
        # treatment as in parse_docx.py — see that file's comment on the
        # table-handling pass for why tables are only skipped based on a
        # known-bad header, not required to have a "Term | Definition"
        # one to be included.
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                if not table:
                    continue
                header = [(c or "").strip() for c in table[0]]
                if is_non_glossary_table(header):
                    continue
                for row in table:
                    cells = [(c or "").strip() for c in row]
                    if len(cells) < 2 or not cells[0] or not cells[1]:
                        continue
                    # See parse_docx.py's identical handling for why —
                    # a source row can contain more than one term glued
                    # together as newline-separated paragraphs within
                    # one cell.
                    terms = cells[0].split("\n")
                    definitions = cells[1].split("\n")
                    pairs = (
                        zip(terms, definitions)
                        if len(terms) == len(definitions) and len(terms) > 1
                        else [(cells[0], cells[1])]
                    )
                    for term, definition in pairs:
                        term, definition = term.strip(), definition.strip()
                        if term and definition and looks_like_glossary_row(term, definition):
                            blocks.append(RawBlock(text=f"{term}\t{definition}", level=5))

    return blocks
