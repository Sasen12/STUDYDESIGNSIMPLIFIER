from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RawBlock:
    """One paragraph of source text, tagged with its heading level.

    Both parse_docx.py and parse_pdf.py reduce very different source
    formats (Word styles vs. PDF font sizes) down to this single common
    shape, so extract_items.py only ever has to deal with one kind of
    input no matter which file format we started from.

    level 0 = ordinary body text (a paragraph, a bullet point, ...).
    level 1-4 = heading depth, matching how VCAA study designs are
    nested: Unit (1) > Area of Study (2) > Outcome (3) >
    "Key knowledge" / "Key skills" section label (4).
    level 5 is a special case used only for glossary/table rows (see
    parse_docx.py / parse_pdf.py) — it's not a "depth", it's a marker
    that this block is a ready-made "Term <TAB> Definition" pair.
    """

    text: str
    level: int = 0


@dataclass
class StudyItem:
    """One row of the final dataset — mirrors lib/models/study_item.dart
    field-for-field so the JSON this produces can be dropped straight
    into the Flutter app without any reshaping on the Dart side.

    is_completed always starts False here: that field is meant to track
    a *user's* personal progress inside the app, not anything we know
    at ingestion time, so we always ship it as an unstarted item.
    """

    id: str
    subject: str
    title: str
    category: str  # 'Outcome' | 'Key Knowledge' | 'Key Skill' | 'Command Term'
    official_text: str
    plain_language_text: str = ""
    unit: str | None = None
    area_of_study: str | None = None
    outcome: str | None = None
    is_completed: bool = False

    def to_json(self) -> dict:
        """Convert to the camelCase dict shape the Dart model expects.

        Python convention is snake_case (official_text) but Dart/JSON
        convention here is camelCase (officialText) — this is the one
        place that translation happens, so nothing else in the pipeline
        needs to think about naming conventions.
        """
        return {
            "id": self.id,
            "subject": self.subject,
            "title": self.title,
            "category": self.category,
            "officialText": self.official_text,
            "plainLanguageText": self.plain_language_text,
            "unit": self.unit,
            "areaOfStudy": self.area_of_study,
            "outcome": self.outcome,
            "isCompleted": self.is_completed,
        }
