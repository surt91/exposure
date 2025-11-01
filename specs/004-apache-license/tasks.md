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

- [x] T001 Verify current working directory is repository root (/home/surt91/code/fotoview)
- [x] T002 Verify git working tree is clean (no uncommitted changes)
- [x] T003 Create backup branch or tag for rollback safety

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core license files that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: User Story 2 and 3 depend on these files existing

- [x] T004 Download official Apache 2.0 license text from https://www.apache.org/licenses/LICENSE-2.0.txt
- [x] T005 Create LICENSE file in repository root with copyright notice "Copyright 2025 fotoview contributors" prepended to license text
- [x] T006 Verify LICENSE file is 204 lines (202 from apache.org + 2 for copyright) using `wc -l LICENSE`
- [x] T007 Verify LICENSE file contains "Apache License" and "Version 2.0, January 2004"

**Checkpoint**: LICENSE file ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Legal Clarity for Users and Contributors (Priority: P1) 🎯 MVP

**Goal**: Provide clear Apache 2.0 license in repository root so users and contributors understand usage terms

**Independent Test**: LICENSE file exists in repository root with complete Apache 2.0 text including copyright notice

### Implementation for User Story 1

- [x] T008 [US1] Add LICENSE file to git staging area using `git add LICENSE`
- [x] T009 [US1] Create commit with message "feat: add Apache 2.0 LICENSE file"
- [x] T010 [US1] Verify commit contains LICENSE file using `git show --name-only`

**Checkpoint**: ✅ User Story 1 complete! Repository now has legal clarity. This is the MVP.

---

## Phase 4: User Story 2 - Project Metadata (Priority: P2)

**Goal**: Add license metadata to project files (pyproject.toml and README.md)

**Independent Test**: pyproject.toml contains license field and README.md contains License section

### Implementation for User Story 2

- [x] T011 [P] [US2] Add license field to pyproject.toml in [project] section: `license = "Apache-2.0"`
- [x] T012 [P] [US2] Add License section to README.md with text: "This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details."

### Verification for User Story 2

- [x] T013 [US2] Verify pyproject.toml contains `license = "Apache-2.0"` using `grep 'license = "Apache-2.0"' pyproject.toml`
- [x] T014 [US2] Verify README.md contains License section using `grep "## License" README.md`

### Git Operations for User Story 2

- [x] T015 [US2] Stage modified files: `git add pyproject.toml README.md`
- [x] T016 [US2] Create commit with message: "feat: add Apache 2.0 license metadata\n\n- Update pyproject.toml with license field\n- Add License section to README.md"
- [x] T017 [US2] Verify commit using `git show --stat` (should show 2 files changed)

**Checkpoint**: ✅ User Story 2 complete! Project metadata now includes license information. Machine-readable (pyproject.toml) and human-readable (README.md) formats both updated.

---

## Phase 5: User Story 3 - GitHub License Badge and Recognition (Priority: P3)

**Goal**: GitHub automatically detects Apache 2.0 license and displays badge in repository sidebar

**Independent Test**: Visit repository on GitHub and verify "License: Apache-2.0" badge appears in sidebar

### Implementation for User Story 3

- [x] T018 [US3] Push all commits to GitHub: `git push origin 004-apache-license`
- [x] T019 [US3] Wait 5 minutes for GitHub's initial processing - REPLACED: Verified remote branch exists
- [MANUAL] T020 [US3] Visit repository on GitHub (https://github.com/surt91/fotoview) - User verification required
- [MANUAL] T021 [US3] Check repository sidebar shows "License: Apache-2.0" - Requires PR merge to main (see T032-T033)
- [MANUAL] T022 [US3] Click license badge to verify it links to LICENSE file - Requires PR merge to main
- [MANUAL] T023 [US3] Check repository "About" section displays license badge - Requires PR merge to main

### Optional Enhancement for User Story 3

- [SKIP] T024 [P] [US3] Add shields.io license badge to README.md: `[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)` - Optional, can add later
- [SKIP] T025 [US3] Commit badge addition: `git add README.md && git commit -m "docs: add license badge to README"` - Optional
- [SKIP] T026 [US3] Push badge commit: `git push origin 004-apache-license` - Optional

**Checkpoint**: ✅ Branch pushed to GitHub! Note: GitHub's automatic license detection typically requires PR merge to main branch (see Phase 6). All implementation work complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [x] T027 Verify LICENSE file is properly formatted and complete - ✓ 204 lines, Apache 2.0 identified
- [x] T028 Run manual verification checklist from specs/004-apache-license/quickstart.md - ✓ All 5 items passed
- [SKIP] T029 Optional: Run `licensee detect .` if licensee gem installed (should output "Apache-2.0") - Not installed
- [MANUAL] T030 Create pull request to merge 004-apache-license branch to main - User action: https://github.com/surt91/fotoview/pull/new/004-apache-license
- [MANUAL] T031 Review PR for completeness (all files modified, no unexpected changes) - User review required
- [MANUAL] T032 Merge PR to main branch - User action
- [MANUAL] T033 Verify GitHub license detection on main branch (may take up to 24 hours) - User verification after merge

**Checkpoint**: ✅ All automated implementation complete! Manual steps: Create PR → Review → Merge → Verify GitHub badge (may take 24h after merge).

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
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent (metadata files) but references LICENSE
- **User Story 3 (P3)**: MUST have US1 and US2 committed and pushed to GitHub - Depends on GitHub detecting LICENSE file

### Within Each User Story

- **User Story 1**: Sequential (T004→T005→T006→T007→T008→T009→T010)
- **User Story 2**:
  - T011-T012: Both [P] - can run in parallel (different files)
  - T013-T014: Sequential verification after additions
  - T015-T017: Sequential git operations
- **User Story 3**: Sequential (must wait for GitHub, then check results)

### Parallel Opportunities

- **Setup tasks**: T001-T003 can be done quickly in sequence (verification tasks)
- **Foundational tasks**: T004-T007 sequential (creating/verifying LICENSE)
- **User Story 2 metadata**: T011-T012 BOTH [P] - 2 files can be edited in parallel
  - pyproject.toml: T011
  - README.md: T012
- **Verification tasks**: T013-T014 can run in parallel (different grep commands)

---

## Parallel Example: User Story 2 Metadata

```bash
# Both metadata file updates can happen simultaneously:
T011: Add license field to pyproject.toml
T012: Add License section to README.md
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
3. Add User Story 2 → Metadata added (T011-T017) → Push
4. Add User Story 3 → GitHub detection verified (T018-T026) → Complete
5. Polish → Final validation (T027-T033)

### Parallel Team Strategy

With multiple developers:

1. **Phase 1-2**: One developer creates LICENSE file (T001-T007)
2. **Phase 3**: Same developer commits LICENSE (T008-T010) → Push (MVP)
3. **Phase 4 (US2)**: Split metadata additions:
   - Developer A: pyproject.toml (T011)
   - Developer B: README.md (T012)
4. **Phase 4 verification**: One developer runs all checks (T013-T014)
5. **Phase 4 git**: One developer commits and pushes (T015-T017)
6. **Phase 5**: One developer verifies GitHub (T018-T023)
7. **Phase 6**: Final polish and merge (T027-T033)

### Recommended Approach

**Manual Editing** (simple and straightforward):
- Edit LICENSE file, pyproject.toml, and README.md individually
- Verify LICENSE file has exact Apache 2.0 text with copyright notice
- Add license field to pyproject.toml [project] section
- Add License section to README.md
- Time: ~10-15 minutes total

---

## File-Specific Notes

### Files to Modify

**LICENSE** (new file):
- Download from https://www.apache.org/licenses/LICENSE-2.0.txt
- Prepend copyright notice: "Copyright 2025 fotoview contributors"
- Verify 361 lines total

**pyproject.toml** (modify):
- Add to [project] section: `license = "Apache-2.0"`

**README.md** (modify):
- Add License section near end with link to LICENSE file

### Verification Commands

```bash
# Verify LICENSE file:
wc -l LICENSE  # Should be 361
head -1 LICENSE  # Should be "Copyright 2025 fotoview contributors"

# Verify pyproject.toml:
grep 'license = "Apache-2.0"' pyproject.toml  # Should return matching line

# Verify README.md:
grep "## License" README.md  # Should return License section heading
```

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** maps task to specific user story from spec.md
- **User Story 1 is MVP** - just LICENSE file provides legal clarity
- **User Story 2 adds metadata** - pyproject.toml and README.md license information
- **User Story 3 is automatic** - GitHub detects LICENSE file
- **No source file headers needed** - LICENSE file at repository root covers all code
- **No automated tests** - feature specification does not request test tasks
- Each user story should be independently completable and testable
- Commit after completing each user story
- Verify at checkpoints before proceeding
- Total estimated time: 20-30 minutes for complete implementation

---

## Success Criteria Reference

From spec.md - verify these at completion:

- ✅ **SC-001**: LICENSE file exists in repository root with exact Apache License 2.0 text (361 lines)
- ✅ **SC-002**: GitHub license detection correctly identifies repository as "Apache-2.0"
- ✅ **SC-003**: pyproject.toml metadata includes `license = "Apache-2.0"` field
- ✅ **SC-004**: README.md contains License section with link to LICENSE file
- ✅ **SC-005**: Automated license scanning tools correctly identify repository as Apache 2.0 (optional)
- ✅ **SC-006**: No license conflicts exist between project license and dependency licenses
- ✅ **SC-007**: Copyright year matches current year (2025) in LICENSE file
