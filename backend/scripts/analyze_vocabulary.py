"""Authoring aid: find candidate words for jargon_dictionary.json from
the actual generated dataset, instead of guessing by hand.

    python scripts/analyze_vocabulary.py [output/study_items.json]
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from ingest.simplify import _JARGON  # noqa: E402

# Long words that show up constantly but aren't jargon to simplify —
# either everyday vocabulary despite length, or a subject's own
# technical term. Extend as you review candidates.
_ALWAYS_SKIP = {
    "information", "including", "different", "understanding", "developing",
    "appropriate", "individual", "structures", "characteristics", "relevant",
    "including", "students", "learning", "resources", "including", "provide",
    "identify", "including", "example", "examples", "specific", "context",
    "application", "applications", "communication", "organisation",
    "development", "environment", "management", "performance", "technology",
    "technologies", "relationship", "relationships", "processes", "process",
}

_WORD_RE = re.compile(r"[a-z]+(?:-[a-z]+)*")


def find_candidates(items: list[dict], min_length: int, min_count: int, top_n: int) -> None:
    """Inputs: items (list[dict]) — study_items.json data; min_length
    (int); min_count (int) — min items a word must appear in; top_n (int).
    Outputs: None — prints results to stdout.
    """
    word_examples: dict[str, list[str]] = defaultdict(list)
    word_counts: Counter[str] = Counter()

    for item in items:
        text = item["officialText"]
        seen_in_this_item = set()
        for word in _WORD_RE.findall(text.lower()):
            if len(word) < min_length or word in _ALWAYS_SKIP or word in _JARGON:
                continue
            if word not in seen_in_this_item:
                word_counts[word] += 1
                seen_in_this_item.add(word)
                if len(word_examples[word]) < 1:
                    word_examples[word].append(text)

    candidates = [(w, c) for w, c in word_counts.items() if c >= min_count]
    # Word length is a better proxy for "genuinely obscure" than raw
    # frequency — the most frequent long words in this corpus are
    # ordinary curriculum terms ("mathematical", "algorithms"), not jargon.
    candidates.sort(key=lambda wc: (-len(wc[0]), -wc[1]))

    print(f"{len(candidates)} candidate words appear in >= {min_count} items "
          f"(length >= {min_length}, not already in jargon_dictionary.json)\n")
    for word, count in candidates[:top_n]:
        example = word_examples[word][0]
        print(f"{count:>4}x  {word}")
        print(f"        e.g. \"{example[:140]}\"")


if __name__ == "__main__":
    data_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "output" / "study_items.json"
    items = json.loads(data_path.read_text())
    find_candidates(items, min_length=9, min_count=8, top_n=60)
