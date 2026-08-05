"""Unit tests for ingest.extract_items.py.

Run from backend/:  .venv/bin/python -m unittest discover -v
"""
import unittest

from ingest.extract_items import (
    _slug,
    assign_ids,
    extract_items,
    split_bundled_subjects,
)
from ingest.models import RawBlock, StudyItem


def body(text, sub=False):
    return RawBlock(text=text, level=0, is_sub_item=sub)


class SlugTest(unittest.TestCase):
    def test_slug_basic(self):
        self.assertEqual(_slug("Hello, World!"), "hello-world")

    def test_slug_empty_falls_back_to_item(self):
        self.assertEqual(_slug("!!!"), "item")

    def test_slug_multi_word(self):
        self.assertEqual(_slug("Key Knowledge"), "key-knowledge")


class ExtractItemsTest(unittest.TestCase):
    def test_outcome_scoped_to_unit_and_area(self):
        blocks = [
            RawBlock("Unit 1: Software development", 1),
            RawBlock("Area of Study 1", 2),
            RawBlock("The business idea", 3),
            RawBlock("Outcome 1", 3),
            body("On completion of this unit the student should be able to solve a problem."),
        ]
        items = extract_items(blocks, "Applied Computing")
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item.category, "Outcome")
        self.assertEqual(item.subject, "Applied Computing")
        self.assertEqual(item.unit, "Unit 1: Software development")
        self.assertEqual(item.area_of_study, "Area of Study 1: The business idea")
        self.assertEqual(item.outcome, "Outcome 1")
        self.assertEqual(
            item.official_text,
            "On completion of this unit the student should be able to solve a problem.",
        )
        self.assertEqual(item.id, "")
        self.assertEqual(item.plain_language_text, "")

    def test_key_knowledge_and_key_skill_items(self):
        blocks = [
            RawBlock("Unit 3: Data analytics", 1),
            RawBlock("Area of Study 1", 2),
            RawBlock("Outcome 1", 3),
            body("Outcome statement body"),
            RawBlock("Key knowledge", 4),
            body("This is the first knowledge point and it is quite long"),
            RawBlock("Key skills", 4),
            body("Apply the technique carefully"),
        ]
        items = extract_items(blocks, "Applied Computing")
        self.assertEqual(
            [i.category for i in items], ["Outcome", "Key Knowledge", "Key Skill"]
        )
        kk = items[1]
        self.assertEqual(
            kk.official_text, "This is the first knowledge point and it is quite long"
        )
        self.assertEqual(kk.title, "This is the first knowledge point and it…")
        self.assertEqual(kk.unit, "Unit 3: Data analytics")
        self.assertEqual(kk.area_of_study, "Area of Study 1")
        self.assertEqual(kk.outcome, "Outcome 1")
        ks = items[2]
        self.assertEqual(ks.official_text, "Apply the technique carefully")
        self.assertEqual(ks.title, "Apply the technique carefully")  # <=8 words: no ellipsis

    def test_sub_item_folds_into_parent(self):
        blocks = [
            RawBlock("Unit 3: Data analytics", 1),
            RawBlock("Area of Study 1", 2),
            RawBlock("Outcome 1", 3),
            body("Statement"),
            RawBlock("Key knowledge", 4),
            body("Parent bullet point"),
            body("First sub detail", sub=True),
            body("Second sub detail", sub=True),
        ]
        items = extract_items(blocks, "Applied Computing")
        kk = items[-1]
        self.assertEqual(kk.category, "Key Knowledge")
        self.assertEqual(
            kk.official_text, "Parent bullet point; First sub detail; Second sub detail"
        )

    def test_glossary_row_is_command_term(self):
        blocks = [
            RawBlock("Unit 3: Data analytics", 1),
            RawBlock("Outcome 1", 3),
            body("Statement"),
            RawBlock("Iteration\tRepeating a block of code", 5),
        ]
        items = extract_items(blocks, "Applied Computing")
        term = items[-1]
        self.assertEqual(term.category, "Command Term")
        self.assertEqual(term.title, "Iteration")
        self.assertEqual(term.official_text, "Repeating a block of code")
        self.assertIsNone(term.unit)
        self.assertIsNone(term.area_of_study)
        self.assertIsNone(term.outcome)

    def test_unscoped_body_text_is_skipped(self):
        blocks = [
            RawBlock("Unit 3: Data analytics", 1),
            RawBlock("Area of Study 1", 2),
            RawBlock("Rationale", 2),  # non-area level-2 heading ends the section
            body("This narrative text is not inside any tracked section"),
        ]
        self.assertEqual(extract_items(blocks, "Applied Computing"), [])

    def test_area_title_not_folded_when_too_long(self):
        long_title = "x" * 120
        blocks = [
            RawBlock("Unit 1: Software development", 1),
            RawBlock("Area of Study 1", 2),
            RawBlock(long_title, 3),
            RawBlock("Outcome 1", 3),
            body("Statement"),
        ]
        items = extract_items(blocks, "Applied Computing")
        self.assertEqual(items[0].area_of_study, "Area of Study 1")

    def test_outcome_heading_not_folded_as_area_title(self):
        blocks = [
            RawBlock("Unit 1: Software development", 1),
            RawBlock("Area of Study 1", 2),
            RawBlock("Outcome 1", 3),
            body("Statement"),
        ]
        items = extract_items(blocks, "Applied Computing")
        self.assertEqual(items[0].area_of_study, "Area of Study 1")
        self.assertEqual(items[0].outcome, "Outcome 1")


class SplitBundledSubjectsTest(unittest.TestCase):
    def _item(self, unit, category="Key Knowledge"):
        return StudyItem(
            id="", subject="Mathematics", title="t", category=category,
            official_text="o", unit=unit,
        )

    def test_single_subject_document_unchanged(self):
        # Real single-subject docs use bare "Unit 1"/"Unit 2" headings,
        # no course-name suffix — nothing to split.
        items = [
            self._item("Unit 1"),
            self._item("Unit 2"),
        ]
        split_bundled_subjects(items)
        self.assertEqual([i.subject for i in items], ["Mathematics", "Mathematics"])

    def test_bundled_courses_reassigned(self):
        items = [
            self._item("Unit 3: General Mathematics"),
            self._item("Unit 4: General Mathematics"),
            self._item("Unit 3: Mathematical Methods"),
            self._item("Unit 4: Mathematical Methods"),
        ]
        split_bundled_subjects(items)
        self.assertEqual(
            {i.subject for i in items},
            {"General Mathematics", "Mathematical Methods"},
        )

    def test_bundled_glossary_duplicated_to_each_course(self):
        items = [
            self._item("Unit 3: General Mathematics"),
            self._item("Unit 4: General Mathematics"),
            self._item("Unit 3: Mathematical Methods"),
            self._item("Unit 4: Mathematical Methods"),
            self._item(None, category="Command Term"),
        ]
        split_bundled_subjects(items)
        glossary = [i for i in items if i.category == "Command Term"]
        self.assertEqual(len(glossary), 2)
        self.assertEqual(
            {i.subject for i in glossary},
            {"General Mathematics", "Mathematical Methods"},
        )


class AssignIdsTest(unittest.TestCase):
    def test_per_subject_category_counters(self):
        items = [
            StudyItem(id="", subject="Applied Computing", title="a", category="Outcome", official_text="o"),
            StudyItem(id="", subject="Applied Computing", title="b", category="Outcome", official_text="o"),
            StudyItem(id="", subject="Applied Computing", title="c", category="Key Knowledge", official_text="o"),
            StudyItem(id="", subject="English", title="d", category="Outcome", official_text="o"),
        ]
        assign_ids(items)
        self.assertEqual(
            [i.id for i in items],
            [
                "applied-computing-outcome-1",
                "applied-computing-outcome-2",
                "applied-computing-key-knowledge-1",
                "english-outcome-1",
            ],
        )


if __name__ == "__main__":
    unittest.main()
