import 'package:flutter/material.dart';
import 'app_colors.dart';

class ThemeModel extends ChangeNotifier {
  bool _isDark = false;

  bool get isDark => _isDark;

  ThemeData get themeData {
    final base = _isDark ? ThemeData.dark() : ThemeData.light();
    return base.copyWith(
      extensions: [_isDark ? AppColors.dark : AppColors.light],
    );
  }

  void toggleTheme() {
    _isDark = !_isDark;
    notifyListeners();
  }
}
