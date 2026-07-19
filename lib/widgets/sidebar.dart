import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

class Sidebar extends StatelessWidget {
  final List<String> subjects;
  final String? selectedSubject;
  final ValueChanged<String> onSubjectSelected;

  const Sidebar({
    super.key,
    required this.subjects,
    required this.selectedSubject,
    required this.onSubjectSelected,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 220,
      child: Container(
        decoration: BoxDecoration(
          color: context.cardBg,
          border: Border(
            right: BorderSide(color: context.border, width: 0.5),
          ),
        ),
        child: ListView.builder(
          padding: const EdgeInsets.symmetric(vertical: 8),
          itemCount: subjects.length,
          itemBuilder: (context, index) {
            final subject = subjects[index];
            final isSelected = subject == selectedSubject;
            return GestureDetector(
              onTap: () => onSubjectSelected(subject),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: BoxDecoration(
                  color: isSelected ? context.statsBg : Colors.transparent,
                  border: isSelected
                      ? Border(
                          right: BorderSide(color: const Color(0xFF007AFF), width: 3),
                        )
                      : null,
                ),
                child: Text(
                  subject,
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                    color: isSelected ? context.textPrimary : context.textSecondary,
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
