"""Cross-item acronym expansion for plain-language text.

VCAA documents define an acronym once and use it bare later, sometimes
in a different Outcome/Unit. Since each StudyItem is self-contained,
this expands bare acronyms in plain_language_text only (never
official_text) using definitions found anywhere in the subject.
"""
from __future__ import annotations

import re

# Matches "(ABBR)" — a 2-6 letter all-caps parenthetical. The
# defining phrase is worked out separately (word by word) rather than
# captured in this regex, to avoid grabbing an over-long/wrong span of
# preceding text.
_ABBR_RE = re.compile(r"\(([A-Z]{2,6})\)")

_STOPWORDS = {"of", "the", "and", "in", "for", "a", "an", "to", "on", "by", "or", "with"}

_MAX_PHRASE_WORDS = 6


def _initials(words: list[str]) -> str:
    """Inputs: words (list[str]). Outputs: str — initials of non-stopwords."""
    significant = [w for w in words if w.lower() not in _STOPWORDS]
    return "".join(w[0] for w in significant).upper()


def _find_defining_phrase(preceding_words: list[str], abbr: str) -> str | None:
    """Shortest trailing run of preceding_words whose initials exactly
    match abbr. Exact match only — no guessing on partial matches.

    Inputs: preceding_words (list[str]); abbr (str).
    Outputs: str | None.
    """
    for word_count in range(1, min(_MAX_PHRASE_WORDS, len(preceding_words)) + 1):
        candidate = preceding_words[-word_count:]
        if _initials(candidate) == abbr:
            return " ".join(candidate)
    return None


def extract_acronym_definitions(texts: list[str]) -> dict[str, str]:
    """Scan texts for "Full Term (ABBR)" definitions.

    Inputs: texts (list[str]) — typically every item's official_text
    for one subject.
    Outputs: dict[str, str] — {ABBR: expansion phrase}.
    """
    definitions: dict[str, str] = {}
    for text in texts:
        for match in _ABBR_RE.finditer(text):
            abbr = match.group(1)
            if abbr in definitions:
                continue
            preceding_words = text[: match.start()].split()
            phrase = _find_defining_phrase(preceding_words, abbr)
            if phrase:
                definitions[abbr] = phrase
    return definitions


def expand_bare_acronyms(text: str, definitions: dict[str, str]) -> str:
    """Insert "(expansion)" after the first bare use of a known
    acronym, unless the text already defines it inline.

    Inputs: text (str); definitions (dict[str, str]).
    Outputs: str.
    """
    if not definitions:
        return text

    result = text
    for abbr, expansion in definitions.items():
        if f"({abbr})" in result:
            continue
        match = re.search(rf"\b{re.escape(abbr)}\b", result)
        if match:
            insert_at = match.end()
            result = f"{result[:insert_at]} ({expansion}){result[insert_at:]}"
    return result
