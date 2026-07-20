# Study Design Simplifier

A Flutter app that turns dense VCE study design documents into a searchable,
plain-language browser. Pick a subject, filter by outcome/key knowledge/key
skill/command term, and see the official wording next to a plain-language
explanation side by side.

## Features

- **Subject sidebar** — switch between subjects. The subject list isn't
  hardcoded; it's derived from whatever's in the bundled dataset (currently:
  Applied Computing, Business Management, Data Analytics, English EAL,
  Foundation Mathematics, General Mathematics, Mathematical Methods, Media,
  Philosophy, Physics, Software Development, Specialist Mathematics).
- **Search** — full-text search across each item's title, official text, and
  plain-language explanation.
- **Category filtering** — narrow results to Outcomes, Key Knowledge, Key
  Skills, or Command Terms.
- **Grouped results list** — items are grouped under Unit / Area of Study
  headers in natural reading order, rather than one flat undifferentiated
  list (a real subject can have 100+ items).
- **Detail panel** — official study design text alongside a plain-language
  rewrite (rendered as a proper bullet list when the source content is a
  list), with a toggle to mark an item as completed.
- **Completion tracking** — a toolbar chip shows how many items are marked
  done out of the total.
- **Light/dark theme** — toggle from the settings slideout.

## Project structure

```
lib/
├── main.dart                        # App entry point, theme wiring
├── models/
│   └── study_item.dart              # StudyItem data model + fromJson
├── data/
│   └── study_data_repository.dart   # Loads assets/data/study_items.json
├── theme/
│   ├── app_colors.dart              # Light/dark color tokens
│   └── theme_model.dart             # ChangeNotifier for theme state
├── screens/
│   └── home_screen.dart             # Three-pane layout + filtering logic
└── widgets/
    ├── sidebar.dart                  # Subject list
    ├── search_bar_widget.dart
    ├── category_tabs.dart            # Category filter pills
    ├── results_list.dart             # Grouped, filtered result cards
    ├── detail_panel.dart             # Selected item detail view
    └── settings_slideout.dart        # Theme toggle panel
assets/data/
└── study_items.json                 # Generated dataset (see backend/)
```

## Current state

- Content comes from `assets/data/study_items.json`, a real dataset (2,206
  items across 12 subjects) generated from actual VCAA study design files by
  the pipeline in `backend/` — see [backend/README.md](backend/README.md).
  Loaded once at startup by `StudyDataRepository` and held in memory.
- State is held in memory with `setState`; completion status and theme
  choice are **not** persisted and reset on every restart.
- The layout is a fixed three-column, desktop-style design (220px sidebar,
  35%-width detail panel) and hasn't been adapted for phone-sized screens.
- The plain-language rewrites are rule-based (extractive + jargon
  substitution, not true paraphrasing) — see backend/README.md for what
  that means and its known limitations.
- To refresh the dataset after adding/updating source study design files,
  re-run the backend pipeline and copy its output over the bundled asset:
  ```bash
  cd backend && source .venv/bin/activate && python -m ingest.build
  cd .. && cp backend/output/study_items.json assets/data/study_items.json
  ```

## Getting started

This project requires the [Flutter SDK](https://docs.flutter.dev/get-started/install)
(Dart SDK `^3.7.2`, per `pubspec.yaml`).

```bash
flutter pub get
flutter run
```

Flutter supports building for Android, iOS, web, macOS, Linux, and Windows;
platform scaffolding for all of them is included in this repo. Run
`flutter devices` to see available targets, or `flutter run -d chrome` /
`-d macos` / etc. to target a specific one.

### Tests

```bash
flutter test
```
