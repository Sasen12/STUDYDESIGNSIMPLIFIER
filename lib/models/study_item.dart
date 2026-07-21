/// One row of the study content dataset — an Outcome, Key Knowledge
/// point, Key Skill point, or Command Term definition.
class StudyItem {
  final String id;
  final String subject;
  final String title;
  final String category;
  final String officialText;
  final String plainLanguageText;
  final String? unit;
  final String? areaOfStudy;
  final String? outcome;
  bool isCompleted;

  StudyItem({
    required this.id,
    required this.subject,
    required this.title,
    required this.category,
    required this.officialText,
    required this.plainLanguageText,
    this.unit,
    this.areaOfStudy,
    this.outcome,
    this.isCompleted = false,
  });

  /// Inputs: `json` — one decoded item from study_items.json.
  /// Outputs: parsed `StudyItem`.
  factory StudyItem.fromJson(Map<String, dynamic> json) {
    return StudyItem(
      id: json['id'] as String,
      subject: json['subject'] as String,
      title: json['title'] as String,
      category: json['category'] as String,
      officialText: json['officialText'] as String,
      plainLanguageText: json['plainLanguageText'] as String,
      unit: json['unit'] as String?,
      areaOfStudy: json['areaOfStudy'] as String?,
      outcome: json['outcome'] as String?,
      isCompleted: json['isCompleted'] as bool? ?? false,
    );
  }
}
