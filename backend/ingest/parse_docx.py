"""Flatten a .docx VCAA study design into an ordered list of RawBlocks.

Word documents carry real structure (paragraph "styles" like Heading 1,
Heading 2, tables, bold runs), so this parser is the more reliable of
the two format parsers — prefer .docx source files over PDF where you
have a choice.
"""
from __future__ import annotations

import re

import docx

from .heading_patterns import looks_like_glossary_row, pattern_level, style_heading_level
from .models import RawBlock


def _heading_level(paragraph) -> int:
    """Work out how "deep" a paragraph is, i.e. whether it's a heading
    and if so which level.

    Checked in priority order:
      1. Does the paragraph's own text match a known VCAA section label
         ("Unit 1", "Outcome 2", "Key knowledge", ...)? This is checked
         first and is authoritative when it matches, because it's true
         regardless of which paragraph style the document's author used
         for it.
      2. Does the paragraph use *any* "Heading N"-shaped style (Word's
         defaults, or a custom one like "VCAA Heading 5")? We treat ANY
         such heading as at least a generic boundary — even one whose
         specific meaning we don't track — because otherwise an
         unrecognised heading (e.g. "School-based assessment") gets
         mistaken for ordinary body text and silently absorbed into
         whatever Key Knowledge/Key Skill list came just before it.
      3. Is every run in a short paragraph bold? (Some section labels
         are just manually bolded text with no heading style at all.)
    """
    level = pattern_level(paragraph.text.strip())
    if level:
        return level

    style_level = style_heading_level(paragraph.style.name)
    if style_level:
        return style_level

    runs = [r for r in paragraph.runs if r.text.strip()]
    if runs and all(r.bold for r in runs) and len(paragraph.text) < 60:
        return 4

    return 0


# Matches "VCAA bullet level 2", "List Paragraph level 3", etc — VCAA
# gives nested dot points (a sub-point indented under another dot
# point) their own style distinct from the top-level bullet style, with
# "level N" (N >= 2) in the name.
_SUB_ITEM_STYLE_RE = re.compile(r"level\s*[2-9]", re.I)


def _is_sub_item(paragraph) -> bool:
    """Detect a nested sub-bullet (see RawBlock.is_sub_item's docstring
    for why this matters) via its paragraph style name.

    Style-name detection, not python-docx's numbering/ilvl API,
    because VCAA's sub-bullets in practice aren't part of the same
    Word numbered-list definition as their parent (each level has its
    own named style, "VCAA bullet" vs "VCAA bullet level 2") — the
    style name is the reliable signal here, not list numbering
    metadata.
    """
    return bool(_SUB_ITEM_STYLE_RE.search(paragraph.style.name))


def parse_docx(path: str) -> list[RawBlock]:
    """Read a .docx file and return its paragraphs (in reading order) as
    RawBlocks, followed by any table rows turned into glossary blocks.
    """
    document = docx.Document(path)
    blocks: list[RawBlock] = []

    # Pass 1: every paragraph in the document body, in order, skipping
    # blank ones (Word documents are full of empty spacer paragraphs).
    for paragraph in document.paragraphs:
        # A manual line break (Shift+Enter) inside a paragraph comes
        # through as a literal "\n" in paragraph.text — collapse any
        # run of whitespace (including those) down to a single space so
        # sentences don't end up with a stray newline mid-word-wrap.
        text = re.sub(r"\s+", " ", paragraph.text).strip()
        if not text:
            continue
        blocks.append(
            RawBlock(text=text, level=_heading_level(paragraph), is_sub_item=_is_sub_item(paragraph))
        )

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
            if len(cells) >= 2 and cells[0] and cells[1] and looks_like_glossary_row(cells[0], cells[1]):
                blocks.append(RawBlock(text=f"{cells[0]}\t{cells[1]}", level=5))

    return blocks
