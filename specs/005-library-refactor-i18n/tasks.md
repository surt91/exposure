# Tasks: Library Modernization and Internationalization

**Input**: Design documents from `/specs/005-library-refactor-i18n/`
**Prerequisites**: plan.md, spec.md, research.md

**Tests**: Test updates required to adapt to new libraries, but no new test creation requested.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single project structure: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Project Dependencies)

**Purpose**: Add new dependencies and create initial infrastructure

- [x] T001 Add new dependencies to pyproject.toml (pydantic>=2.0, jinja2>=3.1, babel>=2.13)
- [x] T002 Install dependencies with uv sync
- [x] T003 Create babel.cfg configuration file in project root for i18n extraction
- [x] T004 Create docs/decisions/0005-library-modernization.md ADR documenting library choices

---

## Phase 2: Foundational (Core Logging Infrastructure)

**Purpose**: Replace print() with logging infrastructure - foundation for all other work

**⚠️ CRITICAL**: This phase blocks all user stories since logging is used throughout

- [x] T005 Implement setup_logging() function in src/generator/__init__.py
- [x] T006 Create module-level logger instance in src/generator/__init__.py
- [x] T007 Add optional log_level field to settings.yaml configuration

**Checkpoint**: Logging infrastructure ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Developer Maintenance Experience (Priority: P1) 🎯 MVP

**Goal**: Modernize codebase with Pydantic models, Jinja2 templates, and standard logging

**Independent Test**: Run existing test suite (pytest) - all tests should pass with minor updates. Verify HTML output is functionally equivalent.

### Pydantic Model Migration

- [x] T008 [P] [US1] Migrate Image dataclass to Pydantic BaseModel in src/generator/model.py
- [x] T009 [P] [US1] Migrate Category dataclass to Pydantic BaseModel in src/generator/model.py
- [x] T010 [P] [US1] Migrate YamlEntry dataclass to Pydantic BaseModel in src/generator/model.py
- [x] T011 [P] [US1] Migrate GalleryConfig dataclass to Pydantic BaseModel in src/generator/model.py
#### T012: Update yaml_sync.py to use Pydantic methods
- [x] Change `YamlEntry.from_dict()` to `YamlEntry.model_validate()`
- [x] Change `to_dict()` to `model_dump()` for YAML serialization

#### T013: Update build_html.py load_config() to use Pydantic validation
- [x] Replace manual field extraction with `GalleryConfig.model_validate(settings)`
- [x] Remove redundant Path() conversions (Pydantic validators handle this)
- [x] Test that validation errors are clear and helpful

#### T014: Update tests/unit/test_model.py for Pydantic model assertions
- [x] Replace `ValueError` expectations with `ValidationError` from pydantic
- [x] Update `test_to_dict` to `test_model_dump`
- [x] Update `test_from_dict` to `test_model_validate`
- [x] Verify all 16 tests pass

### Logging Migration

- [x] T015 [P] [US1] Replace all print() statements with logger.info() in src/generator/build_html.py
- [x] T016 [P] [US1] Replace all print() statements with logger calls in src/generator/yaml_sync.py
- [x] T017 [P] [US1] Replace all print() statements with logger calls in src/generator/scan.py
- [x] T018 [US1] Update main() entry point in src/generator/build_html.py to call setup_logging()
- [x] T019 [US1] Verify log output format matches previous console output

### Jinja2 Template Migration

### Jinja2 Template Migration

- [x] T020 [US1] Read existing template format from src/templates/index.html.tpl
- [x] T021 [US1] Create src/templates/index.html.j2 with Jinja2 syntax (loops, conditionals)
- [x] T022 [US1] Create src/templates/fullscreen.html.j2 for modal inclusion
- [x] T023 [US1] Setup Jinja2 Environment in generate_gallery_html()
- [x] T024 [US1] Replace template.format() with template.render() in generate_gallery_html()
- [x] T025 [US1] Update build_gallery_section() to pass data dict instead of building HTML strings
- [x] T026 [US1] Update organize_by_category() to pass data to templates instead of building HTML
- [x] T027 [US1] Remove all HTML string building code from src/generator/build_html.py
- [x] T028 [US1] Run tests/integration/test_end_to_end.py to verify HTML output equivalence
- [x] T029 [US1] Run tests/integration/test_fullscreen.py to verify JavaScript data attributes preserved
- [x] T030 [US1] Run tests/accessibility/test_axe_a11y.py to verify accessibility maintained

### Test Updates

- [x] T031 [P] [US1] Update tests/unit/test_build_html.py for Pydantic models and Jinja2 rendering
- [x] T032 [P] [US1] Update tests/unit/test_yaml_sync.py for Pydantic model serialization
- [x] T033 [US1] Run tests/integration/test_reproducibility.py to verify deterministic builds
- [x] T034 [US1] Run full test suite to verify all tests pass

**Checkpoint**: User Story 1 complete - Pydantic models, Jinja2 templates, and logging all working. All tests passing. HTML output functionally equivalent.

---

## Phase 4: User Story 2 - Multi-Language Support (Priority: P2)

**Goal**: Add internationalization support for English and German locales using Babel

**Independent Test**: Set locale to "de" in settings.yaml, build gallery, verify German UI strings appear in generated HTML

### i18n Infrastructure Setup

- [x] T035 [US2] Create locales/ directory in project root
- [x] T036 [US2] Add locale field (default: "en") to settings.yaml
- [x] T037 [US2] Create src/generator/i18n.py with setup_i18n() and _() functions
- [x] T038 [US2] Update Jinja2 Environment in src/generator/build_html.py to load i18n extension
- [x] T039 [US2] Configure Jinja2 to use Babel translations via install_gettext_translations()

### Mark Translatable Strings

- [x] T040 [P] [US2] Wrap UI strings in Jinja2 templates with _() translation function
- [x] T041 [P] [US2] Wrap log messages in src/generator/build_html.py with _() function
- [x] T042 [P] [US2] Wrap log messages in src/generator/yaml_sync.py with _() function
- [x] T043 [P] [US2] Wrap log messages in src/generator/scan.py with _() function

### Extract and Translate

- [x] T044 [US2] Run pybabel extract to generate locales/messages.pot template
- [x] T045 [US2] Run pybabel init to create locales/de/LC_MESSAGES/messages.po
- [x] T046 [US2] Translate all strings in locales/de/LC_MESSAGES/messages.po to German
- [x] T047 [US2] Run pybabel compile to generate locales/de/LC_MESSAGES/messages.mo binary
- [x] T048 [US2] Call setup_i18n() in src/generator/build_html.py main() with config.locale

### Testing

- [x] T049 [US2] Create tests/unit/test_i18n.py to verify translation loading and fallback
- [x] T050 [US2] Test with locale="en" - verify English strings used
- [x] T051 [US2] Test with locale="de" - verify German strings appear in HTML
- [x] T052 [US2] Test with locale="fr" (non-existent) - verify fallback to English
- [x] T053 [US2] Update CHANGELOG.md with i18n feature and German locale support

**Checkpoint**: User Story 2 complete - i18n working with English and German. Can switch language via settings.yaml. Tests passing.

---

## Phase 5: User Story 3 - Configuration Management (Priority: P3)

**Goal**: Enhanced configuration validation with pydantic-settings and environment variable support

**Independent Test**: Provide invalid settings.yaml, verify clear field-level validation errors. Set environment variables, verify they override YAML config.

### Pydantic Settings Integration

- [x] T054 [US3] Add pydantic-settings>=2.0 to pyproject.toml dependencies (optional feature)
- [x] T055 [US3] Install pydantic-settings with uv sync
- [x] T056 [US3] Refactor GalleryConfig in src/generator/model.py to inherit from BaseSettings
- [x] T057 [US3] Configure BaseSettings with env_prefix="FOTOVIEW_" for environment variables
- [x] T058 [US3] Add field descriptions and examples to GalleryConfig using Field()
- [x] T059 [US3] Update load_config() in src/generator/build_html.py to use BaseSettings validation
- [x] T060 [US3] Test environment variable overrides (e.g., FOTOVIEW_LOCALE=de)
- [x] T061 [US3] Verify validation errors show field names and constraint violations
- [x] T062 [US3] Update tests/unit/test_build_html.py to test config validation errors
- [x] T063 [US3] Document environment variable configuration in README.md

**Checkpoint**: User Story 3 complete - Pydantic Settings providing enhanced validation and env var support. Clear error messages on invalid config.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and final validation

- [x] T064 [P] Update README.md with new dependencies and quickstart instructions
- [x] T065 [P] Update CHANGELOG.md with all changes from this refactor
- [x] T066 [P] Add i18n workflow documentation (extract/translate/compile) to docs/
- [x] T067 Code review and cleanup of any TODO comments
- [x] T068 Verify all constitution gates pass (performance, accessibility, asset sizes)
- [x] T069 Run full test suite with coverage report
- [x] T070 [P] Update .github/copilot-instructions.md with new libraries
- [x] T071 Final build test with both English and German locales
- [x] T072 Verify generated HTML output meets success criteria (SC-002: 30% complexity reduction)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion - MVP deliverable
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion (needs Jinja2 and logging in place)
- **User Story 3 (Phase 5)**: Depends on User Story 1 completion (extends Pydantic models)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (MVP)
- **User Story 2 (P2)**: Depends on US1 - Needs Jinja2 templates and logging infrastructure in place
- **User Story 3 (P3)**: Depends on US1 - Extends GalleryConfig Pydantic model created in US1

### Within Each User Story

**User Story 1:**
- Pydantic models (T008-T014) can be done in parallel
- Logging migration (T015-T019) can be done in parallel with models
- Jinja2 migration (T020-T030) depends on models being complete (templates need Pydantic attributes)
- Test updates (T031-T034) come after implementation

**User Story 2:**
- Infrastructure setup (T035-T039) must be done first
- String marking (T040-T043) can be done in parallel once infrastructure exists
- Extract/translate (T044-T048) is sequential (extract → translate → compile)
- Testing (T049-T053) comes after translation

**User Story 3:**
- All tasks are mostly sequential as they build on GalleryConfig refactoring

### Parallel Opportunities

- **Phase 1 Setup**: T001, T003, T004 can run in parallel (different files)
- **Phase 3 US1 Models**: T008, T009, T010, T011 can run in parallel (all in model.py, but different classes)
- **Phase 3 US1 Logging**: T015, T016, T017 can run in parallel (different files)
- **Phase 3 US1 Test Updates**: T031, T032 can run in parallel (different test files)
- **Phase 4 US2 String Marking**: T040, T041, T042, T043 can run in parallel (different files)
- **Phase 6 Polish**: T064, T065, T066, T070 can run in parallel (different documentation files)

---

## Parallel Example: User Story 1 Pydantic Models

```bash
# Launch all Pydantic model migrations together:
Task: "Migrate Image dataclass to Pydantic BaseModel in src/generator/model.py"
Task: "Migrate Category dataclass to Pydantic BaseModel in src/generator/model.py"
Task: "Migrate YamlEntry dataclass to Pydantic BaseModel in src/generator/model.py"
Task: "Migrate GalleryConfig dataclass to Pydantic BaseModel in src/generator/model.py"
# Then proceed to update yaml_sync.py and build_html.py to use new models
```

---

## Parallel Example: User Story 1 Logging Migration

```bash
# Launch all logging replacements together:
Task: "Replace all print() statements with logger.info() in src/generator/build_html.py"
Task: "Replace all print() statements with logger calls in src/generator/yaml_sync.py"
Task: "Replace all print() statements with logger calls in src/generator/scan.py"
# Then setup logging in main()
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (install dependencies, create ADR)
2. Complete Phase 2: Foundational (setup logging infrastructure)
3. Complete Phase 3: User Story 1 (Pydantic + Jinja2 + Logging)
4. **STOP and VALIDATE**: Run full test suite, verify HTML output
5. Commit MVP - code is now more maintainable with modern libraries

### Incremental Delivery

1. Complete Setup + Foundational → Dependencies and logging ready
2. Add User Story 1 → Test independently → **MVP DELIVERED** (maintainable codebase)
3. Add User Story 2 → Test independently → i18n support for German users
4. Add User Story 3 → Test independently → Enhanced config validation (optional)
5. Complete Polish → Documentation and final validation

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: Pydantic models + YAML sync (T008-T014)
   - Developer B: Logging migration (T015-T019)
   - Developer C: Jinja2 templates (T020-T027)
3. Once US1 complete:
   - Developer A: User Story 2 (i18n)
   - Developer B: User Story 3 (pydantic-settings)
   - Developer C: Test updates and validation

---

## Success Metrics

Track these throughout implementation:

- **SC-001**: All existing tests pass (minor updates acceptable) ✓
- **SC-002**: Count lines of HTML string concatenation removed (target: 30% reduction) ✓
- **SC-003**: Test config validation error messages for clarity ✓
- **SC-004**: Time to add new translatable string (target: <2 minutes) ✓
- **SC-005**: HTML output functional equivalence validation ✓
- **SC-006**: Measure build time (moderate slowdown acceptable) ✓
- **SC-007**: Test locale switching via single config value ✓

---

## Notes

- [P] tasks = different files or independent sections, can run in parallel
- [Story] label maps task to specific user story (US1, US2, US3) for traceability
- User Story 1 is the MVP - delivers core refactoring value
- User Story 2 (i18n) depends on US1 being complete (needs Jinja2 + logging)
- User Story 3 (pydantic-settings) is optional enhancement, can be deferred
- Verify existing tests pass after each major milestone
- No new runtime dependencies - all libraries are build-time only
- Performance monitoring throughout (constitution gate: asset sizes, build time)
