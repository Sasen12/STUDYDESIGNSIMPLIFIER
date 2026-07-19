import 'package:flutter/material.dart';
import 'theme/theme_model.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const VCEStudyTrackerApp());
}

class VCEStudyTrackerApp extends StatefulWidget {
  const VCEStudyTrackerApp({super.key});

  @override
  State<VCEStudyTrackerApp> createState() => _VCEStudyTrackerAppState();
}

class _VCEStudyTrackerAppState extends State<VCEStudyTrackerApp> {
  final _themeModel = ThemeModel();

  @override
  void dispose() {
    _themeModel.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: _themeModel,
      builder: (context, _) {
        return MaterialApp(
          title: 'VCE Study Tracker',
          debugShowCheckedModeBanner: false,
          theme: _themeModel.themeData,
          home: HomeScreen(themeModel: _themeModel),
        );
      },
    );
  }
}
