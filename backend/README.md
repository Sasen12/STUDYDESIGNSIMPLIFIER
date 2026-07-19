# Ingestion pipeline

Converts raw VCE study design files (.docx / .pdf) into the JSON dataset
the Flutter app displays, with a plain-language rewrite generated for
each item.

This is an **offline pipeline**, not a running server: you run it
locally whenever you have new/updated study design files, and commit
the resulting JSON. The Flutter app just reads that JSON as a bundled
asset — it never talks to this code at runtime.

```
source_docs/          <- drop your .docx / .pdf study design files here (gitignored)
  subjects.json        <- optional: {"filename.docx": "Display Subject Name"} overrides
output/
  study_items.json      <- generated dataset (this IS committed — it's what the app ships)
ingest/
  models.py             <- RawBlock / StudyItem data shapes
  parse_docx.py          <- .docx -> RawBlock list (uses paragraph styles)
  parse_pdf.py            <- .pdf -> RawBlock list (uses font-size + regex heuristics)
  extract_items.py         <- RawBlock list -> StudyItem list (the Unit/Area of Study/
                              Outcome/Key knowledge/Key skills state machine)
  simplify.py               <- StudyItem.official_text -> plain-language rewrite
  jargon_dictionary.json     <- word -> plain-language replacement map used by simplify.py
  build.py                    <- CLI entry point, wires the above together
```

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The first run downloads NLTK's sentence-tokenizer data automatically
(needs network access once; cached under `~/nltk_data` after that).

## Usage

1. Drop your source files into `source_docs/` (e.g.
   `software_development.docx`, `data_analytics.pdf`).
2. If a filename doesn't cleanly title-case into the subject name you
   want shown in the app (the default: `software_development.docx` ->
   "Software Development"), add an entry to `source_docs/subjects.json`:
   ```json
   { "sd_2024_accredited.docx": "Software Development" }
   ```
3. Run the pipeline:
   ```bash
   python -m ingest.build
   ```
4. Check the console output — it prints how many items were extracted
   per file, and warns if any file produced **0 items** (almost always
   means that file's headings don't match the patterns below and the
   parser needs a small tweak).
5. Commit `output/study_items.json`. Wiring it into the Flutter app (as
   a bundled asset, replacing `lib/data/sample_data.dart`) is a
   follow-up step, not done yet.

## How extraction works

Both parsers reduce their very different source formats down to a
common list of `RawBlock`s (a paragraph of text + a heading depth 0-4),
so `extract_items.py` only has to understand one thing: VCAA's
consistent document structure —

```
Unit N                          (level 1)
  Area of Study N                (level 2)
    Outcome N                     (level 3)
      <outcome statement paragraph>   -> one "Outcome" StudyItem
      Key knowledge                    (level 4)
        <dot point>                     -> one "Key Knowledge" StudyItem
        <dot point>                     -> one "Key Knowledge" StudyItem
      Key skills                       (level 4)
        <dot point>                     -> one "Key Skill" StudyItem
```

Glossary tables ("Term | Definition", e.g. VCAA's command-term glossary)
are detected separately and become `"Command Term"` items regardless of
where they appear in the document.

If a real study design's wording differs even slightly from this (e.g.
"Areas of Study" plural, or a document that doesn't use Word heading
styles at all), extraction for that file will likely come back empty or
partial — the fix is almost always a small regex/style-name tweak in
`extract_items.py`, `parse_docx.py`, or `parse_pdf.py`, not a rewrite.

## How simplification works

`simplify.py` does **not** paraphrase — scikit-learn has no text
generation capability, it's a classical ML library. What it actually
does, per item:

1. **Extract** — split the official text into sentences (NLTK), and if
   there's more than a couple, keep only the most representative ones
   using TF-IDF + cosine similarity to the passage's "centroid" vector
   (a standard extractive-summarisation technique). This trims a dense
   paragraph down without inventing new wording.
2. **Rewrite** — swap known jargon words for plain-language equivalents
   (`jargon_dictionary.json`), and split long, multi-clause sentences at
   semicolons/"and" joins into shorter ones.

Both steps are deterministic rule-based text manipulation, not machine
learning "understanding" the content. Known limitation: word-for-word
jargon substitution can read awkwardly for verbs that need sentence
restructuring, not just a swapped word (e.g. "evaluate X" becoming
"judge how good X is" mid-sentence). Getting genuinely fluent, reworded
explanations would require an LLM instead of this approach — out of
scope for this pipeline by design (see project chat history for why
scikit-learn/extractive was chosen over that).

Tune `jargon_dictionary.json` freely — it's just a JSON map, no code
changes needed to add/adjust entries.
