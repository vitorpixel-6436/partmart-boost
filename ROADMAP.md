# 🗃️ Roadmap - PartMart Boost v0.1 → v1.0

## 💫 6-Week Development Plan

**Start**: January 28, 2026  
**Target v1.0 Release**: March 11, 2026  
**Current Version**: v0.1-alpha (planning phase)

---

## WEEK 1-2: MVP (CRITICAL PATH)

**Goal**: Functional GPU optimizer with 1-click boost + overlay

### Phase 1.1: UI Foundation (Day 1-2)
- [ ] PyQt6 setup + QSS dark theme (PartMart colors)
- [ ] Main window layout
- [ ] System info display (GPU, RAM, CPU)
- [ ] Quick Boost button
- [ ] Progress bar + status display

**Deliverable**: Skeleton UI running

### Phase 1.2: GPU Control - NVIDIA (Day 3-5)
- [ ] pynvml initialization + GPU detection
- [ ] Voltage curve control via nvapi64.dll
- [ ] Undervolt: -50mV to -150mV (safe range)
- [ ] Memory OC: +200MHz to +500MHz (conservative start: +200MHz)
- [ ] Fan curve optimization
- [ ] Settings backup before changes
- [ ] Revert to stock function
- [ ] Unit tests (>85% coverage)

**Deliverable**: NVIDIA GPU optimizer working

### Phase 1.3: RAM Optimization (Day 6-7)
- [ ] XMP detection via WMI
- [ ] Ryzen Master SDK integration (AMD platform)
- [ ] Safe XMP enable (check if disabled)
- [ ] EmptyStandbyList wrapper (RAM cleaner)
- [ ] Standby list size monitoring
- [ ] Unit tests

**Deliverable**: RAM XMP working, standby cleaner integrated

### Phase 1.4: Quick Boost Logic (Day 8-9)
- [ ] Combine GPU + RAM + cleanup in one function
- [ ] Sequence: GPU undervolt → memory OC → XMP → clean RAM → test
- [ ] FurMark stability test (30 seconds mandatory)
- [ ] Temperature cap: if >85°C → auto-revert
- [ ] Auto-revert on any failure
- [ ] Results display (FPS estimate, temperature, before/after)
- [ ] Unit + integration tests

**Deliverable**: One-click boost functional end-to-end

### Phase 1.5: RTSS Overlay (Day 10-11)
- [ ] RivaTuner Statistics Server integration
- [ ] FPS counter (in-game)
- [ ] GPU/CPU temperature display
- [ ] GPU load percentage
- [ ] Memory usage
- [ ] Custom overlay styling (PartMart branding)
- [ ] Toggle overlay on/off
- [ ] Integration test

**Deliverable**: Realtime overlay in-game working

### Phase 1.6: Testing & Polish (Day 12-14)
- [ ] Comprehensive unit tests (pytest, coverage >85%)
- [ ] Manual testing on real RTX 3060 hardware
- [ ] Bug fixes + crash investigation
- [ ] Code quality (pylint, black)
- [ ] Error handling + logging
- [ ] Performance profiling
- [ ] Release candidate build

**Deliverable**: `partmart-boost-v0.1-mvp.exe`

**Exit Criteria**:
- ✅ 0 crashes on 100+ test runs
- ✅ +40-60% FPS increase verified (Valorant, CS:GO)
- ✅ Temperature drop verified (-5 to -8°C)
- ✅ <150MB size
- ✅ UI responsive (no hangs)
- ✅ GitHub Release published

---

## WEEK 3-4: FEATURES & INTEGRATIONS

**Goal**: AMD support, FrameGen, game profiles, PartMart integration

### Phase 2.1: AMD GPU Support (Day 1-3)
- [ ] AMD GPU detection (OverdriveNTool)
- [ ] Voltage control for AMD architecture
- [ ] Memory OC for AMD VRAM
- [ ] Power tuning (TDP adjustment)
- [ ] Testing on RX 6700 XT / RX 7600
- [ ] Unit tests for AMD
- [ ] Unified GPU interface (NVIDIA + AMD)

**Deliverable**: AMD GPU optimizer working alongside NVIDIA

### Phase 2.2: FrameGen Integration (Day 4-6)
- [ ] AMD FSR 3 SDK integration (DLL injection)
- [ ] FSR 3 works on all GPUs (NVIDIA + AMD)
- [ ] NVIDIA DLSS 3 support (RTX 40xx only)
- [ ] Lossless Scaling external integration
- [ ] Game process detection + DLL injection
- [ ] Auto-inject toggle
- [ ] Compatibility warnings
- [ ] Tests for each FrameGen tech

**Deliverable**: FrameGen boost available in UI

### Phase 2.3: Game Profiles (Day 7-8)
- [ ] Game executable detection (Valorant, CS2, Cyberpunk, etc.)
- [ ] Predefined optimization profiles (top 20 games)
- [ ] Custom profile creation
- [ ] Game Launcher UI widget
- [ ] 1-click game optimization
- [ ] Auto-inject on game launch
- [ ] Crash detection (revert on 2x crash)
- [ ] Tests

**Deliverable**: Game launcher with auto-inject

### Phase 2.4: PartMart Integration (Day 9-10)
- [ ] Seller ID storage (encrypted)
- [ ] Purchase date display
- [ ] "Thank seller" button → deep link to Avito review
- [ ] Referral system UI
  - [ ] Generate unique referral link
  - [ ] Share on social media
  - [ ] Track referrals (local storage)
- [ ] Avito API integration (if available)
- [ ] PartMart branding throughout UI
- [ ] Tests

**Deliverable**: Full PartMart integration in app

### Phase 2.5: Performance Tracking (Day 11)
- [ ] FPS history tracking (last 30 days)
- [ ] Temperature history graphs
- [ ] Before/After comparison
- [ ] Export stats to CSV
- [ ] Performance insights ("Best day was XX FPS")

**Deliverable**: Performance dashboard working

### Phase 2.6: Auto-Updater (Day 12)
- [ ] GitHub Releases API integration
- [ ] Check for updates on startup
- [ ] Download new version
- [ ] Background installation
- [ ] Restart prompt
- [ ] Changelog display

**Deliverable**: Auto-updater functional

### Phase 2.7: Testing & Release (Day 13-14)
- [ ] Integration tests (GPU + RAM + FrameGen + games)
- [ ] Manual testing on AMD GPU
- [ ] Manual game testing (inject + FrameGen)
- [ ] Regression tests (ensure MVP still works)
- [ ] Release v0.5-beta

**Deliverable**: `partmart-boost-v0.5-beta.exe` on GitHub

**Exit Criteria**:
- ✅ NVIDIA + AMD support verified
- ✅ FrameGen (+50-100% FPS possible with FSR 3)
- ✅ Game profiles work for top 5 games
- ✅ PartMart integration active
- ✅ Auto-updater tested
- ✅ 95%+ stability
- ✅ Ready for public beta testing

---

## WEEK 5-6: POLISH & PUBLIC RELEASE

**Goal**: Production-ready v1.0 with premium tier

### Phase 3.1: Premium Tier (Day 1-2)
- [ ] Subscription model (399₽/год)
- [ ] Custom GPU profiles (save unlimited)
- [ ] DLSS 3 advanced features
- [ ] Unlimited game profiles
- [ ] Cloud sync (if infrastructure available)
- [ ] Priority support
- [ ] Payment gateway (Yandex Kassa / Stripe)
- [ ] License validation

**Deliverable**: Premium tier UI + backend

### Phase 3.2: Advanced RAM Tuning (Day 3)
- [ ] CAS Latency tweaking
- [ ] RCD (Row Cycle Delay) adjustment
- [ ] Frequency fine-tuning (+50-100MHz increments)
- [ ] Voltage micro-tweaks (safe range)
- [ ] Safety warnings + limits
- [ ] Auto-reset to safe defaults

**Deliverable**: Advanced RAM optimizer

### Phase 3.3: Installer & Deployment (Day 4-5)
- [ ] NSIS installer script
  - [ ] PartMart branding + colors
  - [ ] License agreement
  - [ ] Installation directory selection
  - [ ] Start menu shortcuts
  - [ ] Desktop shortcut
  - [ ] Auto-start option
- [ ] Uninstaller (clean removal)
- [ ] Registry entries
- [ ] Updater integration in installer

**Deliverable**: Professional NSIS installer

### Phase 3.4: Code Signing (Day 5)
- [ ] Obtain Authenticode certificate
- [ ] Sign .exe file
- [ ] Sign installer .exe
- [ ] Verify SmartScreen signature (no warnings)
- [ ] Test on clean system (no SmartScreen prompts)

**Deliverable**: Code-signed binaries

### Phase 3.5: Advanced Features (Day 6)
- [ ] Discord Rich Presence integration
  - [ ] Show "Playing with PartMart Boost" in Discord
  - [ ] Display current FPS / game name
- [ ] Advanced analytics dashboard
- [ ] Crash report aggregation
- [ ] User feedback form
- [ ] Feature voting

**Deliverable**: Advanced features activated

### Phase 3.6: Comprehensive QA (Day 7-10)
- [ ] Test on 5+ different GPU models (NVIDIA, AMD)
- [ ] Test on DDR3, DDR4, DDR5 RAM
- [ ] Test on Windows 10 + Windows 11
- [ ] Performance benchmarks (verify +40-80% FPS claims)
- [ ] 1000+ hour stress test (using automated testing)
- [ ] Security audit
  - [ ] No malware
  - [ ] No crypto mining
  - [ ] No spyware
  - [ ] Privacy policy compliance
- [ ] Documentation review
- [ ] FAQ completion

**Deliverable**: Production-ready v1.0

### Phase 3.7: Release & Announcement (Day 11-14)
- [ ] Final build + testing
- [ ] README finalization
- [ ] CHANGELOG creation
- [ ] GitHub Release v1.0
- [ ] Upload installer + .exe
- [ ] Press release to PartMart community
- [ ] Announce on GitHub Discussions
- [ ] Forum announcements

**Deliverable**: `partmart-boost-v1.0-release.exe` OFFICIAL RELEASE

**Exit Criteria**:
- ✅ 99.9% stability (0 crashes on 1000+ installations)
- ✅ +40-80% FPS increase verified (measurable)
- ✅ 95%+ GPU compatibility
- ✅ <150MB size
- ✅ Code signed (no SmartScreen)
- ✅ Premium tier active
- ✅ Full documentation
- ✅ Production ready
- ✅ Public GitHub release

---

## Success Metrics (Target)

### Technical
- ✅ 0 crashes on 1000+ test runs (99.9% stability)
- ✅ +40-80% FPS increase (verified on multiple games)
- ✅ Temperature reduction: -5 to -8°C average
- ✅ <150MB total size
- ✅ 95%+ GPU compatibility (NVIDIA, AMD, Intel)
- ✅ Code coverage: >80%

### User Adoption
- ✅ 10,000+ installations (month 1)
- ✅ 85%+ retention rate (don't uninstall after month 1)
- ✅ 90%+ use Quick Boost at least once
- ✅ 70%+ use game launcher
- ✅ 20%+ subscribe to Premium tier
- ✅ NPS: 8.5+/10

### PartMart Integration
- ✅ 40%+ leave review on Avito
- ✅ 25%+ use referral system
- ✅ 15%+ purchase another PC from PartMart
- ✅ Brand loyalty increase: 60%+ become repeat customers

---

## Post-Launch (After v1.0)

### v1.1 (Month 2)
- Intel Arc GPU support
- ML-based auto-optimization
- Cloud profiles sync
- Mobile app companion

### v1.2 (Month 3)
- Network optimization
- Discord server integration
- YouTube integration (share clips)
- Streaming optimization (OBS, XSplit)

### v2.0 (Future)
- Marketplace for community profiles
- AI-powered anomaly detection
- Predictive analytics
- System-wide optimization (not just GPU)

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| GPU compatibility issues | High | Early testing on RTX 3060 + RX 6700 XT; conservative defaults |
| Stability concerns | High | Mandatory stability test; auto-revert on crash; temperature protection |
| User data loss | Medium | Settings backup; cloud sync for Premium tier |
| Competition | Medium | Fast MVP release; PartMart integration differentiation |
| Support burden | Medium | Comprehensive FAQ; Discord community; automated crash reporting |

---

## Questions / Open Issues

- [ ] Should we support Intel Arc GPU in v1.0? (Nice-to-have, defer to v1.1)
- [ ] Payment processor choice? (Yandex Kassa for Russia)
- [ ] Cloud sync backend? (GitHub? AWS? Self-hosted?)
- [ ] Community Discord server? (Post-launch, Month 2)

---

**Last Updated**: Jan 28, 2026  
**Next Review**: Week 1 completion (Feb 3, 2026)
