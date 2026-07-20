import 'package:flutter_test/flutter_test.dart';
import 'package:vce_study_tracker/main.dart';
import 'package:vce_study_tracker/theme/theme_model.dart';

void main() {
  testWidgets('App renders smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(VCEStudyTrackerApp(themeModel: ThemeModel()));
    expect(find.text('VCE Study Tracker'), findsOneWidget);
  });
}
