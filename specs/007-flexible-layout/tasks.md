# Tasks: Flexible Aspect-Ratio Image Layout

**Input**: Design documents from `/specs/007-flexible-layout/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are included as this feature requires comprehensive testing to ensure zero layout shift and performance requirements are met.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Verify Python 3.11+ environment with Pillow 10.0+ installed
- [ ] T002 [P] Add justified-layout library reference (CDN) to documentation
- [ ] T003 [P] Create src/static/js/layout.js file structure
- [ ] T004 [P] Review current CSS Grid implementation in src/static/css/gallery.css

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Update Image model in src/generator/model.py to add optional width, height fields and aspect_ratio property
- [ ] T006 Implement extract_dimensions() function in src/generator/scan.py using Pillow to extract image dimensions
- [ ] T007 Update image scanning logic in src/generator/scan.py to call extract_dimensions() for all images
- [ ] T008 Update build_html.py in src/generator/build_html.py to pass width/height when creating Image objects
- [ ] T009 Update index.html.j2 template in src/templates/index.html.j2 to include data-width, data-height attributes and img width/height attributes
- [ ] T010 Add justified-layout library CDN script tag in src/templates/index.html.j2 head section
- [ ] T011 [P] Create unit test for Image model with dimensions in tests/unit/test_model.py
- [ ] T012 [P] Create unit test for extract_dimensions() in tests/unit/test_scan.py

**Checkpoint**: Foundation ready - dimension extraction working, templates updated, user story implementation can now begin

---

## Phase 3: User Story 1 - View Uncropped Images (Priority: P1) 🎯 MVP

**Goal**: Display all images at their original aspect ratios without cropping

**Independent Test**: Upload gallery with mixed landscape (16:9), portrait (9:16), and square (1:1) images and verify none are cropped

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T013 [P] [US1] Create test fixture images with various aspect ratios in tests/fixtures/
- [ ] T014 [P] [US1] Add integration test in tests/integration/test_end_to_end.py to verify HTML contains dimension attributes
- [ ] T015 [P] [US1] Add visual verification in tests/integration/test_end_to_end.py that images are not cropped

### Implementation for User Story 1

- [ ] T016 [US1] Implement extractImageData() function in src/static/js/layout.js to read dimensions from DOM
- [ ] T017 [US1] Implement calculateLayout() wrapper function in src/static/js/layout.js that calls justified-layout library
- [ ] T018 [US1] Implement applyLayout() function in src/static/js/layout.js to position images in DOM
- [ ] T019 [US1] Implement init() function in src/static/js/layout.js to initialize layout on DOMContentLoaded
- [ ] T020 [US1] Update CSS in src/static/css/gallery.css to add .layout-calculated class styles for positioned layout
- [ ] T021 [US1] Update CSS in src/static/css/gallery.css to change object-fit from cover to contain for .layout-calculated images
- [ ] T022 [US1] Update asset copying in src/generator/assets.py to include layout.js in build output
- [ ] T023 [US1] Add layout.js script tag in src/templates/index.html.j2 after gallery.js

**Checkpoint**: At this point, User Story 1 should be fully functional - images display without cropping

---

## Phase 4: User Story 2 - Consistent Visual Balance (Priority: P1)

**Goal**: Maintain consistent visual sizing where images appear roughly comparable in size despite different aspect ratios

**Independent Test**: Calculate visible area (width × height) of displayed images and verify they fall within ±50% of median size

### Tests for User Story 2

- [ ] T024 [P] [US2] Add unit test in tests/unit/test_model.py to verify aspect_ratio property calculation
- [ ] T025 [P] [US2] Add integration test in tests/integration/test_end_to_end.py to measure image size variance
- [ ] T026 [P] [US2] Create visual regression test comparing layout consistency across aspect ratios

### Implementation for User Story 2

- [ ] T027 [US2] Configure justified-layout options in src/static/js/layout.js with targetRowHeight: 320px
- [ ] T028 [US2] Configure justified-layout options in src/static/js/layout.js with maxRowHeight: 480px
- [ ] T029 [US2] Add aspect ratio validation in src/static/js/layout.js to clamp extreme ratios (0.25 to 4.0)
- [ ] T030 [US2] Implement responsive targetRowHeight adjustment in src/static/js/layout.js based on viewport width
- [ ] T031 [US2] Add CSS transitions in src/static/css/gallery.css for smooth layout changes
- [ ] T032 [US2] Test and adjust spacing parameter in src/static/js/layout.js (default: 8px) for optimal visual balance

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - images uncropped and consistently sized

---

## Phase 5: User Story 3 - Efficient Space Usage (Priority: P2)

**Goal**: Minimize white space between images while maintaining clean spacing

**Independent Test**: Measure ratio of image area to total layout area and verify it exceeds 75%

### Tests for User Story 3

- [ ] T033 [P] [US3] Add unit test in tests/unit/test_layout_algorithm.py for space efficiency calculation
- [ ] T034 [P] [US3] Add integration test in tests/integration/test_end_to_end.py to verify layout space efficiency metric
- [ ] T035 [P] [US3] Create test for edge case: single image per category

### Implementation for User Story 3

- [ ] T036 [US3] Fine-tune boxSpacing parameter in src/static/js/layout.js for optimal space usage
- [ ] T037 [US3] Implement row height calculation optimization in src/static/js/layout.js
- [ ] T038 [US3] Add container padding configuration in src/static/js/layout.js (containerPadding: 0)
- [ ] T039 [US3] Handle edge case for single image layouts in src/static/js/layout.js
- [ ] T040 [US3] Update gallery container styles in src/static/css/gallery.css to minimize external margins
- [ ] T041 [US3] Add handling for partial last row in src/static/js/layout.js (forceLastRow: false)

**Checkpoint**: All priority P1 and P2 user stories complete - layout is uncropped, balanced, and space-efficient

---

## Phase 6: User Story 4 - Fast Initial Display (Priority: P3)

**Goal**: Images appear quickly in correct layout positions without reflow or jumping (CLS=0.0)

**Independent Test**: Simulate 3G network and measure Time to First Meaningful Paint and Cumulative Layout Shift metrics

### Tests for User Story 4

- [ ] T042 [P] [US4] Add performance test in tests/integration/test_end_to_end.py to measure layout calculation time (<500ms for 100 images)
- [ ] T043 [P] [US4] Create CLS measurement test in tests/integration/test_end_to_end.py to verify zero layout shift
- [ ] T044 [P] [US4] Add test in tests/integration/test_asset_budgets.py to verify JS bundle size under 75KB

### Implementation for User Story 4

- [ ] T045 [US4] Move layout calculation to synchronous execution before DOMContentLoaded in src/static/js/layout.js
- [ ] T046 [US4] Pre-calculate layout before first paint by executing in head in src/templates/index.html.j2
- [ ] T047 [US4] Add performance timing instrumentation in src/static/js/layout.js to measure calculation time
- [ ] T048 [US4] Implement loading state styling in src/static/css/gallery.css with skeleton placeholders
- [ ] T049 [US4] Add decoding="async" attribute to img tags in src/templates/index.html.j2
- [ ] T050 [US4] Optimize layout calculation by caching container width in src/static/js/layout.js
- [ ] T051 [US4] Implement debounced resize handler in src/static/js/layout.js (150ms debounce)
- [ ] T052 [US4] Add error handling for layout calculation failures in src/static/js/layout.js with fallback to CSS Grid

**Checkpoint**: All user stories complete - layout is fast, shift-free, uncropped, balanced, and space-efficient

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T053 [P] Create ADR 0007 in docs/decisions/0007-flexible-layout-algorithm.md documenting algorithm choice
- [ ] T054 [P] Update README.md with flexible layout feature description
- [ ] T055 [P] Add browser compatibility notes to documentation
- [ ] T056 [P] Add unit tests for edge cases in tests/unit/test_scan.py: invalid files, missing dimensions, extreme aspect ratios
- [ ] T057 [P] Add accessibility regression tests in tests/accessibility/test_axe_a11y.py for new layout
- [ ] T058 [P] Add responsive layout tests in tests/integration/test_end_to_end.py for mobile (320px) and desktop (1920px)
- [ ] T059 Code review for performance optimization opportunities across all layout code
- [ ] T060 Verify all acceptance scenarios from spec.md work correctly
- [ ] T061 Run quickstart.md validation to ensure implementation matches documented workflow
- [ ] T062 [P] Update i18n workflow documentation in docs/i18n-workflow.md if any user-facing strings added
- [ ] T063 Performance profiling for galleries with 500+ images

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (US1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (US2): Depends on US1 (builds on layout implementation)
  - User Story 3 (US3): Depends on US2 (fine-tunes layout created by US1/US2)
  - User Story 4 (US4): Depends on US1-US3 (optimizes complete layout implementation)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Implements basic layout without cropping
- **User Story 2 (P1)**: Depends on US1 - Adds visual balance configuration to layout
- **User Story 3 (P2)**: Depends on US2 - Optimizes space efficiency of balanced layout
- **User Story 4 (P3)**: Depends on US1-US3 - Adds performance optimizations to complete layout

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Layout algorithm core (US1) before visual tuning (US2) before space optimization (US3) before performance optimization (US4)
- CSS changes after JavaScript implementation to ensure proper styling for calculated layout
- Integration tests after implementation to verify end-to-end behavior

### Parallel Opportunities

- **Phase 1**: All 4 setup tasks marked [P] can run in parallel
- **Phase 2**: Tasks T011 and T012 (unit tests) can run in parallel with each other after T005-T010 complete
- **User Story 1**: Tasks T013, T014, T015 (test creation) can all run in parallel before implementation
- **User Story 2**: Tasks T024, T025, T026 (tests) can run in parallel before implementation
- **User Story 3**: Tasks T033, T034, T035 (tests) can run in parallel before implementation
- **User Story 4**: Tasks T042, T043, T044 (performance tests) can run in parallel before implementation
- **Phase 7**: All tasks marked [P] (T053-T058, T062) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all test creation tasks for User Story 1 together:
Task: "Create test fixture images with various aspect ratios in tests/fixtures/"
Task: "Add integration test to verify HTML contains dimension attributes"
Task: "Add visual verification that images are not cropped"

# These can run in parallel as they create different test files
```

## Parallel Example: Phase 7 (Polish)

```bash
# Launch all documentation tasks together:
Task: "Create ADR 0007 in docs/decisions/0007-flexible-layout-algorithm.md"
Task: "Update README.md with flexible layout feature description"
Task: "Add browser compatibility notes to documentation"
Task: "Add unit tests for edge cases in tests/unit/test_scan.py"
Task: "Add accessibility regression tests in tests/accessibility/test_axe_a11y.py"
Task: "Add responsive layout tests in tests/integration/test_end_to_end.py"
Task: "Update i18n workflow documentation in docs/i18n-workflow.md"

# All these tasks operate on different files and have no dependencies
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (4 tasks)
2. Complete Phase 2: Foundational (12 tasks including tests) - **CRITICAL**
3. Complete Phase 3: User Story 1 (11 tasks) - Basic uncropped layout
4. Complete Phase 4: User Story 2 (6 tasks) - Visual balance
5. **STOP and VALIDATE**: Test that images display uncropped with consistent sizing
6. Deploy/demo if ready

**Estimated Time**: ~4-5 hours for MVP (US1 + US2)

### Full Feature (All User Stories)

1. Complete Setup + Foundational → Foundation ready (16 tasks)
2. Add User Story 1 → Basic layout works (11 tasks)
3. Add User Story 2 → Visual balance added (6 tasks)
4. Add User Story 3 → Space efficiency optimized (6 tasks)
5. Add User Story 4 → Performance optimized (8 tasks)
6. Complete Polish phase → Documentation and edge cases (11 tasks)

**Estimated Time**: ~8-10 hours for full feature

### Incremental Delivery Milestones

1. **Milestone 1** (US1): Images display without cropping - validates core algorithm
2. **Milestone 2** (US2): Images have consistent sizing - validates visual design
3. **Milestone 3** (US3): Space usage optimized - validates layout efficiency
4. **Milestone 4** (US4): Performance optimized - validates production readiness
5. **Milestone 5** (Polish): Documentation complete - validates maintainability

---

## Total Task Count

- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 8 tasks
- **Phase 3 (User Story 1)**: 11 tasks (3 tests + 8 implementation)
- **Phase 4 (User Story 2)**: 6 tasks (3 tests + 3 implementation)
- **Phase 5 (User Story 3)**: 6 tasks (3 tests + 3 implementation)
- **Phase 6 (User Story 4)**: 8 tasks (3 tests + 5 implementation)
- **Phase 7 (Polish)**: 11 tasks
- **Total**: 54 tasks

**Parallel Opportunities**: 18 tasks can run in parallel (marked with [P])

**MVP Scope**: Phases 1-4 = 29 tasks (~4-5 hours)

---

## Notes

- [P] tasks = different files, no dependencies on other incomplete tasks
- [Story] label maps task to specific user story from spec.md
- Each user story builds incrementally on previous stories
- Tests are included due to strict CLS=0.0 and performance requirements
- Verify tests fail before implementing features
- Commit after each logical group of tasks
- Stop at any checkpoint/milestone to validate independently
- CSS Grid provides fallback if JavaScript disabled or layout fails
