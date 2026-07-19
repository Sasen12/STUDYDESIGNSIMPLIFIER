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

import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
        # match.group(0) preserves whatever capitalisation was in the
        # source text; we look it up lowercase since the dictionary
        # keys are all lowercase.
        return _JARGON[match.group(0).lower()]

    return _JARGON_RE.sub(repl, sentence)


def _split_long_clauses(sentence: str) -> str:
    """Break a sentence at semicolons, and at " and " joins between two
    clauses that each look like they could stand alone, turning one
    dense multi-clause sentence into several short ones.

    This is a blunt, regex-level heuristic — it doesn't parse grammar,
    so it can occasionally split somewhere a linguist wouldn't (e.g.
    inside a simple list like "reading and writing"). In practice this
    trade-off favours short, scannable sentences over rare mis-splits,
    which fits what a student skimming a study design actually wants.
    """
    # " and (?=[a-z])" only matches when the word after "and" starts
    # lowercase, as a cheap way to avoid splitting right before a proper
    # noun or the start of an unrelated new sentence.
    parts = re.split(r";\s*| and (?=[a-z])", sentence)
    parts = [p.strip().rstrip(".") for p in parts if p.strip()]
    # Re-capitalise the first letter of each fragment (splitting can
    # leave a fragment starting mid-sentence, lowercase) and re-join
    # with ". " so each fragment reads as its own sentence.
    return ". ".join(p[0].upper() + p[1:] if p else p for p in parts) + "."


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
    centroid = matrix.mean(axis=0)  # the "average sentence" for this passage
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

    _ensure_nltk_data()
    sentences = nltk.sent_tokenize(text)  # e.g. handles "e.g." not being a sentence end
    selected = _most_representative_sentences(sentences, _MAX_SENTENCES)

    rewritten = [_split_long_clauses(_replace_jargon(s)) for s in selected]
    return " ".join(rewritten)
