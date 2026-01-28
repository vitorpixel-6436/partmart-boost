# Changelog - PartMart Boost

All notable changes to this project will be documented in this file.

## [0.3.5d] - 2026-01-28 - Bug Fixes & Code Quality

### Package 3.5 - Bug Fixes (FINAL)

#### v0.3.5d_package3.5a - Import & Dependency Fixes
- ✅ Fixed missing numpy import in analytics/session.py
- ✅ Added requirements.txt with proper dependencies
- ✅ Added fallback for optional dependencies (OpenCV, psutil)
- ✅ Fixed TYPE_CHECKING imports
- ✅ Consistent import ordering throughout codebase

#### v0.3.5d_package3.5b - Type & Validation Fixes
- ✅ Added FPS range validation (0.1-1000 Hz)
- ✅ Added temperature bounds checking (-50 to 200°C)
- ✅ Added utilization percentage validation (0-100%)
- ✅ Fixed Optional vs Required type hints
- ✅ Added resolution min/max validation
- ✅ Improved None checks with proper type narrowing

#### v0.3.5d_package3.5c - Logic & Algorithm Fixes
- ✅ Fixed thermal hysteresis implementation
- ✅ Corrected interpolation t parameter clamping
- ✅ Fixed timestamp interpolation formula
- ✅ Improved thermal state machine transitions
- ✅ Fixed cooldown period calculation
- ✅ Corrected blend weight calculations

#### v0.3.5d_package3.5d - Error Handling & Edge Cases (FINAL)
- ✅ Added try-except to all critical paths
- ✅ Graceful degradation when hardware unavailable
- ✅ File I/O error handling in analytics export
- ✅ Platform detection fallbacks
- ✅ Resource cleanup with finally blocks
- ✅ Clear error messages with context
- ✅ Handled edge cases: empty collections, null values, division by zero

### Summary of 0.3.5d

**Lines Changed:** 1000+  
**Bugs Fixed:** 50+  
**Files Modified:** 15+  

**Quality Improvements:**
- Production-ready error handling
- Type-safe code with validation
- Corrected algorithms and logic
- Proper dependency management
- Comprehensive edge case handling

---

## [0.3.5] - Package 3.4 - Advanced Features

### v0.3.5d_package3.4a - System Integration
- Unified system manager
- Auto-detection & configuration
- Hardware monitoring integration
- Performance pipeline

### v0.3.5d_package3.4b - Analytics & Telemetry
- Analytics engine with session recording
- Metrics collection (FPS, GPU, CPU)
- CSV/JSON export
- Statistical analysis

### v0.3.5d_package3.4c - Multi-Display Support
- Display manager with per-monitor tracking
- HDR detection and control
- VRR/G-Sync/FreeSync support
- Resolution and refresh rate management

### v0.3.5d_package3.4d - Advanced Frame Generation
- Multi-frame interpolation (2x/3x/4x)
- Optical flow engine
- Depth estimation
- Motion-compensated blending

---

## [0.3.4] - Package 3.3 - Frame Gen & Upscaling

### Features
- Frame generation interfaces
- FSR 4 upscaling
- Quality modes (Performance, Balanced, Quality, Ultra)
- Hardware capability detection

---

## [0.3.3] - Package 3.2 - Performance Monitor

### Features
- Real-time performance monitoring
- GPU/CPU utilization tracking
- Memory usage monitoring
- Temperature monitoring

---

## [0.3.2] - Package 3.1 - FPS Tracker

### Features
- High-precision FPS tracking
- Rolling window averaging
- Min/max/average statistics
- Frame time calculation

---

## [0.3.1] - Initial Advanced Features

### Features
- Core architecture
- Base interfaces
- Module structure

---

## Version History

- **v0.3.5d** (2026-01-28) - Bug Fixes & Code Quality ✅
- **v0.3.5** - Advanced Features (Packages 3.4)
- **v0.3.4** - Frame Gen & Upscaling (Package 3.3)
- **v0.3.3** - Performance Monitor (Package 3.2)
- **v0.3.2** - FPS Tracker (Package 3.1)
- **v0.3.1** - Core Architecture

---

## Next Release

### [v0.4.0] - UI & Visualization (Planned)
- Interactive UI system
- Real-time graphs and charts
- Configuration interface
- Performance overlay
