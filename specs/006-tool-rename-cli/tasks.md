# Tasks: Tool Rename and CLI Simplification

**Input**: Design documents from `/specs/006-tool-rename-cli/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-entrypoint.md

**Tests**: Tests are NOT explicitly requested in the specification. Test tasks are included only for validation purposes - existing tests will be updated to reflect the rename, not new tests written.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization - prepare build environment

- [ ] T001 Verify all existing tests pass on branch `006-tool-rename-cli`
- [ ] T002 Run `grep -r "fotoview" . --exclude-dir=.git --exclude-dir=specs` to establish baseline of current references

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core package metadata and entry point that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Update package name from "fotoview" to "exposure" in `pyproject.toml`
- [ ] T004 Bump version from "0.1.0" to "0.2.0" in `pyproject.toml` (minor version for new CLI feature)
- [ ] T005 Add console_scripts entry point `exposure = "src.generator.build_html:main"` in `[project.scripts]` section of `pyproject.toml`
- [ ] T006 Run `uv sync` to reinstall package with new entry point
- [ ] T007 Verify new command works: `uv run exposure` successfully builds gallery

**Checkpoint**: Foundation ready - CLI command works, user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Simple Command Invocation (Priority: P1) 🎯 MVP

**Goal**: Developer can build gallery with simple command `uv run exposure` from project root

**Independent Test**: Clone repository, navigate to root, run `uv run exposure`, verify gallery builds successfully in output directory

### Implementation for User Story 1

- [ ] T008 [P] [US1] Update logger name from `logging.getLogger("fotoview")` to `logging.getLogger("exposure")` in `src/generator/__init__.py`
- [ ] T009 [P] [US1] Update logger name from `logging.getLogger("fotoview")` to `logging.getLogger("exposure")` in `src/generator/build_html.py`
- [ ] T010 [P] [US1] Update logger name from `logging.getLogger("fotoview")` to `logging.getLogger("exposure")` in `src/generator/i18n.py`
- [ ] T011 [P] [US1] Update logger name from `logging.getLogger("fotoview")` to `logging.getLogger("exposure")` in `src/generator/model.py`
- [ ] T012 [P] [US1] Update logger name from `logging.getLogger("fotoview")` to `logging.getLogger("exposure")` in `src/generator/scan.py`
- [ ] T013 [P] [US1] Update logger name from `logging.getLogger("fotoview")` to `logging.getLogger("exposure")` in `src/generator/yaml_sync.py`
- [ ] T014 [P] [US1] Update logger name from `logging.getLogger("fotoview")` to `logging.getLogger("exposure")` in `src/generator/assets.py`
- [ ] T015 [US1] Change environment variable prefix from `env_prefix="FOTOVIEW_"` to `env_prefix="EXPOSURE_"` in GalleryConfig model in `src/generator/model.py`
- [ ] T016 [US1] Update module docstrings that reference "fotoview" across all files in `src/generator/` directory
- [ ] T017 [US1] Test command with environment variable override: `EXPOSURE_LOCALE=de uv run exposure`
- [ ] T018 [US1] Test command with multiple environment overrides: `EXPOSURE_LOG_LEVEL=DEBUG EXPOSURE_OUTPUT_DIR=build uv run exposure`
- [ ] T019 [US1] Update README quickstart section to use `uv run exposure` command instead of `uv run python -m src.generator.build_html`
- [ ] T020 [US1] Update all command examples in README.md to use new `EXPOSURE_*` environment variable prefix
- [ ] T021 [US1] Add entry to CHANGELOG.md for version 0.2.0 documenting the rename and new CLI command

**Checkpoint**: At this point, User Story 1 is complete - developers can use simple `uv run exposure` command successfully

---

## Phase 4: User Story 2 - Clear Project Identity (Priority: P2)

**Goal**: Project name "exposure" is clear, memorable, and consistently used in all branding touchpoints

**Independent Test**: Search all documentation, code, and configuration for tool references and verify all use consistent new name

### Implementation for User Story 2

- [ ] T022 [P] [US2] Update translatable string from `_("Fotoview Gallery Generator")` to `_("Exposure Gallery Generator")` in `src/generator/build_html.py`
- [ ] T023 [P] [US2] Update meta generator tag from `<meta name="generator" content="Fotoview">` to `<meta name="generator" content="Exposure">` in `src/templates/index.html.j2`
- [ ] T024 [P] [US2] Update meta generator tag if present in `src/templates/fullscreen.html.j2`
- [ ] T025 [US2] Extract new translatable strings: `uv run pybabel extract -F babel.cfg -o locales/messages.pot .`
- [ ] T026 [US2] Update .po files with new strings: `uv run pybabel update -i locales/messages.pot -d locales`
- [ ] T027 [US2] Manually edit `locales/de/LC_MESSAGES/messages.po` to translate "Exposure Gallery Generator" to "Exposure Galerie-Generator"
- [ ] T028 [US2] Update any other German translation strings that reference "Fotoview" in `locales/de/LC_MESSAGES/messages.po`
- [ ] T029 [US2] Compile translations: `uv run pybabel compile -d locales`
- [ ] T030 [US2] Test English output: Run `uv run exposure` and verify log shows "Exposure Gallery Generator"
- [ ] T031 [US2] Test German output: Run `EXPOSURE_LOCALE=de uv run exposure` and verify log shows "Exposure Galerie-Generator"
- [ ] T032 [US2] Verify generated HTML contains correct meta tag: `grep 'generator' dist/index.html`
- [ ] T033 [US2] Update project title from "# Fotoview" to "# Exposure" in README.md
- [ ] T034 [US2] Update project description references from "fotoview" to "exposure" in README.md introduction

**Checkpoint**: At this point, User Stories 1 AND 2 are complete - command works and branding is consistent in user-facing output

---

## Phase 5: User Story 3 - Consistent Documentation (Priority: P3)

**Goal**: All documentation, error messages, and code references use consistent new name with no confusing old references

**Independent Test**: Search all documentation and code files for tool name references and verify consistency

### Implementation for User Story 3

- [ ] T035 [P] [US3] Update header comment from "# Fotoview Gallery Configuration" to "# Exposure Gallery Configuration" in `config/settings.yaml`
- [ ] T036 [P] [US3] Update copyright holder from "fotoview contributors" to "exposure contributors" in LICENSE file
- [ ] T037 [P] [US3] Search and update SPDX license headers that reference "fotoview contributors" in all Python source files in `src/` directory
- [ ] T038 [P] [US3] Update all command examples in `docs/i18n-workflow.md` to use `EXPOSURE_*` environment variables
- [ ] T039 [P] [US3] Update tool name references in `docs/hosting.md`
- [ ] T040 [P] [US3] Review and update project name references in all ADR files in `docs/decisions/` directory
- [ ] T041 [P] [US3] Update project title and references in `.github/copilot-instructions.md`
- [ ] T042 [P] [US3] Update environment variable tests from `monkeypatch.setenv("FOTOVIEW_LOCALE", ...)` to `monkeypatch.setenv("EXPOSURE_LOCALE", ...)` in `tests/unit/test_model.py`
- [ ] T043 [P] [US3] Update environment variable tests in any other test files in `tests/unit/` directory
- [ ] T044 [P] [US3] Update string assertions from "Fotoview Gallery Generator" to "Exposure Gallery Generator" in `tests/unit/test_i18n.py`
- [ ] T045 [P] [US3] Update string assertions and logger name tests in `tests/unit/test_build_html.py`
- [ ] T046 [P] [US3] Review and update tool name references in integration tests in `tests/integration/` directory
- [ ] T047 [P] [US3] Review and update tool name references in accessibility tests in `tests/accessibility/` directory
- [ ] T048 [US3] Run full test suite to verify all tests pass: `uv run pytest`
- [ ] T049 [US3] Run test suite with coverage to ensure no regressions: `uv run pytest --cov=src --cov-report=html`
- [ ] T050 [US3] Run linter to verify code quality: `uv run ruff check .`
- [ ] T051 [US3] Search for remaining old references: `grep -r "fotoview" . --exclude-dir=.git --exclude-dir=specs --exclude-dir=dist` (should find minimal/acceptable references)

**Checkpoint**: All user stories complete - documentation is fully consistent with new name

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and quality checks across all user stories

- [ ] T052 Verify quickstart.md validation: Follow all steps in `specs/006-tool-rename-cli/quickstart.md` Layer 1-8
- [ ] T053 Run comprehensive smoke test: `uv run exposure` builds successfully
- [ ] T054 Run comprehensive smoke test: `EXPOSURE_LOCALE=de uv run exposure` builds with German locale
- [ ] T055 Run comprehensive smoke test: `EXPOSURE_OUTPUT_DIR=build uv run exposure` outputs to custom directory
- [ ] T056 Verify generated HTML quality: Check `dist/index.html` for correct meta tag and no old references
- [ ] T057 Run type checking if configured: Verify no type errors introduced
- [ ] T058 Final search validation: Confirm only acceptable "fotoview" references remain (specs/, git history, intentional)
- [ ] T059 Update .github/copilot-instructions.md with new command syntax in Commands section
- [ ] T060 Commit all changes with message: "Rename tool from fotoview to exposure with simple CLI command"

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational (Phase 2) completion
  - User Story 1 can start immediately after Foundational
  - User Story 2 can start after Foundational (can run parallel with US1 for most tasks)
  - User Story 3 can start after Foundational (some tasks depend on US1/US2 being complete)
- **Polish (Phase 6)**: Depends on all user stories (Phase 3-5) being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends only on Foundational (Phase 2) - Core CLI functionality
- **User Story 2 (P2)**: Depends on Foundational (Phase 2) - Can start parallel with US1, but translations (T025-T029) should wait until US1 T022 completes to capture all new strings
- **User Story 3 (P3)**: Depends on Foundational (Phase 2) - Documentation and test updates reference new command from US1, so T042-T047 should wait for US1 completion

### Within Each User Story

**User Story 1**:
- T008-T014 can all run in parallel (different files, all logger updates)
- T015 must wait for logger updates to maintain consistency
- T016 should follow T008-T015 to avoid conflicts
- T017-T018 are validation tests, run after T015
- T019-T021 are documentation, can run parallel after T017-T018 validation

**User Story 2**:
- T022-T024 can all run in parallel (different files)
- T025-T029 must run sequentially (Babel workflow is sequential)
- T030-T032 are validation tests
- T033-T034 can run parallel with translations after T022 completes

**User Story 3**:
- T035-T047 can all run in parallel (different files)
- T048-T051 must run sequentially (validation sequence)

### Parallel Opportunities

**Foundational Phase (Phase 2)**: T003-T005 can be done in single edit of pyproject.toml, then T006-T007 sequentially

**User Story 1**: Tasks T008-T014 (7 logger updates) can all run in parallel

**User Story 2**: Tasks T022-T024 (3 template updates) can run in parallel

**User Story 3**: Tasks T035-T047 (13 documentation/test updates) can all run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all logger updates together:
Task: "Update logger name in src/generator/__init__.py"
Task: "Update logger name in src/generator/build_html.py"
Task: "Update logger name in src/generator/i18n.py"
Task: "Update logger name in src/generator/model.py"
Task: "Update logger name in src/generator/scan.py"
Task: "Update logger name in src/generator/yaml_sync.py"
Task: "Update logger name in src/generator/assets.py"
```

## Parallel Example: User Story 3

```bash
# Launch all documentation and test updates together:
Task: "Update header comment in config/settings.yaml"
Task: "Update copyright in LICENSE"
Task: "Update SPDX headers in src/"
Task: "Update docs/i18n-workflow.md"
Task: "Update docs/hosting.md"
Task: "Update docs/decisions/"
Task: "Update .github/copilot-instructions.md"
Task: "Update tests/unit/test_model.py"
Task: "Update tests/unit/test_i18n.py"
Task: "Update tests/unit/test_build_html.py"
Task: "Update tests/integration/"
Task: "Update tests/accessibility/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002) - ~5 minutes
2. Complete Phase 2: Foundational (T003-T007) - ~15 minutes
3. Complete Phase 3: User Story 1 (T008-T021) - ~45 minutes
4. **STOP and VALIDATE**: Test `uv run exposure` command works
5. Can deploy/demo basic CLI at this point if needed

**Total MVP Time**: ~65 minutes

### Incremental Delivery

1. Complete Setup + Foundational (T001-T007) → CLI command works
2. Add User Story 1 (T008-T021) → Simple command ready for developers → Deploy/Demo (MVP!)
3. Add User Story 2 (T022-T034) → Professional branding complete → Deploy/Demo
4. Add User Story 3 (T035-T051) → Full documentation consistency → Deploy/Demo
5. Polish (T052-T060) → Production ready

**Total Time Estimate**: ~2.5 hours (matches quickstart.md estimate)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T007)
2. Once Foundational is done:
   - Developer A: User Story 1 (T008-T021) - Core CLI
   - Developer B: User Story 2 starting with T022-T024, wait for A's T022 completion before T025-T029 - Branding
   - Developer C: Wait for A completion, then User Story 3 (T035-T051) - Documentation
3. Developer A can help with validation once US1 complete
4. Team converges on Polish phase (T052-T060)

---

## Validation Checklist

After completing all tasks:

- [ ] `uv run exposure` builds gallery successfully
- [ ] Generated HTML has correct meta tag: `<meta name="generator" content="Exposure">`
- [ ] German locale works: `EXPOSURE_LOCALE=de uv run exposure`
- [ ] Environment overrides work: `EXPOSURE_OUTPUT_DIR=build uv run exposure`
- [ ] All tests pass: `uv run pytest`
- [ ] Test coverage maintained: `uv run pytest --cov=src`
- [ ] Linting passes: `uv run ruff check .`
- [ ] Type checking passes (if configured)
- [ ] README examples use new command
- [ ] CHANGELOG documents the change
- [ ] No "fotoview" in user-facing strings (except historical/intentional references)
- [ ] Search validation: `grep -r "fotoview" . --exclude-dir=.git --exclude-dir=specs` returns only acceptable results

---

## Notes

- **[P] tasks**: Different files, no dependencies - safe for parallel execution
- **[Story] label**: Maps task to specific user story for traceability and independent delivery
- **Command reduction**: From 41 characters (`uv run python -m src.generator.build_html`) to 18 characters (`uv run exposure`) - 56% reduction
- **No breaking changes**: gallery.yaml format unchanged, existing build reproducibility maintained
- **Clean break**: Old `FOTOVIEW_*` environment variables not supported - no backward compatibility needed
- **Repository name**: GitHub repo remains "fotoview" to preserve links and history
- **Backward compatibility**: Old module invocation `python -m src.generator.build_html` continues to work as Python language feature
- **Translation workflow**: Standard Babel extract-update-compile maintains translation quality
- **Asset budgets**: No changes to generated HTML/CSS/JS output, only meta tag update

---

## Risk Mitigation

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Missed reference in obscure file | Medium | Comprehensive grep searches at T002, T051, T058 |
| Translation compilation fails | Low | Test Babel workflow in T025-T029, validate in T030-T031 |
| Tests break with new command | Medium | Run test suite after each phase (T048-T049), incremental fixes |
| Logger name inconsistency | Low | Parallel execution of T008-T014 with clear file paths |
| Environment variable confusion | Low | Clear documentation in T019-T020, examples in T017-T018 |

---

## Summary

- **Total Tasks**: 60 tasks across 6 phases
- **Task Distribution**:
  - Phase 1 (Setup): 2 tasks
  - Phase 2 (Foundational): 5 tasks
  - Phase 3 (US1): 14 tasks
  - Phase 4 (US2): 13 tasks
  - Phase 5 (US3): 17 tasks
  - Phase 6 (Polish): 9 tasks
- **Parallel Opportunities**: 33 tasks marked [P] can run in parallel within their phase
- **MVP Scope**: Complete Phases 1-3 (T001-T021) for basic CLI functionality
- **Suggested Delivery**: Incremental - MVP first, then add US2 and US3 for complete polish
- **Estimated Time**: 2.5 hours total (following quickstart.md guidance)
- **Independent Tests**: Each user story has clear acceptance criteria for independent validation
