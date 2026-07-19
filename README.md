# Study Design Simplifier

A Flutter app that turns dense VCE study design documents into a searchable,
plain-language browser. Pick a subject, filter by outcome/key knowledge/key
skill/command term, and see the official wording next to a plain-language
explanation side by side.

## Features

- **Subject sidebar** — switch between subjects (Software Development, Data
  Analytics, Business Management, General Mathematics, English, Physics,
  Mathematical Methods).
- **Search** — full-text search across each item's title, official text, and
  plain-language explanation.
- **Category filtering** — narrow results to Outcomes, Key Knowledge, Key
  Skills, or Command Terms.
- **Detail panel** — official study design text alongside a plain-language
  rewrite, with a toggle to mark an item as completed.
- **Completion tracking** — a toolbar chip shows how many items are marked
  done out of the total.
- **Light/dark theme** — toggle from the settings slideout.

## Project structure

```
lib/
├── main.dart                # App entry point, theme wiring
├── models/
│   └── study_item.dart      # StudyItem data model
├── data/
│   └── sample_data.dart     # In-memory sample dataset
├── theme/
│   ├── app_colors.dart      # Light/dark color tokens
│   └── theme_model.dart     # ChangeNotifier for theme state
├── screens/
│   └── home_screen.dart     # Three-pane layout + filtering logic
└── widgets/
    ├── sidebar.dart          # Subject list
    ├── search_bar_widget.dart
    ├── category_tabs.dart    # Category filter pills
    ├── results_list.dart     # Filtered result cards
    ├── detail_panel.dart     # Selected item detail view
    └── settings_slideout.dart # Theme toggle panel
```

## Current state

This is an early UI-only build:

- Content is served from a hardcoded sample dataset
  (`lib/data/sample_data.dart`) — there's no backend or content-import
  pipeline yet.
- State is held in memory with `setState`; completion status and theme
  choice are **not** persisted and reset on every restart.
- The layout is a fixed three-column, desktop-style design (220px sidebar,
  35%-width detail panel) and hasn't been adapted for phone-sized screens.

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
