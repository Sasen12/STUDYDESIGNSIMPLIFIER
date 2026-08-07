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

  runApp(VCEUnpackedApp(themeModel: themeModel));
}

class VCEUnpackedApp extends StatefulWidget {
  final ThemeModel themeModel;

  const VCEUnpackedApp({super.key, required this.themeModel});

  @override
  State<VCEUnpackedApp> createState() => _VCEUnpackedAppState();
}

class _VCEUnpackedAppState extends State<VCEUnpackedApp> {
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
          title: 'VCE Unpacked',
          debugShowCheckedModeBanner: false,
          theme: widget.themeModel.themeData,
          home: HomeScreen(themeModel: widget.themeModel),
        );
      },
    );
  }
}
