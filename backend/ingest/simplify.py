"""Extractive + rule-based text simplifier.

Important: this is NOT paraphrasing. scikit-learn doesn't generate new
text — it's a classical ML library (classification, clustering, TF-IDF
vectors), so "simplifying" here means something narrower and fully
deterministic:

  1. EXTRACT the most representative sentence(s) out of a long official
     passage (scikit-learn's TF-IDF + cosine similarity), so we're not
     dumping the whole dense paragraph on the student.
  2. REWRITE those sentences with two fixed rules: swap known jargon
     words for plain-language equivalents (jargon_dictionary.json), and
     break run-on, multi-clause sentences into shorter ones.

If you want true paraphrasing (a human-like reworded explanation, not
just a trimmed-and-swapped version of the original), that needs an LLM
instead — this module deliberately doesn't attempt that.
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

# Loaded once, lazily, at first use rather than at import time — spaCy
# model loading takes a noticeable moment (~1s), not worth paying on
# every `import ingest.simplify` (e.g. in scripts that only need the
# jargon dictionary) if simplify() itself never gets called.
_nlp: spacy.language.Language | None = None


def _get_nlp() -> spacy.language.Language:
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp

# jargon_dictionary.json is a flat {"jargon word": "plain replacement"}
# map. Loaded once at import time (not per-call) since it's small and
# never changes during a single run of the pipeline.
_JARGON_PATH = Path(__file__).parent / "jargon_dictionary.json"
_JARGON: dict[str, str] = json.loads(_JARGON_PATH.read_text())

# One big alternation regex ("\b(word1|word2|...)\b") built from every
# jargon key, so we can find *all* jargon words in a sentence with a
# single re.sub pass instead of looping over the dictionary and
# re-scanning the string once per entry. `\b` word boundaries stop it
# from matching jargon as a substring of an unrelated word.
_JARGON_RE = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in _JARGON) + r")\b", re.IGNORECASE
)

# How many sentences we keep from a passage when it's long enough to
# need trimming. 2 is a starting point, not a law — raise it if
# simplified text ends up too choppy/losing meaning for your content.
_MAX_SENTENCES = 2


def _ensure_nltk_data() -> None:
    """NLTK's sentence tokenizer needs a small pretrained model
    ("punkt") downloaded to disk before first use — it's not bundled
    with the pip package. This checks whether it's already there and
    only hits the network to fetch it the first time the pipeline runs
    on a given machine.
    """
    for resource in ("tokenizers/punkt_tab", "tokenizers/punkt"):
        try:
            nltk.data.find(resource)
            return
        except LookupError:
            continue
    nltk.download("punkt_tab", quiet=True)


def _replace_jargon(sentence: str) -> str:
    """Swap every jargon word found in `sentence` for its plain-language
    equivalent, case-insensitively, in one pass over the string.

    Note this is a literal word-for-word substitution, not a
    grammar-aware rewrite: a jargon word that's a noun in the dictionary
    ("rationale" -> "reasoning") swaps cleanly, but a verb whose plain
    version needs a different sentence shape ("evaluate X" really means
    "judge how good X is", not just "judge-how-good-and-effective X")
    can come out reading awkwardly. That's an inherent limit of
    dictionary substitution, not a bug — true grammatical rewriting is
    an LLM's job, not this pipeline's.
    """

    def repl(match: re.Match) -> str:
        original = match.group(0)
        # Dictionary keys/values are all lowercase, so look up
        # case-insensitively — but if the matched text was capitalised
        # (most commonly a sentence-initial phrase like "On completion
        # of..."), capitalise the replacement's first letter too,
        # rather than silently lowercasing the start of a sentence.
        replacement = _JARGON[original.lower()]
        if original[:1].isupper():
            replacement = replacement[:1].upper() + replacement[1:]
        return replacement

    return _JARGON_RE.sub(repl, sentence)


def _clause_split_ranges(sentence: str) -> list[tuple[int, int]]:
    """Find character ranges in `sentence` that should be treated as
    separators (removed, splitting the text on either side into
    separate fragments) — semicolons, and coordinating "and"s that
    join two genuinely independent clauses.

    An earlier version of this split at *every* " and ", using only
    "is the next word lowercase?" as a guard. That over-split VCE
    outcome statements badly: "the student should be able to discuss
    and analyse the specific vocabulary..." became "Discuss." +
    "Analyse the specific vocabulary...", because VCE outcomes are
    almost always ONE instruction with several compound predicates or
    conjoined nouns sharing an implicit subject ("the student should
    be able to [X], [Y] and [Z]"), not several independent sentences.

    The dependency-parse check here distinguishes the two cases
    correctly: for each "and" attached to a verb/aux, only treat it as
    a real clause boundary if that verb has its *own* subject (nsubj) —
    i.e. "...X and the teacher should Y" (two independent clauses,
    split) vs "...X, Y and Z" (one clause, compound predicate, don't
    split) or "belief formation and justification" (two nouns, no verb
    at all, don't split).
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
        # Consume one adjacent space on each side so the separator
        # disappears cleanly rather than leaving a stray leading/
        # trailing space on the fragments next to it.
        if start > 0 and sentence[start - 1] == " ":
            start -= 1
        if end < len(sentence) and sentence[end] == " ":
            end += 1
        ranges.append((start, end))

    return sorted(ranges)


def _split_long_clauses(sentence: str) -> str:
    """Break a sentence into separate fragments at each genuine clause
    boundary found by `_clause_split_ranges`, then rejoin them as
    separate sentences — turning one dense, multi-clause instruction
    into several short, scannable ones without breaking apart compound
    predicates or conjoined nouns that only look similar on the surface.
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
    # Re-capitalise the first letter of each fragment (splitting can
    # leave a fragment starting mid-sentence, lowercase) and re-join
    # with ". " so each fragment reads as its own sentence.
    return ". ".join(f[0].upper() + f[1:] if f else f for f in fragments) + "."


def _simplify_list(text: str) -> str:
    """Simplify text that's really a semicolon-joined list of dot
    points (produced when extract_items.py folds nested sub-bullets
    back into their parent item — e.g. "structural characteristics of
    RDBMS, such as:; tables; queries; relationships...").

    This is NOT prose, so running it through sentence tokenization,
    TF-IDF extraction, and clause-splitting (as `simplify()` does for
    ordinary official text) actively hurts it — those tools assume
    grammatical sentences and end up chopping each list entry into a
    meaningless sentence fragment. Instead we keep the list structure
    intact and only apply the one rule that still makes sense for a
    list: swapping jargon words for plain-language equivalents.
    """
    segments = [s.strip() for s in text.split(";") if s.strip()]
    return "; ".join(_replace_jargon(s) for s in segments)


def _most_representative_sentences(sentences: list[str], limit: int) -> list[str]:
    """Pick the `limit` sentences that best represent the whole passage,
    using TF-IDF + cosine similarity to a "centroid" (average) vector —
    a standard, lightweight extractive-summarisation technique.

    Intuition: TfidfVectorizer turns every sentence into a vector of
    "how important is each word to this sentence, relative to the
    others". The centroid is the average of all those vectors — i.e.
    what the passage is "about" overall. Sentences whose own vector
    points closest (cosine similarity) to that average are the ones
    that best summarise the passage as a whole, as opposed to sentences
    that veer off into one narrow detail.
    """
    if len(sentences) <= limit:
        # Nothing to trim — short passages are returned as-is.
        return sentences

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(sentences)  # one TF-IDF row per sentence
    # matrix.mean(axis=0) returns a np.matrix (a legacy numpy type), which
    # newer scikit-learn's cosine_similarity refuses to accept — convert
    # it to a plain ndarray first.
    centroid = np.asarray(matrix.mean(axis=0))  # the "average sentence" for this passage
    scores = cosine_similarity(matrix, centroid).ravel()  # similarity of each sentence to that average

    # Rank sentence indices by score (highest similarity first), take
    # the top `limit`, then re-sort back into original reading order —
    # otherwise a highly-ranked *later* sentence could end up printed
    # before an earlier one, which would read strangely.
    ranked_indices = sorted(range(len(sentences)), key=lambda i: -scores[i])[:limit]
    return [sentences[i] for i in sorted(ranked_indices)]


def simplify(text: str) -> str:
    """Full simplification pipeline for one passage of official text:
    tokenize into sentences -> keep only the most representative ones
    -> swap jargon -> split long clauses -> rejoin into one string.

    This is the only function other modules (build.py) call directly;
    everything above is a private helper.
    """
    text = text.strip()
    if not text:
        return ""

    if ";" in text:
        # A semicolon almost never appears in a single VCAA sentence —
        # in practice it's the join character extract_items.py uses
        # when it folds nested sub-bullets into their parent, so this
        # is really a list, not prose. Handle it separately (see
        # _simplify_list's docstring for why).
        return _simplify_list(text)

    _ensure_nltk_data()
    sentences = nltk.sent_tokenize(text)  # e.g. handles "e.g." not being a sentence end
    selected = _most_representative_sentences(sentences, _MAX_SENTENCES)

    rewritten = [_split_long_clauses(_replace_jargon(s)) for s in selected]
    return " ".join(rewritten)
