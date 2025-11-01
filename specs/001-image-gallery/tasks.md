---
description: "Task list for Modern Image Gallery implementation"
---

# Tasks: Modern Image Gallery

**Input**: Design documents from `/specs/001-image-gallery/`
**Prerequisites**: plan.md (required), spec.md, research.md, data-model.md, contracts/

**Tests**: Tests included (unit + integration) to ensure generator correctness and accessibility/performance hooks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create base directories (src/generator, src/static/css, src/static/js, src/templates, tests/unit, tests/integration, config, content)
- [X] T002 Initialize Python project metadata (pyproject.toml) with PyYAML + Pillow (optional) deps at repository root (managed via uv)
- [X] T002a [P] Generate uv lock file `uv.lock` ensuring reproducible dependency resolution
- [X] T002b [P] Add `uv` install & run instructions to README (development + test commands)
- [X] T002c Add CI workflow step placeholder for `uv sync` in `.github/workflows/ci.yml`
- [X] T003 Create `config/settings.yaml` with default paths (content_dir, gallery_yaml_path, default_category, enable_thumbnails)
- [X] T004 Add `.gitignore` entries for `dist/` and cache artifacts
- [X] T005 [P] Create placeholder `config/gallery.yaml` with categories list and empty images section
- [X] T006 [P] Create initial README quickstart section referencing generator usage
- [X] T007 Add LICENSE placeholder (if required) in repository root
- [X] T008 Configure basic `pytest` settings (add `tests/__init__.py` and `pytest.ini`)
- [X] T009 Add initial CHANGELOG.md with Unreleased section

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T010 Implement data models in `src/generator/model.py` (Image, Category, GalleryConfig, YamlEntry)
- [X] T011 [P] Implement YAML loader/saver utilities in `src/generator/yaml_sync.py` (read, write, stub append)
- [X] T012 [P] Implement image scanning logic in `src/generator/scan.py` (discover files, detect duplicates)
- [X] T013 Implement basic hashing utility in `src/generator/assets.py` (hash + copy static assets)
- [X] T014 Create template placeholders: `src/templates/index.html.tpl` and `src/templates/fullscreen.html.part` (structure only)
- [X] T015 [P] Add unit tests for models and validation rules in `tests/unit/test_model.py`
- [X] T016 [P] Add unit tests for YAML sync (existing entry, stub creation) in `tests/unit/test_yaml_sync.py`
- [X] T017 Add unit tests for scan behavior (duplicates, filtering) in `tests/unit/test_scan.py`
- [X] T018 Establish build script entry point stub `src/generator/build_html.py` (parse settings, orchestrate pipeline skeleton)
- [X] T019 Integration test skeleton `tests/integration/test_end_to_end.py` (invokes build and asserts basic outputs exist)
- [X] T020 Add accessibility test harness placeholder script `tests/accessibility/axe_runner.sh` (to be wired in CI)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Browse Scrollable Gallery (Priority: P1) 🎯 MVP

**Goal**: Display scrollable gallery with category ordering from YAML

**Independent Test**: Given sample YAML with categories A then B, generated `dist/index.html` lists A images then B images; >30 images scroll without layout breakage; asset budget script passes.

### Tests for User Story 1

- [X] T021 [P] [US1] Add template logic for category ordering & image loops in `src/templates/index.html.tpl`
- [X] T022 [P] [US1] Implement gallery HTML generation in `src/generator/build_html.py` (index page rendering)
- [X] T023 [US1] Implement CSS baseline (responsive grid, mobile friendly) in `src/static/css/gallery.css`
- [X] T024 [P] [US1] Implement JS for lazy loading / progressive enhancement in `src/static/js/gallery.js`
- [X] T025 [US1] Add unit test for category ordering in `tests/unit/test_build_html.py`
- [X] T026 [US1] Extend integration test verifying scrollable content structure in `tests/integration/test_end_to_end.py`
- [X] T027 [US1] Add asset budget enforcement test `tests/integration/test_asset_budgets.py` (HTML ≤30KB, critical CSS ≤25KB, initial JS ≤75KB uncompressed)
- [X] T027a [P] [US1] Add CI workflow step to run asset budget & Lighthouse checks `.github/workflows/ci.yml` (fail if thresholds exceeded)
- [X] T028 [US1] Generate dist output and manual verify (document in test) `dist/index.html`

**Checkpoint**: Gallery MVP complete; fulfills SC-001, partial SC-004

---

## Phase 4: User Story 2 - View Image Fullscreen (Priority: P2)

**Goal**: Fullscreen overlay/modal on image click with metadata, keyboard navigation

**Independent Test**: Clicking image opens overlay; esc closes; left/right cycle; focus returns to originating thumbnail

### Tests for User Story 2

- [X] T029 [P] [US2] Implement overlay HTML partial injection logic in `src/generator/build_html.py`
- [X] T030 [US2] Add JS overlay controller in `src/static/js/fullscreen.js`
- [X] T031 [P] [US2] Add ARIA roles & focus trapping helpers in `src/static/js/a11y.js`
- [X] T032 [US2] Add metadata (filename/category) display mapping inside overlay template part `src/templates/fullscreen.html.part`
- [X] T033 [US2] Add unit tests for overlay markup generation in `tests/unit/test_build_html.py` (extend existing)
- [X] T034 [US2] Add integration test for fullscreen open/close behavior (DOM presence) `tests/integration/test_fullscreen.py`
- [ ] T035 [US2] Add accessibility test case in axe harness referencing overlay `tests/accessibility/axe_runner.sh`
- [X] T036 [US2] Update performance budget test if overlay assets increase size `tests/integration/test_performance_budget.py`
 - [X] T035a [US2] Add fullscreen latency test `tests/integration/test_fullscreen_latency.py` (overlay visible <300ms average over 5 opens)

**Checkpoint**: Fullscreen feature complete; fulfills SC-002 & part of accessibility goals

---

## Phase 5: User Story 3 - YAML Auto-Stub Generation (Priority: P3)

**Goal**: Auto-append stub entries for missing images preserving category order

**Independent Test**: Add new images (not in YAML) → run build → YAML updated with stubs at end under default category

### Tests for User Story 3

- [X] T037 [P] [US3] Implement stub detection & append in `src/generator/yaml_sync.py` (extend earlier logic)
- [X] T038 [US3] Add unit tests for stub generation ordering in `tests/unit/test_yaml_sync.py`
- [X] T039 [P] [US3] Add integration test adding new images then verifying YAML updated `tests/integration/test_stub_generation.py`
- [X] T040 [US3] Add validation: no category order mutation in `tests/integration/test_stub_generation.py`
- [X] T041 [US3] Update end-to-end test to include stub scenario `tests/integration/test_end_to_end.py`
 - [ ] T041a [US3] Add stub coverage test `tests/integration/test_stub_coverage.py` (assert 100% content/ images represented in YAML after build)
 - [ ] T041b [P] [US3] Add batch stub generation performance test `tests/integration/test_stub_batch.py` (50 new images; ordering preserved; runtime <5s)

**Checkpoint**: Auto-stub functionality complete; fulfills SC-003 & SC-005

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T042 [P] Add hashing integration for static assets in `src/generator/assets.py` (inject hashed names into HTML)
- [ ] T043 Add reproducibility check script `tests/integration/test_reproducibility.py` (two builds identical hashes)
- [ ] T044 [P] Add CSP documentation file `docs/hosting.md` with header config
- [ ] T045 Add ADR 0001 for templating decision in `docs/decisions/0001-templating.md`
- [ ] T046 Performance optimization pass (evaluate image decoding hints) in `src/static/js/gallery.js`
- [ ] T047 [P] Add keyboard navigation tests for arrow keys in `tests/integration/test_fullscreen.py`
- [ ] T048 Add README section for accessibility & performance budgets
- [ ] T049 Security review checklist update `docs/decisions/0002-security-baseline.md`
- [ ] T050 [P] Add optional Pillow thumbnail generation path in `src/generator/scan.py` & config flag integration
- [ ] T051 Add coverage configuration (if desired) `pyproject.toml` updates + integrate with `uv run`
- [ ] T052 Final Lighthouse / axe report capture for documentation `docs/metrics/INITIAL_REPORT.md`
 - [ ] T053 Add release changelog update script `scripts/update_changelog.py`
 - [ ] T054 Add release workflow `.github/workflows/release.yml` (tag + CHANGELOG verification)
 - [ ] T055 Add changelog gate script `scripts/check_changelog.py` (fail PR if version entry missing)
 - [ ] T056 Add governance review checklist `docs/governance/review_checklist.md`
 - [ ] T057 Add monthly governance CI workflow `.github/workflows/monthly_governance.yml` (schedule monthly)

---

## Dependencies & Execution Order

### Phase Dependencies
- Setup (Phase 1) → Foundational (Phase 2) → User Stories (3 → 4 → 5) → Polish (Phase 6)
- User Stories 2 and 3 depend on completion of Foundational + relevant prior story assets where shared (overlay relies on gallery structure; stub logic independent but uses YAML utilities)

### User Story Independence
- US1 independent after Foundation
- US2 depends on gallery markup for thumbnails
- US3 depends on YAML utilities only (can theoretically run parallel with US2 after Foundation)

### Parallel Opportunities
- Marked [P] tasks in each phase: independent files (e.g., separate modules, tests)
- After Foundation, US2 and US3 can proceed in parallel once US1 core HTML loop stable (T021–T024 completion)

## Parallel Example: User Story 1

```bash
# Parallelizable tasks after foundational completion:
T021, T022, T024 can proceed together (template, generator logic, JS) while T023 (CSS) runs concurrently.
```

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Phase 1 & 2
2. Implement Phase 3 (US1)
3. Validate performance + accessibility basics
4. Ship MVP

### Incremental Delivery
1. Add US2 fullscreen overlay
2. Add US3 auto-stub generation
3. Apply Polish phase

### Parallel Team Strategy
After Phase 2:
- Dev A: US1 templates & build logic (T021–T022)
- Dev B: US1 CSS/JS (T023–T024)
- Dev C: Prepare US2 overlay groundwork (blocked until T021 complete)

## Notes
- Tasks ensure each story is independently testable.
- Tests front-load validation for YAML, scanning, and build reproducibility.
- Accessibility and performance integrated early to satisfy constitution.
