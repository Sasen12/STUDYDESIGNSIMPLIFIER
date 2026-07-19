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
    subject_slug = _slug(subject)

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

    # Per-category counters used to build sequential, stable ids like
    # "software-development-key-knowledge-3". Kept separate per category
    # (rather than one global counter) so ids read naturally and don't
    # shift around if, say, a Key Skill gets inserted before a Key
    # Knowledge item in a future re-run.
    counters = {"Outcome": 0, "Key Knowledge": 0, "Key Skill": 0, "Command Term": 0}

    def add_item(category: str, title: str, official_text: str) -> None:
        """Build and append one StudyItem, stamped with whatever
        unit/area_of_study/outcome context we're currently inside.
        """
        counters[category] += 1
        items.append(
            StudyItem(
                id=f"{subject_slug}-{_slug(category)}-{counters[category]}",
                subject=subject,
                title=title,
                category=category,
                official_text=official_text,
                unit=unit,
                area_of_study=area_of_study,
                outcome=outcome_title,
            )
        )

    for block in blocks:
        text, level = block.text, block.level

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

        if level == 2:  # "Area of Study N: ..."
            area_of_study = text
            outcome_title = None
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
