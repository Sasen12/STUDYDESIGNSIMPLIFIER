import 'package:flutter/material.dart';
import '../models/study_item.dart';
import '../data/study_data_repository.dart';
import '../widgets/sidebar.dart';
import '../widgets/search_bar_widget.dart';
import '../widgets/category_tabs.dart';
import '../widgets/results_list.dart';
import '../widgets/detail_panel.dart';
import '../theme/theme_model.dart';
import '../theme/app_colors.dart';
import '../widgets/settings_slideout.dart';
import '../widgets/loading_screen.dart';

/// Main screen for the VCE Study Tracker.
///
/// Implements a three-column macOS-style layout:
///   1. Sidebar — subject list (fixed 220 px).
///   2. Centre — search bar, category pills, scrollable result cards,
///      and a footer showing the result count.
///   3. Detail panel — shows the selected item's official text and
///      plain-language explanation (35 % of window width).
///
/// State is managed with plain [setState]; filtering is done entirely
/// in memory via [_applyFilters].  No backend or persistence layer yet.
class HomeScreen extends StatefulWidget {
  final ThemeModel themeModel;

  const HomeScreen({super.key, required this.themeModel});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _searchController = TextEditingController();
  final _repository = StudyDataRepository();

  bool _loading = true;
  String? _loadError;

  String? _selectedSubject;
  String? _selectedCategory;
  StudyItem? _selectedItem;
  List<StudyItem> _items = [];
  List<StudyItem> _filteredItems = [];

  // Populated from the loaded dataset once it arrives — the app no
  // longer hardcodes which subjects exist, since that's driven entirely
  // by whatever source files the backend/ pipeline was run against.
  List<String> _subjects = [];

  // Category filter options.  'All' shows every category for the active subject.
  final _categories = [
    'All',
    'Outcome',
    'Key Knowledge',
    'Key Skill',
    'Command Term',
  ];

  @override
  void initState() {
    super.initState();
    _loadItems();
  }

  Future<void> _loadItems() async {
    try {
      final items = await _repository.loadItems();
      final subjects = items.map((i) => i.subject).toSet().toList()..sort();
      setState(() {
        _items = items;
        _subjects = subjects;
        _selectedSubject = subjects.isNotEmpty ? subjects.first : null;
        _selectedCategory = _categories[0];
        _loading = false;
      });
      _applyFilters();
    } catch (e) {
      setState(() {
        _loadError = e.toString();
        _loading = false;
      });
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  /// Re-runs the in-memory filter against [_items] and writes the result
  /// into [_filteredItems].  Three axes are ANDed together:
  ///   1. Subject match (sidebar selection).
  ///   2. Category match (pills — skips when 'All').
  ///   3. Full-text search across title, official text and plain language.
  int _filterGeneration = 0;

  void _applyFilters() {
    setState(() {
      _filterGeneration++;
      _filteredItems =
          _items.where((item) {
            if (_selectedSubject != null && item.subject != _selectedSubject) {
              return false;
            }
            if (_selectedCategory != null &&
                _selectedCategory != 'All' &&
                item.category != _selectedCategory) {
              return false;
            }
            if (_searchController.text.isNotEmpty) {
              final query = _searchController.text.toLowerCase();
              // Search across all three text fields for broad matches.
              if (!item.title.toLowerCase().contains(query) &&
                  !item.officialText.toLowerCase().contains(query) &&
                  !item.plainLanguageText.toLowerCase().contains(query)) {
                return false;
              }
            }
            return true;
          }).toList();
    });
  }

  /// Count of marked-complete items shown in the toolbar stat chip.
  int get _completedCount => _items.where((i) => i.isCompleted).length;

  void _onSubjectSelected(String subject) {
    setState(() {
      _selectedSubject = subject;
      _selectedItem = null; // clear detail panel when switching subject
    });
    _applyFilters();
  }

  void _onCategorySelected(String category) {
    setState(() {
      _selectedCategory = category;
    });
    _applyFilters();
  }

  void _onSearchChanged(String query) {
    _applyFilters();
  }

  void _onItemSelected(StudyItem item) {
    setState(() {
      _selectedItem = item;
    });
  }

  void _onCompletionChanged(bool completed) {
    if (_selectedItem == null) return;
    setState(() {
      _selectedItem!.isCompleted = completed;
    });
  }

  /// Opens the settings slideout panel from the right edge.
  void _openSettings() {
    SettingsSlideout.show(context, widget.themeModel);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: context.surfaceBg,
      body: SafeArea(
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.fromLTRB(20, 12, 20, 10),
              decoration: BoxDecoration(
                color: context.cardBg,
                border: Border(
                  bottom: BorderSide(color: context.border, width: 0.5),
                ),
              ),
              child: Row(
                children: [
                  Container(
                    width: 32,
                    height: 32,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF007AFF), Color(0xFF5AC8FA)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Center(
                      child: Text(
                        'V',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w700,
                          fontSize: 16,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Text(
                    'VCE Study Tracker',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: context.textPrimary,
                    ),
                  ),
                  const Spacer(),
                  _buildStatChip(
                    context,
                    Icons.check_circle_outline,
                    '$_completedCount / ${_items.length}',
                  ),
                  const SizedBox(width: 8),
                  GestureDetector(
                    onTap: _openSettings,
                    child: Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        color: context.statsBg,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: context.borderStrong,
                          width: 0.5,
                        ),
                      ),
                      child: Icon(
                        Icons.settings,
                        size: 16,
                        color: context.textSecondary,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            Expanded(
              // A startup load (or its failure) is a one-time event, so a
              // slightly longer, gentle crossfade here is appropriate —
              // unlike the results list, which updates on every keystroke
              // and deliberately isn't animated.
              child: AnimatedSwitcher(
                duration: const Duration(milliseconds: 300),
                switchInCurve: Curves.easeOut,
                switchOutCurve: Curves.easeIn,
                transitionBuilder:
                    (child, animation) =>
                        FadeTransition(opacity: animation, child: child),
                child:
                    _loading
                        ? const LoadingScreen(key: ValueKey('loading'))
                        : _loadError != null
                        ? Center(
                          key: const ValueKey('error'),
                          child: Text(
                            'Could not load study data:\n$_loadError',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: context.textSecondary),
                          ),
                        )
                        : Row(
                          key: const ValueKey('content'),
                          // Without this, the detail panel — which has
                          // no Expanded/flex child of its own to force
                          // it to fill height, unlike the center list
                          // column — shrink-wraps to its content height
                          // and sits centered in the Row's cross axis,
                          // leaving grey gaps above and below it.
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Sidebar(
                              subjects: _subjects,
                              selectedSubject: _selectedSubject,
                              onSubjectSelected: _onSubjectSelected,
                            ),
                            Expanded(
                              child: Container(
                                decoration: BoxDecoration(
                                  color: context.cardBg,
                                  border: Border(
                                    right: BorderSide(
                                      color: context.borderStrong,
                                      width: 0.5,
                                    ),
                                  ),
                                ),
                                child: Column(
                                  children: [
                                    SearchBarWidget(
                                      controller: _searchController,
                                      onChanged: _onSearchChanged,
                                    ),
                                    CategoryTabs(
                                      categories: _categories,
                                      selectedCategory: _selectedCategory,
                                      onCategorySelected: _onCategorySelected,
                                    ),
                                    Padding(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 16,
                                      ),
                                      child: Divider(
                                        height: 1,
                                        color: context.border,
                                      ),
                                    ),
                                    Expanded(
                                      child: ResultsList(
                                        items: _filteredItems,
                                        selectedItem: _selectedItem,
                                        onItemSelected: _onItemSelected,
                                        generation: _filterGeneration,
                                      ),
                                    ),
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 16,
                                        vertical: 6,
                                      ),
                                      decoration: BoxDecoration(
                                        color: context.cardBg,
                                        border: Border(
                                          top: BorderSide(
                                            color: context.border,
                                            width: 0.5,
                                          ),
                                        ),
                                      ),
                                      child: Row(
                                        children: [
                                          Icon(
                                            Icons.search,
                                            size: 12,
                                            color: context.textSecondary,
                                          ),
                                          const SizedBox(width: 4),
                                          Text(
                                            '${_filteredItems.length} result${_filteredItems.length == 1 ? '' : 's'}',
                                            style: TextStyle(
                                              fontSize: 11,
                                              color: context.textSecondary,
                                            ),
                                          ),
                                          if (_searchController
                                              .text
                                              .isNotEmpty) ...[
                                            const SizedBox(width: 8),
                                            GestureDetector(
                                              onTap: () {
                                                _searchController.clear();
                                                _applyFilters();
                                              },
                                              child: Text(
                                                'Clear',
                                                style: TextStyle(
                                                  fontSize: 11,
                                                  color: context.textPrimary,
                                                  fontWeight: FontWeight.w600,
                                                ),
                                              ),
                                            ),
                                          ],
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                            SizedBox(
                              width: MediaQuery.of(context).size.width * 0.35,
                              child: DetailPanel(
                                item: _selectedItem,
                                onCompletionChanged: _onCompletionChanged,
                              ),
                            ),
                          ],
                        ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Small stat badge shown in the toolbar (e.g. "5 / 15" completion count).
  Widget _buildStatChip(BuildContext context, IconData icon, String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: context.statsBg,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: context.borderStrong, width: 0.5),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: const Color(0xFF34C759)),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: context.textPrimary,
            ),
          ),
        ],
      ),
    );
  }
}
