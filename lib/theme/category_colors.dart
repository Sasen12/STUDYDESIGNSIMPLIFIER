import 'package:flutter/material.dart';

/// One accent color per StudyItem category, shared by the results list
/// (left border stripe + tinted badge) and the detail panel (badge),
/// so the same category always reads as the same color everywhere in
/// the app. Fixed colors rather than theme-derived ones — they're
/// meant to stay visually distinct and legible in both light and dark
/// mode, not shift with the surrounding surface.
Color categoryColor(String category) {
  switch (category) {
    case 'Outcome':
      return const Color(0xFF007AFF); // blue
    case 'Key Knowledge':
      return const Color(0xFFAF52DE); // purple
    case 'Key Skill':
      return const Color(0xFFFF9500); // orange
    case 'Command Term':
      return const Color(0xFF30B0C7); // teal
    default:
      return const Color(0xFF8E8E93); // grey fallback
  }
}
