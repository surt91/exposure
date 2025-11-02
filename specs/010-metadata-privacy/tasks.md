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

**Scope**: Metadata stripping applies to BOTH thumbnails AND full-size original images (shown in modal/lightbox view).

**Library**: Uses piexif 1.1+ for EXIF manipulation with named constants (e.g., piexif.ExifIFD.BodySerialNumber instead of 0xA431).

**Tests**: No test tasks included - feature specification does not request test-driven development approach. Tests will be added during implementation as needed for validation.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install piexif library and create shared metadata filtering module

- [x] T001 Install piexif dependency by adding `piexif = "^1.1.3"` to `pyproject.toml` under `[project.dependencies]`
- [x] T002 Create `src/generator/metadata_filter.py` module with piexif imports
- [x] T003 Define `SENSITIVE_EXIF_TAGS` constant set in `src/generator/metadata_filter.py` using piexif named constants (piexif.ExifIFD.BodySerialNumber, piexif.ExifIFD.LensSerialNumber, piexif.ImageIFD.Artist, piexif.ImageIFD.Copyright, piexif.ImageIFD.XPAuthor, piexif.ImageIFD.Software, piexif.ImageIFD.ProcessingSoftware)
- [x] T004 Define `SENSITIVE_0TH_TAGS` constant set in `src/generator/metadata_filter.py` for thumbnail-related tags (piexif.ImageIFD.JPEGInterchangeFormat, piexif.ImageIFD.JPEGInterchangeFormatLength, piexif.ImageIFD.Compression for thumbnails)
- [x] T005 Define `SAFE_EXIF_TAGS` constant set in `src/generator/metadata_filter.py` using piexif named constants (piexif.ImageIFD.Orientation, piexif.ExifIFD.ColorSpace, piexif.ExifIFD.DateTimeOriginal, piexif.ExifIFD.DateTimeDigitized, piexif.ImageIFD.DateTime, piexif.ImageIFD.Make, piexif.ImageIFD.Model, piexif.ExifIFD.LensModel, piexif.ExifIFD.LensMake)
- [x] T006 Define `SAFE_0TH_TAGS` constant set in `src/generator/metadata_filter.py` for display-critical fields

---

## Phase 2: Core Metadata Filtering Logic

**Purpose**: Implement shared metadata filtering functions used by both thumbnails and full-size images

- [x] T007 Implement `filter_metadata(source_path: Path) -> Optional[bytes]` function in `src/generator/metadata_filter.py` that loads EXIF with piexif.load(), removes GPS IFD via exif_dict.pop("GPS", None), filters sensitive tags, returns cleaned EXIF bytes via piexif.dump()
- [x] T008 Implement `_remove_sensitive_tags(exif_dict: dict) -> dict` helper function in `src/generator/metadata_filter.py` to filter EXIF/0th IFDs using SENSITIVE_EXIF_TAGS and SENSITIVE_0TH_TAGS constants
- [x] T009 Implement error handling in `filter_metadata()` to catch piexif.InvalidImageDataError and return None on failure with logging
- [x] T010 Implement `strip_and_save(src_path: Path, dest_path: Path) -> bool` function in `src/generator/metadata_filter.py` that calls filter_metadata(), opens image with Pillow, saves with cleaned EXIF, returns success status
- [x] T011 Add logging in `strip_and_save()` to log warnings with "⚠ WARNING:" prefix when metadata stripping fails

## Phase 3: Data Model Enhancements

**Purpose**: Update data models to track metadata stripping status

- [x] T012 Add `metadata_stripped: bool = True` field to `ThumbnailImage` model in `src/generator/model.py`
- [x] T013 Add `metadata_strip_warning: Optional[str] = None` field to `ThumbnailImage` model in `src/generator/model.py`
- [x] T014 Add `metadata_stripped: bool = True` field to `CacheEntry` model in `src/generator/cache.py`
- [x] T015 Bump `CACHE_VERSION` in `src/generator/cache.py` to force rebuild with metadata stripping

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 4: User Story 1 - Location Privacy Protection (Priority: P1) 🎯 MVP

**Goal**: Automatically remove GPS coordinates and location metadata from BOTH thumbnails AND full-size images to protect photographer locations

**Independent Test**: Build gallery with GPS-tagged images, inspect generated thumbnails AND full-size originals with exiftool or Pillow, verify GPS coordinates completely removed from both

### Implementation for User Story 1 - Thumbnails

- [x] T016 [US1] Import `filter_metadata` from `src/generator/metadata_filter` in `src/generator/thumbnails.py`
- [x] T017 [US1] Call `filter_metadata(source_path)` in `generate_thumbnail()` method in `src/generator/thumbnails.py` after reading source image
- [x] T018 [US1] Update `_save_thumbnails()` method in `src/generator/thumbnails.py` to save WebP with cleaned EXIF bytes via `exif=cleaned_exif` parameter
- [x] T019 [US1] Update `_save_thumbnails()` method in `src/generator/thumbnails.py` to save JPEG with cleaned EXIF bytes via `exif=cleaned_exif` parameter
- [x] T020 [US1] Populate `ThumbnailImage.metadata_stripped` and `metadata_strip_warning` fields in `generate_thumbnail()` method in `src/generator/thumbnails.py` based on filter_metadata() result

### Implementation for User Story 1 - Full-Size Originals

- [x] T021 [US1] Import `strip_and_save` from `src/generator/metadata_filter` in `src/generator/assets.py`
- [x] T022 [US1] Add `strip_metadata: bool = False` parameter to `copy_with_hash()` function in `src/generator/assets.py`
- [x] T023 [US1] Add image format detection in `copy_with_hash()` in `src/generator/assets.py` (check if extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])
- [x] T024 [US1] Call `strip_and_save(src, dest)` for image files when `strip_metadata=True` in `copy_with_hash()` in `src/generator/assets.py`
- [x] T025 [US1] Add fallback to `shutil.copy2()` if `strip_and_save()` fails with warning log in `copy_with_hash()` in `src/generator/assets.py`
- [x] T026 [US1] Update call sites in `src/generator/build_html.py` to pass `strip_metadata=True` when copying full-size original images

**Checkpoint**: At this point, GPS and location data should be completely removed from all generated thumbnails AND full-size originals

---

## Phase 5: User Story 2 - Comprehensive Sensitive Metadata Removal (Priority: P1)

**Goal**: Remove camera serial numbers, personal information, and software metadata while preserving display-critical fields

**Independent Test**: Process images with extensive EXIF/IPTC/XMP metadata, inspect thumbnails AND full-size originals to verify personal identifiers removed while basic display properties remain

### Implementation for User Story 2

- [x] T027 [US2] Verify `SENSITIVE_EXIF_TAGS` includes camera serial numbers (piexif.ExifIFD.BodySerialNumber, piexif.ExifIFD.LensSerialNumber) in `src/generator/metadata_filter.py`
- [x] T028 [US2] Verify `SENSITIVE_EXIF_TAGS` includes creator fields (piexif.ImageIFD.Artist, piexif.ImageIFD.Copyright, piexif.ImageIFD.XPAuthor) in `src/generator/metadata_filter.py`
- [x] T029 [US2] Verify `SENSITIVE_EXIF_TAGS` includes software fields (piexif.ImageIFD.Software, piexif.ImageIFD.ProcessingSoftware) in `src/generator/metadata_filter.py`
- [x] T030 [US2] Verify `SAFE_EXIF_TAGS` includes timestamp fields (piexif.ExifIFD.DateTimeOriginal, piexif.ExifIFD.DateTimeDigitized, piexif.ImageIFD.DateTime) in `src/generator/metadata_filter.py`
- [x] T031 [US2] Verify ICC color profile preservation in `strip_and_save()` method in `src/generator/metadata_filter.py` (Pillow preserves via img.info['icc_profile'])
- [x] T032 [US2] Verify `SAFE_EXIF_TAGS` includes orientation metadata (piexif.ImageIFD.Orientation) in `src/generator/metadata_filter.py`
- [x] T033 [US2] Verify `SAFE_EXIF_TAGS` includes camera/lens information (piexif.ImageIFD.Make, piexif.ImageIFD.Model, piexif.ExifIFD.LensModel, piexif.ExifIFD.LensMake) per FR-008a in `src/generator/metadata_filter.py`
- [x] T034 [US2] Verify `SENSITIVE_0TH_TAGS` includes embedded thumbnail removal (piexif.ImageIFD.JPEGInterchangeFormat, piexif.ImageIFD.JPEGInterchangeFormatLength) in `src/generator/metadata_filter.py`

**Checkpoint**: At this point, all sensitive personal metadata should be removed while display-critical fields are preserved

---

## Phase 6: User Story 3 - Build Progress Visibility (Priority: P2)

**Goal**: Show real-time progress with filename and file size reduction percentage for each processed image

**Independent Test**: Run build with 20+ images, observe console output to verify progress messages appear for each image with filename and size reduction

### Implementation for User Story 3

- [x] T035 [P] [US3] Implement `_format_size()` helper method in `src/generator/thumbnails.py` to format bytes as human-readable strings (MB/KB/B with proper precision)
- [x] T036 [US3] Add INFO-level progress logging in `generate_thumbnail()` method in `src/generator/thumbnails.py` after successful thumbnail generation
- [x] T037 [US3] Format progress log message as "✓ {filename} → {source_size} → {thumb_size} ({reduction_pct}% reduction)" in `generate_thumbnail()` method in `src/generator/thumbnails.py`
- [x] T038 [US3] Calculate file size reduction percentage using formula `((original_size - thumbnail_size) / original_size) × 100` in `generate_thumbnail()` method in `src/generator/thumbnails.py`
- [x] T039 [US3] Add WARNING-level logging with "⚠ WARNING:" prefix when metadata stripping fails in `generate_thumbnail()` method in `src/generator/thumbnails.py`
- [x] T040 [US3] Ensure progress logs appear in real-time (use `logger.info()` immediately after each image, not batched) in `generate_thumbnail()` method in `src/generator/thumbnails.py`

**Checkpoint**: At this point, build process should show clear real-time progress with size reduction stats

---

## Phase 7: User Story 4 - Selective Metadata Preservation (Priority: P3)

**Goal**: Intelligently preserve non-sensitive metadata (orientation, color profiles, timestamps, camera info) while removing privacy-sensitive fields

**Independent Test**: Process images with various metadata types, verify display-critical fields remain while privacy-sensitive fields are removed

### Implementation for User Story 4

- [x] T041 [US4] Verify orientation preservation by ensuring piexif.ImageIFD.Orientation is in `SAFE_EXIF_TAGS` and never in `SENSITIVE_EXIF_TAGS` in `src/generator/metadata_filter.py`
- [x] T042 [US4] Verify color profile preservation by ensuring ICC profile handling in `strip_and_save()` method in `src/generator/metadata_filter.py` (preserve via Pillow's info dict)
- [x] T043 [US4] Verify timestamp preservation by ensuring piexif.ExifIFD.DateTimeOriginal/DateTimeDigitized/DateTime are in `SAFE_EXIF_TAGS` in `src/generator/metadata_filter.py`
- [x] T044 [US4] Verify camera/lens info preservation by ensuring Make/Model/LensModel/LensMake tags are in `SAFE_EXIF_TAGS` per FR-008a in `src/generator/metadata_filter.py`
- [x] T045 [US4] Verify GPS tags are never preserved by testing that GPS IFD is removed via exif_dict.pop("GPS", None) in `filter_metadata()` in `src/generator/metadata_filter.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Error Handling & Edge Cases

**Purpose**: Graceful handling of failures and edge cases

- [x] T046 Implement graceful handling for images with no EXIF metadata in `filter_metadata()` method in `src/generator/metadata_filter.py` (return None, which means no metadata to strip)
- [x] T047 Implement graceful handling for corrupted EXIF data in `filter_metadata()` method in `src/generator/metadata_filter.py` (catch piexif.InvalidImageDataError, log warning, return None, continue build)
- [x] T048 Implement graceful handling for unsupported image formats in `filter_metadata()` method in `src/generator/metadata_filter.py` (catch exceptions, return None)
- [x] T049 Ensure build continues when metadata stripping fails per FR-021 in `generate_thumbnail()` method in `src/generator/thumbnails.py` (populate metadata_strip_warning but continue)
- [x] T050 Verify failed images still included in gallery output per FR-023 in `generate_thumbnail()` method in `src/generator/thumbnails.py`

---

## Phase 9: Cache Integration

**Purpose**: Ensure incremental builds work correctly with metadata stripping

- [x] T051 Update cache write logic in `src/generator/cache.py` to save `metadata_stripped` field from `ThumbnailImage` to `CacheEntry`
- [x] T052 Verify cache invalidation on `CACHE_VERSION` bump triggers full rebuild with metadata stripping in `src/generator/cache.py`
- [x] T053 Test cache hit behavior in `generate_thumbnail()` method in `src/generator/thumbnails.py` to ensure cached thumbnails already have metadata stripped (log at DEBUG level)

---

## Phase 10: Polish & Validation

**Purpose**: Documentation, validation, and cross-cutting improvements

- [x] T054 [P] Update README.md to document metadata privacy feature (what's removed, what's preserved, how to verify)
- [x] T055 [P] Verify all functional requirements FR-001 through FR-024 are implemented by reviewing code against spec.md
- [x] T056 [P] Verify all success criteria SC-001 through SC-010 can be measured by testing with exiftool
- [x] T057 [P] Add example to quickstart.md showing how to verify metadata removal with exiftool
- [x] T058 Run manual validation per quickstart.md test scenarios (GPS-tagged images, images with serial numbers, images with no metadata)
- [x] T059 Verify build time impact is ≤15% increase per performance goal in plan.md (updated from 10% to account for full-size processing)
- [x] T060 [P] Add inline code comments documenting metadata stripping logic in `src/generator/metadata_filter.py`
- [x] T061 Verify no console output shows "summary report" of failures per FR-024 (inline warnings only)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately (T001-T006)
- **Core Logic (Phase 2)**: Depends on Setup - implements shared metadata filtering module (T007-T011)
- **Data Models (Phase 3)**: Depends on Setup - updates data models to track metadata status (T012-T015)
- **User Stories (Phase 4-7)**: All depend on Phase 1-3 completion
  - User Story 1 (P1 - Phase 4): Core metadata stripping for thumbnails AND full-size (T016-T026)
  - User Story 2 (P1 - Phase 5): Comprehensive field coverage verification (T027-T034)
  - User Story 3 (P2 - Phase 6): Progress logging (T035-T040)
  - User Story 4 (P3 - Phase 7): Validation of selective preservation (T041-T045)
- **Error Handling (Phase 8)**: Should be integrated during US1-US4 implementation (T046-T050)
- **Cache Integration (Phase 9)**: Can start after US1 (core stripping) is complete (T051-T053)
- **Polish (Phase 10)**: Depends on all user stories being complete (T054-T061)

### User Story Dependencies

- **User Story 1 (P1 - Location Privacy)**: No dependencies on other stories - Core functionality (thumbnails + full-size)
- **User Story 2 (P1 - Comprehensive Removal)**: Extends US1 but can be developed in parallel (same priority)
- **User Story 3 (P2 - Progress Logging)**: Independent of US1/US2 - Can be developed in parallel
- **User Story 4 (P3 - Selective Preservation)**: Validates US1/US2 work - Best done after US1/US2 complete

### Within Each User Story

- **User Story 1 (Phase 4)**: T016-T020 (thumbnails) can run in parallel with T021-T026 (full-size originals) since they modify different files
- **User Story 2 (Phase 5)**: All tasks are verification tasks - can run in parallel after US1 complete
- **User Story 3 (Phase 6)**: T035 can run in parallel with other tasks; T036-T040 sequential (build logging pipeline)
- **User Story 4 (Phase 7)**: All tasks are verification tasks - can run in parallel after US1/US2 complete

### Parallel Opportunities

**Phase 1 (Setup)**: T001-T006 - All constant definitions can be done in one file edit session

**Phase 2 (Core Logic)**: T007-T011 sequential (implement shared metadata_filter.py module)

**Phase 3 (Data Models)**:
- T012, T013 (model.py) together
- T014, T015 (cache.py) together
- Both pairs can run in parallel

**Phase 4 (User Story 1)**:
- T016-T020 (thumbnails.py) can run in parallel with T021-T026 (assets.py) - different files
- Within thumbnails: T016-T020 sequential
- Within full-size: T021-T026 sequential

**Phase 5 (User Story 2)**:
- T027-T034 all verification tasks - can run in parallel (same file review)

**Phase 6 (User Story 3)**:
- T035 can be written independently
- T036-T040 sequential (logging pipeline)

**Phase 7 (User Story 4)**:
- T041-T045 all verification tasks - can run in parallel

**Phase 8 (Error Handling)**: T046-T050 can be written together in same method

**Phase 9 (Cache)**: T051-T053 sequential (modify cache logic)

**Phase 10 (Polish)**: T054, T055, T056, T057, T060 can all run in parallel (different files/activities)

---

## Parallel Example: User Story 1 - Dual Track Implementation

```bash
# Track A (thumbnails.py) and Track B (assets.py) run in parallel:

Track A - Thumbnails:               Track B - Full-Size Originals:
T016: Import filter_metadata        T021: Import strip_and_save
  ↓                                   ↓
T017: Call filter_metadata()        T022: Add strip_metadata parameter
  ↓                                   ↓
T018: Save WebP with clean EXIF     T023: Add format detection
  ↓                                   ↓
T019: Save JPEG with clean EXIF     T024: Call strip_and_save()
  ↓                                   ↓
T020: Populate fields               T025: Add fallback to copy2()
                                      ↓
                                    T026: Update call sites
```

## Parallel Example: User Story 2 Verification

```bash
# Launch all verification tasks together:
Task T027: Verify serial number tags
Task T028: Verify creator field tags
Task T029: Verify software field tags
Task T030: Verify timestamp tags
Task T031: Verify ICC profile handling
Task T032: Verify orientation tags
Task T033: Verify camera/lens tags
Task T034: Verify embedded thumbnail removal
# All examining same metadata_filter.py file
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 - Both P1)

1. Complete Phase 1: Setup (install piexif, create metadata_filter.py, define constants)
2. Complete Phase 2: Core Logic (implement filter_metadata and strip_and_save)
3. Complete Phase 3: Data Models (update ThumbnailImage and CacheEntry)
4. Complete Phase 4: User Story 1 (integrate stripping for thumbnails AND full-size)
5. Complete Phase 5: User Story 2 (comprehensive field coverage verification)
6. **STOP and VALIDATE**: Test with GPS-tagged images, inspect both thumbnails and full-size originals with exiftool
7. Deploy/demo if ready

**Rationale**: US1 and US2 are both P1 and work together to provide complete metadata privacy for BOTH thumbnails and full-size images. US3 (progress logging) and US4 (validation) are nice-to-have enhancements.

### Incremental Delivery

1. **MVP**: Setup + Core Logic + Data Models + US1 + US2 → Privacy protection complete (both thumbnails and full-size)
2. **Enhanced UX**: Add US3 → Progress visibility for long builds
3. **Validation**: Add US4 → Verify selective preservation working correctly
4. **Production Ready**: Add Phase 8 (error handling), Phase 9 (cache), Phase 10 (polish)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Core Logic + Data Models together
2. Once Phase 1-3 complete:
   - Developer A: User Story 1 - Thumbnails (T016-T020)
   - Developer B: User Story 1 - Full-Size (T021-T026)
   - Developer C: User Story 3 (progress logging - independent)
3. After US1 complete:
   - Developer A: User Story 2 verification (T027-T034)
   - Developer B: Error handling (Phase 8) and cache integration (Phase 9)
   - Developer C: User Story 4 validation
4. Final polish:
   - All developers: Phase 10 polish tasks in parallel

---

## Summary

**Total Tasks**: 61 tasks across 10 phases

**Task Distribution by Phase**:
- Phase 1 - Setup: 6 tasks (install piexif, create module, define constants)
- Phase 2 - Core Logic: 5 tasks (implement shared metadata filtering)
- Phase 3 - Data Models: 4 tasks (update ThumbnailImage, CacheEntry)
- Phase 4 - User Story 1 (P1): 11 tasks (core stripping for thumbnails + full-size)
- Phase 5 - User Story 2 (P1): 8 tasks (comprehensive field coverage)
- Phase 6 - User Story 3 (P2): 6 tasks (progress logging)
- Phase 7 - User Story 4 (P3): 5 tasks (selective preservation validation)
- Phase 8 - Error Handling: 5 tasks (graceful failures)
- Phase 9 - Cache Integration: 3 tasks (incremental builds)
- Phase 10 - Polish: 8 tasks (documentation and validation)

**Critical Path**: Phase 1 (Setup) → Phase 2 (Core Logic) → Phase 3 (Data Models) → Phase 4 (US1) → Phase 5 (US2) → Phase 8 (Error Handling) → Phase 9 (Cache) → Phase 10 (Polish)

**MVP Scope** (Suggested): Phases 1-5 (Setup through US2) = 34 tasks
- Delivers core privacy protection (GPS removal, serial number removal, personal info removal)
- Applies to BOTH thumbnails AND full-size originals
- Preserves display-critical metadata (orientation, color, timestamps, camera info)
- Uses piexif library for robust EXIF manipulation
- Can be fully tested and deployed independently

**Parallel Opportunities**:
- Phase 1: All 6 constant definitions in one session
- Phase 3: model.py and cache.py can run in parallel
- Phase 4: Thumbnails (T016-T020) and Full-Size (T021-T026) can run in parallel
- Phase 5: All 8 verification tasks can run in parallel
- Phase 6: T035 independent, T036-T040 sequential
- Phase 7: All 5 verification tasks can run in parallel
- Phase 10: 5 parallel documentation/validation tasks

**Independent Testing**:
- After Phase 4: Test GPS removal from both thumbnails AND full-size originals with sample GPS-tagged images
- After Phase 5: Test comprehensive metadata removal with images containing serial numbers, creator info, software metadata
- After Phase 6: Test progress logging with 20+ image build
- After Phase 7: Test selective preservation with images containing various metadata types

---

## Notes

- **No test tasks included**: Feature specification does not explicitly request TDD approach. Tests will be added during implementation for validation purposes.
- **Verification tasks**: US2 and US4 include "verify" tasks to ensure constants are correctly defined - these are code review/validation tasks, not test writing.
- **Error handling integrated**: Phase 8 error handling should be integrated during US1-US4 implementation rather than as a separate phase.
- **Format compliance**: All tasks follow `- [ ] [ID] [P?] [Story?] Description with file path` format
- **File paths**: All tasks include exact file paths for implementation
- **Incremental**: Each user story delivers independently testable value
- **Constitution compliant**: All tasks align with static-first, privacy-enhancing principles
- **Scope expansion**: Tasks cover BOTH thumbnails AND full-size originals (not just thumbnails)
- **Library adoption**: Uses piexif 1.1+ instead of manual EXIF manipulation for reduced complexity
- **Shared module**: metadata_filter.py provides shared filtering logic for both thumbnails.py and assets.py

