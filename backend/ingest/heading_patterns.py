"""Shared heading-detection patterns used by both parse_docx.py and
parse_pdf.py.

VCAA's own paragraph/style naming is inconsistent between documents and
even between sections of the same document (we've seen "Heading 3" used
for both an Area of Study's descriptive title AND its Outcome heading in
the same file, and Key knowledge/Key skills sometimes on a "Heading 5"
style that isn't even in the standard Word heading set). The section
*wording* itself, on the other hand, is completely consistent across
every VCAA study design — so both parsers check these patterns FIRST,
before falling back to anything format-specific (Word style name / PDF
font size). That's what makes extraction resilient across many
differently-styled source documents instead of needing per-file tuning.
"""
from __future__ import annotations

import re

# (pattern, heading level) — checked in order, first match wins.
# Level numbering matches RawBlock's docstring: Unit=1, Area of Study=2,
# Outcome=3, Key knowledge/Key skills=4.
HEADING_PATTERNS = [
    (re.compile(r"^Unit\s+\d+\b", re.I), 1),
    (re.compile(r"^Area of [Ss]tudy\s+\d+\b", re.I), 2),
    (re.compile(r"^Outcome\s+\d+\b", re.I), 3),
    (re.compile(r"^Key (knowledge|skills)\b", re.I), 4),
]


def pattern_level(text: str) -> int:
    """Return the heading level implied by `text`'s own wording, or 0 if
    it doesn't match any known VCAA section label.
    """
    for pattern, level in HEADING_PATTERNS:
        if pattern.match(text):
            # A real heading is a short label ("Unit 3: Data analytics"),
            # not a full sentence. Without this guard, ordinary body text
            # that happens to start the same way — e.g. a rationale
            # paragraph beginning "Unit 3 comprises Data analysis and
            # Recursion..." — gets mistaken for a structural heading and
            # corrupts the running unit/area/outcome context.
            if len(text) > 100:
                continue
            return level
    return 0


# Matches "Heading 3", "VCAA Heading 3", or any other "<prefix> Heading
# N" style name — VCAA documents use their own custom style names (not
# just Word's default "Heading N"), and that prefix varies between
# documents, so we look for the trailing "Heading <digit>" rather than
# needing an exact string match per document.
_STYLE_HEADING_RE = re.compile(r"heading\s*([1-9])", re.I)


def style_heading_level(style_name: str) -> int:
    """Return the heading level implied by a Word paragraph style name,
    generically handling any "<prefix> Heading N" naming — or 0 if the
    style name isn't a recognisable heading style at all.

    Capped at 4 because that's as deep as RawBlock's level scheme goes
    (Unit/Area of Study/Outcome/Key knowledge-or-skills) — anything
    beyond that is still worth flagging as *a* heading (so it correctly
    ends whatever Key Knowledge/Key Skill list came before it) even
    though we don't track what kind of heading it specifically is.
    """
    if style_name.strip().lower() == "title":
        return 1
    match = _STYLE_HEADING_RE.search(style_name)
    if match:
        return min(int(match.group(1)), 4)
    return 0


def looks_like_glossary_row(term: str, definition: str) -> bool:
    """Decide whether a two-column table row genuinely looks like a
    "Command Term | Definition" glossary entry, as opposed to some
    other two-column table VCAA documents also use, which have the same
    shape but aren't glossary content — seen in practice:
      - assessment mark-allocation tables ("Outcome 1 | 20 marks")
      - a document version-history table ("Version | Status", "1.1 |
        Current")
      - a prerequisites/overlap table ("General Mathematics | General
        Mathematics or Foundation Mathematics")

    Heuristics: a real command term is a short word/phrase (VCAA's
    glossary terms are things like "Analyse", "Evaluate", "Compare and
    contrast" — never more than a handful of words), and its definition
    is a genuine, substantial explanation — not just a number, a bare
    status word, or a restatement of the term itself.
    """
    if term.lower().startswith(("outcome", "unit", "total")):
        return False
    if len(term.split()) > 4:
        return False
    if definition.strip().replace("%", "").isdigit():
        return False
    if len(definition) < 4:
        return False
    # Real definitions explain the term, they don't just repeat it back
    # ("Foundation Mathematics" -> "Foundation Mathematics") or restate
    # it as a prefix ("General Mathematics" -> "General Mathematics or
    # Foundation Mathematics") — both patterns show up in prerequisite
    # tables, not glossaries.
    if definition.lower().startswith(term.lower()):
        return False
    # A genuine definition is a real explanatory phrase, not a single
    # status word ("Current", "Superseded", "Status") — version-history
    # tables have exactly this one-or-two-word shape.
    if len(definition.split()) < 4:
        return False
    return True
