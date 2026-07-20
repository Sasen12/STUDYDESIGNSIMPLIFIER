import 'package:flutter/foundation.dart'
    show defaultTargetPlatform, TargetPlatform;
import 'package:flutter/material.dart';
import '../data/preferences_repository.dart';
import 'app_colors.dart';

// ".AppleSystemUIFont" is a magic value Flutter/Skia resolves directly
// to the real native system font (San Francisco) on iOS/macOS, with no
// font files to bundle. defaultTargetPlatform (not dart:io Platform) is
// used here since dart:io isn't available on web — this keeps the rest
// of the app's styling identical across platforms and only swaps the
// font where a matching system face actually exists.
String? get _systemFontFamily {
  switch (defaultTargetPlatform) {
    case TargetPlatform.macOS:
    case TargetPlatform.iOS:
      return '.AppleSystemUIFont';
    default:
      return null;
  }
}

class ThemeModel extends ChangeNotifier {
  final PreferencesRepository _preferences;

  ThemeModel({PreferencesRepository? preferences})
    : _preferences = preferences ?? PreferencesRepository();

  bool _isDark = false;

  bool get isDark => _isDark;

  ThemeData get themeData {
    final base = _isDark ? ThemeData.dark() : ThemeData.light();
    final colors = _isDark ? AppColors.dark : AppColors.light;
    final systemFont = _systemFontFamily;
    return base.copyWith(
      textTheme:
          systemFont == null
              ? base.textTheme
              : base.textTheme.apply(fontFamily: systemFont),
      primaryTextTheme:
          systemFont == null
              ? base.primaryTextTheme
              : base.primaryTextTheme.apply(fontFamily: systemFont),
      extensions: [colors],
      // Thin, rounded, hover/scroll-revealed overlay scrollbars —
      // Windows/GTK-style permanently-visible thick scrollbars are one
      // of the more obviously "not Mac" details a desktop app can have.
      scrollbarTheme: ScrollbarThemeData(
        thumbColor: WidgetStatePropertyAll(
          colors.textSecondary.withValues(alpha: 0.5),
        ),
        radius: const Radius.circular(8),
        thickness: const WidgetStatePropertyAll(6),
        mainAxisMargin: 4,
        crossAxisMargin: 2,
      ),
    );
  }

  /// Loads the persisted dark-mode preference. Call once, before the
  /// first frame — see main.dart — so the app never flashes the wrong
  /// theme and then flips to the saved one.
  Future<void> load() async {
    _isDark = await _preferences.loadDarkMode();
    notifyListeners();
  }

  void toggleTheme() {
    _isDark = !_isDark;
    notifyListeners();
    _preferences.saveDarkMode(_isDark);
  }
}
