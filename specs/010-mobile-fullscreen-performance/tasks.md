# Tasks: Mobile Full-Screen Experience & Advanced Performance

**Input**: Design documents from `/specs/010-mobile-fullscreen-performance/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not requested in specification - focusing on implementation tasks only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single project structure with:
- `src/generator/` - Python build tooling
- `src/templates/` - Jinja2 HTML templates
- `src/static/` - Frontend assets (CSS, JavaScript)
- `tests/` - Test suites

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and configuration for new features

- [X] T001 Create ADR document for blur placeholder strategy at docs/decisions/0012-blur-placeholder-strategy.md
- [X] T002 Update pyproject.toml dependencies to ensure Pillow 10.0+ with ImageFilter support
- [X] T003 Verify existing build cache infrastructure in src/generator/cache.py supports versioning

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models and configuration that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Add BlurPlaceholder and BlurPlaceholderConfig data models to src/generator/model.py
- [X] T005 [P] Extend ImageMetadata model with blur_placeholder field in src/generator/model.py
- [X] T006 [P] Extend BuildCacheEntry model with blur_placeholder field and bump cache version to 2.0.0 in src/generator/cache.py
- [X] T007 Add BlurPlaceholderConfig to Settings model with default values (enabled=True, target_size=20, blur_radius=10, jpeg_quality=50) in src/generator/model.py
- [X] T008 Add cache validation method is_valid() to BuildCacheEntry to check blur placeholder hashes in src/generator/cache.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 3 - Ultra-Fast Load with Blur Placeholders (Priority: P1) 🎯 MVP

**Goal**: Generate ultra-low-resolution blur placeholders during build process, embed as data URLs in HTML, display instantly on page load for perceived performance improvement

**Independent Test**: Throttle network to Slow 3G, clear cache, open gallery - blur placeholders should appear instantly (<50ms) before any network requests complete, then smoothly fade to thumbnails

### Implementation for User Story 3

- [X] T009 [P] [US3] Implement generate_blur_placeholder() function in src/generator/thumbnails.py using Pillow (resize to 20x20, apply GaussianBlur radius 10, JPEG quality 50, base64 encode)
- [X] T010 [P] [US3] Add _compute_image_hash() helper function in src/generator/thumbnails.py for SHA256 hashing of source images
- [X] T011 [P] [US3] Add _optimize_data_url_size() helper in src/generator/thumbnails.py to iteratively reduce JPEG quality if data URL exceeds max_size_bytes
- [X] T012 [US3] Integrate blur placeholder generation into existing thumbnail generation workflow in src/generator/thumbnails.py (check cache first, skip if disabled)
- [X] T013 [US3] Update build cache save/load logic in src/generator/cache.py to serialize/deserialize BlurPlaceholder objects
- [X] T014 [US3] Modify scan.py to pass blur placeholder config from settings to thumbnail generator
- [X] T015 [US3] Update build_html.py to pass blur_placeholder data to template context for each image
- [X] T016 [US3] Modify templates/index.html.j2 to embed blur placeholders as inline background-image style on .image-container divs
- [ ] T017 [US3] Modify templates/fullscreen.html.j2 to embed blur placeholders for fullscreen overlay
- [X] T018 [P] [US3] Add CSS styles for blur placeholder progressive loading in src/static/css/gallery.css (.image-container background-size: cover, .image-progressive opacity transition 300ms)
- [X] T019 [US3] Implement progressive image loading JavaScript in src/static/js/gallery.js (load thumbnail → fade in, skip blur if cached)
- [X] T020 [US3] Add intelligent skip logic in gallery.js to detect fast-loading cached images (<100ms) and skip blur placeholder display

**Checkpoint**: At this point, blur placeholders should generate during build, embed in HTML, display instantly, and progressively enhance to thumbnails

---

## Phase 4: User Story 1 - True Full-Screen Mobile Image View (Priority: P1)

**Goal**: Implement true full-screen mode on mobile devices where images fill entire viewport, browser UI minimizes/hides, providing immersive viewing experience

**Independent Test**: Open gallery on mobile device (or DevTools mobile emulation), tap any image - browser should enter full-screen mode (or simulate it), image fills entire screen, no gallery layout elements visible

### Implementation for User Story 1

- [ ] T021 [P] [US1] Create new FullscreenManager class in src/static/js/fullscreen-manager.js implementing native Fullscreen API with vendor prefixes
- [ ] T022 [P] [US1] Implement enterFullscreen() method with iOS Safari fallback (fixed positioning + viewport units) in src/static/js/fullscreen-manager.js
- [ ] T023 [P] [US1] Implement exitFullscreen() method handling both native API and fallback mode in src/static/js/fullscreen-manager.js
- [ ] T024 [P] [US1] Implement isFullscreen() method and fullscreen state tracking in src/static/js/fullscreen-manager.js
- [ ] T025 [P] [US1] Add handleOrientationChange() method to recalculate dimensions on device rotation in src/static/js/fullscreen-manager.js
- [ ] T026 [US1] Integrate FullscreenManager into existing fullscreen.js overlay initialization
- [ ] T027 [US1] Add fullscreen mode trigger on image click/tap in src/static/js/fullscreen.js
- [ ] T028 [US1] Add fullscreen exit trigger on close button or ESC key in src/static/js/fullscreen.js
- [ ] T029 [P] [US1] Add CSS styles for fullscreen mode in src/static/css/fullscreen.css (position: fixed, width: 100vw, height: 100vh, z-index: 9999)
- [ ] T030 [P] [US1] Add CSS safe area insets for notched devices in src/static/css/fullscreen.css (padding with env(safe-area-inset-*))
- [ ] T031 [US1] Add orientation change event listeners in src/static/js/fullscreen.js to maintain fullscreen through rotation
- [ ] T032 [US1] Implement fallback for iOS Safari (scroll to hide address bar, prevent body scroll) in src/static/js/fullscreen-manager.js

**Checkpoint**: At this point, mobile users should have true full-screen image viewing with browser UI hidden

---

## Phase 5: User Story 2 - Invisible Navigation Controls on Mobile (Priority: P1)

**Goal**: Hide navigation controls by default on mobile full-screen mode, show on tap with 3-second auto-hide timer, ensuring no image obstruction

**Independent Test**: Open image in full-screen on mobile - controls should be invisible, tap image to show controls, wait 3 seconds - controls auto-hide

### Implementation for User Story 2

- [ ] T033 [P] [US2] Create new ControlVisibilityManager class in src/static/js/control-visibility-manager.js with state machine (HIDDEN/VISIBLE/PENDING)
- [ ] T034 [P] [US2] Implement showControls() method with 300ms fade-in transition in src/static/js/control-visibility-manager.js
- [ ] T035 [P] [US2] Implement hideControls() method with 300ms fade-out transition in src/static/js/control-visibility-manager.js
- [ ] T036 [P] [US2] Implement resetHideTimer() method with 3-second countdown in src/static/js/control-visibility-manager.js
- [ ] T037 [P] [US2] Add mobile detection logic (viewport width < 768px) in src/static/js/control-visibility-manager.js
- [ ] T038 [P] [US2] Implement handleUserInteraction() event handler (tap, click, swipe) in src/static/js/control-visibility-manager.js
- [ ] T039 [US2] Integrate ControlVisibilityManager into fullscreen.js overlay initialization
- [ ] T040 [US2] Add tap event listener on fullscreen image area to toggle control visibility in src/static/js/fullscreen.js
- [ ] T041 [US2] Add control button click handlers that reset auto-hide timer in src/static/js/fullscreen.js
- [ ] T042 [US2] Add swipe gesture detection to keep controls hidden during navigation in src/static/js/fullscreen.js
- [ ] T043 [P] [US2] Add CSS styles for control visibility states in src/static/css/fullscreen.css (opacity: 0/1, pointer-events: none/auto, transition: 300ms)
- [ ] T044 [P] [US2] Add CSS media query to keep controls visible on desktop (min-width: 768px) in src/static/css/fullscreen.css
- [ ] T045 [US2] Add keyboard accessibility support (Tab, :focus-within keeps controls visible) in src/static/css/fullscreen.css
- [ ] T046 [US2] Add destroy() cleanup method to remove event listeners in src/static/js/control-visibility-manager.js

**Checkpoint**: All user stories should now be independently functional - mobile users have full-screen with hidden controls, blur placeholders load instantly

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, documentation, and validation

- [ ] T047 [P] Update README.md with blur placeholder feature description and configuration options
- [ ] T048 [P] Update README.md with mobile full-screen feature description and browser compatibility notes
- [ ] T049 [P] Add logging for blur placeholder generation (success/failure counts, size statistics) in src/generator/thumbnails.py
- [ ] T050 [P] Add performance monitoring logging in src/static/js/gallery.js (time to first blur display, time to thumbnail load)
- [ ] T051 Update tests/integration/test_asset_budgets.py to adjust HTML size budget expectations for blur placeholder data URLs
- [ ] T052 Add graceful fallback handling when blur placeholder generation fails (log warning, use solid color background) in src/generator/thumbnails.py
- [ ] T053 Add configuration validation warnings if blur placeholder config will exceed budget in src/generator/model.py
- [ ] T054 Test blur placeholder generation with various image formats (JPEG, PNG, WebP, GIF) and edge cases
- [ ] T055 Test full-screen mode on real mobile devices (iOS Safari, Chrome Mobile) and verify orientation changes
- [ ] T056 Test control visibility behavior on various mobile viewports (320px-768px width)
- [ ] T057 Verify keyboard accessibility (Tab, ESC, Arrow keys) still works in full-screen mode
- [ ] T058 Run full build process and verify HTML size increase is within acceptable limits
- [ ] T059 [P] Validate quickstart.md instructions work for new contributors
- [ ] T060 Create example gallery with high-quality test images to demo progressive loading

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3, 4, 5)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed) since they modify different files
  - Or sequentially in implementation order (US3 → US1 → US2)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 3 (Blur Placeholders)**: Can start after Foundational - No dependencies on other stories
- **User Story 1 (Full-Screen Mode)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (Control Visibility)**: Can start after Foundational - Integrates with US1 but should be independently testable

**Note**: US3 is prioritized first in implementation order because blur placeholders benefit from being in place before full-screen features are added. However, all three stories are P1 priority and can technically be developed in parallel.

### Within Each User Story

- **US3**: Models → Thumbnail generation → Cache integration → Template embedding → JavaScript loading → CSS transitions
- **US1**: FullscreenManager class → API methods → Integration into fullscreen.js → CSS styles → Event listeners
- **US2**: ControlVisibilityManager class → State management methods → Integration with fullscreen → CSS visibility styles → Accessibility

### Parallel Opportunities

- **Phase 1**: All 3 setup tasks can run in parallel
- **Phase 2**: Tasks T004, T005, T006 can run in parallel (different models/files)
- **Phase 3 (US3)**: Tasks T009, T010, T011, T018 can run in parallel (different files/functions)
- **Phase 4 (US1)**: Tasks T021-T025, T029-T030 can run in parallel (FullscreenManager methods and CSS are independent)
- **Phase 5 (US2)**: Tasks T033-T038, T043-T045 can run in parallel (ControlVisibilityManager methods and CSS are independent)
- **Phase 6**: Tasks T047, T048, T049, T050 can all run in parallel (documentation and logging)

**All three user stories (Phase 3, 4, 5) can be worked on in parallel by different team members after Phase 2 completes**

---

## Parallel Example: User Story 3 (Blur Placeholders)

```bash
# Launch these tasks together for User Story 3:
Task T009: "Implement generate_blur_placeholder() in src/generator/thumbnails.py"
Task T010: "Add _compute_image_hash() helper in src/generator/thumbnails.py"
Task T011: "Add _optimize_data_url_size() helper in src/generator/thumbnails.py"
Task T018: "Add CSS styles for blur placeholder in src/static/css/gallery.css"

# These modify different functions/files with no conflicts
```

## Parallel Example: User Story 1 (Full-Screen)

```bash
# Launch these tasks together for User Story 1:
Task T021: "Create FullscreenManager class in src/static/js/fullscreen-manager.js"
Task T022: "Implement enterFullscreen() method"
Task T023: "Implement exitFullscreen() method"
Task T024: "Implement isFullscreen() method"
Task T025: "Add handleOrientationChange() method"
Task T029: "Add CSS fullscreen styles in src/static/css/fullscreen.css"
Task T030: "Add CSS safe area insets in src/static/css/fullscreen.css"

# All FullscreenManager methods can be written in parallel, CSS is separate file
```

---

## Implementation Strategy

### MVP First (All Three P1 User Stories)

All three user stories are P1 priority and together constitute the MVP:

1. Complete Phase 1: Setup (ADR, dependencies, verification)
2. Complete Phase 2: Foundational (data models, cache structure) - CRITICAL
3. Complete Phase 3: User Story 3 (Blur Placeholders) - Core performance feature
4. Complete Phase 4: User Story 1 (Full-Screen Mode) - Core mobile UX feature
5. Complete Phase 5: User Story 2 (Control Visibility) - Completes full-screen UX
6. **STOP and VALIDATE**: Test all three stories work together on mobile
7. Complete Phase 6: Polish and documentation
8. Deploy/demo complete feature

### Incremental Delivery Alternative

If staging releases are desired:

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 3 (Blur Placeholders) → Test independently → Deploy (perceived performance improvement visible)
3. Add User Story 1 (Full-Screen Mode) → Test independently → Deploy (mobile viewing experience improved)
4. Add User Story 2 (Control Visibility) → Test independently → Deploy (polish complete)
5. Polish phase → Final deployment

### Parallel Team Strategy

With 3 developers:

1. Team completes Setup + Foundational together (Days 1-2)
2. Once Foundational is done:
   - Developer A: User Story 3 (Blur Placeholders) - Python + Templates + CSS/JS
   - Developer B: User Story 1 (Full-Screen Mode) - JavaScript + CSS
   - Developer C: User Story 2 (Control Visibility) - JavaScript + CSS
3. Stories integrate at Phase 6 for polish and testing

**Estimated Time**:
- Phase 1-2: 2-3 days
- Phase 3: 3-4 days (blur placeholder generation is complex)
- Phase 4: 2-3 days (full-screen API integration)
- Phase 5: 2-3 days (control visibility state management)
- Phase 6: 1-2 days (polish and validation)
- **Total**: 10-15 days for single developer, 6-8 days with parallel team

---

## Notes

- [P] tasks = different files/functions, no dependencies, can run in parallel
- [Story] label (US1, US2, US3) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- HTML size budget violation is documented and accepted (see plan.md Complexity Tracking)
- Blur placeholders are build-time generated (no runtime performance impact)
- Full-screen mode has iOS Safari fallback for browser compatibility
- Control visibility only applies to mobile (<768px), desktop always shows controls
- All features maintain keyboard accessibility (WCAG 2.1 AA compliance)
