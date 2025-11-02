````markdown
# Tasks: Gallery Banner and Title

**Feature**: 009-gallery-banner
**Input**: Design documents from `/specs/009-gallery-banner/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md, contracts/template-context.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and verify development environment is ready

- [ ] T001 Verify branch 009-gallery-banner is checked out and up to date with main
- [ ] T002 [P] Run existing test suite to establish baseline (uv run pytest)
- [ ] T003 [P] Verify Pydantic 2.0+, Jinja2 3.1+, Pillow 10.0+, PyYAML 6.0+, Babel 2.13+ installed
- [ ] T004 [P] Create test banner image in content/ directory for testing

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Extend GalleryConfig model with banner_image and gallery_title fields in src/generator/model.py
- [ ] T006 Add field validator for banner_image path validation in src/generator/model.py
- [ ] T007 Add field validator for gallery_title text validation in src/generator/model.py
- [ ] T008 [P] Add i18n translation key for "Gallery" default title in locales/messages.pot
- [ ] T009 [P] Update German translation for default gallery title in locales/de/LC_MESSAGES/messages.po
- [ ] T010 Compile i18n translations (uv run pybabel compile -d locales)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 3 - Configure Banner and Title (Priority: P1) 🎯 MVP Foundation

**Goal**: Gallery owners can specify their banner image and title through configuration files

**Independent Test**: Edit settings.yaml with banner/title values, rebuild gallery, verify changes appear correctly

### Implementation for User Story 3

- [ ] T011 [P] [US3] Add banner_image configuration example to config/settings.yaml
- [ ] T012 [P] [US3] Add gallery_title configuration example to config/settings.yaml
- [ ] T013 [US3] Test GalleryConfig loads banner_image from settings.yaml correctly
- [ ] T014 [US3] Test GalleryConfig loads gallery_title from settings.yaml correctly
- [ ] T015 [US3] Test GalleryConfig validation rejects invalid banner image paths
- [ ] T016 [US3] Test GalleryConfig validation rejects empty/whitespace gallery titles
- [ ] T017 [US3] Test GalleryConfig validation rejects gallery titles over 200 characters
- [ ] T018 [US3] Test GalleryConfig works with None values (backward compatibility)

**Checkpoint**: Configuration system works - can now build rendering pipeline

---

## Phase 4: User Story 1 - Display Banner Image (Priority: P1) 🎯 MVP Core

**Goal**: Gallery visitors see a visually appealing banner image at the top spanning full viewport width

**Independent Test**: Configure banner image in settings, verify it displays full-width at top of gallery

### Implementation for User Story 1

- [ ] T019 [US1] Implement copy_banner_image function in src/generator/build_html.py
- [ ] T020 [US1] Integrate banner image copying into build_gallery function in src/generator/build_html.py
- [ ] T021 [US1] Add banner_image to template context in src/generator/build_html.py
- [ ] T022 [US1] Update index.html.j2 template to render banner section in src/templates/index.html.j2
- [ ] T023 [US1] Add semantic header element with role="banner" in src/templates/index.html.j2
- [ ] T024 [US1] Add conditional banner display logic to template in src/templates/index.html.j2
- [ ] T025 [US1] Add .gallery-banner CSS class in src/static/style.css
- [ ] T026 [US1] Add .banner-image CSS with object-fit: cover in src/static/style.css
- [ ] T027 [US1] Add viewport-relative height (40vh desktop) in src/static/style.css
- [ ] T028 [US1] Add responsive breakpoints for tablet (30vh) in src/static/style.css
- [ ] T029 [US1] Add responsive breakpoints for mobile (25vh) in src/static/style.css
- [ ] T030 [US1] Add CSS custom properties for banner heights in src/static/style.css
- [ ] T031 [US1] Test banner image copies to dist/images/banner/ directory
- [ ] T032 [US1] Test banner displays at full viewport width across screen sizes
- [ ] T033 [US1] Test banner cropping with tall images (object-fit behavior)
- [ ] T034 [US1] Test build without banner configured (backward compatibility)
- [ ] T035 [US1] Test banner image missing/invalid produces clear error

**Checkpoint**: Banner image displays correctly - ready to add title overlay

---

## Phase 5: User Story 2 - Display Gallery Title (Priority: P2)

**Goal**: Gallery visitors see a prominent, stylistically enhanced title identifying the collection

**Independent Test**: Configure title text in settings, verify it displays prominently with enhanced styling

### Implementation for User Story 2

- [ ] T036 [P] [US2] Implement get_default_title function with i18n in src/generator/build_html.py
- [ ] T037 [US2] Add gallery_title and default_title to template context in src/generator/build_html.py
- [ ] T038 [US2] Add title rendering logic to template (overlay on banner or standalone) in src/templates/index.html.j2
- [ ] T039 [US2] Add proper alt text for banner image using title in src/templates/index.html.j2
- [ ] T040 [US2] Add h1 element with gallery title in src/templates/index.html.j2
- [ ] T041 [US2] Add .banner-title CSS class for overlay positioning in src/static/style.css
- [ ] T042 [US2] Add title typography (3rem font-size, 700 weight) in src/static/style.css
- [ ] T043 [US2] Add white text color with text-shadow for readability in src/static/style.css
- [ ] T044 [US2] Add gradient overlay (::after pseudo-element) for text contrast in src/static/style.css
- [ ] T045 [US2] Add z-index layering for title above gradient in src/static/style.css
- [ ] T046 [US2] Add responsive title sizing (2rem mobile) in src/static/style.css
- [ ] T047 [US2] Add responsive title positioning adjustments in src/static/style.css
- [ ] T048 [US2] Test title displays on banner with proper overlay
- [ ] T049 [US2] Test title displays without banner (simple header)
- [ ] T050 [US2] Test default title displays when gallery_title not configured
- [ ] T051 [US2] Test title text readability on various banner backgrounds
- [ ] T052 [US2] Test title wrapping on narrow viewports
- [ ] T053 [US2] Test special characters in title display correctly

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Integration & Testing

**Purpose**: Cross-story validation and quality assurance

- [ ] T054 [P] Write unit test for banner_image validation in tests/unit/test_model.py
- [ ] T055 [P] Write unit test for banner_image relative path resolution in tests/unit/test_model.py
- [ ] T056 [P] Write unit test for gallery_title validation in tests/unit/test_model.py
- [ ] T057 [P] Write unit test for gallery_title length limits in tests/unit/test_model.py
- [ ] T058 [P] Write integration test for build with banner and title in tests/integration/test_build.py
- [ ] T059 [P] Write integration test for build without banner in tests/integration/test_build.py
- [ ] T060 [P] Write integration test for banner asset copying in tests/integration/test_build.py
- [ ] T061 [P] Write accessibility test for banner section in tests/accessibility/test_a11y.py
- [ ] T062 [P] Write accessibility test for title contrast in tests/accessibility/test_a11y.py
- [ ] T063 [P] Write accessibility test for heading hierarchy in tests/accessibility/test_a11y.py
- [ ] T064 Run full test suite and verify all tests pass (uv run pytest)
- [ ] T065 Run accessibility tests and verify compliance (uv run pytest -m a11y)
- [ ] T066 Run coverage report and verify adequate coverage (uv run pytest --cov=src --cov-report=html)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and final quality checks

- [ ] T067 [P] Update README.md with banner/title configuration examples
- [ ] T068 [P] Add CHANGELOG.md entry for version 0.3.0 with banner feature
- [ ] T069 [P] Create ADR for banner cropping approach in docs/decisions/
- [ ] T070 [P] Update config/settings.yaml with documented banner/title fields
- [ ] T071 Verify HTML payload is within 30KB budget (du -h dist/index.html)
- [ ] T072 Verify CSS payload is within 25KB budget (du -h dist/style.css)
- [ ] T073 Test gallery builds and displays correctly in Chrome browser
- [ ] T074 Test gallery builds and displays correctly in Firefox browser
- [ ] T075 Test gallery builds and displays correctly in Safari browser
- [ ] T076 Test responsive display from 320px to 3840px viewport widths
- [ ] T077 Test dark mode toggle with banner (if dark mode implemented)
- [ ] T078 Verify quickstart.md implementation steps are accurate
- [ ] T079 Test manual scenarios from quickstart.md validation checklist
- [ ] T080 Run final full test suite before PR (uv run pytest --cov=src)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 3 (Phase 3)**: Configuration - depends on Foundational (Phase 2)
- **User Story 1 (Phase 4)**: Banner Display - depends on US3 configuration foundation
- **User Story 2 (Phase 5)**: Title Display - depends on US1 banner infrastructure
- **Integration & Testing (Phase 6)**: Depends on all user stories being implemented
- **Polish (Phase 7)**: Depends on testing phase completion

### User Story Dependencies

- **User Story 3 (P1 - Configuration)**: Foundation for both US1 and US2 - must complete first
- **User Story 1 (P1 - Banner Image)**: Depends on US3 configuration - renders the banner element that US2 overlays on
- **User Story 2 (P2 - Gallery Title)**: Depends on US1 banner structure - adds title overlay or standalone title

### Within Each User Story

**User Story 3 (Configuration)**:
1. Add configuration fields (T011, T012) - can run in parallel
2. Test configuration loading (T013, T014) - sequential
3. Test validation rules (T015-T018) - sequential after implementation

**User Story 1 (Banner Display)**:
1. Build script changes (T019-T021) - sequential (same file)
2. Template changes (T022-T024) - sequential (same file)
3. CSS styling (T025-T030) - sequential (same file, logical order)
4. Testing (T031-T035) - sequential after implementation

**User Story 2 (Title Display)**:
1. Build script for title (T036-T037) - can run in parallel with each other
2. Template changes (T038-T040) - sequential (same file)
3. CSS styling (T041-T047) - sequential (same file)
4. Testing (T048-T053) - sequential after implementation

### Parallel Opportunities

**Phase 1 (Setup)**: T002, T003, T004 can run in parallel

**Phase 2 (Foundational)**: T008, T009 can run in parallel (different files)

**Phase 3 (US3 Configuration)**: T011, T012 can run in parallel (independent edits)

**Phase 5 (US2 Title)**: T036 (build script) can run in parallel with T037 (template context)

**Phase 6 (Testing)**: All unit tests (T054-T057), integration tests (T058-T060), and accessibility tests (T061-T063) can be written in parallel

**Phase 7 (Polish)**: T067, T068, T069, T070 can run in parallel (different files)

---

## Parallel Execution Examples

### Phase 2: Foundational Setup
```bash
# These can happen simultaneously:
Task T008: "Add i18n translation key in locales/messages.pot"
Task T009: "Update German translation in locales/de/LC_MESSAGES/messages.po"
```

### Phase 3: Configuration Examples
```bash
# These can happen simultaneously:
Task T011: "Add banner_image configuration example to config/settings.yaml"
Task T012: "Add gallery_title configuration example to config/settings.yaml"
```

### Phase 6: Test Writing
```bash
# All unit tests can be written in parallel:
Task T054: "Write unit test for banner_image validation"
Task T055: "Write unit test for banner_image relative path resolution"
Task T056: "Write unit test for gallery_title validation"
Task T057: "Write unit test for gallery_title length limits"

# All integration tests can be written in parallel:
Task T058: "Write integration test for build with banner and title"
Task T059: "Write integration test for build without banner"
Task T060: "Write integration test for banner asset copying"

# All accessibility tests can be written in parallel:
Task T061: "Write accessibility test for banner section"
Task T062: "Write accessibility test for title contrast"
Task T063: "Write accessibility test for heading hierarchy"
```

### Phase 7: Documentation
```bash
# These can happen simultaneously:
Task T067: "Update README.md with banner/title configuration examples"
Task T068: "Add CHANGELOG.md entry for version 0.3.0"
Task T069: "Create ADR for banner cropping approach"
Task T070: "Update config/settings.yaml with documented banner/title fields"
```

---

## Implementation Strategy

### MVP First (Minimum Viable Product)

The MVP is **all three user stories** since they form a cohesive feature:

1. **Phase 1**: Setup (T001-T004)
2. **Phase 2**: Foundational (T005-T010) - CRITICAL foundation
3. **Phase 3**: User Story 3 - Configuration (T011-T018)
4. **Phase 4**: User Story 1 - Banner Display (T019-T035)
5. **Phase 5**: User Story 2 - Title Display (T036-T053)
6. **STOP and VALIDATE**: Test all three stories working together
7. Complete testing and polish phases

**Rationale**: All three user stories are marked P1/P2 priority and together form the complete "banner and title" feature. Configuration (US3) is the foundation, banner (US1) provides the visual element, and title (US2) provides the identification. They're designed to work together as a single cohesive feature.

### Incremental Delivery Strategy

1. **Phase 1+2**: Complete Setup + Foundational → Foundation ready
2. **Phase 3**: Add Configuration (US3) → Test config validation independently
3. **Phase 4**: Add Banner Display (US1) → Test banner rendering independently
4. **Phase 5**: Add Title Display (US2) → Test title overlay/standalone independently
5. **Phase 6**: Integration testing → Verify all stories work together
6. **Phase 7**: Polish & documentation → Ready for production

Each phase can be tested at its checkpoint before moving to the next.

### Single Developer Strategy

Work sequentially through phases:
1. Setup → Foundational → US3 → US1 → US2 → Testing → Polish
2. Stop at each checkpoint to verify story independently
3. Use [P] markers within phases for context switching when blocked

### Parallel Team Strategy

With 2-3 developers (after Foundational phase completes):
- **Developer A**: US3 Configuration (Phase 3)
- **Developer B**: Can start US1 Banner (Phase 4) once US3 is done
- **Developer C**: Can start US2 Title (Phase 5) once US1 is done
- **All Together**: Integration testing (Phase 6) and Polish (Phase 7)

Note: Sequential dependency due to US2 needing US1's banner structure

---

## Task Count Summary

- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 6 tasks
- **Phase 3 (US3 - Configuration)**: 8 tasks
- **Phase 4 (US1 - Banner Display)**: 17 tasks
- **Phase 5 (US2 - Title Display)**: 18 tasks
- **Phase 6 (Integration & Testing)**: 13 tasks
- **Phase 7 (Polish)**: 14 tasks

**Total**: 80 tasks

**Parallel Opportunities**: 22 tasks marked [P] can run in parallel within their phases

**Story Breakdown**:
- User Story 3 (Configuration): 8 tasks
- User Story 1 (Banner Display): 17 tasks
- User Story 2 (Title Display): 18 tasks
- Infrastructure & Testing: 37 tasks

---

## Notes

- All tasks follow checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
- [P] tasks target different files and have no dependencies on incomplete tasks
- [Story] labels (US1, US2, US3) map to user stories from spec.md
- File paths are absolute from repository root (/home/surt91/code/fotoview)
- Each checkpoint validates independent story functionality
- Constitution requirements verified: static-first ✅, performance budgets ✅, accessibility ✅
- Backward compatibility maintained: galleries without banner/title continue working
- Tests are included as this is a core feature requiring quality validation
- Estimated implementation time: 2-3 hours (per quickstart.md)

````
