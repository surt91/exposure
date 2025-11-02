# Tasks: Image Metadata Privacy and Build Progress Logging

**Feature**: `010-metadata-privacy` | **Branch**: `010-metadata-privacy` | **Date**: 2025-11-02

**Input**: Design documents from `/specs/010-metadata-privacy/`
- plan.md (tech stack, implementation approach)
- spec.md (user stories with priorities)
- data-model.md (entity enhancements)
- contracts/ (API contracts)
- research.md (technical decisions)
- quickstart.md (test scenarios)

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

**Tests**: No test tasks included - feature specification does not request test-driven development approach. Tests will be added during implementation as needed for validation.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Define metadata field constants and prepare infrastructure

- [ ] T001 Define `SENSITIVE_EXIF_TAGS` constant set in `src/generator/constants.py` (GPS tags 0x0000-0x001F, serial numbers 0xA431/0xA435, creator tags 0x013B/0x8298/0x9C9D, software tags 0x0131/0x000B, embedded thumbnails 0x0201/0x0202/0x0103)
- [ ] T002 Define `SAFE_EXIF_TAGS` constant set in `src/generator/constants.py` (orientation 0x0112, color 0xA001, timestamps 0x9003/0x9004/0x0132, camera/lens 0x010F/0x0110/0xA434/0xA433, exposure 0x829D/0x829A/0x8827/0x920A)
- [ ] T003 Validate tag set disjointness in `src/generator/constants.py` (ensure no tag appears in both SENSITIVE and SAFE sets)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data model enhancements that all user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Add `metadata_stripped: bool = True` field to `ThumbnailImage` model in `src/generator/model.py`
- [ ] T005 Add `metadata_strip_warning: Optional[str] = None` field to `ThumbnailImage` model in `src/generator/model.py`
- [ ] T006 Add `metadata_stripped: bool = True` field to `CacheEntry` model in `src/generator/cache.py`
- [ ] T007 Create `MetadataStripResult` dataclass in `src/generator/thumbnails.py` with fields: success, image, warning, sensitive_fields_removed, safe_fields_preserved
- [ ] T008 Bump `CACHE_VERSION` to "2.0" in `src/generator/constants.py` to force rebuild with metadata stripping

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Location Privacy Protection (Priority: P1) 🎯 MVP

**Goal**: Automatically remove GPS coordinates and location metadata from thumbnails to protect photographer locations

**Independent Test**: Build gallery with GPS-tagged images, inspect generated thumbnails with exiftool or Pillow, verify GPS coordinates completely removed

### Implementation for User Story 1

- [ ] T009 [US1] Implement `_strip_metadata()` method in `src/generator/thumbnails.py` to extract EXIF data using `img.getexif()`
- [ ] T010 [US1] Implement tag filtering logic in `_strip_metadata()` method in `src/generator/thumbnails.py` to create new EXIF with only `SAFE_EXIF_TAGS` fields
- [ ] T011 [US1] Implement error handling in `_strip_metadata()` method in `src/generator/thumbnails.py` to return `MetadataStripResult` with success/failure status
- [ ] T012 [US1] Integrate `_strip_metadata()` call into `generate_thumbnail()` method in `src/generator/thumbnails.py` after thumbnail creation, before save
- [ ] T013 [US1] Update `_save_thumbnails()` method in `src/generator/thumbnails.py` to save images with stripped metadata for both WebP and JPEG formats
- [ ] T014 [US1] Populate `ThumbnailImage.metadata_stripped` and `metadata_strip_warning` fields in `generate_thumbnail()` method in `src/generator/thumbnails.py` based on `MetadataStripResult`

**Checkpoint**: At this point, GPS and location data should be completely removed from all generated thumbnails

---

## Phase 4: User Story 2 - Comprehensive Sensitive Metadata Removal (Priority: P1)

**Goal**: Remove camera serial numbers, personal information, and software metadata while preserving display-critical fields

**Independent Test**: Process images with extensive EXIF/IPTC/XMP metadata, inspect thumbnails to verify personal identifiers removed while basic display properties remain

### Implementation for User Story 2

- [ ] T015 [US2] Verify `SENSITIVE_EXIF_TAGS` includes camera serial numbers (0xA431 BodySerialNumber, 0xA435 LensSerialNumber) in `src/generator/constants.py`
- [ ] T016 [US2] Verify `SENSITIVE_EXIF_TAGS` includes creator fields (0x013B Artist, 0x8298 Copyright, 0x9C9D XPAuthor) in `src/generator/constants.py`
- [ ] T017 [US2] Verify `SENSITIVE_EXIF_TAGS` includes software fields (0x0131 Software, 0x000B ProcessingSoftware) in `src/generator/constants.py`
- [ ] T018 [US2] Verify `SAFE_EXIF_TAGS` includes timestamp fields (0x9003 DateTimeOriginal, 0x9004 DateTimeDigitized, 0x0132 DateTime) in `src/generator/constants.py`
- [ ] T019 [US2] Verify `SAFE_EXIF_TAGS` includes ICC color profile preservation via Pillow's info dict handling in `_strip_metadata()` method in `src/generator/thumbnails.py`
- [ ] T020 [US2] Verify `SAFE_EXIF_TAGS` includes orientation metadata (0x0112 Orientation) in `src/generator/constants.py`
- [ ] T021 [US2] Verify `SAFE_EXIF_TAGS` includes camera/lens information (0x010F Make, 0x0110 Model, 0xA434 LensModel, 0xA433 LensMake) per FR-008a in `src/generator/constants.py`
- [ ] T022 [US2] Add handling for embedded thumbnail removal (tags 0x0201, 0x0202, 0x0103) in `_strip_metadata()` method in `src/generator/thumbnails.py`

**Checkpoint**: At this point, all sensitive personal metadata should be removed while display-critical fields are preserved

---

## Phase 5: User Story 3 - Build Progress Visibility (Priority: P2)

**Goal**: Show real-time progress with filename and file size reduction percentage for each processed image

**Independent Test**: Run build with 20+ images, observe console output to verify progress messages appear for each image with filename and size reduction

### Implementation for User Story 3

- [ ] T023 [P] [US3] Implement `_format_size()` helper method in `src/generator/thumbnails.py` to format bytes as human-readable strings (MB/KB/B with proper precision)
- [ ] T024 [US3] Add INFO-level progress logging in `generate_thumbnail()` method in `src/generator/thumbnails.py` after successful thumbnail generation
- [ ] T025 [US3] Format progress log message as "✓ {filename} → {source_size} → {thumb_size} ({reduction_pct}% reduction)" in `generate_thumbnail()` method in `src/generator/thumbnails.py`
- [ ] T026 [US3] Calculate file size reduction percentage using formula `((original_size - thumbnail_size) / original_size) × 100` in `generate_thumbnail()` method in `src/generator/thumbnails.py`
- [ ] T027 [US3] Add WARNING-level logging with "⚠ WARNING:" prefix when metadata stripping fails in `generate_thumbnail()` method in `src/generator/thumbnails.py`
- [ ] T028 [US3] Ensure progress logs appear in real-time (use `logger.info()` immediately after each image, not batched) in `generate_thumbnail()` method in `src/generator/thumbnails.py`

**Checkpoint**: At this point, build process should show clear real-time progress with size reduction stats

---

## Phase 6: User Story 4 - Selective Metadata Preservation (Priority: P3)

**Goal**: Intelligently preserve non-sensitive metadata (orientation, color profiles, timestamps, camera info) while removing privacy-sensitive fields

**Independent Test**: Process images with various metadata types, verify display-critical fields remain while privacy-sensitive fields are removed

### Implementation for User Story 4

- [ ] T029 [US4] Verify orientation preservation by ensuring 0x0112 is in `SAFE_EXIF_TAGS` and never in `SENSITIVE_EXIF_TAGS` in `src/generator/constants.py`
- [ ] T030 [US4] Verify color profile preservation by ensuring ICC profile handling in `_strip_metadata()` method in `src/generator/thumbnails.py` (preserve via Pillow's info dict)
- [ ] T031 [US4] Verify timestamp preservation by ensuring date/time tags (0x9003, 0x9004, 0x0132) are in `SAFE_EXIF_TAGS` in `src/generator/constants.py`
- [ ] T032 [US4] Verify camera/lens info preservation by ensuring Make/Model/LensModel/LensMake tags are in `SAFE_EXIF_TAGS` per FR-008a in `src/generator/constants.py`
- [ ] T033 [US4] Add validation logic to ensure GPS tags (0x0000-0x001F) are never preserved in `_strip_metadata()` method in `src/generator/thumbnails.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Error Handling & Edge Cases

**Purpose**: Graceful handling of failures and edge cases

- [ ] T034 Implement graceful handling for images with no EXIF metadata in `_strip_metadata()` method in `src/generator/thumbnails.py` (return success with 0 fields removed)
- [ ] T035 Implement graceful handling for corrupted EXIF data in `_strip_metadata()` method in `src/generator/thumbnails.py` (catch exceptions, return failure with warning, continue build)
- [ ] T036 Implement graceful handling for unsupported image formats in `_strip_metadata()` method in `src/generator/thumbnails.py` (return success with no stripping needed)
- [ ] T037 Ensure build continues when metadata stripping fails per FR-021 in `generate_thumbnail()` method in `src/generator/thumbnails.py` (return `ThumbnailImage` not `None`)
- [ ] T038 Verify failed images still included in gallery output per FR-023 in `generate_thumbnail()` method in `src/generator/thumbnails.py`

---

## Phase 8: Cache Integration

**Purpose**: Ensure incremental builds work correctly with metadata stripping

- [ ] T039 Update cache write logic in `src/generator/cache.py` to save `metadata_stripped` field from `ThumbnailImage` to `CacheEntry`
- [ ] T040 Verify cache invalidation on `CACHE_VERSION` bump triggers full rebuild with metadata stripping in `src/generator/cache.py`
- [ ] T041 Test cache hit behavior in `generate_thumbnail()` method in `src/generator/thumbnails.py` to ensure cached thumbnails already have metadata stripped (log at DEBUG level)

---

## Phase 9: Polish & Validation

**Purpose**: Documentation, validation, and cross-cutting improvements

- [ ] T042 [P] Update README.md to document metadata privacy feature (what's removed, what's preserved, how to verify)
- [ ] T043 [P] Verify all functional requirements FR-001 through FR-024 are implemented by reviewing code against spec.md
- [ ] T044 [P] Verify all success criteria SC-001 through SC-010 can be measured by testing with exiftool
- [ ] T045 [P] Add example to quickstart.md showing how to verify metadata removal with exiftool
- [ ] T046 Run manual validation per quickstart.md test scenarios (GPS-tagged images, images with serial numbers, images with no metadata)
- [ ] T047 Verify build time impact is ≤10% increase per performance goal in plan.md
- [ ] T048 [P] Add inline code comments documenting metadata stripping logic in `src/generator/thumbnails.py`
- [ ] T049 Verify no console output shows "summary report" of failures per FR-024 (inline warnings only)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Phase 2 - Core metadata stripping
  - User Story 2 (P1): Can start after Phase 2 - Extends US1 with additional field coverage
  - User Story 3 (P2): Can start after Phase 2 - Progress logging (independent of metadata stripping)
  - User Story 4 (P3): Can start after Phase 2 - Validation of selective preservation
- **Error Handling (Phase 7)**: Should be integrated during US1-US4 implementation
- **Cache Integration (Phase 8)**: Can start after US1 (core stripping) is complete
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Location Privacy)**: No dependencies on other stories - Core functionality
- **User Story 2 (P1 - Comprehensive Removal)**: Extends US1 but can be developed in parallel (same priority)
- **User Story 3 (P2 - Progress Logging)**: Independent of US1/US2 - Can be developed in parallel
- **User Story 4 (P3 - Selective Preservation)**: Validates US1/US2 work - Best done after US1/US2 complete

### Within Each User Story

- **User Story 1**: T009 → T010 → T011 → T012 → T013 → T014 (sequential - build metadata stripping pipeline)
- **User Story 2**: All tasks are verification tasks - can run in parallel after US1 complete
- **User Story 3**: T023 can run in parallel with other tasks; T024-T028 sequential (build logging pipeline)
- **User Story 4**: All tasks are verification tasks - can run in parallel after US1/US2 complete

### Parallel Opportunities

**Phase 1 (Setup)**: All 3 tasks can be done in one file edit or sequentially (small tasks)

**Phase 2 (Foundational)**:
- T004, T005 (model.py) together
- T006 (cache.py) in parallel with T004/T005
- T007 (thumbnails.py dataclass) in parallel with T004/T005/T006
- T008 (constants.py) in parallel with all above

**Phase 3 (User Story 1)**: Sequential pipeline (each step depends on previous)

**Phase 4 (User Story 2)**:
- T015, T016, T017 (constants.py verification) together
- T018, T020, T021 (constants.py verification) together
- T019, T022 (thumbnails.py enhancements) together

**Phase 5 (User Story 3)**:
- T023 can be written independently in parallel
- T024-T028 sequential (logging pipeline)

**Phase 6 (User Story 4)**:
- T029, T031, T032 (constants.py verification) together
- T030 (ICC profile), T033 (GPS validation) in parallel

**Phase 7 (Error Handling)**: T034-T038 can be written together in same method

**Phase 8 (Cache)**: T039-T041 sequential (modify cache logic)

**Phase 9 (Polish)**: T042, T043, T044, T045, T048 can all run in parallel (different files/activities)

---

## Parallel Example: User Story 1 Core Implementation

```bash
# Sequential pipeline for metadata stripping:
T009: Implement _strip_metadata() extraction
  ↓
T010: Implement tag filtering logic
  ↓
T011: Implement error handling
  ↓
T012: Integrate into generate_thumbnail()
  ↓
T013: Update _save_thumbnails()
  ↓
T014: Populate ThumbnailImage fields
```

## Parallel Example: User Story 2 Verification

```bash
# Launch all verification tasks together:
Task T015: Verify serial number tags
Task T016: Verify creator field tags
Task T017: Verify software field tags
Task T018: Verify timestamp tags
Task T020: Verify orientation tags
Task T021: Verify camera/lens tags
# All examining same constants.py file
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 - Both P1)

1. Complete Phase 1: Setup (define metadata field constants)
2. Complete Phase 2: Foundational (data model enhancements)
3. Complete Phase 3: User Story 1 (core metadata stripping)
4. Complete Phase 4: User Story 2 (comprehensive field coverage)
5. **STOP and VALIDATE**: Test with GPS-tagged images, inspect with exiftool
6. Deploy/demo if ready

**Rationale**: US1 and US2 are both P1 and work together to provide complete metadata privacy. US3 (progress logging) and US4 (validation) are nice-to-have enhancements.

### Incremental Delivery

1. **MVP**: Setup + Foundational + US1 + US2 → Privacy protection complete
2. **Enhanced UX**: Add US3 → Progress visibility for long builds
3. **Validation**: Add US4 → Verify selective preservation working correctly
4. **Production Ready**: Add Phase 7 (error handling), Phase 8 (cache), Phase 9 (polish)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 + User Story 2 (same developer, sequential)
   - Developer B: User Story 3 (progress logging - independent)
   - Developer C: Documentation and validation prep
3. After US1/US2 complete:
   - Developer A: Error handling (Phase 7) and cache integration (Phase 8)
   - Developer B: User Story 4 validation
   - Developer C: Polish and documentation (Phase 9)

---

## Summary

**Total Tasks**: 49 tasks across 9 phases

**Task Distribution by User Story**:
- Setup: 3 tasks
- Foundational: 5 tasks (BLOCKING)
- User Story 1 (P1): 6 tasks (core metadata stripping)
- User Story 2 (P1): 8 tasks (comprehensive removal)
- User Story 3 (P2): 6 tasks (progress logging)
- User Story 4 (P3): 5 tasks (selective preservation validation)
- Error Handling: 5 tasks
- Cache Integration: 3 tasks
- Polish: 8 tasks

**Critical Path**: Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1) → Phase 4 (US2) → Phase 7 (Error Handling) → Phase 8 (Cache) → Phase 9 (Polish)

**MVP Scope** (Suggested): Phases 1-4 (Setup, Foundational, US1, US2) = 22 tasks
- Delivers core privacy protection (GPS removal, serial number removal, personal info removal)
- Preserves display-critical metadata (orientation, color, timestamps, camera info)
- Includes foundational error handling within US1 implementation
- Can be fully tested and deployed independently

**Parallel Opportunities**:
- Phase 2 (Foundational): 4 parallel tracks (model.py, cache.py, thumbnails.py, constants.py)
- Phase 4 (US2): 3 parallel batches of verification tasks
- Phase 5 (US3): T023 can be written independently
- Phase 6 (US4): 2 parallel batches of verification tasks
- Phase 9 (Polish): 5 parallel documentation/validation tasks

**Independent Testing**:
- After Phase 3: Test GPS removal with sample GPS-tagged images
- After Phase 4: Test comprehensive metadata removal with images containing serial numbers, creator info, software metadata
- After Phase 5: Test progress logging with 20+ image build
- After Phase 6: Test selective preservation with images containing various metadata types

---

## Notes

- **No test tasks included**: Feature specification does not explicitly request TDD approach. Tests will be added during implementation for validation purposes.
- **Verification tasks**: US2 and US4 include "verify" tasks to ensure constants are correctly defined - these are code review/validation tasks, not test writing.
- **Error handling integrated**: Phase 7 error handling should be integrated during US1-US4 implementation rather than as a separate phase.
- **Format compliance**: All tasks follow `- [ ] [ID] [P?] [Story?] Description with file path` format
- **File paths**: All tasks include exact file paths for implementation
- **Incremental**: Each user story delivers independently testable value
- **Constitution compliant**: All tasks align with static-first, privacy-enhancing principles

