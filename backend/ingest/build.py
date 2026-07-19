"""CLI entry point: source_docs/*.docx|*.pdf -> output/study_items.json

This is the "top" of the pipeline — it doesn't know how to parse
documents or simplify text itself, it just wires the other modules
together in order for every file it finds:

    parse_docx/parse_pdf -> extract_items -> simplify -> write JSON

Usage:
    python -m ingest.build
    python -m ingest.build --input source_docs --output output/study_items.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .extract_items import extract_items
from .models import StudyItem
from .parse_docx import parse_docx
from .parse_pdf import parse_pdf
from .simplify import simplify

# Which parser function handles which file extension. Adding support for
# a new source format later (e.g. .doc, .txt) means writing a
# parse_x(path) -> list[RawBlock] function and adding one line here —
# nothing else in this file needs to change.
_PARSERS = {".docx": parse_docx, ".pdf": parse_pdf}


def _subject_for(path: Path, overrides: dict[str, str]) -> str:
    """Work out the display subject name for one source file.

    Study design documents don't reliably state their own subject name
    anywhere machine-readable, so by default we guess from the filename
    (software_development.docx -> "Software Development"). If that
    guess is wrong, or the filename is a code you don't want shown to
    students (e.g. "vce_sd_2024.pdf"), add an explicit entry to
    source_docs/subjects.json instead of renaming the file.
    """
    if path.name in overrides:
        return overrides[path.name]
    return path.stem.replace("_", " ").replace("-", " ").title()


def _load_overrides(input_dir: Path) -> dict[str, str]:
    """Load source_docs/subjects.json if present — an optional
    {"filename.docx": "Display Subject Name"} map for when the
    filename-based guess in _subject_for isn't good enough.
    """
    config_path = input_dir / "subjects.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {}


def build(input_dir: Path, output_path: Path) -> list[StudyItem]:
    """Run the full pipeline over every supported file in `input_dir`
    and write the combined result to `output_path` as one JSON array.
    """
    overrides = _load_overrides(input_dir)
    source_files = sorted(
        p for p in input_dir.iterdir() if p.suffix.lower() in _PARSERS
    )

    if not source_files:
        print(f"No .docx/.pdf files found in {input_dir}", file=sys.stderr)
        return []

    all_items: list[StudyItem] = []
    for path in source_files:
        subject = _subject_for(path, overrides)

        # Step 1: format-specific parsing -> flat, format-agnostic blocks.
        blocks = _PARSERS[path.suffix.lower()](str(path))

        # Step 2: turn those blocks into structured StudyItem rows.
        items = extract_items(blocks, subject)

        if not items:
            # Extracting zero items almost always means the document's
            # headings didn't match the patterns extract_items.py/
            # parse_pdf.py expect (VCAA wording can differ slightly
            # between subjects/years) — flag it loudly rather than
            # silently shipping an empty subject.
            print(f"  WARNING: extracted 0 items from {path.name} — check its heading structure", file=sys.stderr)

        # Step 3: fill in the plain-language rewrite for each item.
        # Done here (not inside extract_items) so extract_items.py stays
        # purely about document structure and doesn't need to know
        # anything about simplification.
        for item in items:
            item.plain_language_text = simplify(item.official_text)

        print(f"  {path.name} -> {subject}: {len(items)} items")
        all_items.extend(items)

    # Stable, predictable ordering makes the output JSON diff nicely in
    # git between pipeline runs — new items append at the end of their
    # category rather than shuffling existing ones around.
    all_items.sort(key=lambda i: (i.subject, i.category, i.id))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps([i.to_json() for i in all_items], indent=2, ensure_ascii=False)
    )
    print(f"Wrote {len(all_items)} items to {output_path}")
    return all_items


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="source_docs", type=Path)
    parser.add_argument("--output", default="output/study_items.json", type=Path)
    args = parser.parse_args()

    build(args.input, args.output)


if __name__ == "__main__":
    main()
