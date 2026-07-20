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
from collections import Counter
from pathlib import Path

from .extract_items import assign_ids, extract_items, split_bundled_subjects
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


def _dump_blocks(path: Path, blocks: list, dump_dir: Path) -> None:
    """Write one file's parsed RawBlocks out as their own JSON file —
    e.g. source_docs/2023PhysicsSD.docx -> output/blocks/2023PhysicsSD.json.

    This is a debugging aid, not part of the StudyItem pipeline itself:
    it lets you see exactly what parse_docx.py/parse_pdf.py extracted
    (every paragraph, its detected heading level, whether it was
    treated as a nested sub-bullet) *before* extract_items.py's
    Unit/Area of Study/Outcome state machine runs on top of it — the
    place to look first when a document's item count looks wrong.
    """
    dump_dir.mkdir(parents=True, exist_ok=True)
    out_path = dump_dir / f"{path.stem}.json"
    out_path.write_text(
        json.dumps(
            [{"text": b.text, "level": b.level, "isSubItem": b.is_sub_item} for b in blocks],
            indent=2,
            ensure_ascii=False,
        )
    )


def build(input_dir: Path, output_path: Path, dump_blocks_dir: Path | None = None) -> list[StudyItem]:
    """Run the full pipeline over every supported file in `input_dir`
    and write the combined result to `output_path` as one JSON array.

    If `dump_blocks_dir` is given, also writes each file's raw parsed
    blocks out as its own JSON file there (see _dump_blocks) — useful
    for debugging a document whose extracted item count looks wrong.
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

        if dump_blocks_dir is not None:
            _dump_blocks(path, blocks, dump_blocks_dir)

        # Step 2: turn those blocks into structured StudyItem rows.
        items = extract_items(blocks, subject)

        if not items:
            # Extracting zero items almost always means the document's
            # headings didn't match the patterns extract_items.py/
            # parse_pdf.py expect (VCAA wording can differ slightly
            # between subjects/years) — flag it loudly rather than
            # silently shipping an empty subject.
            print(f"  WARNING: extracted 0 items from {path.name} — check its heading structure", file=sys.stderr)

        # Step 3: some files bundle several VCE studies into one
        # document (e.g. the combined Mathematics study design covers
        # General/Specialist/Foundation Mathematics and Mathematical
        # Methods as four separate courses) — split those out into
        # their real subjects before anything downstream treats them as
        # one. No-op for ordinary single-subject files.
        split_bundled_subjects(items)

        # Step 4: fill in the plain-language rewrite for each item.
        # Done here (not inside extract_items) so extract_items.py stays
        # purely about document structure and doesn't need to know
        # anything about simplification.
        for item in items:
            item.plain_language_text = simplify(item.official_text)

        subject_breakdown = Counter(item.subject for item in items)
        if len(subject_breakdown) > 1:
            detail = ", ".join(f"{s}: {n}" for s, n in subject_breakdown.items())
            print(f"  {path.name} -> split into {len(subject_breakdown)} subjects ({detail}), {len(items)} items total")
        else:
            print(f"  {path.name} -> {subject}: {len(items)} items")
        all_items.extend(items)

    # Ids are assigned last, over the *combined* list from every file —
    # not per file — so that if two different source files ever produced
    # items for the same subject, their ids would still number
    # continuously rather than each file restarting from 1 and colliding.
    assign_ids(all_items)

    # Group by subject only, and rely on Python's sort being *stable* to
    # leave every subject's items in the natural order they were
    # extracted in — Unit 1 -> Area of Study 1 -> Outcome 1 -> its Key
    # Knowledge/Key Skill points -> Area of Study 2 -> ..., the same
    # order a student reading the study design top-to-bottom would see,
    # with Command Term glossary entries trailing at the end (they're
    # parsed last, from the document's tables). Sorting by category too
    # (e.g. alphabetically) would scramble that back into "all Key
    # Knowledge, then all Key Skill" with no unit/outcome structure —
    # exactly what the app's grouped results list needs to NOT happen.
    all_items.sort(key=lambda i: i.subject)

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
    parser.add_argument(
        "--dump-blocks",
        type=Path,
        default=None,
        metavar="DIR",
        help="also write each source file's raw parsed blocks as JSON into DIR, for debugging",
    )
    args = parser.parse_args()

    build(args.input, args.output, args.dump_blocks)


if __name__ == "__main__":
    main()
