# Tasks: Apache 2.0 License

**Input**: Design documents from `/specs/004-apache-license/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/license-header-format.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparation and verification before license addition

- [ ] T001 Verify current working directory is repository root (/home/surt91/code/fotoview)
- [ ] T002 Verify git working tree is clean (no uncommitted changes)
- [ ] T003 Create backup branch or tag for rollback safety

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core license files that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: User Story 2 and 3 depend on these files existing

- [ ] T004 Download official Apache 2.0 license text from https://www.apache.org/licenses/LICENSE-2.0.txt
- [ ] T005 Create LICENSE file in repository root with copyright notice "Copyright 2025 fotoview contributors" prepended to license text
- [ ] T006 Verify LICENSE file is exactly 361 lines using `wc -l LICENSE`
- [ ] T007 Verify LICENSE file contains "Apache License" and "Version 2.0, January 2004"

**Checkpoint**: LICENSE file ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Legal Clarity for Users and Contributors (Priority: P1) 🎯 MVP

**Goal**: Provide clear Apache 2.0 license in repository root so users and contributors understand usage terms

**Independent Test**: LICENSE file exists in repository root with complete Apache 2.0 text including copyright notice

### Implementation for User Story 1

- [ ] T008 [US1] Add LICENSE file to git staging area using `git add LICENSE`
- [ ] T009 [US1] Create commit with message "feat: add Apache 2.0 LICENSE file"
- [ ] T010 [US1] Verify commit contains LICENSE file using `git show --name-only`

**Checkpoint**: At this point, User Story 1 is complete and the repository has legal clarity. This is the MVP.

---

## Phase 4: User Story 2 - License Declaration in Source Files (Priority: P2)

**Goal**: Add SPDX license headers to all source files so licensing is clear when files are viewed individually

**Independent Test**: All Python, JavaScript, and CSS source files contain "SPDX-License-Identifier: Apache-2.0" header

### Implementation for User Story 2 - Python Files

- [ ] T011 [P] [US2] Add license header to src/__init__.py (2 lines: copyright + SPDX)
- [ ] T012 [P] [US2] Add license header to src/generator/__init__.py
- [ ] T013 [P] [US2] Add license header to src/generator/assets.py
- [ ] T014 [P] [US2] Add license header to src/generator/build_html.py (after shebang if present)
- [ ] T015 [P] [US2] Add license header to src/generator/model.py
- [ ] T016 [P] [US2] Add license header to src/generator/scan.py
- [ ] T017 [P] [US2] Add license header to src/generator/yaml_sync.py
- [ ] T018 [P] [US2] Add license header to tests/__init__.py
- [ ] T019 [P] [US2] Add license header to tests/accessibility/__init__.py
- [ ] T020 [P] [US2] Add license header to tests/accessibility/test_axe_a11y.py
- [ ] T021 [P] [US2] Add license header to tests/integration/test_asset_budgets.py
- [ ] T022 [P] [US2] Add license header to tests/integration/test_end_to_end.py
- [ ] T023 [P] [US2] Add license header to tests/integration/test_fullscreen.py
- [ ] T024 [P] [US2] Add license header to tests/integration/test_reproducibility.py
- [ ] T025 [P] [US2] Add license header to tests/unit/test_build_html.py
- [ ] T026 [P] [US2] Add license header to tests/unit/test_model.py
- [ ] T027 [P] [US2] Add license header to tests/unit/test_scan.py
- [ ] T028 [P] [US2] Add license header to tests/unit/test_yaml_sync.py

### Implementation for User Story 2 - JavaScript Files

- [ ] T029 [P] [US2] Add license header to src/static/js/a11y.js (block comment format)
- [ ] T030 [P] [US2] Add license header to src/static/js/fullscreen.js (block comment format)
- [ ] T031 [P] [US2] Add license header to src/static/js/gallery.js (block comment format)

### Implementation for User Story 2 - CSS Files

- [ ] T032 [P] [US2] Add license header to src/static/css/gallery.css (block comment format)
- [ ] T033 [P] [US2] Add license header to src/static/css/fullscreen.css (block comment format)

### Implementation for User Story 2 - Metadata Files

- [ ] T034 [US2] Add license field to pyproject.toml in [project] section: `license = "Apache-2.0"`
- [ ] T035 [US2] Add License section to README.md with text: "This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details."

### Verification for User Story 2

- [ ] T036 [US2] Verify all Python files have headers: `find src tests -name "*.py" | xargs grep -L "SPDX-License-Identifier: Apache-2.0"` (should return empty)
- [ ] T037 [US2] Verify all JavaScript files have headers: `find src/static/js -name "*.js" | xargs grep -L "SPDX-License-Identifier: Apache-2.0"` (should return empty)
- [ ] T038 [US2] Verify all CSS files have headers: `find src/static/css -name "*.css" | xargs grep -L "SPDX-License-Identifier: Apache-2.0"` (should return empty)
- [ ] T039 [US2] Verify pyproject.toml contains `license = "Apache-2.0"` using `grep 'license = "Apache-2.0"' pyproject.toml`
- [ ] T040 [US2] Verify README.md contains License section using `grep "## License" README.md`
- [ ] T041 [US2] Count total files with headers (should be ~25): `find src tests -name "*.py" -o -name "*.js" -o -name "*.css" | xargs grep -l "SPDX-License-Identifier: Apache-2.0" | wc -l`

### Git Operations for User Story 2

- [ ] T042 [US2] Stage all modified source files: `git add src/ tests/ pyproject.toml README.md`
- [ ] T043 [US2] Create commit with message: "feat: add Apache 2.0 license headers to all source files\n\n- Add SPDX headers to Python files (src/, tests/)\n- Add SPDX headers to JavaScript files (src/static/js/)\n- Add SPDX headers to CSS files (src/static/css/)\n- Update pyproject.toml with license metadata\n- Add License section to README.md"
- [ ] T044 [US2] Verify commit using `git show --stat` (should show ~28 files changed)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. All source files have license headers.

---

## Phase 5: User Story 3 - GitHub License Badge and Recognition (Priority: P3)

**Goal**: GitHub automatically detects Apache 2.0 license and displays badge in repository sidebar

**Independent Test**: Visit repository on GitHub and verify "License: Apache-2.0" badge appears in sidebar

### Implementation for User Story 3

- [ ] T045 [US3] Push all commits to GitHub: `git push origin 004-apache-license`
- [ ] T046 [US3] Wait 5 minutes for GitHub's initial processing
- [ ] T047 [US3] Visit repository on GitHub (https://github.com/surt91/fotoview)
- [ ] T048 [US3] Check repository sidebar shows "License: Apache-2.0"
- [ ] T049 [US3] Click license badge to verify it links to LICENSE file
- [ ] T050 [US3] Check repository "About" section displays license badge

### Optional Enhancement for User Story 3

- [ ] T051 [P] [US3] Add shields.io license badge to README.md: `[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)`
- [ ] T052 [US3] Commit badge addition: `git add README.md && git commit -m "docs: add license badge to README"`
- [ ] T053 [US3] Push badge commit: `git push origin 004-apache-license`

**Checkpoint**: All user stories should now be independently functional. Repository is fully Apache 2.0 licensed with GitHub recognition.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [ ] T054 Verify no license headers in excluded files (config/, docs/, specs/, output/, __pycache__/)
- [ ] T055 Run manual verification checklist from specs/004-apache-license/quickstart.md
- [ ] T056 Optional: Run `licensee detect .` if licensee gem installed (should output "Apache-2.0")
- [ ] T057 Create pull request to merge 004-apache-license branch to main
- [ ] T058 Review PR for completeness (all files modified, no unexpected changes)
- [ ] T059 Merge PR to main branch
- [ ] T060 Verify GitHub license detection on main branch (may take up to 24 hours)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase (LICENSE file) completion
  - User Story 1 (T008-T010): Depends on T004-T007 (LICENSE file created)
  - User Story 2 (T011-T044): Can start after Phase 2, but logically follows US1
  - User Story 3 (T045-T053): Depends on US1 and US2 being committed and pushed
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can complete after Foundational (Phase 2) - Independent (just LICENSE file)
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent (source headers) but references LICENSE
- **User Story 3 (P3)**: MUST have US1 committed and pushed to GitHub - Depends on GitHub detecting LICENSE file

### Within Each User Story

- **User Story 1**: Sequential (T004→T005→T006→T007→T008→T009→T010)
- **User Story 2**: 
  - T011-T033: All [P] - can run in parallel (different files)
  - T034-T035: Sequential after headers (metadata files)
  - T036-T041: Sequential verification after all additions
  - T042-T044: Sequential git operations
- **User Story 3**: Sequential (must wait for GitHub, then check results)

### Parallel Opportunities

- **Setup tasks**: T001-T003 can be done quickly in sequence (verification tasks)
- **Foundational tasks**: T004-T007 sequential (creating/verifying LICENSE)
- **User Story 2 headers**: T011-T033 ALL [P] - 23 files can be edited in parallel by different team members or tools
  - Python files: T011-T028 (18 files)
  - JavaScript files: T029-T031 (3 files)
  - CSS files: T032-T033 (2 files)
- **Verification tasks**: T036-T041 can run in parallel (different grep commands)

---

## Parallel Example: User Story 2 Headers

```bash
# All Python header additions can happen simultaneously:
T011: Add header to src/__init__.py
T012: Add header to src/generator/__init__.py
T013: Add header to src/generator/assets.py
T014: Add header to src/generator/build_html.py
... (all 18 Python files)

# All JavaScript header additions can happen simultaneously:
T029: Add header to src/static/js/a11y.js
T030: Add header to src/static/js/fullscreen.js
T031: Add header to src/static/js/gallery.js

# All CSS header additions can happen simultaneously:
T032: Add header to src/static/css/gallery.css
T033: Add header to src/static/css/fullscreen.css
```

**Bulk Addition Script** (from quickstart.md):
```bash
# Python files (for files without shebang/encoding):
for file in src/**/*.py tests/**/*.py; do
    echo "# Copyright 2025 fotoview contributors
# SPDX-License-Identifier: Apache-2.0

$(cat $file)" > $file
done

# JavaScript files:
for file in src/static/js/*.js; do
    echo "/*
 * Copyright 2025 fotoview contributors
 * SPDX-License-Identifier: Apache-2.0
 */

$(cat $file)" > $file
done

# CSS files:
for file in src/static/css/*.css; do
    echo "/*
 * Copyright 2025 fotoview contributors
 * SPDX-License-Identifier: Apache-2.0
 */

$(cat $file)" > $file
done
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T007) - LICENSE file created
3. Complete Phase 3: User Story 1 (T008-T010) - LICENSE committed
4. **STOP and VALIDATE**: Verify LICENSE file exists and is correct
5. Push to GitHub - repository now has legal clarity (MVP complete!)

### Incremental Delivery

1. Complete Setup + Foundational → LICENSE file ready (T001-T007)
2. Add User Story 1 → LICENSE committed (T008-T010) → Push (MVP!)
3. Add User Story 2 → All source headers added (T011-T044) → Push
4. Add User Story 3 → GitHub detection verified (T045-T053) → Complete
5. Polish → Final validation (T054-T060)

### Parallel Team Strategy

With multiple developers:

1. **Phase 1-2**: One developer creates LICENSE file (T001-T007)
2. **Phase 3**: Same developer commits LICENSE (T008-T010) → Push (MVP)
3. **Phase 4 (US2)**: Split header additions:
   - Developer A: Python files in src/ (T011-T017)
   - Developer B: Python files in tests/ (T018-T028)
   - Developer C: JavaScript and CSS files (T029-T033)
   - Developer D: Metadata files (T034-T035)
4. **Phase 4 verification**: One developer runs all checks (T036-T041)
5. **Phase 4 git**: One developer commits and pushes (T042-T044)
6. **Phase 5**: One developer verifies GitHub (T045-T050)
7. **Phase 6**: Final polish and merge (T054-T060)

### Recommended Approach

**Option 1: Manual + Careful** (safest for first-time license addition):
- Edit each file individually in editor
- Verify header format matches contracts/license-header-format.md
- Handles shebang/encoding edge cases correctly
- Time: ~30-45 minutes for 25 files

**Option 2: Bulk Script + Review** (faster but requires validation):
- Use bulk addition scripts from quickstart.md
- Review all changes in git diff before committing
- Manually fix any files with shebang/encoding issues
- Time: ~15-20 minutes + review time

**Option 3: Semi-Automated** (recommended):
- Use scripts for files without shebang/encoding (most files)
- Manually edit the few files with shebang/encoding
- Review all changes in git diff
- Time: ~20-25 minutes

---

## File-Specific Notes

### Files Requiring Special Attention

**Python files with shebang** (place header AFTER shebang):
- Check if any files in src/generator/ start with `#!/usr/bin/env python3`
- If found, manually edit to place header after shebang line

**Python files with encoding** (place header AFTER encoding):
- Check if any files start with `# -*- coding: utf-8 -*-`
- If found, manually edit to place header after encoding line

**Files to exclude** (no headers needed):
- config/gallery.yaml, config/settings.yaml (user configuration)
- README.md, CHANGELOG.md, LICENSE (documentation)
- specs/**, docs/** (documentation)
- output/**, __pycache__/** (generated files)
- pyproject.toml, pytest.ini (only add metadata field, not header)

### Verification Commands

```bash
# Verify LICENSE file:
wc -l LICENSE  # Should be 361
head -1 LICENSE  # Should be "Copyright 2025 fotoview contributors"

# Find all source files:
find src tests -name "*.py" -o -name "*.js" -o -name "*.css" | wc -l  # ~25 files

# Check for missing headers:
find src tests -name "*.py" | while read f; do
    grep -q "SPDX-License-Identifier: Apache-2.0" "$f" || echo "Missing: $f"
done

# Check header format:
find src tests -name "*.py" | xargs head -3 | less  # Review first 3 lines of each file
```

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** maps task to specific user story from spec.md
- **User Story 1 is MVP** - just LICENSE file provides legal clarity
- **User Story 2 adds headers** - best practice but not strictly required
- **User Story 3 is automatic** - GitHub detects LICENSE file
- **No automated tests** - feature specification does not request test tasks
- Each user story should be independently completable and testable
- Commit after completing each user story
- Verify at checkpoints before proceeding
- Total estimated time: 1-2 hours for complete implementation

---

## Success Criteria Reference

From spec.md - verify these at completion:

- ✅ **SC-001**: LICENSE file exists in repository root with exact Apache License 2.0 text (361 lines)
- ✅ **SC-002**: 100% of Python source files in src/ directory contain valid Apache 2.0 license headers
- ✅ **SC-003**: 100% of JavaScript and CSS files in src/static/ contain valid Apache 2.0 license headers
- ✅ **SC-004**: GitHub license detection correctly identifies repository as "Apache-2.0"
- ✅ **SC-005**: pyproject.toml metadata includes `license = "Apache-2.0"` field
- ✅ **SC-006**: README.md contains License section with link to LICENSE file
- ✅ **SC-007**: Automated license scanning tools correctly identify all files as Apache 2.0 (optional)
- ✅ **SC-008**: No license conflicts exist between project license and dependency licenses
- ✅ **SC-009**: Copyright year matches current year (2025) in all license notices
- ✅ **SC-010**: All license headers use consistent format (SPDX identifier + copyright notice)
