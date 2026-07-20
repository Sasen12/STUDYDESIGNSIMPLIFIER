"""Cross-item acronym expansion for plain-language text.

VCAA documents define an acronym once — "relational database
management systems (RDBMS)" — and then use the bare acronym ("RDBMS")
in later dot points, sometimes in a completely different Outcome or
Unit. Since each StudyItem is one self-contained dot point, a later
item that only says "RDBMS" has no way to show a student what that
means on its own.

This module fixes that for the *plain-language* text only (never
official_text, which must stay verbatim to the source): scan every
item's official text for a subject to build a {ABBR: expansion} map,
then for any item whose plain-language text uses a known acronym
without defining it inline, insert the expansion in parentheses after
its first occurrence.
"""
from __future__ import annotations

import re

# Finds every "(ABBR)" — a 2-6 letter all-caps parenthetical — without
# trying to also capture its preceding phrase in the same regex. The
# phrase is worked out separately by _find_defining_phrase, word by
# word, which is what avoids grabbing an over-long, wrong span of
# preceding text (the previous character-based approach here would
# grab up to 80 characters of preceding text regardless of word
# boundaries, often truncating mid-word and pulling in unrelated
# clauses — e.g. "y and secondary data and information using the
# American Psychological Association" instead of just "American
# Psychological Association").
_ABBR_RE = re.compile(r"\(([A-Z]{2,6})\)")

_STOPWORDS = {"of", "the", "and", "in", "for", "a", "an", "to", "on", "by", "or", "with"}

# How many words to look back from an abbreviation when searching for
# its defining phrase. Real VCAA acronym expansions are short technical
# terms (2-6 significant words), never a whole clause.
_MAX_PHRASE_WORDS = 6


def _initials(words: list[str]) -> str:
    significant = [w for w in words if w.lower() not in _STOPWORDS]
    return "".join(w[0] for w in significant).upper()


def _find_defining_phrase(preceding_words: list[str], abbr: str) -> str | None:
    """Given the words immediately before an "(ABBR)", find the
    shortest trailing run of them whose initials exactly match `abbr`
    — e.g. for ["using", "the", "American", "Psychological",
    "Association"] and abbr "APA", the 3-word tail "American
    Psychological Association" has initials "APA", an exact match, so
    that's returned (not the whole 5-word list, and not a 2-word tail
    like "Psychological Association" -> "PA", which doesn't match).

    Requiring an *exact* match (not just "abbr is a substring of the
    initials") is what keeps this from grabbing an unrelated, too-long,
    or wrong preceding phrase — if nothing matches exactly, we return
    None rather than guess.
    """
    for word_count in range(1, min(_MAX_PHRASE_WORDS, len(preceding_words)) + 1):
        candidate = preceding_words[-word_count:]
        if _initials(candidate) == abbr:
            return " ".join(candidate)
    return None


def extract_acronym_definitions(texts: list[str]) -> dict[str, str]:
    """Scan `texts` (typically every item's official_text for one
    subject) and return {ABBR: expansion phrase} for every acronym
    whose defining phrase could be confidently identified (see
    _find_defining_phrase). First definition found for a given
    abbreviation wins if it appears more than once.
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
    """Insert "(expansion)" after the first standalone occurrence of any
    acronym in `text` that's in `definitions` but isn't already defined
    inline in this particular text.
    """
    if not definitions:
        return text

    result = text
    for abbr, expansion in definitions.items():
        if f"({abbr})" in result:
            continue  # this text already defines it itself
        match = re.search(rf"\b{re.escape(abbr)}\b", result)
        if match:
            insert_at = match.end()
            result = f"{result[:insert_at]} ({expansion}){result[insert_at:]}"
    return result
