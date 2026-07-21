"""Extractive + rule-based text simplifier — not paraphrasing (no LLM):

1. EXTRACT the most representative sentence(s) via TF-IDF + cosine
   similarity (scikit-learn).
2. REWRITE: swap jargon words/phrases (jargon_dictionary.json), split
   run-on sentences at genuine clause boundaries (spaCy dependency
   parse — not a generative model, just POS/dependency tagging).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import nltk
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_nlp: spacy.language.Language | None = None


def _get_nlp() -> spacy.language.Language:
    """Inputs: —. Outputs: spacy.language.Language (loaded once, cached)."""
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


_JARGON_PATH = Path(__file__).parent / "jargon_dictionary.json"
_JARGON: dict[str, str] = json.loads(_JARGON_PATH.read_text())

_JARGON_RE = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in _JARGON) + r")\b", re.IGNORECASE
)

# How many sentences to keep from a long passage.
_MAX_SENTENCES = 2


def _ensure_nltk_data() -> None:
    """Downloads NLTK's sentence tokenizer data if not already present.
    Inputs: —. Outputs: None."""
    for resource in ("tokenizers/punkt_tab", "tokenizers/punkt"):
        try:
            nltk.data.find(resource)
            return
        except LookupError:
            continue
    nltk.download("punkt_tab", quiet=True)


def _replace_jargon(sentence: str) -> str:
    """Swap every known jargon word/phrase for its plain equivalent.
    Word-for-word substitution, not grammar-aware — can read awkwardly
    for verbs needing restructuring; that's a known limit, not a bug.

    Inputs: sentence (str).
    Outputs: str.
    """

    def repl(match: re.Match) -> str:
        original = match.group(0)
        replacement = _JARGON[original.lower()]
        if original[:1].isupper():
            replacement = replacement[:1].upper() + replacement[1:]
        return replacement

    return _JARGON_RE.sub(repl, sentence)


def _clause_split_ranges(sentence: str) -> list[tuple[int, int]]:
    """Character ranges to treat as separators: semicolons, and "and"s
    that join two independent clauses (the following verb has its own
    subject in the dependency parse) — not compound predicates or
    conjoined nouns sharing one subject ("X, Y and Z" stays one clause).

    Inputs: sentence (str).
    Outputs: list[tuple[int, int]] — sorted (start, end) ranges.
    """
    ranges = [(m.start(), m.end()) for m in re.finditer(r";\s*", sentence)]

    doc = _get_nlp()(sentence)
    for token in doc:
        if token.dep_ != "cc" or token.text.lower() != "and":
            continue
        head = token.head
        if head.pos_ not in ("VERB", "AUX"):
            continue
        if not any(child.dep_ in ("nsubj", "nsubjpass") for child in head.children):
            continue
        start, end = token.idx, token.idx + len(token.text)
        if start > 0 and sentence[start - 1] == " ":
            start -= 1
        if end < len(sentence) and sentence[end] == " ":
            end += 1
        ranges.append((start, end))

    return sorted(ranges)


def _split_long_clauses(sentence: str) -> str:
    """Break a sentence at each range from _clause_split_ranges and
    rejoin as separate sentences.

    Inputs: sentence (str).
    Outputs: str.
    """
    fragments: list[str] = []
    cursor = 0
    for start, end in _clause_split_ranges(sentence):
        if start > cursor:
            fragments.append(sentence[cursor:start])
        cursor = max(cursor, end)
    fragments.append(sentence[cursor:])

    fragments = [f.strip().rstrip(".,;") for f in fragments if f.strip()]
    if not fragments:
        return sentence
    return ". ".join(f[0].upper() + f[1:] if f else f for f in fragments) + "."


def _simplify_list(text: str) -> str:
    """Simplify semicolon-joined list text (sub-bullets folded into a
    parent item) — skips sentence/clause splitting, which would chop
    each entry into a fragment; only swaps jargon.

    Inputs: text (str).
    Outputs: str.
    """
    segments = [s.strip() for s in text.split(";") if s.strip()]
    return "; ".join(_replace_jargon(s) for s in segments)


def _most_representative_sentences(sentences: list[str], limit: int) -> list[str]:
    """Pick the `limit` sentences closest (TF-IDF + cosine similarity)
    to the passage's overall "centroid" — standard extractive summarisation.

    Inputs: sentences (list[str]); limit (int).
    Outputs: list[str] — up to `limit` sentences, original order.
    """
    if len(sentences) <= limit:
        return sentences

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        matrix = vectorizer.fit_transform(sentences)
    except ValueError:
        # Empty vocabulary (all sentences were stop words/numbers) —
        # fall back to unsimplified rather than crash the build.
        return sentences[:limit]
    centroid = np.asarray(matrix.mean(axis=0))
    scores = cosine_similarity(matrix, centroid).ravel()

    ranked_indices = sorted(range(len(sentences)), key=lambda i: -scores[i])[:limit]
    return [sentences[i] for i in sorted(ranked_indices)]


def simplify(text: str) -> str:
    """Full pipeline: tokenize -> keep most representative sentences ->
    swap jargon -> split clauses -> rejoin.

    Inputs: text (str) — one StudyItem's official_text.
    Outputs: str — plain-language rewrite ("" if text is empty).
    """
    text = text.strip()
    if not text:
        return ""

    if ";" in text:
        return _simplify_list(text)

    _ensure_nltk_data()
    sentences = nltk.sent_tokenize(text)
    selected = _most_representative_sentences(sentences, _MAX_SENTENCES)

    rewritten = [_split_long_clauses(_replace_jargon(s)) for s in selected]
    return " ".join(rewritten)
