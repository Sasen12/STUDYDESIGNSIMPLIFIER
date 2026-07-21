"""Flatten a VCAA study design PDF into an ordered list of RawBlocks.

PDFs have no paragraph styles, so headings are inferred from: (1)
regex match on known VCAA section wording (primary signal), (2) font
size relative to the page's most common size (fallback).
"""
from __future__ import annotations

from collections import Counter

import pdfplumber

from .heading_patterns import is_non_glossary_table, looks_like_glossary_row, pattern_level
from .models import RawBlock


def parse_pdf(path: str) -> list[RawBlock]:
    """Read a PDF file into RawBlocks: every text line in reading
    order, then glossary table rows appended at the end.

    Inputs: path (str) — filesystem path to a .pdf file.
    Outputs: list[RawBlock].
    """
    blocks: list[RawBlock] = []

    with pdfplumber.open(path) as pdf:
        # Two passes: first tally font sizes to find the page's body
        # text size, then classify each line against it.
        sizes = Counter()
        lines_with_size: list[tuple[str, float]] = []

        for page in pdf.pages:
            for line in page.extract_text_lines() or []:
                text = line["text"].strip()
                if not text:
                    continue
                char_sizes = [c["size"] for c in line.get("chars", []) if "size" in c]
                size = round(max(char_sizes), 1) if char_sizes else 0
                sizes[size] += 1
                lines_with_size.append((text, size))

        body_size = sizes.most_common(1)[0][0] if sizes else 0

        for text, size in lines_with_size:
            # Regex match is authoritative; font size is only a
            # fallback, to avoid misreading large pull-quotes/footers.
            level = pattern_level(text)
            if not level and size > body_size + 1:
                level = 4
            blocks.append(RawBlock(text=text, level=level))

        # Glossary tables: same handling as parse_docx.py — skip
        # tables with a clearly-non-glossary header, else check every
        # row (including the first) via looks_like_glossary_row.
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
                    # A row can contain multiple terms glued together
                    # as newline-separated paragraphs in one cell.
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
