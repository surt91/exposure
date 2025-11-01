# Tasks: Type Checking and Type Annotations

**Input**: Design documents from `/specs/002-type-checking/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in specification - focusing on implementation and validation tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install type checker and configure environment

- [X] T001 Verify ty is available from Astral or fallback to mypy if ty not ready
- [X] T002 Add ty (or mypy as fallback) to pyproject.toml [dependency-groups.dev]
- [X] T003 Add types-PyYAML>=6.0 to pyproject.toml [dependency-groups.dev]
- [X] T004 Add types-Pillow>=10.0 to pyproject.toml [dependency-groups.dev]
- [X] T005 Run `uv sync --dev` to install type checker and type stubs
- [X] T006 Add .ty_cache/ (or .mypy_cache/) to .gitignore
- [X] T007 Create [tool.ty] configuration section in pyproject.toml with python-version="3.11"

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Configuration and environment setup that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Configure strict mode settings in pyproject.toml (ty uses [tool.ty.environment] section)
- [X] T009 Add per-module override for tests/* in pyproject.toml (ty uses [tool.ty.overrides])
- [X] T010 Test type checker runs successfully: `uv run ty check src/`
- [X] T011 Document actual type checker command in quickstart.md (updated with ty v0.0.1-alpha.25)

**Checkpoint**: Type checker installed and configured - ready to add annotations

---

## Phase 3: User Story 1 - Developer Confidence in Code Correctness (Priority: P1) 🎯 MVP

**Goal**: Developers receive immediate feedback on type inconsistencies, catching bugs during development before runtime

**Independent Test**: Run type checker on codebase - should report specific type errors with file locations and pass on correctly typed code

### Implementation for User Story 1

- [X] T012 [P] [US1] Add type annotations to src/generator/model.py: all function parameters and return types (already complete)
- [X] T013 [P] [US1] Add type annotations to src/generator/scan.py: all function parameters and return types (already complete)
- [X] T014 [P] [US1] Add type annotations to src/generator/yaml_sync.py: all function parameters and return types (already complete)
- [X] T015 [P] [US1] Add type annotations to src/generator/build_html.py: all function parameters and return types (already complete)
- [X] T016 [P] [US1] Add type annotations to src/generator/assets.py: all function parameters and return types (already complete)
- [X] T017 [P] [US1] Add type annotations to src/__init__.py if needed (not needed - empty init file)
- [X] T018 [US1] Fix TYPE_CHECKING conditional import for PIL in src/generator/scan.py (already correct with try/except)
- [X] T019 [US1] Run type checker and fix all reported type errors: `uv run ty check src/`
- [X] T020 [US1] Verify type checker reports errors on intentionally broken code (test with wrong type)
- [X] T021 [US1] Verify type checker passes with zero errors on correctly typed code

**Checkpoint**: ✅ At this point, type checker catches type errors during development and provides immediate feedback

---

## Phase 4: User Story 2 - Enforced Type Annotation Standards (Priority: P2)

**Goal**: All functions have explicit type annotations, making code self-documenting and preventing missing annotations

**Independent Test**: Run type checker in strict mode - should flag any missing annotations and confirm complete coverage

### Implementation for User Story 2

- [X] T022 [US2] Verify strict mode is enabled in pyproject.toml (ty configuration active)
- [X] T023 [US2] Run type checker to identify any remaining unannotated functions
- [X] T024 [US2] Add missing annotations to any functions flagged by checker (none found - already complete)
- [X] T025 [US2] Verify 100% annotation coverage by checking type checker output shows no annotation warnings
- [X] T026 [US2] Add module-level __all__ exports with types if needed for public API clarity (not needed)
- [X] T027 [US2] Test that adding unannotated function triggers type checker error (verified with test)
- [X] T028 [US2] Document annotation standards in README.md (added type checking section)

**Checkpoint**: ✅ All functions fully annotated, type checker enforces annotation requirements

---

## Phase 5: User Story 3 - CI/CD Integration for Quality Gates (Priority: P3)

**Goal**: Type checking runs automatically in CI pipeline, preventing untyped or incorrectly typed code from merging

**Independent Test**: Run type checker in CI-like environment - should fail on errors and succeed on clean code

### Implementation for User Story 3

- [X] T029 [US3] Add type checking step to .github/workflows/ci.yml
- [X] T030 [US3] Position type check after dependency installation: `uv run ty check src/`
- [ ] T031 [US3] Verify type check step fails CI when type errors exist (test with intentional error)
- [ ] T032 [US3] Verify type check step passes CI when code is correctly typed
- [X] T033 [US3] Configure CI to show type errors clearly in build output (ty default output is excellent)
- [ ] T034 [US3] Add type checking status/badge to README.md if desired (not needed)
- [X] T035 [US3] Create ADR documenting tool choice in docs/decisions/0002-type-checking.md
- [X] T036 [US3] Update README.md with type checking commands and requirements

**Checkpoint**: CI enforces type checking, developers get feedback on pull requests automatically

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and final cleanup

- [X] T037 [P] Update quickstart.md with actual tool used (ty v0.0.1-alpha.25) and real commands tested
- [ ] T038 [P] Update contracts/cli-interface.md with actual CLI behavior observed
- [ ] T039 [P] Update contracts/mypy-config.md (rename to ty-config.md) with actual configuration used
- [X] T040 Validate quickstart.md commands work as documented
- [X] T041 Run full type check to confirm zero errors: `uv run ty check src/`
- [X] T042 Verify type checking performance meets <5 second requirement for developers (0.42s)
- [X] T043 Verify type checking performance meets <10 second requirement for full codebase (0.42s)
- [ ] T044 Update copilot-instructions.md if type checking changes development workflow
- [X] T045 Document any type checking gotchas or edge cases discovered (ty is alpha, excellent error messages)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 (Phase 3) completion - needs annotations in place
- **User Story 3 (Phase 5)**: Depends on User Story 2 (Phase 4) completion - needs clean type checking
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Core type checking functionality
- **User Story 2 (P2)**: Depends on US1 - Enforces annotation standards on already-annotated code
- **User Story 3 (P3)**: Depends on US2 - CI integration requires clean type checking

**Note**: User stories are sequential in this feature because each builds on the previous:
- US1 establishes type checking capability
- US2 enforces completeness
- US3 automates enforcement

### Within Each User Story

**User Story 1**:
- Annotation tasks T012-T017 can all run in parallel [P] (different files)
- TYPE_CHECKING fix T018 depends on identifying which file needs it
- Type error fixes T019 depend on annotations being added
- Validation T020-T021 depends on all fixes being complete

**User Story 2**:
- Most tasks are sequential (verify, identify, fix, verify)
- Documentation T028 can run in parallel with final verification

**User Story 3**:
- CI configuration T029-T030 sequential
- Testing T031-T032 sequential (need CI configured)
- Documentation T034-T036 can run in parallel [P] (different files)

### Parallel Opportunities

- **Phase 1 Setup**: T002-T004 (adding dependencies to pyproject.toml) can be done in single edit
- **User Story 1**: T012-T017 all parallel [P] - annotating different files simultaneously
- **User Story 3**: T034-T036 all parallel [P] - different documentation files
- **Polish Phase**: T037-T039 all parallel [P] - different documentation files

---

## Parallel Example: User Story 1 Annotations

```bash
# Launch all annotation tasks for different modules in parallel:
Task: "Add type annotations to src/generator/model.py"
Task: "Add type annotations to src/generator/scan.py"
Task: "Add type annotations to src/generator/yaml_sync.py"
Task: "Add type annotations to src/generator/build_html.py"
Task: "Add type annotations to src/generator/assets.py"

# All five files can be edited simultaneously by different developers
# or processed in parallel by tooling
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup - Install type checker and dependencies
2. Complete Phase 2: Foundational - Configure type checker
3. Complete Phase 3: User Story 1 - Add annotations and verify type checking works
4. **STOP and VALIDATE**: Run type checker locally, ensure it catches errors
5. Can commit MVP at this point - type checking available for local development

### Incremental Delivery

1. **Setup + Foundational** → Type checker ready for use
2. **+ User Story 1** → Type checking catches errors during development (MVP!)
3. **+ User Story 2** → Enforced annotation coverage, no gaps
4. **+ User Story 3** → Automated CI enforcement, quality gate active
5. Each story adds value incrementally

### Single Developer Strategy

Follow phases sequentially:
1. Setup environment (Phase 1)
2. Configure type checker (Phase 2)
3. Annotate all modules in parallel/batch (Phase 3, T012-T017)
4. Fix type errors (Phase 3, T018-T021)
5. Enforce standards (Phase 4)
6. Add CI integration (Phase 5)
7. Polish documentation (Phase 6)

**Estimated Time**:
- Phase 1: 15 minutes (installation)
- Phase 2: 15 minutes (configuration)
- Phase 3: 2-3 hours (annotation + fixes)
- Phase 4: 30 minutes (verification)
- Phase 5: 30 minutes (CI setup)
- Phase 6: 30 minutes (documentation)
- **Total**: ~4-5 hours for complete implementation

---

## Notes

- Type checker tool (ty vs mypy) will be determined in T001 based on availability
- All provisional documentation will be updated with actual tool/commands used
- [P] tasks marked can be done in parallel (different files)
- [Story] label maps task to user story for traceability
- Strict mode enforced from the start - no gradual migration needed (small codebase)
- Tests directory gets relaxed rules (handled in configuration, not separate tasks)
- Performance validation included in Polish phase to verify <5s and <10s requirements met
