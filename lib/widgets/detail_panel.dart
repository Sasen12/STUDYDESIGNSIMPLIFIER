import 'package:flutter/material.dart';
import '../models/study_item.dart';
import '../theme/app_colors.dart';

class DetailPanel extends StatelessWidget {
  final StudyItem? item;
  final ValueChanged<bool> onCompletionChanged;

  const DetailPanel({
    super.key,
    required this.item,
    required this.onCompletionChanged,
  });

  @override
  Widget build(BuildContext context) {
    if (item == null) {
      return Container(
        decoration: BoxDecoration(color: context.cardBg),
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Text(
              'Select a study item to view details',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: context.textSecondary),
            ),
          ),
        ),
      );
    }

    final studyItem = item!;

    return Container(
      decoration: BoxDecoration(color: context.cardBg),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (studyItem.unit != null || studyItem.areaOfStudy != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Text(
                  [
                    if (studyItem.unit != null) studyItem.unit!,
                    if (studyItem.areaOfStudy != null) studyItem.areaOfStudy!,
                    if (studyItem.outcome != null) studyItem.outcome!,
                  ].join(' > '),
                  style: TextStyle(
                    fontSize: 11,
                    color: const Color(0xFF007AFF),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Text(
                    studyItem.title,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                      color: context.textPrimary,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: context.statsBg,
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: context.borderStrong, width: 0.5),
                  ),
                  child: Text(
                    studyItem.category,
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w500,
                      color: context.textSecondary,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              studyItem.subject,
              style: TextStyle(fontSize: 12, color: context.textSecondary),
            ),
            const SizedBox(height: 20),
            Text(
              'Official Text',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: context.textSecondary,
                letterSpacing: 0.5,
              ),
            ),
            const SizedBox(height: 6),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: context.surfaceBg,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: context.border, width: 0.5),
              ),
              child: Text(
                studyItem.officialText,
                style: TextStyle(
                  fontSize: 13,
                  color: context.textPrimary,
                  height: 1.6,
                ),
              ),
            ),
            const SizedBox(height: 20),
            Text(
              'Plain Language',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: const Color(0xFF34C759),
                letterSpacing: 0.5,
              ),
            ),
            const SizedBox(height: 6),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFE8F8E8),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: const Color(0xFF34C759).withValues(alpha: 0.3), width: 0.5),
              ),
              child: Text(
                studyItem.plainLanguageText,
                style: TextStyle(
                  fontSize: 13,
                  color: const Color(0xFF1C1C1E),
                  height: 1.6,
                ),
              ),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                SizedBox(
                  height: 32,
                  child: ElevatedButton.icon(
                    onPressed: () => onCompletionChanged(!studyItem.isCompleted),
                    icon: Icon(
                      studyItem.isCompleted ? Icons.undo : Icons.check_circle_outline,
                      size: 16,
                    ),
                    label: Text(
                      studyItem.isCompleted ? 'Mark Incomplete' : 'Mark Complete',
                      style: const TextStyle(fontSize: 12),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: studyItem.isCompleted
                          ? context.statsBg
                          : const Color(0xFF007AFF),
                      foregroundColor: studyItem.isCompleted
                          ? context.textPrimary
                          : Colors.white,
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                        side: studyItem.isCompleted
                            ? BorderSide(color: context.borderStrong, width: 0.5)
                            : BorderSide.none,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
