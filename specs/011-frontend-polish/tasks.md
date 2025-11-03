---
description: "Task list for Frontend Polish & Mobile Improvements"
---

# Tasks: Frontend Polish & Mobile Improvements

**Feature**: 011-frontend-polish
**Branch**: `011-frontend-polish`
**Input**: Design documents from `/specs/011-frontend-polish/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: This feature does not require new test implementation tasks. Existing test infrastructure (pytest, playwright, axe) will be used to validate changes manually and through existing test suites.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a single-project static site generator:
- Frontend assets: `src/static/css/`, `src/static/js/`
- HTML templates: `src/templates/`
- Tests: `tests/integration/`, `tests/e2e/`

---

## Phase 1: Setup (No Tasks)

**Status**: ✅ Complete - Feature branch already exists, no new dependencies, no project structure changes

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core CSS architecture fix that MUST be complete before user story work

**⚠️ CRITICAL**: This fixes the root cause of horizontal scrolling and simplifies all subsequent CSS work

- [X] T001 Refactor body padding architecture in src/static/css/gallery.css (remove body padding, add padding to .gallery container, simplify .gallery-banner width calculation, remove negative margins)

**Checkpoint**: CSS architecture simplified - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Mobile Image Overlay Navigation (Priority: P1) 🎯 MVP

**Goal**: Enable mobile users to swipe left/right in fullscreen overlay to navigate between images, seamlessly crossing category boundaries

**Independent Test**: Open gallery on mobile device, tap any image to open overlay, swipe left (next) and right (previous). Navigation should work smoothly and cross category boundaries with updated labels.

### Implementation for User Story 1

- [X] T002 [P] [US1] Flatten images array structure in src/static/js/fullscreen.js (create allImages flat array on init, assign globalIndex to each image across all categories)
- [X] T003 [P] [US1] Add touch event state variables in src/static/js/fullscreen.js (touchStartX, touchStartY, touchEndX, touchEndY, touchStartTime, touchEndTime)
- [X] T004 [US1] Implement handleTouchStart function in src/static/js/fullscreen.js (record touch coordinates and timestamp on touchstart event)
- [X] T005 [US1] Implement handleTouchEnd function in src/static/js/fullscreen.js (record final coordinates and timestamp on touchend event, call handleSwipeGesture)
- [X] T006 [US1] Implement handleSwipeGesture function in src/static/js/fullscreen.js (calculate deltaX/deltaY, validate angle threshold <30° or >150°, validate minimum distance >50px, call showNextImage or showPreviousImage)
- [X] T007 [US1] Attach touch event listeners in src/static/js/fullscreen.js (addEventListener touchstart and touchend to #fullscreen-modal)
- [X] T008 [US1] Update showNextImage function in src/static/js/fullscreen.js (use modulo arithmetic for wrapping: (currentIndex + 1) % allImages.length)
- [X] T009 [US1] Update showPreviousImage function in src/static/js/fullscreen.js (use modulo arithmetic for wrapping: (currentIndex - 1 + allImages.length) % allImages.length)
- [X] T010 [US1] Update openFullscreen to use category label from image data in src/static/js/fullscreen.js (modalCategory.textContent = imageItem.categoryName for cross-category navigation)

**Checkpoint**: Mobile users can swipe through all images seamlessly with category labels updating automatically

---

## Phase 4: User Story 2 - Progressive Image Loading (Priority: P1) 🎯 MVP

**Goal**: Display thumbnail immediately when opening overlay, load original image in background, smoothly transition when original loads

**Independent Test**: Throttle network to Fast 3G in DevTools, click any image. Thumbnail should appear <100ms, original loads in background, smooth fade-in when ready.

### Implementation for User Story 2

- [X] T011 [P] [US2] Add data attributes to gallery.html template in src/templates/index.html.j2 (data-thumbnail-src="{{ image.thumbnail_jpeg_href }}", data-original-src="{{ image.url }}", data-category="{{ image.category }}")
- [X] T012 [P] [US2] Add currentImageLoader variable in src/static/js/fullscreen.js (global variable to track Image() preloader, initialized to null)
- [X] T013 [US2] Update openFullscreen to display thumbnail immediately in src/static/js/fullscreen.js (set modalImg.src to thumbnailSrc from data attribute, remove 'loaded' class)
- [X] T014 [US2] Implement Image() preloader in openFullscreen in src/static/js/fullscreen.js (create new Image(), set onload handler to swap src and add 'loaded' class, set onerror handler, assign originalSrc)
- [X] T015 [US2] Add load cancellation logic in openFullscreen in src/static/js/fullscreen.js (null out currentImageLoader before starting new load to cancel previous)
- [X] T016 [P] [US2] Add CSS transition for thumbnail-to-original swap in src/static/css/fullscreen.css (#modal-image transition opacity 0.3s, :not(.loaded) opacity 0.95, .loaded opacity 1)

**Checkpoint**: Users see immediate thumbnail display, smooth transition to original, no blank screens while loading

---

## Phase 5: User Story 3 - Mobile Layout Consistency (Priority: P2)

**Goal**: Eliminate all horizontal scrolling on mobile viewports, ensure banner fits perfectly within viewport

**Independent Test**: Open gallery on mobile (320px, 375px, 414px widths in DevTools), scroll entire page. No horizontal scrollbar should appear.

### Implementation for User Story 3

- [X] T017 [P] [US3] Add overflow-x hidden to body in src/static/css/gallery.css (overflow-x: hidden, max-width: 100vw) - DONE IN T001
- [X] T018 [P] [US3] Update header:has(.gallery-banner) selector in src/static/css/gallery.css (remove negative margin-left, margin-right, margin-top since body padding is removed) - DONE IN T001
- [X] T019 [US3] Add padding to header:not(:has(.gallery-banner)) in src/static/css/gallery.css (padding: calc(var(--spacing-unit) * 2) var(--spacing-unit) for spacing when banner absent) - DONE IN T001

**Checkpoint**: Gallery displays without horizontal scrolling on all mobile viewport sizes (320px-768px)

---

## Phase 6: User Story 4 - Optimized Overlay Layout (Priority: P2)

**Goal**: Maximize image size in overlay, de-emphasize category label for better visual hierarchy

**Independent Test**: Open any image in overlay, visually verify image is larger (80vh desktop, 75vh mobile), category label is smaller and less prominent than title.

### Implementation for User Story 4

- [X] T020 [P] [US4] Increase desktop image max-height in src/static/css/fullscreen.css (.modal-content img max-height: 80vh, increased from 70vh)
- [X] T021 [P] [US4] Increase mobile image max-height in src/static/css/fullscreen.css (@media (max-width: 768px) .modal-content img max-height: 75vh, increased from 60vh)
- [X] T022 [P] [US4] Reduce category label prominence in src/static/css/fullscreen.css (.modal-category font-size: 0.75rem, opacity: 0.7)
- [X] T023 [US4] Optimize metadata spacing in src/static/css/fullscreen.css (.modal-metadata margin-top: 1rem reduced from 1.5rem, add padding: 0 1rem for mobile)

**Checkpoint**: Images appear significantly larger in overlay, category is visually secondary to title/description

---

## Phase 7: User Story 5 - Visual Polish & Bug Fixes (Priority: P3)

**Goal**: Eliminate visual artifacts, refine loading animation to be more subtle and professional

**Independent Test**: View banner on desktop/mobile (no black lines), observe shimmer animation on lazy-loaded images (slower, reduced contrast).

### Implementation for User Story 5

- [X] T024 [P] [US5] Refine shimmer animation contrast in src/static/css/gallery.css (.image-item img[loading="lazy"] background gradient use rgba(255, 255, 255, 0.3) instead of #f8f8f8)
- [X] T025 [P] [US5] Slow shimmer animation speed in src/static/css/gallery.css (animation: shimmer 2.0s ease-in-out infinite, increased from 1.5s)
- [X] T026 [P] [US5] Add dark mode shimmer refinement in src/static/css/gallery.css (@media (prefers-color-scheme: dark) use rgba(255, 255, 255, 0.05) for even more subtlety)

**Checkpoint**: Visual polish complete - no artifacts, loading animation professional and unobtrusive

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Validation, documentation, and final cleanup

- [ ] T027 [P] Manual testing: Verify no horizontal scroll on mobile (320px, 375px, 414px, 480px viewports in Chrome DevTools)
- [ ] T028 [P] Manual testing: Test swipe gestures on physical iOS Safari device (iPhone) and Android Chrome device
- [ ] T029 [P] Manual testing: Test progressive loading with network throttling (Fast 3G in DevTools, verify <100ms thumbnail display)
- [ ] T030 [P] Manual testing: Verify overlay image size increase (80vh desktop, 75vh mobile, measure via DevTools computed styles)
- [ ] T031 [P] Manual testing: Verify cross-category navigation works seamlessly (test wrapping at gallery boundaries, category label updates)
- [ ] T032 Run existing pytest test suite to verify no regressions (uv run pytest)
- [ ] T033 Run existing Playwright accessibility tests to verify no violations (uv run pytest tests/integration/test_accessibility.py)
- [ ] T034 Run asset budget tests to verify size limits (uv run pytest tests/integration/test_asset_budgets.py, expect JS ~30KB total)
- [ ] T035 [P] Update CHANGELOG.md with user-facing improvements (mobile swipe navigation, faster image loading, better mobile layout)
- [ ] T036 Run quickstart.md validation (follow all steps in specs/011-frontend-polish/quickstart.md)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: ✅ Complete - No tasks needed
- **Foundational (Phase 2)**: T001 MUST complete first - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion (T001)
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after T001 - No dependencies on other stories
- **User Story 2 (P1)**: Can start after T001 - No dependencies on other stories (works independently)
- **User Story 3 (P2)**: Can start after T001 - No dependencies on other stories (layout fix is foundational)
- **User Story 4 (P2)**: Can start after T001 - No dependencies on other stories
- **User Story 5 (P3)**: Can start after T001 - No dependencies on other stories

**CRITICAL**: User Stories 1 and 2 are BOTH P1 (MVP). They can be implemented in parallel after T001 completes.

### Within Each User Story

**User Story 1** (Touch Swipe Navigation):
- T002, T003 can run in parallel (different parts of code)
- T004-T006 must be sequential (build on each other)
- T007-T010 can be done after T004-T006 complete

**User Story 2** (Progressive Image Loading):
- T011, T012, T016 can run in parallel (template, JS variable, CSS)
- T013-T015 must be sequential (modify openFullscreen function)

**User Story 3** (Mobile Layout):
- T017, T018, T019 can run in parallel (different CSS selectors)

**User Story 4** (Overlay Layout):
- T020-T023 can all run in parallel (different CSS selectors)

**User Story 5** (Visual Polish):
- T024-T026 can all run in parallel (different CSS selectors)

**Polish Phase**:
- T027-T031 manual tests can run in any order
- T032-T034 automated tests should run after all implementation complete
- T035-T036 documentation should be last

### Parallel Opportunities

- **After T001**: US1, US2, US3, US4, US5 can all start in parallel
- **Within US1**: T002+T003 in parallel
- **Within US2**: T011+T012+T016 in parallel
- **Within US3**: T017+T018+T019 in parallel
- **Within US4**: T020+T021+T022 in parallel (T023 depends on T022 for spacing adjustment)
- **Within US5**: T024+T025+T026 in parallel
- **Polish**: T027-T031 in parallel, T032-T034 in parallel, T035+T036 after tests pass

---

## Parallel Example: User Story 1

```bash
# Launch parallel tasks for US1:
Task: "Flatten images array structure in src/static/js/fullscreen.js"
Task: "Add touch event state variables in src/static/js/fullscreen.js"

# Then sequential implementation:
Task: "Implement handleTouchStart function"
Task: "Implement handleTouchEnd function"
Task: "Implement handleSwipeGesture function"
```

---

## Parallel Example: User Story 2

```bash
# Launch all parallel tasks for US2:
Task: "Add data attributes to gallery.html template in src/templates/gallery.html"
Task: "Add currentImageLoader variable in src/static/js/fullscreen.js"
Task: "Add CSS transition for thumbnail-to-original swap in src/static/css/fullscreen.css"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 2: Foundational (T001 - CSS architecture fix)
2. Complete Phase 3: User Story 1 (T002-T010 - Touch swipe navigation)
3. Complete Phase 4: User Story 2 (T011-T016 - Progressive loading)
4. **STOP and VALIDATE**: Test on mobile with swipe and loading
5. Deploy/demo if ready - core mobile experience dramatically improved

**Rationale**: US1 + US2 deliver the biggest UX improvements for mobile users (primary audience). US3-US5 are polish that can follow.

### Incremental Delivery

1. Complete Foundational (T001) → CSS architecture fixed
2. Add User Story 1 (T002-T010) → Test independently → Mobile swipe works! 🎉
3. Add User Story 2 (T011-T016) → Test independently → Instant thumbnails! 🎉
4. Add User Story 3 (T017-T019) → Test independently → No horizontal scroll! 🎉
5. Add User Story 4 (T020-T023) → Test independently → Bigger images! 🎉
6. Add User Story 5 (T024-T026) → Test independently → Subtle animations! 🎉
7. Polish phase (T027-T036) → Full validation and documentation

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers (or working on multiple tasks):

1. Developer/Session 1: T001 (Foundational - required first)
2. Once T001 done, split work:
   - Developer A: User Story 1 (T002-T010)
   - Developer B: User Story 2 (T011-T016)
   - Developer C: User Story 3 (T017-T019)
3. Stories complete and integrate independently

### Single Developer Strategy

**Recommended order**:
1. T001 (Foundation - required)
2. T002-T010 (US1 - highest UX impact)
3. T011-T016 (US2 - highest performance impact)
4. T017-T019 (US3 - critical bug fix)
5. T020-T023 (US4 - UX polish)
6. T024-T026 (US5 - visual polish)
7. T027-T036 (Validation and docs)

**Estimated time**: 4-6 hours total for experienced developer familiar with codebase

---

## Summary

- **Total Tasks**: 36
- **Foundational**: 1 task (T001 - BLOCKS all stories)
- **User Story 1** (P1 - Mobile Swipe): 9 tasks (T002-T010)
- **User Story 2** (P1 - Progressive Loading): 6 tasks (T011-T016)
- **User Story 3** (P2 - Layout Fix): 3 tasks (T017-T019)
- **User Story 4** (P2 - Overlay Optimization): 4 tasks (T020-T023)
- **User Story 5** (P3 - Visual Polish): 3 tasks (T024-T026)
- **Polish**: 10 tasks (T027-T036)

**MVP Scope**: T001 + US1 + US2 = 16 tasks (44% of total, delivers 80% of user value)

**Parallel Opportunities**:
- Foundational (T001): 1 task, must complete first
- After T001: All 5 user stories can start in parallel
- Within stories: 19 tasks marked [P] can run in parallel with others in same story
- Polish phase: Most validation tasks can run in parallel

**Independent Test Criteria**:
- Each user story has clear acceptance criteria in spec.md
- Each phase has checkpoint validation in quickstart.md
- Manual + automated testing covers all changes
- No breaking changes to existing functionality

---

## Notes

- [P] tasks = different files or non-overlapping code sections, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No new test implementation tasks - existing test infrastructure is sufficient
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
