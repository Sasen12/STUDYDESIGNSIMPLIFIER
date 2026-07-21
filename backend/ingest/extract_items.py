"""Turn a flat list of RawBlocks into StudyItem records.

Walks blocks once, top to bottom, tracking current Unit/Area of
Study/Outcome/section — the same way a reader would — so a Key
Knowledge bullet several paragraphs later still knows which Outcome it
belongs to.
"""
from __future__ import annotations

import re
import sys

from .models import RawBlock, StudyItem

_OUTCOME_RE = re.compile(r"^Outcome\s+(\d+)", re.I)
_KEY_KNOWLEDGE_RE = re.compile(r"^Key knowledge", re.I)
_KEY_SKILLS_RE = re.compile(r"^Key skills", re.I)

# Distinguishes a genuine "Area of Study N" heading from any other
# level-2-styled heading ("School-based assessment", a TOC line) —
# parsers assign level=2 to any Heading-2-shaped style, not just ones
# that say "Area of Study".
_AREA_OF_STUDY_RE = re.compile(r"^Area of [Ss]tudy\s+\d+", re.I)


def _slug(text: str) -> str:
    """Lowercase, hyphenated, ID-safe string for StudyItem ids.

    Inputs: text (str).
    Outputs: str (falls back to "item" if empty).
    """
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "item"


def extract_items(blocks: list[RawBlock], subject: str) -> list[StudyItem]:
    """Walk blocks and emit one StudyItem per Outcome statement, Key
    Knowledge point, Key Skill point, and Command Term row.

    Inputs: blocks (list[RawBlock]) — one file's parsed content;
    subject (str) — file-level default subject name.
    Outputs: list[StudyItem] — id="" and plain_language_text="" (filled
    in later by assign_ids()/simplify()).
    """
    items: list[StudyItem] = []

    # Running "where are we" state, reset top-down like nested folders
    # (a new Unit wipes area_of_study/outcome, etc).
    unit: str | None = None
    area_of_study: str | None = None
    outcome_title: str | None = None
    section: str | None = None  # None | 'awaiting_outcome_statement' | 'Key Knowledge' | 'Key Skill'

    # Dot point a sub-bullet should fold into — the most recent item
    # added *within the current section*, not just the last item added
    # overall (which could belong to a different section).
    current_section_parent: StudyItem | None = None

    def add_item(category: str, title: str, official_text: str) -> StudyItem:
        """Build + append one StudyItem from the current context.

        Inputs: category (str), title (str), official_text (str).
        Outputs: StudyItem (also appended to `items`).
        """
        # Command Term rows aren't scoped to a unit — they're general
        # reference material, not part of any one unit's content.
        is_glossary = category == "Command Term"
        item = StudyItem(
            id="",
            subject=subject,
            title=title,
            category=category,
            official_text=official_text,
            unit=None if is_glossary else unit,
            area_of_study=None if is_glossary else area_of_study,
            outcome=None if is_glossary else outcome_title,
        )
        items.append(item)
        return item

    for block in blocks:
        text, level = block.text, block.level

        if block.is_sub_item and section in ("Key Knowledge", "Key Skill"):
            # Fold a nested sub-bullet into its parent dot point.
            if current_section_parent is not None:
                current_section_parent.official_text += f"; {text}"
            else:
                # No parent yet in this section — drop rather than
                # fabricate a fragment item or glue onto an unrelated one.
                print(
                    f"  WARNING: orphaned sub-item with no parent dot point, skipping: {text[:60]!r}",
                    file=sys.stderr,
                )
            continue

        # Glossary table row: "Term<TAB>Definition", self-contained.
        if level == 5:
            term, _, definition = text.partition("\t")
            if term and definition:
                add_item("Command Term", term.strip(), definition.strip())
            continue

        # Headings update state; the item itself is created when the
        # following body text is reached.
        if level == 1:  # "Unit N: ..."
            unit = text
            area_of_study = outcome_title = None
            section = None
            continue

        if level == 2 and _AREA_OF_STUDY_RE.match(text):
            area_of_study = text
            outcome_title = None
            # The descriptive title sometimes comes as its own heading
            # right after — flag that we're expecting one.
            section = "awaiting_area_title"
            continue

        if level == 2:
            # A level-2 heading that isn't "Area of Study N" (e.g.
            # "School-based assessment") — ends the current section
            # without being treated as a new Area of Study.
            section = None
            continue

        if (
            level == 3
            and section == "awaiting_area_title"
            and not _OUTCOME_RE.match(text)
            and len(text) <= 100
        ):
            # Fold the descriptive title into area_of_study (e.g.
            # "Area of Study 1: The business idea"). Length guard: a
            # real title is short, not a sentence.
            area_of_study = f"{area_of_study}: {text}"
            section = None
            continue

        if level == 3 and section == "awaiting_area_title":
            section = None  # didn't qualify as a title — stop waiting

        if level == 3 and _OUTCOME_RE.match(text):
            # Next body paragraph is the outcome statement itself.
            outcome_title = text
            section = "awaiting_outcome_statement"
            continue

        if level == 4 and _KEY_KNOWLEDGE_RE.match(text):
            section = "Key Knowledge"
            current_section_parent = None
            continue

        if level == 4 and _KEY_SKILLS_RE.match(text):
            section = "Key Skill"
            current_section_parent = None
            continue

        if level != 0:
            # Some other heading we don't track (e.g. "Rationale").
            continue

        # Body text: what to do depends on `section`.
        if section == "awaiting_outcome_statement" and outcome_title:
            add_item("Outcome", outcome_title, text)
            section = None
        elif section in ("Key Knowledge", "Key Skill"):
            words = text.split()
            title = " ".join(words[:8]) + ("…" if len(words) > 8 else "")
            current_section_parent = add_item(section, title, text)
        # else: narrative text outside a tracked section — skipped.

    return items


# Matches "Unit 3: Data analytics" / "Units 3 and 4: Foundation
# Mathematics", capturing the part after the colon.
_UNIT_SUFFIX_RE = re.compile(r"^Units?\s+\d+(?:\s+and\s+\d+)?\s*:\s*(.+)$", re.I)


def split_bundled_subjects(items: list[StudyItem]) -> None:
    """Split a file that bundles several VCE studies (e.g. combined
    Mathematics -> General/Specialist/Foundation Mathematics +
    Mathematical Methods) into their real per-course subjects, detected
    from "Unit N: <course name>" repeating across >=2 unit numbers.
    No-op for ordinary single-subject documents.

    Inputs: items (list[StudyItem]) — one file's extracted items.
    Outputs: None — mutates `subject` in place.
    """
    suffix_unit_numbers: dict[str, set[str]] = {}
    for item in items:
        if not item.unit:
            continue
        match = _UNIT_SUFFIX_RE.match(item.unit)
        if not match:
            continue
        suffix_unit_numbers.setdefault(match.group(1).strip(), set()).add(item.unit)

    bundled_course_names = {
        suffix for suffix, units in suffix_unit_numbers.items() if len(units) >= 2
    }
    if not bundled_course_names:
        return

    for item in items:
        if not item.unit:
            continue
        match = _UNIT_SUFFIX_RE.match(item.unit)
        if match and match.group(1).strip() in bundled_course_names:
            item.subject = match.group(1).strip().title()


def assign_ids(items: list[StudyItem]) -> None:
    """Fill in each item's id from its final subject. Call after
    split_bundled_subjects(). Counters are per (subject, category) so
    ids number naturally and re-running the pipeline doesn't renumber
    unrelated subjects.

    Inputs: items (list[StudyItem]) — the combined list from every file.
    Outputs: None — mutates `id` in place.
    """
    counters: dict[tuple[str, str], int] = {}
    for item in items:
        key = (item.subject, item.category)
        counters[key] = counters.get(key, 0) + 1
        item.id = f"{_slug(item.subject)}-{_slug(item.category)}-{counters[key]}"
