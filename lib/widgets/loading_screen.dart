import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

/// Branded loading state shown in the body while the study dataset
/// (a ~1.5MB bundled JSON asset) is being read and parsed on startup.
/// The app name already appears in the persistent header above this,
/// so this only repeats the logo mark, not the "VCE Study Tracker"
/// text — a startup load is a rare, one-time event (not something a
/// user sees tens of times a day), so it's a reasonable place to spend
/// a bit of polish rather than the terse treatment given to frequent
/// actions, without being redundant with the header.
class LoadingScreen extends StatelessWidget {
  const LoadingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF007AFF), Color(0xFF5AC8FA)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(14),
            ),
            child: const Center(
              child: Text(
                'V',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                  fontSize: 28,
                ),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Loading study content…',
            style: TextStyle(fontSize: 12, color: context.textSecondary),
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: 22,
            height: 22,
            child: CircularProgressIndicator(
              strokeWidth: 2.4,
              valueColor: const AlwaysStoppedAnimation(Color(0xFF007AFF)),
              backgroundColor: context.statsBg,
            ),
          ),
        ],
      ),
    );
  }
}
