# Changelog

All notable changes to PartMart Boost will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Planned
- Configuration save/load
- Per-game profiles
- Enhanced visualization
- Multiple themes

## [0.3.5d+patch5] - 2026-01-28

### Changed
- Cleaned up repository structure
- Moved documentation to `docs/` folder
- Consolidated duplicate files
- Removed old changelogs (history preserved in git)

### Removed
- `CHANGELOG_v0.3.5c.md`
- `CHANGELOG_v0.3.5c_hotfix.md`
- `CHANGELOG_v0.3.5c_hotfix2.md`
- `CHANGELOG_v0.3.5d.md`
- `CLEANUP_REPORT.md`
- `requirements-lock.txt`
- `INSTALL.md` (merged into README)
- `SECURITY_QUICKSTART.md` (merged into SECURITY.md)

## [0.3.5d+patch4] - 2026-01-28

### Fixed
- launcher.bat encoding issues (removed emoji)
- Missing FSR4 module causing import errors
- GUI launch failures on Python 3.14

### Added
- `launcher_simple.bat` for easier Windows launch
- `src/fsr4/__init__.py` placeholder module
- Better error handling in GUI

## [0.4.0-alpha] - 2026-01-28

### Added
- Full PyQt6 GUI interface
- Dashboard with real-time FPS graph
- Performance monitoring tab
- Settings panel with presets
- Logs viewer
- Dark theme
- Menu system
- Status bar

### Changed
- Main launcher now starts GUI by default
- CLI mode moved to `main_cli.py`

## [0.3.5d] - 2026-01-27

### Added
- Package 3.6a - Deep Bug Hunt
  - Part 1: FPS & Performance fixes
  - Part 2: Frame Processing improvements
  - Part 3: Thermal & Power Management
  - Part 4: Resource & State Management
- Comprehensive test suite
- Resource manager with deadlock prevention
- Starvation prevention with aging

### Fixed
- 40+ critical bugs across all modules
- Thread safety issues (100% coverage)
- Memory leaks and buffer overflows
- Race conditions
- Data integrity issues
- Thermal oscillation
- Power state synchronization

## [0.3.5c] - 2026-01-26

### Added
- Advanced thermal management
- Power management system
- System integration module
- Performance monitoring

### Changed
- Improved frame generation quality
- Better upscaling algorithms
- Enhanced error handling

### Fixed
- Frame timing issues
- Memory alignment problems
- Aspect ratio preservation

## [0.3.0] - 2026-01-25

### Added
- Frame generation system
- Motion estimation
- Quality modes (Performance/Balanced/Quality)
- Frame interpolation

## [0.2.0] - 2026-01-24

### Added
- Thermal management
- Power management
- Adaptive systems
- Performance monitoring

## [0.1.0] - 2026-01-23

### Added
- Initial release
- Basic FPS tracking
- Simple upscaling
- Core architecture
- CLI interface

---

**Legend:**
- `Added` - New features
- `Changed` - Changes to existing features
- `Deprecated` - Soon-to-be removed features
- `Removed` - Removed features
- `Fixed` - Bug fixes
- `Security` - Security improvements
