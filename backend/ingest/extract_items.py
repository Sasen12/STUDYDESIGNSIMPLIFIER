"""Turn a flat list of RawBlocks into StudyItem records.

This is the heart of the ingestion pipeline: parse_docx.py / parse_pdf.py
only know how to strip formatting out of one file format each, and hand
back a flat, format-agnostic list of RawBlocks. This module is where we
actually understand VCAA's document structure and turn that flat list
into meaningful, separate StudyItem rows.

We walk the blocks exactly once, top to bottom, the same way you'd read
the document yourself: whenever we see a "Unit" heading we remember
we're now inside that unit, whenever we see an "Outcome" heading we
remember that too, and so on. That running memory (unit / area_of_study
/ outcome / section below) is what lets a Key Knowledge bullet point
three paragraphs later still know which Outcome it belongs to, even
though nothing in the bullet point's own text says so.

This is heuristic and tuned to the sections VCAA study designs share
(Unit N / Area of Study N / Outcome N / Key knowledge / Key skills). Real
source files will likely need small pattern tweaks — see README.md.
"""
from __future__ import annotations

import re

from .models import RawBlock, StudyItem

# Only "Outcome N" needs its own regex here (to pull heading text out
# for level-3 blocks); "Key knowledge" / "Key skills" already got
# reduced to level=4 by the parsers, but we still need to tell those two
# apart from each other, hence these two extra patterns.
_OUTCOME_RE = re.compile(r"^Outcome\s+(\d+)", re.I)
_KEY_KNOWLEDGE_RE = re.compile(r"^Key knowledge", re.I)
_KEY_SKILLS_RE = re.compile(r"^Key skills", re.I)


def _slug(text: str) -> str:
    """Turn arbitrary text into a lowercase, hyphenated, URL/ID-safe
    string, e.g. "Software Development" -> "software-development".
    Used to build stable, human-readable StudyItem ids.
    """
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "item"


def extract_items(blocks: list[RawBlock], subject: str) -> list[StudyItem]:
    """Walk `blocks` in order and emit one StudyItem per outcome
    statement, key knowledge dot point, key skill dot point, and
    command-term glossary row found along the way.

    `subject` is passed in rather than detected from the document,
    because a study design PDF/DOCX rarely states its own subject name
    anywhere machine-readable — build.py derives it from the filename
    (or a subjects.json override) instead.
    """
    items: list[StudyItem] = []

    # --- Running "where are we in the document" state -----------------
    # These four variables are the entire memory of the walk: whichever
    # heading we most recently saw at each level, plus which body-text
    # section (if any) we're currently inside. They get reset whenever a
    # higher-level heading appears, exactly like nested folders — a new
    # Unit heading wipes out area_of_study/outcome because a new unit
    # means we're no longer inside the old one's areas of study.
    unit: str | None = None
    area_of_study: str | None = None
    outcome_title: str | None = None
    section: str | None = None  # None | 'awaiting_outcome_statement' | 'Key Knowledge' | 'Key Skill'

    def add_item(category: str, title: str, official_text: str) -> None:
        """Build and append one StudyItem, stamped with whatever
        unit/area_of_study/outcome context we're currently inside.

        id is left blank here — assign_ids() fills it in afterwards,
        once split_bundled_subjects() (see below) has had a chance to
        correct `subject` for documents that bundle multiple VCE
        studies into one file. Assigning ids before that split would
        bake in the wrong (file-level default) subject slug.
        """
        # Command Term glossary rows aren't scoped to whichever unit
        # happened to be current when their table was encountered —
        # they're general reference material for the whole study, not
        # part of any one unit's content — so they deliberately don't
        # inherit unit/area_of_study/outcome the way every other
        # category does.
        is_glossary = category == "Command Term"
        items.append(
            StudyItem(
                id="",
                subject=subject,
                title=title,
                category=category,
                official_text=official_text,
                unit=None if is_glossary else unit,
                area_of_study=None if is_glossary else area_of_study,
                outcome=None if is_glossary else outcome_title,
            )
        )

    for block in blocks:
        text, level = block.text, block.level

        if block.is_sub_item and section in ("Key Knowledge", "Key Skill") and items:
            # A nested sub-bullet (e.g. "Boolean" indented under "types
            # of data, such as:") means nothing to a student on its own
            # — fold it into the dot point it belongs under instead of
            # giving it its own StudyItem. That parent is always
            # `items[-1]`: the item we most recently added while inside
            # this same Key Knowledge/Key Skill section.
            items[-1].official_text += f"; {text}"
            continue

        # --- Glossary table row: "Term<TAB>Definition" -----------------
        # These come pre-packaged from the parser (level=5) and don't
        # need any of the heading/section state above — a command term
        # definition is self-contained, so we handle it immediately and
        # move on to the next block without touching `section` etc.
        if level == 5:
            term, _, definition = text.partition("\t")
            if term and definition:
                add_item("Command Term", term.strip(), definition.strip())
            continue

        # --- Heading levels: update "where we are" and move on ---------
        # None of these four branches emit a StudyItem themselves — a
        # heading is just a label. The actual item gets created later,
        # when we reach the body-text paragraph(s) that the heading
        # introduces (see the "Body text" section below).

        if level == 1:  # "Unit N: ..."
            unit = text
            # Entering a new unit means any Area of Study / Outcome we
            # remembered belonged to the *previous* unit, so they must
            # be cleared — otherwise later items would be mis-tagged as
            # belonging to a unit they don't.
            area_of_study = outcome_title = None
            section = None
            continue

        if level == 2:  # "Area of Study N"
            area_of_study = text
            outcome_title = None
            # Some documents write just "Area of Study 1" here and put
            # its descriptive title ("The business idea") on its own
            # heading line right after — flag that so we can append it
            # below if that's what comes next.
            section = "awaiting_area_title"
            continue

        if level == 3 and section == "awaiting_area_title" and not _OUTCOME_RE.match(text):
            # The heading right after "Area of Study N" wasn't another
            # Outcome/Unit/etc. — treat it as that area's descriptive
            # title and fold it into area_of_study for a more readable
            # label (e.g. "Area of Study 1: The business idea").
            area_of_study = f"{area_of_study}: {text}"
            section = None
            continue

        if level == 3 and _OUTCOME_RE.match(text):
            # We've just seen "Outcome N" — the very next body-text
            # paragraph is that outcome's statement (VCAA always writes
            # it as "On completion of this unit the student should be
            # able to ..." immediately after the heading), so flag that
            # we're expecting it next rather than creating the item now.
            outcome_title = text
            section = "awaiting_outcome_statement"
            continue

        if level == 4 and _KEY_KNOWLEDGE_RE.match(text):
            # Every body paragraph from here on (until the next heading)
            # is one Key Knowledge dot point.
            section = "Key Knowledge"
            continue

        if level == 4 and _KEY_SKILLS_RE.match(text):
            section = "Key Skill"
            continue

        if level != 0:
            # Some other heading level/pattern we don't specifically
            # track (e.g. a "Rationale" or "Assessment" section title).
            # We deliberately don't clear `section` here, in case it's
            # just a stray heading-styled paragraph in the middle of a
            # Key Knowledge list (this happens in some real documents).
            continue

        # --- Body text: what we do with it depends on `section` --------
        if section == "awaiting_outcome_statement" and outcome_title:
            # This is the single paragraph that follows an "Outcome N"
            # heading — the outcome statement itself.
            add_item("Outcome", outcome_title, text)
            # Only the first paragraph after the heading is the
            # statement; reset `section` so any further body text (e.g.
            # explanatory notes) isn't mistaken for more outcome text.
            section = None
        elif section in ("Key Knowledge", "Key Skill"):
            # Each body paragraph inside one of these sections is its
            # own dot point / bullet — build a short title by taking the
            # first few words (dot points don't come with their own
            # titles the way Outcomes do).
            words = text.split()
            title = " ".join(words[:8]) + ("…" if len(words) > 8 else "")
            add_item(section, title, text)
        # else: narrative text outside any tracked section (e.g. a
        # "Rationale" paragraph) — intentionally skipped, since it's not
        # one of the four StudyItem categories the app displays.

    return items


# Matches a unit heading like "Unit 3: Data analytics" or
# "Units 3 and 4: Foundation Mathematics", capturing the part after the
# colon.
_UNIT_SUFFIX_RE = re.compile(r"^Units?\s+\d+(?:\s+and\s+\d+)?\s*:\s*(.+)$", re.I)


def split_bundled_subjects(items: list[StudyItem]) -> None:
    """Some VCAA files aren't one subject's study design — they're
    several related VCE studies bundled into a single document. The
    combined Mathematics study design, for example, covers General
    Mathematics, Mathematical Methods, Specialist Mathematics, and
    Foundation Mathematics as four separate courses, each with their
    own Unit 1-4 sequence, inside one file; the combined Applied
    Computing document is the same for Applied Computing, Data
    Analytics, and Software Development.

    build.py assigns every item from a file the same subject up front
    (guessed from the filename), which is wrong for these bundled
    files. This function re-labels items in place, splitting them out
    by their *actual* course, detected from the "Unit N: <course
    name>" heading text — but only when that course name repeats across
    at least two different unit numbers, which is what distinguishes a
    genuine bundled sub-study name ("Data analytics" shared by both
    Unit 3 and Unit 4) from an ordinary single-subject unit title that
    happens to follow the same "Unit N: ..." shape (e.g. Business
    Management's "Unit 1: Planning a business" — a title unique to that
    one unit, not a second subject).

    Call this once per source file, after extract_items() and before
    simplify() — it's a no-op (leaves item.subject untouched) for
    ordinary single-subject documents.
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
        return  # ordinary single-subject document — nothing to split

    for item in items:
        if not item.unit:
            continue
        match = _UNIT_SUFFIX_RE.match(item.unit)
        if match and match.group(1).strip() in bundled_course_names:
            item.subject = match.group(1).strip().title()


def assign_ids(items: list[StudyItem]) -> None:
    """Fill in each item's `id`, in place, from its *final* subject —
    call this last, after split_bundled_subjects() has corrected
    `subject` for any bundled documents, so ids like
    "general-mathematics-key-skill-4" always match the subject the item
    actually ends up filed under.

    Counters are kept per (subject, category) rather than one global
    counter, both so ids read naturally (each subject's items number
    from 1) and so re-running the pipeline after adding a new source
    file doesn't renumber — and thus doesn't invalidate — ids for
    subjects that didn't change.
    """
    counters: dict[tuple[str, str], int] = {}
    for item in items:
        key = (item.subject, item.category)
        counters[key] = counters.get(key, 0) + 1
        item.id = f"{_slug(item.subject)}-{_slug(item.category)}-{counters[key]}"
