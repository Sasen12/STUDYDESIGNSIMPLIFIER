import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;

import '../models/study_item.dart';

/// Loads the generated study item dataset (assets/data/study_items.json,
/// produced by the backend/ ingestion pipeline from real VCAA study
/// design files) as a bundled asset.
class StudyDataRepository {
  static const _assetPath = 'assets/data/study_items.json';

  Future<List<StudyItem>> loadItems() async {
    final raw = await rootBundle.loadString(_assetPath);
    final decoded = jsonDecode(raw) as List<dynamic>;
    return decoded
        .map((json) => StudyItem.fromJson(json as Map<String, dynamic>))
        .toList();
  }
}
