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

- [X] T001 Verify branch 009-gallery-banner is checked out and up to date with main
- [X] T002 [P] Run existing test suite to establish baseline (uv run pytest)
- [X] T003 [P] Verify Pydantic 2.0+, Jinja2 3.1+, Pillow 10.0+, PyYAML 6.0+, Babel 2.13+ installed
- [X] T004 [P] Create test banner image in content/ directory for testing

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Extend GalleryConfig model with banner_image and gallery_title fields in src/generator/model.py
- [X] T006 Add field validator for banner_image path validation in src/generator/model.py
- [X] T007 Add field validator for gallery_title text validation in src/generator/model.py
- [X] T008 [P] Add i18n translation key for "Gallery" default title in locales/messages.pot
- [X] T009 [P] Update German translation for default gallery title in locales/de/LC_MESSAGES/messages.po
- [X] T010 Compile i18n translations (uv run pybabel compile -d locales)

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

## Phase 6: User Story 4 - Display Gallery Subtitle (Priority: P3)

**Goal**: Gallery owners can display a descriptive subtitle beneath the main title to provide additional context

**Independent Test**: Configure subtitle text alongside title in settings, verify it displays with secondary styling beneath title

### Implementation for User Story 4

- [ ] T054 [US4] Add gallery_subtitle field to GalleryConfig model in src/generator/model.py
- [ ] T055 [US4] Add field validator for gallery_subtitle in src/generator/model.py
- [ ] T056 [US4] Add gallery_subtitle to template context in src/generator/build_html.py
- [ ] T057 [US4] Add subtitle rendering logic to template (below title, requires title) in src/templates/index.html.j2
- [ ] T058 [US4] Add conditional subtitle display (only when gallery_title present) in src/templates/index.html.j2
- [ ] T059 [US4] Add .banner-subtitle CSS class for positioning below title in src/static/style.css
- [ ] T060 [US4] Add subtitle typography (1.5rem font-size, 400 weight) in src/static/style.css
- [ ] T061 [US4] Add subtitle opacity (0.9) for secondary emphasis in src/static/style.css
- [ ] T062 [US4] Add subtitle text-shadow for readability in src/static/style.css
- [ ] T063 [US4] Adjust banner-title bottom positioning to make room for subtitle in src/static/style.css
- [ ] T064 [US4] Add responsive subtitle sizing (1.125rem mobile) in src/static/style.css
- [ ] T065 [US4] Add responsive subtitle positioning adjustments in src/static/style.css
- [ ] T066 [US4] Test subtitle displays below title with proper styling
- [ ] T067 [US4] Test subtitle not displayed when gallery_title is not configured
- [ ] T068 [US4] Test subtitle wrapping on narrow viewports
- [ ] T069 [US4] Test subtitle with special characters displays correctly
- [ ] T070 [US4] Test subtitle visual hierarchy (secondary to title)
- [ ] T071 [US4] Test empty/whitespace subtitle treated as None

**Checkpoint**: Subtitle feature complete - can display contextual information below title

---

## Phase 7: Integration & Testing

**Purpose**: Cross-story validation and quality assurance

- [ ] T072 [P] Write unit test for banner_image validation in tests/unit/test_model.py
- [ ] T073 [P] Write unit test for banner_image relative path resolution in tests/unit/test_model.py
- [ ] T074 [P] Write unit test for gallery_title validation in tests/unit/test_model.py
- [ ] T075 [P] Write unit test for gallery_title length limits in tests/unit/test_model.py
- [ ] T076 [P] Write unit test for gallery_subtitle validation in tests/unit/test_model.py
- [ ] T077 [P] Write unit test for gallery_subtitle length limits in tests/unit/test_model.py
- [ ] T078 [P] Write integration test for build with banner, title, and subtitle in tests/integration/test_build.py
- [ ] T079 [P] Write integration test for build without banner in tests/integration/test_build.py
- [ ] T080 [P] Write integration test for build with title but no subtitle in tests/integration/test_build.py
- [ ] T081 [P] Write integration test for banner asset copying in tests/integration/test_build.py
- [ ] T082 [P] Write accessibility test for banner section in tests/accessibility/test_a11y.py
- [ ] T083 [P] Write accessibility test for title contrast in tests/accessibility/test_a11y.py
- [ ] T084 [P] Write accessibility test for heading hierarchy in tests/accessibility/test_a11y.py
- [ ] T085 [P] Write accessibility test for subtitle readability in tests/accessibility/test_a11y.py
- [ ] T086 Run full test suite and verify all tests pass (uv run pytest)
- [ ] T087 Run accessibility tests and verify compliance (uv run pytest -m a11y)
- [ ] T088 Run coverage report and verify adequate coverage (uv run pytest --cov=src --cov-report=html)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and final quality checks

- [ ] T089 [P] Update README.md with banner/title/subtitle configuration examples
- [ ] T090 [P] Add CHANGELOG.md entry for version 0.3.0 with banner, title, and subtitle features
- [ ] T091 [P] Create ADR for banner cropping approach in docs/decisions/
- [ ] T092 [P] Update config/settings.yaml with documented banner/title/subtitle fields
- [ ] T093 Verify HTML payload is within 30KB budget (du -h dist/index.html)
- [ ] T094 Verify CSS payload is within 25KB budget (du -h dist/style.css)
- [ ] T095 Test gallery builds and displays correctly in Chrome browser
- [ ] T096 Test gallery builds and displays correctly in Firefox browser
- [ ] T097 Test gallery builds and displays correctly in Safari browser
- [ ] T098 Test responsive display from 320px to 3840px viewport widths
- [ ] T099 Test dark mode toggle with banner (if dark mode implemented)
- [ ] T100 Test all subtitle combinations (with/without title/banner)
- [ ] T101 Verify quickstart.md implementation steps are accurate
- [ ] T102 Test manual scenarios from quickstart.md validation checklist
- [ ] T103 Run final full test suite before PR (uv run pytest --cov=src)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 3 (Phase 3)**: Configuration - depends on Foundational (Phase 2)
- **User Story 1 (Phase 4)**: Banner Display - depends on US3 configuration foundation
- **User Story 2 (Phase 5)**: Title Display - depends on US1 banner infrastructure
- **User Story 4 (Phase 6)**: Subtitle Display - depends on US2 title implementation
- **Integration & Testing (Phase 7)**: Depends on all user stories being implemented
- **Polish (Phase 8)**: Depends on testing phase completion

### User Story Dependencies

- **User Story 3 (P1 - Configuration)**: Foundation for US1, US2, and US4 - must complete first
- **User Story 1 (P1 - Banner Image)**: Depends on US3 configuration - renders the banner element that US2 overlays on
- **User Story 2 (P2 - Gallery Title)**: Depends on US1 banner structure - adds title overlay or standalone title
- **User Story 4 (P3 - Gallery Subtitle)**: Depends on US2 title implementation - subtitle requires title to be present

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

**User Story 4 (Subtitle Display)**:
1. Model and build script changes (T054-T056) - sequential (same files as title)
2. Template changes (T057-T058) - sequential (same file)
3. CSS styling (T059-T065) - sequential (same file)
4. Testing (T066-T071) - sequential after implementation

### Parallel Opportunities

**Phase 1 (Setup)**: T002, T003, T004 can run in parallel

**Phase 2 (Foundational)**: T008, T009 can run in parallel (different files)

**Phase 3 (US3 Configuration)**: T011, T012 can run in parallel (independent edits)

**Phase 5 (US2 Title)**: T036 (build script) can run in parallel with T037 (template context)

**Phase 7 (Testing)**: All unit tests (T072-T077), integration tests (T078-T081), and accessibility tests (T082-T085) can be written in parallel

**Phase 8 (Polish)**: T089, T090, T091, T092 can run in parallel (different files)

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

### Phase 7: Test Writing
```bash
# All unit tests can be written in parallel:
Task T072: "Write unit test for banner_image validation"
Task T073: "Write unit test for banner_image relative path resolution"
Task T074: "Write unit test for gallery_title validation"
Task T075: "Write unit test for gallery_title length limits"
Task T076: "Write unit test for gallery_subtitle validation"
Task T077: "Write unit test for gallery_subtitle length limits"

# All integration tests can be written in parallel:
Task T078: "Write integration test for build with banner, title, and subtitle"
Task T079: "Write integration test for build without banner"
Task T080: "Write integration test for build with title but no subtitle"
Task T081: "Write integration test for banner asset copying"

# All accessibility tests can be written in parallel:
Task T082: "Write accessibility test for banner section"
Task T083: "Write accessibility test for title contrast"
Task T084: "Write accessibility test for heading hierarchy"
Task T085: "Write accessibility test for subtitle readability"
```

### Phase 8: Documentation
```bash
# These can happen simultaneously:
Task T089: "Update README.md with banner/title/subtitle configuration examples"
Task T090: "Add CHANGELOG.md entry for version 0.3.0"
Task T091: "Create ADR for banner cropping approach"
Task T092: "Update config/settings.yaml with documented banner/title/subtitle fields"
```

---

## Implementation Strategy

### MVP First (Minimum Viable Product)

The MVP is **User Stories 1-3** (P1/P2 priorities):

1. **Phase 1**: Setup (T001-T004)
2. **Phase 2**: Foundational (T005-T010) - CRITICAL foundation
3. **Phase 3**: User Story 3 - Configuration (T011-T018)
4. **Phase 4**: User Story 1 - Banner Display (T019-T035)
5. **Phase 5**: User Story 2 - Title Display (T036-T053)
6. **STOP and VALIDATE**: Test MVP (banner + title) working
7. **Optional**: Phase 6 - User Story 4 - Subtitle (T054-T071) - P3 enhancement
8. Complete testing and polish phases

**Rationale**: US3 (Configuration), US1 (Banner), and US2 (Title) form the core MVP. US4 (Subtitle) is a P3 enhancement that adds contextual information but is not essential for the basic feature. Can be delivered in a follow-up iteration.

### Incremental Delivery Strategy

1. **Phase 1+2**: Complete Setup + Foundational → Foundation ready
2. **Phase 3**: Add Configuration (US3) → Test config validation independently
3. **Phase 4**: Add Banner Display (US1) → Test banner rendering independently
4. **Phase 5**: Add Title Display (US2) → Test title overlay/standalone independently
5. **CHECKPOINT**: MVP complete and testable
6. **Phase 6**: Add Subtitle Display (US4) → Test subtitle as enhancement
7. **Phase 7**: Integration testing → Verify all stories work together
8. **Phase 8**: Polish & documentation → Ready for production

Each phase can be tested at its checkpoint before moving to the next.

### Single Developer Strategy

Work sequentially through phases:
1. Setup → Foundational → US3 → US1 → US2 → (MVP checkpoint) → US4 → Testing → Polish
2. Stop at each checkpoint to verify story independently
3. Use [P] markers within phases for context switching when blocked
4. Can skip US4 if time-constrained (P3 priority)

### Parallel Team Strategy

With 2-3 developers (after Foundational phase completes):
- **Developer A**: US3 Configuration (Phase 3)
- **Developer B**: Can start US1 Banner (Phase 4) once US3 is done
- **Developer C**: Can start US2 Title (Phase 5) once US1 is done, then US4 Subtitle (Phase 6) once US2 is done
- **All Together**: Integration testing (Phase 7) and Polish (Phase 8)

Note: Sequential dependency chain: US3 → US1 → US2 → US4

---

## Task Count Summary

- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 6 tasks
- **Phase 3 (US3 - Configuration)**: 8 tasks
- **Phase 4 (US1 - Banner Display)**: 17 tasks
- **Phase 5 (US2 - Title Display)**: 18 tasks
- **Phase 6 (US4 - Subtitle Display)**: 18 tasks
- **Phase 7 (Integration & Testing)**: 17 tasks
- **Phase 8 (Polish)**: 15 tasks

**Total**: 103 tasks

**Parallel Opportunities**: 26 tasks marked [P] can run in parallel within their phases

**Story Breakdown**:
- User Story 3 (Configuration): 8 tasks
- User Story 1 (Banner Display): 17 tasks
- User Story 2 (Title Display): 18 tasks
- User Story 4 (Subtitle Display): 18 tasks
- Infrastructure & Testing: 42 tasks

---

## Notes

- All tasks follow checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
- [P] tasks target different files and have no dependencies on incomplete tasks
- [Story] labels (US1, US2, US3, US4) map to user stories from spec.md
- File paths are absolute from repository root (/home/surt91/code/fotoview)
- Each checkpoint validates independent story functionality
- Constitution requirements verified: static-first ✅, performance budgets ✅, accessibility ✅
- Backward compatibility maintained: galleries without banner/title/subtitle continue working
- Tests are included as this is a core feature requiring quality validation
- Estimated implementation time: 2-3 hours for MVP (US1-US3), +30-45 min for subtitle (US4)
- User Story 4 (Subtitle) is P3 priority and can be skipped if time-constrained

````
