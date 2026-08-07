import 'package:flutter_test/flutter_test.dart';
import 'package:vce_unpacked/main.dart';
import 'package:vce_unpacked/theme/theme_model.dart';

void main() {
  testWidgets('App renders smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(VCEUnpackedApp(themeModel: ThemeModel()));
    expect(find.text('VCE Unpacked'), findsOneWidget);
  });
}
