from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RawBlock:
    """One paragraph/line of source text with its detected heading level.

    Common output shape for both parse_docx.py and parse_pdf.py, so
    extract_items.py only deals with one input format.

    level: 0 = body text, 1-4 = heading depth (Unit/Area of Study/
    Outcome/Key knowledge-or-skills), 5 = glossary table row.
    is_sub_item: True for a nested sub-bullet (folded into its parent
    item by extract_items.py instead of becoming its own StudyItem).

    Inputs: text (str), level (int, default 0), is_sub_item (bool,
    default False).
    Outputs: — (plain data holder).
    """

    text: str
    level: int = 0
    is_sub_item: bool = False


@dataclass
class StudyItem:
    """One row of the final dataset. Mirrors
    lib/models/study_item.dart field-for-field.

    Inputs: id/subject/title/category/official_text (str),
    plain_language_text (str, default ""), unit/area_of_study/outcome
    (str | None), is_completed (bool, default False).
    Outputs: — (plain data holder; see to_json()).
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

        Inputs: —
        Outputs: dict (camelCase keys, matches Dart's fromJson()).
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
