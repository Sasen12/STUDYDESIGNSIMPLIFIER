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
}
