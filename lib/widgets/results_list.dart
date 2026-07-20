import 'package:flutter/material.dart';
import '../models/study_item.dart';
import '../theme/app_colors.dart';
import '../theme/category_colors.dart';

/// Displays [items] grouped under Unit / Area of Study headers, in the
/// order the backend pipeline emitted them (Unit 1 -> its Areas of
/// Study -> each Outcome and its Key Knowledge/Key Skill points, then
/// Unit 2, ...). Items with no unit (Command Term glossary entries)
/// are grouped under a trailing "Glossary" header instead.
///
/// A flat, ungrouped list works fine for a handful of hand-written
/// sample items, but a real subject can have 100+ extracted items —
/// without this grouping a student sees one undifferentiated scroll
/// with no sense of which unit/outcome they're looking at.
class ResultsList extends StatelessWidget {
  final List<StudyItem> items;
  final StudyItem? selectedItem;
  final ValueChanged<StudyItem> onItemSelected;
  final int generation;

  const ResultsList({
    super.key,
    required this.items,
    required this.selectedItem,
    required this.onItemSelected,
    required this.generation,
  });

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return Center(
        child: Text(
          'No results found',
          style: TextStyle(fontSize: 13, color: context.textSecondary),
        ),
      );
    }

    final children = <Widget>[];
    String? lastUnit;
    String? lastAreaOfStudy;
    var glossaryHeaderShown = false;

    for (final item in items) {
      if (item.unit == null) {
        // Command Term glossary entries aren't scoped to a unit — group
        // them under one trailing header instead of a Unit/Area one.
        if (!glossaryHeaderShown) {
          children.add(const _GroupHeader('Glossary of Command Terms'));
          glossaryHeaderShown = true;
        }
      } else {
        if (item.unit != lastUnit) {
          children.add(_GroupHeader(item.unit!));
          lastUnit = item.unit;
          lastAreaOfStudy = null; // force the area header to re-show too
        }
        if (item.areaOfStudy != lastAreaOfStudy) {
          lastAreaOfStudy = item.areaOfStudy;
          if (item.areaOfStudy != null) {
            children.add(_SubGroupHeader(item.areaOfStudy!));
          }
        }
      }
      children.add(
        _ItemCard(
          item: item,
          isSelected: item.id == selectedItem?.id,
          onTap: () => onItemSelected(item),
        ),
      );
    }

    return ListView(
      key: ValueKey(generation),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      children: children,
    );
  }
}

class _GroupHeader extends StatelessWidget {
  final String text;
  const _GroupHeader(this.text);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(4, 16, 4, 6),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 13,
          fontWeight: FontWeight.w700,
          color: context.textPrimary,
        ),
      ),
    );
  }
}

class _SubGroupHeader extends StatelessWidget {
  final String text;
  const _SubGroupHeader(this.text);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(4, 4, 4, 8),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w600,
          color: const Color(0xFF007AFF),
          letterSpacing: 0.2,
        ),
      ),
    );
  }
}

/// Turns a semicolon-joined list of dot points (the shape produced when
/// nested sub-bullets get folded into their parent item — see
/// backend/README.md) into a plain, comma-joined phrase for the card's
/// truncated preview line.
///
/// The detail panel renders these as real bullets, but a 2-line card
/// preview has no room for a bullet list — left as-is, the raw
/// semicolons show through as a broken-looking run-on line like "...such
/// as:; interviews and surveys...; sensor data...". Stripping the colon
/// and joining with ", " instead reads as one flowing sentence.
String _previewText(StudyItem item) {
  final text = item.plainLanguageText;
  if (!text.contains('; ')) return text;
  return text.replaceAll(':; ', ', ').replaceAll('; ', ', ');
}

class _ItemCard extends StatefulWidget {
  final StudyItem item;
  final bool isSelected;
  final VoidCallback onTap;

  const _ItemCard({
    required this.item,
    required this.isSelected,
    required this.onTap,
  });

  @override
  State<_ItemCard> createState() => _ItemCardState();
}

class _ItemCardState extends State<_ItemCard> {
  bool _pressed = false;

  // Outcome and Command Term items have a genuinely meaningful title
  // ("Outcome 1", "Analyse") — Key Knowledge/Key Skill points don't
  // (their "title" is just the first few words of a sentence), so for
  // those we lead with the plain-language preview instead of a fake
  // bolded headline.
  bool get _hasRealTitle =>
      widget.item.category == 'Outcome' ||
      widget.item.category == 'Command Term';

  @override
  Widget build(BuildContext context) {
    final item = widget.item;
    final isSelected = widget.isSelected;
    final accent = categoryColor(item.category);
    final neutral = isSelected ? context.borderStrong : context.border;
    final neutralWidth = isSelected ? 1.0 : 0.5;
    return GestureDetector(
      onTap: widget.onTap,
      // Press feedback: every pressable element should feel like it
      // heard the tap. Kept short (120ms) and transform-only so it
      // stays cheap even when scrolling through a long results list.
      onTapDown: (_) => setState(() => _pressed = true),
      onTapUp: (_) => setState(() => _pressed = false),
      onTapCancel: () => setState(() => _pressed = false),
      child: AnimatedScale(
        scale: _pressed ? 0.98 : 1.0,
        duration: const Duration(milliseconds: 120),
        curve: Curves.easeOut,
        child: Container(
          margin: const EdgeInsets.only(bottom: 6),
          // Flutter can't paint a BorderRadius on a Border with
          // per-side colors — a Stack + ClipRRect gives the same
          // rounded-corner-with-a-colored-edge look without that
          // restriction: the accent stripe is a plain colored Container
          // clipped to the same rounded rect as the card underneath it.
          child: ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: Stack(
              children: [
                AnimatedContainer(
                  duration: const Duration(milliseconds: 150),
                  curve: Curves.easeOut,
                  padding: const EdgeInsets.fromLTRB(15, 12, 12, 12),
                  decoration: BoxDecoration(
                    color: isSelected ? context.statsBg : context.cardBg,
                    border: Border.all(color: neutral, width: neutralWidth),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              _hasRealTitle ? item.title : _previewText(item),
                              maxLines: _hasRealTitle ? 1 : 2,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight:
                                    _hasRealTitle
                                        ? FontWeight.w600
                                        : FontWeight.w500,
                                color: context.textPrimary,
                                height: 1.35,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 6,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: accent.withValues(alpha: 0.12),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              item.category,
                              style: TextStyle(
                                fontSize: 10,
                                color: accent,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ),
                      if (_hasRealTitle) ...[
                        const SizedBox(height: 4),
                        Text(
                          item.plainLanguageText,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            fontSize: 12,
                            color: context.textSecondary,
                            height: 1.4,
                          ),
                        ),
                      ],
                      if (item.isCompleted) ...[
                        const SizedBox(height: 6),
                        Row(
                          children: [
                            const Icon(
                              Icons.check_circle,
                              size: 12,
                              color: Color(0xFF34C759),
                            ),
                            const SizedBox(width: 4),
                            const Text(
                              'Completed',
                              style: TextStyle(
                                fontSize: 10,
                                color: Color(0xFF34C759),
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
                // Category-colored left stripe, clipped to the same
                // rounded rect as the card via the ClipRRect above.
                Positioned(
                  left: 0,
                  top: 0,
                  bottom: 0,
                  child: Container(width: 3, color: accent),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
