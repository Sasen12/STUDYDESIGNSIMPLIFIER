import 'package:flutter/material.dart';
import '../models/study_item.dart';
import '../theme/app_colors.dart';

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

    return ListView.builder(
      key: ValueKey(generation),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final item = items[index];
        final isSelected = item.id == selectedItem?.id;
        return GestureDetector(
          onTap: () => onItemSelected(item),
          child: Container(
            margin: const EdgeInsets.only(bottom: 6),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: isSelected ? context.statsBg : context.cardBg,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(
                color: isSelected ? context.borderStrong : context.border,
                width: isSelected ? 1 : 0.5,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        item.title,
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: context.textPrimary,
                        ),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: context.surfaceBg,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        item.category,
                        style: TextStyle(
                          fontSize: 10,
                          color: context.textSecondary,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
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
                if (item.isCompleted) ...[
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      Icon(Icons.check_circle, size: 12, color: const Color(0xFF34C759)),
                      const SizedBox(width: 4),
                      Text(
                        'Completed',
                        style: TextStyle(
                          fontSize: 10,
                          color: const Color(0xFF34C759),
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }
}
