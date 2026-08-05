import '../models/study_item.dart';

/// One row of the results list: either a group header or an item.
///
/// Extracted out of `ResultsList` so the grouping logic — pure string
/// comparison over `items`, the same code path the UI re-runs on every
/// keystroke — can be unit-tested in isolation.
///
/// A sealed type rather than two parallel lists (one of header strings,
/// one of items) or a single `List<Object>` with runtime `is` checks:
/// the UI builds a different widget per row, and a sealed type lets its
/// `switch` be checked exhaustively at compile time — a new subtype the
/// widget forgets to handle is a compile error, not a runtime bug.
sealed class StudyRow {
  const StudyRow();
}

/// A Unit, Area of Study or Glossary header row. [isSubHeader]
/// distinguishes the smaller blue Area of Study headers from the bolder
/// Unit headers.
class StudyHeaderRow extends StudyRow {
  final String text;
  final bool isSubHeader;

  const StudyHeaderRow(this.text, {this.isSubHeader = false});
}

/// A single result card row.
class StudyItemRow extends StudyRow {
  final StudyItem item;

  const StudyItemRow(this.item);
}

/// Groups [items] under Unit / Area of Study headers, in the order the
/// backend pipeline emitted them (Unit 1 -> its Areas of Study -> each
/// Outcome and its Key Knowledge/Key Skill points, then Unit 2, ...).
/// Items with no unit (Command Term glossary entries) are grouped under
/// a trailing "Glossary" header instead.
///
/// Building rows up front instead of inline keeps the results list's
/// `ListView.builder` cheap: it constructs only the widgets actually
/// near the viewport, never one card per item.
List<StudyRow> buildRows(List<StudyItem> items) {
  final rows = <StudyRow>[];
  String? lastUnit;
  String? lastAreaOfStudy;
  var glossaryHeaderShown = false;

  for (final item in items) {
    if (item.unit == null) {
      // Command Term glossary entries aren't scoped to a unit — group
      // them under one trailing header instead of a Unit/Area one.
      if (!glossaryHeaderShown) {
        rows.add(const StudyHeaderRow('Glossary of Command Terms'));
        glossaryHeaderShown = true;
      }
    } else {
      if (item.unit != lastUnit) {
        rows.add(StudyHeaderRow(item.unit!));
        lastUnit = item.unit;
        lastAreaOfStudy = null; // force the area header to re-show too
      }
      if (item.areaOfStudy != lastAreaOfStudy) {
        lastAreaOfStudy = item.areaOfStudy;
        if (item.areaOfStudy != null) {
          rows.add(StudyHeaderRow(item.areaOfStudy!, isSubHeader: true));
        }
      }
    }
    rows.add(StudyItemRow(item));
  }
  return rows;
}

/// A short, clean one-line headline for a card — not the full preview
/// text truncated wherever the 2nd line happens to run out.
///
/// List-shaped content (produced when nested sub-bullets get folded
/// into their parent item — see backend/README.md) always has a short
/// natural lead-in before its first semicolon ("types and purposes of
/// qualitative and quantitative data, such as:; interviews and
/// surveys...; sensor data..."). Showing just that lead-in gives a
/// clean, short title instead of either a mid-word ellipsis cut or a
/// long joined-list sentence that reads near-identically to the
/// official text (list items rarely contain jargon to swap, so their
/// plain-language and official text are often the same anyway — the
/// value here is a scannable label, not a second copy of the content).
/// Non-list content has no such natural short lead-in, so it falls
/// back to the full text with the UI's own line-clamp truncation.
String cardHeadline(StudyItem item) {
  final text = item.plainLanguageText;
  if (!text.contains('; ')) return text;
  final intro = text.split(';').first.trim();
  return intro;
}
