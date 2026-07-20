import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

/// A macOS-style segmented control (like System Settings' view
/// switcher, or Mail's inbox/flagged/unread toggle) — one connected
/// track with a single sliding selection indicator, rather than a row
/// of separate pill buttons. This is the app's one deliberately
/// "native Mac" signature element: everything else in the redesign is
/// quieter supporting detail (selection capsules, system font, thin
/// scrollbars), but the segmented control is the piece a Mac user
/// would recognise on sight.
class CategoryTabs extends StatelessWidget {
  final List<String> categories;
  final String? selectedCategory;
  final ValueChanged<String> onCategorySelected;

  const CategoryTabs({
    super.key,
    required this.categories,
    required this.selectedCategory,
    required this.onCategorySelected,
  });

  @override
  Widget build(BuildContext context) {
    final selectedIndex =
        selectedCategory == null
            ? 0
            : categories
                .indexOf(selectedCategory!)
                .clamp(0, categories.length - 1);

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
      child: Container(
        height: 28,
        padding: const EdgeInsets.all(2),
        decoration: BoxDecoration(
          color: context.surfaceBg,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: context.border, width: 0.5),
        ),
        // Measured *inside* the padding, not outside it — segmentWidth
        // must match the width Stack/Row actually receive as children
        // of this padded Container, or the Row's summed segment widths
        // overflow the real available space by exactly the padding
        // amount (found by a layout test, not visually obvious at a
        // glance).
        child: LayoutBuilder(
          builder: (context, constraints) {
            final segmentWidth = constraints.maxWidth / categories.length;
            return Stack(
              children: [
                // The sliding selection indicator sits behind the
                // labels and animates its position — this is what
                // makes it read as one connected control rather than a
                // row of buttons.
                AnimatedPositioned(
                  duration: const Duration(milliseconds: 180),
                  curve: Curves.easeOut,
                  left: segmentWidth * selectedIndex,
                  width: segmentWidth,
                  top: 0,
                  bottom: 0,
                  child: Container(
                    margin: const EdgeInsets.symmetric(horizontal: 1),
                    decoration: BoxDecoration(
                      color: context.cardBg,
                      borderRadius: BorderRadius.circular(6),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withValues(alpha: 0.08),
                          blurRadius: 3,
                          offset: const Offset(0, 1),
                        ),
                      ],
                    ),
                  ),
                ),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children:
                      categories.map((category) {
                        final isSelected = category == selectedCategory;
                        return SizedBox(
                          width: segmentWidth,
                          child: GestureDetector(
                            onTap: () => onCategorySelected(category),
                            behavior: HitTestBehavior.opaque,
                            child: Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 4,
                              ),
                              // "Command Term" is long enough to
                              // overflow a narrow segment at some panel
                              // widths — FittedBox scales the label
                              // down to fit instead, which reads better
                              // than an ellipsis on a 1-2 word label.
                              child: Center(
                                child: FittedBox(
                                  fit: BoxFit.scaleDown,
                                  child: AnimatedDefaultTextStyle(
                                    duration: const Duration(milliseconds: 150),
                                    curve: Curves.easeOut,
                                    style: TextStyle(
                                      fontSize: 11,
                                      fontWeight:
                                          isSelected
                                              ? FontWeight.w600
                                              : FontWeight.w500,
                                      color:
                                          isSelected
                                              ? context.textPrimary
                                              : context.textSecondary,
                                    ),
                                    child: Text(category, maxLines: 1),
                                  ),
                                ),
                              ),
                            ),
                          ),
                        );
                      }).toList(),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}
