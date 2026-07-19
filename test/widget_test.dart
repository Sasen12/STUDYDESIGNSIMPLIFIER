import 'package:flutter_test/flutter_test.dart';
import 'package:vce_study_tracker/main.dart';

void main() {
  testWidgets('App renders smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const VCEStudyTrackerApp());
    expect(find.text('VCE Study Tracker'), findsOneWidget);
  });
}
