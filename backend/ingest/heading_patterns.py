"""Shared heading-detection patterns used by parse_docx.py and parse_pdf.py.

Matches on a heading's own wording first (consistent across VCAA
documents), falling back to Word style/PDF font size only when wording
doesn't match.
"""
from __future__ import annotations

import re

# (pattern, heading level) — first match wins. Unit=1, Area of Study=2,
# Outcome=3, Key knowledge/Key skills=4.
HEADING_PATTERNS = [
    (re.compile(r"^Unit\s+\d+\b", re.I), 1),
    (re.compile(r"^Area of [Ss]tudy\s+\d+\b", re.I), 2),
    (re.compile(r"^Outcome\s+\d+\b", re.I), 3),
    (re.compile(r"^Key (knowledge|skills)\b", re.I), 4),
]


def pattern_level(text: str) -> int:
    """Heading level implied by text's own wording.

    Inputs: text (str).
    Outputs: int — level 0-4 (0 = not a recognised heading). Rejects
    matches over 100 chars (a heading is a short label, not a sentence).
    """
    for pattern, level in HEADING_PATTERNS:
        if pattern.match(text):
            if len(text) > 100:
                continue
            return level
    return 0


# Matches "Heading 3", "VCAA Heading 3", etc — any "<prefix> Heading N"
# style name, since VCAA uses inconsistent custom style prefixes.
_STYLE_HEADING_RE = re.compile(r"heading\s*([1-9])", re.I)


def style_heading_level(style_name: str) -> int:
    """Heading level implied by a Word paragraph style name.

    Inputs: style_name (str).
    Outputs: int — level 0-4 (capped at 4; 0 = not a heading style).
    """
    if style_name.strip().lower() == "title":
        return 1
    match = _STYLE_HEADING_RE.search(style_name)
    if match:
        return min(int(match.group(1)), 4)
    return 0


# Header first-cell text that reliably identifies a table as NOT a
# command-term glossary (confirmed against all 7 real VCAA files this
# pipeline has run against). Denylist, not an allowlist requiring
# "Term | Definition" — real glossary tables sometimes have no header
# row at all.
_NON_GLOSSARY_HEADERS = {
    "outcomes",
    "version",
    "key idea",
    "english students",
    "stage and activities",
    "poster section",
    "tabulation of data",
    "key science skill",
    "area of study",
}


def is_non_glossary_table(header_cells: list[str]) -> bool:
    """Whether a table's header row marks it as clearly NOT a glossary.

    Inputs: header_cells (list[str]) — a table's first row.
    Outputs: bool — True if the whole table should be skipped.
    """
    if not header_cells or not header_cells[0]:
        return False
    first_cell = header_cells[0].strip().lower()
    return any(first_cell == h or first_cell.startswith(h + " ") for h in _NON_GLOSSARY_HEADERS)


def looks_like_glossary_row(term: str, definition: str) -> bool:
    """Whether a two-column row looks like a real "Term | Definition"
    glossary entry, vs. a mark-allocation/version-history/prerequisite
    table row with the same shape.

    Inputs: term (str), definition (str) — one row's two cells.
    Outputs: bool.
    """
    if term.lower().startswith(("outcome", "unit", "total")):
        return False
    if len(term.split()) > 4:
        return False
    if definition.strip().replace("%", "").isdigit():
        return False
    if len(definition) < 4:
        return False
    # Real definitions explain the term rather than repeating/prefixing it.
    if definition.lower().startswith(term.lower()):
        return False
    # A real definition is a phrase, not a single status word.
    if len(definition.split()) < 4:
        return False
    return True
