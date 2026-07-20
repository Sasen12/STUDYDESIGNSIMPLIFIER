import 'package:flutter/material.dart';
import 'theme/theme_model.dart';
import 'screens/home_screen.dart';

Future<void> main() async {
  // Needed before using SharedPreferences (inside ThemeModel.load())
  // this early, ahead of runApp.
  WidgetsFlutterBinding.ensureInitialized();

  final themeModel = ThemeModel();
  // Awaited here rather than loaded lazily inside the widget tree, so
  // the app never flashes light mode and then flips to a saved dark
  // preference on the first frame.
  await themeModel.load();

  runApp(VCEStudyTrackerApp(themeModel: themeModel));
}

class VCEStudyTrackerApp extends StatefulWidget {
  final ThemeModel themeModel;

  const VCEStudyTrackerApp({super.key, required this.themeModel});

  @override
  State<VCEStudyTrackerApp> createState() => _VCEStudyTrackerAppState();
}

class _VCEStudyTrackerAppState extends State<VCEStudyTrackerApp> {
  @override
  void dispose() {
    widget.themeModel.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: widget.themeModel,
      builder: (context, _) {
        return MaterialApp(
          title: 'VCE Study Tracker',
          debugShowCheckedModeBanner: false,
          theme: widget.themeModel.themeData,
          home: HomeScreen(themeModel: widget.themeModel),
        );
      },
    );
  }
}
