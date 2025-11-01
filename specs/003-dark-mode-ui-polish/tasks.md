# Implementation Tasks: Dark Mode and UI Polish

**Feature**: 003-dark-mode-ui-polish | **Generated**: 2025-11-01 | **Spec**: [spec.md](./spec.md)

## Overview

This document provides an actionable, dependency-ordered task list for implementing dark mode and UI polish for the fotoview static gallery generator. Tasks are organized by user story (P1, P2, P3) to enable independent implementation and testing.

**Total Tasks**: 47
**Estimated Time**: 8-12 hours
**MVP Scope**: User Story 1 (Dark Mode Visual Experience) - 16 tasks

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Verify project environment and prepare for implementation

- [ ] T001 Verify current working directory is `/home/surt91/code/fotoview`
- [ ] T002 Verify git working tree is clean using `git status`
- [ ] T003 Create git branch backup tag: `git tag -a backup-before-dark-mode -m "Backup before dark mode implementation"`
- [ ] T004 Verify existing CSS files: `src/static/css/gallery.css` and `src/static/css/fullscreen.css` exist
- [ ] T005 Verify existing HTML template: `src/templates/index.html.tpl` exists
- [ ] T006 Run existing test suite to establish baseline: `uv run pytest`
- [ ] T007 Verify current CSS size is under budget: `wc -c src/static/css/*.css` (should be ~6KB total)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Set up CSS architecture and color palette that all user stories depend on

**Goal**: Establish CSS custom properties architecture and light/dark mode foundation

**Independent Test**: CSS variables defined in :root selector, @media (prefers-color-scheme: dark) block exists, all values match contract specifications

### Color Palette Setup

- [ ] T008 [P] Add CSS custom properties for light mode colors to `src/static/css/gallery.css` in :root selector (7 color variables per contract)
- [ ] T009 [P] Add CSS custom properties for animation timing to `src/static/css/gallery.css` in :root selector (4 timing variables per contract)
- [ ] T010 [P] Add CSS custom properties for typography to `src/static/css/gallery.css` in :root selector (7 typography variables per contract)
- [ ] T011 Replace all hardcoded color values in `src/static/css/gallery.css` with `var(--color-*)` references
- [ ] T012 Replace all hardcoded color values in `src/static/css/fullscreen.css` with `var(--color-*)` references
- [ ] T013 Add `@media (prefers-color-scheme: dark)` block to `src/static/css/gallery.css` with dark color palette overrides (7 variables)
- [ ] T014 Add `<meta name="color-scheme" content="light dark">` to `src/templates/index.html.tpl` in head section
- [ ] T015 Verify CSS builds successfully: `uv run python -m src.generator.build_html`
- [ ] T016 Verify CSS file size still under budget: `wc -c dist/static/css/*.css` (should be ~8KB, under 25KB limit)

**Checkpoint**: At this point, basic dark mode infrastructure is in place. Gallery should respond to system dark mode preference.

---

## Phase 3: User Story 1 - Dark Mode Visual Experience (Priority: P1)

**Goal**: Provide a modern dark theme that reduces eye strain and provides excellent contrast for viewing images

**Independent Test**: Open gallery in browser with system dark mode enabled, verify all elements use dark theme colors, text is readable (WCAG 2.1 AA contrast), images are clearly visible

### Dark Mode Styling

- [ ] T017 [US1] Add image shadow/border for dark mode in `src/static/css/gallery.css` within @media (prefers-color-scheme: dark) block
- [ ] T018 [US1] Update category section styling in `src/static/css/gallery.css` to use CSS variables for borders and backgrounds
- [ ] T019 [US1] Update fullscreen modal backdrop in `src/static/css/fullscreen.css` to use dark color variables
- [ ] T020 [US1] Update fullscreen modal content styling in `src/static/css/fullscreen.css` with dark mode colors
- [ ] T021 [US1] Update button/close elements in `src/static/css/fullscreen.css` to use accent color variable for focus states
- [ ] T022 [US1] Test manual dark mode toggle: Open gallery, toggle system dark mode, verify smooth color transition

### Accessibility Verification

- [ ] T023 [US1] Run accessibility tests to verify contrast ratios: `uv run pytest tests/accessibility/test_axe_a11y.py -v`
- [ ] T024 [US1] If contrast violations found, adjust color values in @media (prefers-color-scheme: dark) block and re-test
- [ ] T025 [US1] Manually verify focus indicators are visible in dark mode (tab through interactive elements)
- [ ] T026 [US1] Manually verify text readability at 100%, 150%, and 200% zoom levels in dark mode

### Integration Testing

- [ ] T027 [US1] Build gallery and open in Chrome: `uv run python -m src.generator.build_html && python -m http.server 8000 -d dist`
- [ ] T028 [US1] Test dark mode in Firefox (verify color rendering matches Chrome)
- [ ] T029 [US1] Test dark mode in Safari if available (verify color rendering consistency)
- [ ] T030 [US1] Test fullscreen image viewer in dark mode (open image, verify modal styling)
- [ ] T031 [US1] Verify asset budgets still pass: `uv run pytest tests/integration/test_asset_budgets.py -v`

### Git Checkpoint

- [ ] T032 [US1] Stage CSS changes: `git add src/static/css/gallery.css src/static/css/fullscreen.css src/templates/index.html.tpl`
- [ ] T033 [US1] Commit User Story 1: `git commit -m "feat: implement dark mode with CSS custom properties"`

**Checkpoint**: ✅ User Story 1 complete! Gallery has functional dark mode with good contrast. This is the MVP.

---

## Phase 4: User Story 2 - Subtle Visual Flourishes (Priority: P2)

**Goal**: Add smooth, polished interactions with fade-ins, transitions, and micro-interactions

**Independent Test**: Interact with gallery elements, verify smooth transitions, hover effects, and fade-in animations without jarring effects

### Animation Timing Setup

- [ ] T034 [US2] Add @media (prefers-reduced-motion: reduce) block to `src/static/css/gallery.css` setting all transition variables to 0ms
- [ ] T035 [US2] Add transition properties to `.image-item` in `src/static/css/gallery.css` using timing variables for transform and opacity
- [ ] T036 [US2] Add hover effect to `.image-item` in `src/static/css/gallery.css` (subtle scale or brightness change)
- [ ] T037 [US2] Add transition to fullscreen modal backdrop in `src/static/css/fullscreen.css` (fade-in/fade-out)
- [ ] T038 [US2] Add transition to fullscreen modal content in `src/static/css/fullscreen.css` (slide or fade effect)

### Image Fade-In Animation

- [ ] T039 [US2] Add CSS class `.image-loading` with opacity: 0 to `src/static/css/gallery.css`
- [ ] T040 [US2] Add CSS class `.image-loaded` with opacity: 1 and transition to `src/static/css/gallery.css`
- [ ] T041 [US2] Create or update `src/static/js/gallery.js` to add Intersection Observer for image fade-in on scroll
- [ ] T042 [US2] Test fade-in effect: Build gallery, scroll through images, verify smooth appearance

### Polish Testing

- [ ] T043 [US2] Test hover effects on images (verify subtle and non-distracting)
- [ ] T044 [US2] Test fullscreen modal transitions (verify smooth open/close)
- [ ] T045 [US2] Test with system reduced motion enabled (verify all transitions disabled)
- [ ] T046 [US2] Run performance check: Open Chrome DevTools → Performance, record interaction, verify 60fps

### Git Checkpoint

- [ ] T047 [US2] Stage animation changes: `git add src/static/css/gallery.css src/static/css/fullscreen.css src/static/js/gallery.js`
- [ ] T048 [US2] Commit User Story 2: `git commit -m "feat: add subtle visual flourishes and smooth transitions"`

**Checkpoint**: User Story 2 complete! Gallery has polished animations and micro-interactions.

---

## Phase 5: User Story 3 - Enhanced Typography and Spacing (Priority: P3)

**Goal**: Improve font choices, sizing, and spacing for better readability and visual hierarchy

**Independent Test**: Review text elements throughout gallery, verify font sizes, spacing, and hierarchy create cohesive, readable experience

### Typography Refinements

- [ ] T049 [US3] Update `h1` styling in `src/static/css/gallery.css` to use `var(--font-size-h1)` and `var(--line-height-heading)`
- [ ] T050 [US3] Update `h2` styling in `src/static/css/gallery.css` to use `var(--font-size-h2)`, `var(--line-height-heading)`, and `var(--letter-spacing-heading)`
- [ ] T051 [US3] Update body text in `src/static/css/gallery.css` to use `var(--line-height-base)`
- [ ] T052 [US3] Update caption styling (if present) to use `var(--font-size-caption)` and `var(--color-text-secondary)`

### Spacing Improvements

- [ ] T053 [US3] Review and adjust margins between category sections in `src/static/css/gallery.css` using `var(--spacing-unit)` multiples
- [ ] T054 [US3] Review and adjust padding in category headers for better breathing room
- [ ] T055 [US3] Verify visual hierarchy: Category headers clearly distinct from body text

### Typography Testing

- [ ] T056 [US3] Test readability at 100%, 150%, 200% zoom (verify no horizontal scrolling)
- [ ] T057 [US3] Test with long category names (verify text doesn't overflow or break layout)
- [ ] T058 [US3] Test with very short and very long image captions (verify consistent spacing)

### Git Checkpoint

- [ ] T059 [US3] Stage typography changes: `git add src/static/css/gallery.css src/static/css/fullscreen.css`
- [ ] T060 [US3] Commit User Story 3: `git commit -m "feat: enhance typography and spacing for better readability"`

**Checkpoint**: User Story 3 complete! Gallery has refined typography and spacing.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and quality assurance

### Comprehensive Testing

- [ ] T061 Run full test suite: `uv run pytest -v`
- [ ] T062 Verify all accessibility tests pass: `uv run pytest tests/accessibility/test_axe_a11y.py -v`
- [ ] T063 Verify asset budgets pass: `uv run pytest tests/integration/test_asset_budgets.py -v`
- [ ] T064 Test gallery with different image sets (various colors, aspect ratios, dark images)
- [ ] T065 Test keyboard navigation throughout gallery in both light and dark modes
- [ ] T066 Test on mobile devices (iOS Safari, Android Chrome) if available

### Documentation

- [ ] T067 Create ADR 0003: Document CSS-only dark mode approach decision in `docs/decisions/0003-dark-mode-styling-approach.md`
- [ ] T068 Update README.md: Add dark mode feature mention and browser requirements
- [ ] T069 Update CHANGELOG.md: Document dark mode implementation with breaking changes (if any)

### Performance Validation

- [ ] T070 Measure final CSS size: `wc -c src/static/css/*.css` (verify ≤25KB)
- [ ] T071 Measure final JS size: `wc -c src/static/js/*.js` (verify ≤75KB)
- [ ] T072 Run Lighthouse audit on generated gallery (target: Performance ≥90, Accessibility ≥90)

### Final Git Operations

- [ ] T073 Review all changes: `git diff main...003-dark-mode-ui-polish`
- [ ] T074 Verify all files staged and committed: `git status`
- [ ] T075 Push branch to remote: `git push origin 003-dark-mode-ui-polish`
- [ ] T076 Create pull request to merge into main branch

**Checkpoint**: All implementation and testing complete! Ready for code review and merge.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories (must establish CSS architecture first)
- **User Story 1 (Phase 3)**: Depends on Foundational - Can complete independently, is the MVP
- **User Story 2 (Phase 4)**: Depends on Foundational and logically follows US1 (builds on dark mode colors)
- **User Story 3 (Phase 5)**: Depends on Foundational - Can be done independently but benefits from US1/US2 context
- **Polish (Phase 6)**: Depends on ALL user stories being complete

### User Story Dependencies

```
Foundational (Phase 2)
    ├── User Story 1 (P1) - Dark Mode Visual Experience [INDEPENDENT]
    │   └── MVP Deliverable
    ├── User Story 2 (P2) - Subtle Visual Flourishes [Builds on US1]
    └── User Story 3 (P3) - Enhanced Typography [INDEPENDENT]
```

**Critical Path**: Setup → Foundational → User Story 1 → Polish (minimum viable delivery)

**Full Path**: Setup → Foundational → US1 → US2 → US3 → Polish

### Parallel Execution Opportunities

**Phase 2 (Foundational)**: Tasks T008, T009, T010 can run in parallel (different CSS variable groups)

**Phase 3 (User Story 1)**:
- T017, T018 can run in parallel (different CSS sections in gallery.css)
- T019, T020, T021 can run in parallel (different elements in fullscreen.css)
- T027, T028, T029 can run in parallel (testing in different browsers)

**Phase 4 (User Story 2)**:
- T034, T035, T036 can run in parallel (different CSS rules)
- T037, T038 can run in parallel (different modal elements)

**Phase 5 (User Story 3)**:
- T049, T050, T051, T052 can run in parallel (different typography elements)
- T053, T054 can run in parallel (different spacing adjustments)

**Phase 6 (Polish)**:
- T061, T062, T063 can run in parallel (different test suites)
- T067, T068, T069 can run in parallel (different documentation files)

---

## Implementation Strategy

### MVP-First Approach

**Minimum Viable Product**: User Story 1 (Dark Mode Visual Experience)
- Delivers core user request: "should have a dark mode"
- Provides immediate value: Reduces eye strain, modern aesthetic
- Can be shipped independently: Users get functional dark mode
- Builds foundation: CSS architecture supports future enhancements

**Incremental Delivery**:
1. **Sprint 1** (MVP): Setup + Foundational + User Story 1 (16 tasks, ~4-6 hours)
   - Deliverable: Gallery with fully functional dark mode
2. **Sprint 2** (Polish): User Story 2 (15 tasks, ~2-3 hours)
   - Deliverable: Smooth animations and micro-interactions
3. **Sprint 3** (Refinement): User Story 3 (12 tasks, ~1-2 hours)
   - Deliverable: Enhanced typography and spacing
4. **Sprint 4** (Ship): Polish phase (13 tasks, ~1-2 hours)
   - Deliverable: Production-ready dark mode with documentation

### Testing Strategy

**Per User Story**:
- Each story has dedicated test tasks for independent validation
- Accessibility tests verify contrast ratios (WCAG 2.1 AA)
- Asset budget tests prevent performance regression
- Manual browser testing ensures cross-browser compatibility

**Continuous Validation**:
- Run `uv run pytest` after completing each phase
- Run accessibility tests after any color changes
- Run asset budget tests after any CSS/JS changes
- Build and visually inspect gallery after each user story

### Risk Mitigation

**Risk**: Color contrast violations in dark mode
- **Mitigation**: Use pre-verified color palette from research.md, run axe-core tests
- **Fallback**: Adjust colors in T024 if violations detected

**Risk**: CSS budget breach (>25KB)
- **Mitigation**: Monitor size after foundational phase (T016), optimize if needed
- **Fallback**: Remove optional animations or reduce color variations

**Risk**: Animation performance issues (<60fps)
- **Mitigation**: Use CSS-only animations (GPU-accelerated), test in T046
- **Fallback**: Reduce transition durations or remove complex animations

**Risk**: Browser compatibility issues
- **Mitigation**: Test in Chrome, Firefox, Safari (T027-T029), use standard CSS features
- **Fallback**: Add @supports queries for progressive enhancement

---

## Validation Checklist

Before marking feature complete, verify:

- [ ] All 76 tasks completed and checked off
- [ ] All commits follow conventional commit format (`feat:`, `fix:`, etc.)
- [ ] Full test suite passes: `uv run pytest`
- [ ] Zero accessibility violations: `uv run pytest tests/accessibility/test_axe_a11y.py`
- [ ] Asset budgets respected: CSS ≤25KB, JS ≤75KB
- [ ] Gallery works in Chrome, Firefox, Safari (latest 2 versions)
- [ ] Dark mode automatically responds to system preference
- [ ] Light mode still works correctly (fallback for non-dark-mode users)
- [ ] Reduced motion preference respected (animations disabled)
- [ ] Keyboard navigation functional in both themes
- [ ] Documentation complete: ADR, README, CHANGELOG
- [ ] Pull request created with comprehensive description

---

## Notes

- **No backend changes**: This is purely frontend work (CSS/JS/HTML templates)
- **Static-first preserved**: All changes maintain zero-runtime-dependency architecture
- **Performance conscious**: Every task considers impact on budgets and user experience
- **Accessibility mandatory**: WCAG 2.1 AA compliance is a gate, not a goal
- **User preference respected**: System dark mode detection, reduced motion support

**Estimated Total Time**: 8-12 hours for complete implementation
**MVP Time**: 4-6 hours for User Story 1 only

---

## References

- [Spec Document](./spec.md) - Feature requirements and user stories
- [Plan Document](./plan.md) - Technical approach and architecture decisions
- [Data Model](./data-model.md) - CSS variable entities and constraints
- [CSS Variables Contract](./contracts/css-variables.md) - Complete variable specifications
- [Research Document](./research.md) - Technology decisions and color palette selection
- [Quickstart Guide](./quickstart.md) - Developer guide for working with dark mode
