# Roadmap

**Version:** 0.3.5d+patch5  
**Updated:** January 2026

## Released Versions

### ✅ v0.1.0 - Initial Release
- Basic FPS tracking
- Simple upscaling
- Core architecture

### ✅ v0.2.0 - Adaptive Systems
- Thermal management
- Power management
- Performance monitoring

### ✅ v0.3.0 - Frame Generation
- Frame interpolation
- Motion estimation
- Quality modes

### ✅ v0.3.5 - Stability & Polish
- Bug fixes (40+)
- Thread safety
- Memory leak fixes
- Error handling

### ✅ v0.4.0-alpha - GUI
- PyQt6 interface
- Real-time monitoring
- Settings panel
- Dark theme

## Current Version

### 🔄 v0.4.0-beta (In Progress)
**Target:** February 2026

#### Features:
- [ ] Configuration save/load
- [ ] Per-game profiles
- [ ] Enhanced graphs (zoom, export)
- [ ] Multiple themes
- [ ] System tray notifications
- [ ] Hotkey support

#### Improvements:
- [ ] Better error messages
- [ ] Logging to file
- [ ] Crash reporting
- [ ] Auto-update check

## Upcoming Versions

### 🔮 v0.5.0 - FSR 4 Integration
**Target:** March 2026

#### Features:
- Full FSR 4 implementation
- Advanced upscaling modes:
  - Ultra Performance
  - Performance
  - Balanced
  - Quality
  - Ultra Quality
- Sharpening controls
- Native AA option

#### Technical:
- GPU compute shaders
- Multi-GPU support
- Async frame processing
- Zero-copy pipelines

### 🔮 v0.6.0 - Advanced Features
**Target:** April 2026

#### Frame Generation v2:
- AI-based interpolation
- Motion vector refinement
- Artifact reduction
- HDR support

#### Performance:
- Lock-free algorithms
- SIMD optimizations
- Cache-friendly data structures
- Reduced memory footprint

### 🔮 v0.7.0 - Platform Expansion
**Target:** May 2026

#### Platforms:
- [ ] Linux support
- [ ] macOS support (Metal)
- [ ] Steam Deck optimization

#### Integration:
- [ ] Steam overlay
- [ ] Discord Rich Presence
- [ ] OBS plugin
- [ ] Streaming optimizations

### 🔮 v1.0.0 - Production Release
**Target:** June 2026

#### Requirements:
- ✅ All core features complete
- ✅ Comprehensive testing
- ✅ Full documentation
- ✅ Performance benchmarks
- ✅ No critical bugs
- ✅ Stable API

#### Features:
- Complete feature set
- Professional UI
- Extensive configuration
- Automatic optimization
- Profile system
- Cloud sync (optional)

## Long-Term Vision

### v1.x Series - Refinement
**2026 H2**

- Machine learning optimization
- Per-scene adaptation
- Predictive frame generation
- Advanced analytics

### v2.0 - Next Generation
**2027**

- Full AI integration
- Real-time ray tracing support
- Neural upscaling
- Latency compensation
- VR/AR support

## Feature Requests

Top community requests:

1. **Multi-monitor support** - v0.5.0
2. **HDR support** - v0.6.0
3. **Per-game profiles** - v0.4.0-beta
4. **Linux support** - v0.7.0
5. **OBS integration** - v0.7.0
6. **Mobile companion app** - v1.x

## Research & Experiments

### Active Research:
- AI-powered frame generation
- Latency reduction techniques
- Power efficiency improvements
- Memory bandwidth optimization

### Experimental Features:
- Neural sharpening
- Adaptive LOD
- Dynamic resolution scaling
- Predictive loading

## Technology Stack Evolution

### Current:
- Python 3.8+
- PyQt6 (GUI)
- NumPy (arrays)
- Threading (concurrency)

### Future:
- Rust (performance-critical paths)
- Vulkan/DirectX 12 (GPU)
- ONNX Runtime (ML inference)
- WebAssembly (web demo)

## Community Involvement

### How to Contribute:

1. **Code:** Submit PRs for features or fixes
2. **Testing:** Report bugs and test betas
3. **Documentation:** Improve docs
4. **Feedback:** Suggest features

### Priority Areas:

- Performance testing
- Cross-platform testing
- Documentation improvements
- Translation (future)

## Milestones

### Q1 2026
- [x] v0.3.5 - Stability
- [x] v0.4.0-alpha - GUI
- [ ] v0.4.0-beta - Polish

### Q2 2026
- [ ] v0.5.0 - FSR 4
- [ ] v0.6.0 - Advanced Features
- [ ] v1.0.0-rc1 - Release Candidate

### Q3 2026
- [ ] v1.0.0 - Production
- [ ] v1.1.0 - Refinement

### Q4 2026
- [ ] v1.2.0 - Platform Expansion
- [ ] v2.0.0-alpha - Next Gen Preview

## Version Numbering

Format: `MAJOR.MINOR.PATCH[-LABEL]`

- **MAJOR:** Breaking changes
- **MINOR:** New features
- **PATCH:** Bug fixes
- **LABEL:** alpha, beta, rc

Examples:
- `0.4.0-alpha` - Alpha release
- `0.4.0-beta` - Beta release
- `0.4.0` - Stable release
- `1.0.0` - Major release

## Support Timeline

| Version | Released | Support Until |
|---------|----------|---------------|
| 0.3.x | Jan 2026 | Mar 2026 |
| 0.4.x | Feb 2026 | Jun 2026 |
| 0.5.x | Mar 2026 | Jul 2026 |
| 1.0.x | Jun 2026 | Dec 2027 |

**LTS versions** will be supported longer (TBD).

---

**Questions?** Open an issue on GitHub!
**Want to help?** Check our contributing guidelines!
