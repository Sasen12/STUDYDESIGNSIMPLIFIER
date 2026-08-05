"""Unit tests for ingest.simplify.py.

Run from backend/:  .venv/bin/python -m unittest discover -v
"""
import unittest

from ingest import simplify as simp


class SimplifyTest(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(simp.simplify(""), "")
        self.assertEqual(simp.simplify("   \n  "), "")

    def test_plain_sentence_passthrough(self):
        self.assertEqual(simp.simplify("Hello world."), "Hello world.")

    def test_jargon_words_swapped(self):
        self.assertEqual(simp.simplify("Please utilise the methodology."), "Please use the method.")

    def test_jargon_capitalisation_preserved(self):
        self.assertEqual(simp.simplify("Utilise this tool."), "Use this tool.")

    def test_multiword_jargon_phrase(self):
        self.assertEqual(
            simp.simplify("Discuss the data with reference to the evidence."),
            "Discuss the data about the evidence.",
        )

    def test_list_text_keeps_structure(self):
        self.assertEqual(
            simp.simplify("utilise spreadsheets; utilise databases"),
            "use spreadsheets; use databases",
        )

    def test_max_two_sentences(self):
        text = "Alpha cats fly high. Beta dogs swim deep. Gamma birds sing loud. Delta fish hide fast."
        self.assertEqual(simp.simplify(text).count("."), 2)

    def test_run_on_split_at_clause_boundary(self):
        self.assertEqual(simp.simplify("The sun rises and the birds sing."), "The sun rises. The birds sing.")

    def test_conjoined_nouns_not_split(self):
        # "and" joining nouns ("tea and coffee") isn't a clause boundary.
        self.assertEqual(simp.simplify("I like tea and coffee."), "I like tea and coffee.")


if __name__ == "__main__":
    unittest.main()
