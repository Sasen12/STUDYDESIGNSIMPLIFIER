"""CLI entry point: source_docs/*.docx|*.pdf -> output/study_items.json

    parse_docx/parse_pdf -> extract_items -> simplify -> write JSON

Usage:
    python -m ingest.build
    python -m ingest.build --input source_docs --output output/study_items.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from .acronyms import expand_bare_acronyms, extract_acronym_definitions
from .extract_items import assign_ids, extract_items, split_bundled_subjects
from .models import StudyItem
from .parse_docx import parse_docx
from .parse_pdf import parse_pdf
from .simplify import simplify

_PARSERS = {".docx": parse_docx, ".pdf": parse_pdf}


def _subject_for(path: Path, overrides: dict[str, str]) -> str:
    """Display subject name for one file: overrides.json entry if
    present, else title-cased filename.

    Inputs: path (Path); overrides (dict[str, str]).
    Outputs: str.
    """
    if path.name in overrides:
        return overrides[path.name]
    return path.stem.replace("_", " ").replace("-", " ").title()


def _load_overrides(input_dir: Path) -> dict[str, str]:
    """Load source_docs/subjects.json if present.

    Inputs: input_dir (Path).
    Outputs: dict[str, str] — {filename: subject name}, {} if no file.
    Exits the process if the file exists but is invalid JSON.
    """
    config_path = input_dir / "subjects.json"
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: {config_path} is not valid JSON: {e}", file=sys.stderr)
        raise SystemExit(1)


def _dump_blocks(path: Path, blocks: list, dump_dir: Path) -> None:
    """Debug aid: write one file's raw parsed blocks as their own JSON
    file, for inspecting extraction before extract_items.py runs.

    Inputs: path (Path); blocks (list[RawBlock]); dump_dir (Path).
    Outputs: None (writes a file).
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
    """Run the full pipeline over every file in input_dir and write the
    combined result to output_path.

    Inputs: input_dir (Path); output_path (Path); dump_blocks_dir
    (Path | None, optional debug dump).
    Outputs: list[StudyItem] (also written to output_path as JSON).
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

        try:
            blocks = _PARSERS[path.suffix.lower()](str(path))

            if dump_blocks_dir is not None:
                _dump_blocks(path, blocks, dump_blocks_dir)

            items = extract_items(blocks, subject)

            if not items:
                print(f"  WARNING: extracted 0 items from {path.name} — check its heading structure", file=sys.stderr)

            # Splits bundled multi-course files into real subjects
            # (no-op for single-subject files).
            split_bundled_subjects(items)

            for item in items:
                item.plain_language_text = simplify(item.official_text)
        except Exception as e:
            # One bad file used to crash the whole build and lose every
            # other file's already-processed output. Skip and continue
            # instead.
            print(f"  WARNING: failed to process {path.name} ({type(e).__name__}: {e}) — skipping this file", file=sys.stderr)
            continue

        subject_breakdown = Counter(item.subject for item in items)
        if len(subject_breakdown) > 1:
            detail = ", ".join(f"{s}: {n}" for s, n in subject_breakdown.items())
            print(f"  {path.name} -> split into {len(subject_breakdown)} subjects ({detail}), {len(items)} items total")
        else:
            print(f"  {path.name} -> {subject}: {len(items)} items")
        all_items.extend(items)

    # Expand bare acronyms per subject, over the combined list (so a
    # definition is found regardless of which file/unit it came from).
    items_by_subject: dict[str, list[StudyItem]] = defaultdict(list)
    for item in all_items:
        items_by_subject[item.subject].append(item)
    for subject_items in items_by_subject.values():
        definitions = extract_acronym_definitions(
            [i.official_text for i in subject_items]
        )
        for item in subject_items:
            item.plain_language_text = expand_bare_acronyms(
                item.plain_language_text, definitions
            )

    # Ids over the combined list so re-running after adding a file
    # doesn't renumber existing subjects.
    assign_ids(all_items)

    # Stable sort by subject only, preserving each subject's natural
    # reading order (Unit 1 -> its Areas -> Outcomes -> ...) — the app's
    # grouped results list depends on this order.
    all_items.sort(key=lambda i: i.subject)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps([i.to_json() for i in all_items], indent=2, ensure_ascii=False)
    )
    print(f"Wrote {len(all_items)} items to {output_path}")
    return all_items


def main() -> None:
    """CLI entry point.

    Inputs: command-line args (--input, --output, --dump-blocks).
    Outputs: None (writes the output JSON via build()).
    """
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
