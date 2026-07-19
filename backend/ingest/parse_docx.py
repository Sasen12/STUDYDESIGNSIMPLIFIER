"""Flatten a .docx VCAA study design into an ordered list of RawBlocks.

Word documents carry real structure (paragraph "styles" like Heading 1,
Heading 2, tables, bold runs), so this parser is the more reliable of
the two format parsers — prefer .docx source files over PDF where you
have a choice.
"""
from __future__ import annotations

import docx

from .models import RawBlock

# Maps a Word paragraph style name to the heading depth we use elsewhere
# in the pipeline (see RawBlock's docstring for what each level means).
# If your source document uses different style names (some VCAA exports
# use "heading 1" lowercase, or custom style names like "VCAA H1"), add
# them here rather than touching the parsing logic below.
_HEADING_STYLE_LEVEL = {
    "Title": 1,
    "Heading 1": 1,
    "Heading 2": 2,
    "Heading 3": 3,
    "Heading 4": 4,
}


def _heading_level(paragraph) -> int:
    """Work out how "deep" a paragraph is, i.e. whether it's a heading
    and if so which level.

    Word's built-in heading styles are the first and most reliable
    signal, so we check those first. But VCAA documents don't always
    use heading styles consistently — sometimes a section label like
    "Key knowledge" is just a plain paragraph with **bold** text instead
    of a proper Heading 4. So as a fallback, if every run in a short
    paragraph is bold, we treat it as a level-4 heading too.
    """
    style_level = _HEADING_STYLE_LEVEL.get(paragraph.style.name, 0)
    if style_level:
        return style_level

    # Fallback heuristic: a short, fully-bold paragraph almost certainly
    # a section label, not a real sentence of body text (which would be
    # longer and wouldn't be entirely bold).
    runs = [r for r in paragraph.runs if r.text.strip()]
    if runs and all(r.bold for r in runs) and len(paragraph.text) < 60:
        return 4

    return 0


def parse_docx(path: str) -> list[RawBlock]:
    """Read a .docx file and return its paragraphs (in reading order) as
    RawBlocks, followed by any table rows turned into glossary blocks.
    """
    document = docx.Document(path)
    blocks: list[RawBlock] = []

    # Pass 1: every paragraph in the document body, in order, skipping
    # blank ones (Word documents are full of empty spacer paragraphs).
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue
        blocks.append(RawBlock(text=text, level=_heading_level(paragraph)))

    # Pass 2: tables. VCAA study designs put their "Glossary of command
    # terms" in a two-column table (Term | Definition) rather than as
    # regular paragraphs, so python-docx's paragraph iteration above
    # never sees them — we have to walk document.tables separately.
    # We tag each row as level=5 so extract_items.py can recognise it as
    # a ready-made (term, definition) pair rather than trying to run it
    # through the heading/body-text state machine.
    for table in document.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells]
            if len(cells) >= 2 and cells[0] and cells[1]:
                blocks.append(RawBlock(text=f"{cells[0]}\t{cells[1]}", level=5))

    return blocks
