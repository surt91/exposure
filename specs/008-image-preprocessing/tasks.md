# Tasks: High-Performance Image Preprocessing with WebP Thumbnails

**Feature**: `008-image-preprocessing`
**Branch**: `008-image-preprocessing`
**Input**: Design documents from `/specs/008-image-preprocessing/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the feature specification, so test tasks are omitted. Focus is on implementation tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create `src/generator/thumbnails.py` module with basic structure and imports
- [X] T002 [P] Add ThumbnailConfig model to `src/generator/model.py` with validation rules
- [X] T003 [P] Add ThumbnailImage model to `src/generator/model.py` with derived properties
- [X] T004 [P] Add ImageMetadata model to `src/generator/model.py` for metadata extraction
- [X] T005 [P] Add BuildCache and CacheEntry models to `src/generator/model.py` for incremental builds
- [X] T006 Extend Image model in `src/generator/model.py` with optional thumbnail field and URL properties
- [X] T007 Extend GalleryConfig model in `src/generator/model.py` with enable_thumbnails and thumbnail_config fields
- [X] T008 [P] Create test file `tests/unit/test_thumbnails.py` with basic test structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Implement `calculate_thumbnail_dimensions()` helper function in `src/generator/thumbnails.py`
- [X] T010 [P] Implement `generate_content_hash()` helper function in `src/generator/thumbnails.py`
- [X] T011 [P] Implement `apply_exif_orientation()` helper function in `src/generator/thumbnails.py`
- [X] T012 Implement `ThumbnailGenerator.__init__()` constructor in `src/generator/thumbnails.py` with config validation
- [X] T013 [P] Implement `ThumbnailGenerator.load_cache()` method in `src/generator/thumbnails.py`
- [X] T014 [P] Implement `ThumbnailGenerator.save_cache()` method in `src/generator/thumbnails.py`
- [X] T015 Implement `ThumbnailGenerator.extract_metadata()` method in `src/generator/thumbnails.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Fast Gallery Loading (Priority: P1) 🎯 MVP

**Goal**: Generate optimized thumbnails during build to enable fast gallery page loads with 50+ images

**Independent Test**: Build gallery with 50 high-resolution images and verify page loads in <3 seconds on 10Mbps connection with thumbnails displayed

### Implementation for User Story 1

- [X] T016 [US1] Implement `ThumbnailGenerator.generate_thumbnail()` core method in `src/generator/thumbnails.py` with EXIF handling and format conversion
- [X] T017 [US1] Add thumbnail file writing logic (WebP and JPEG) in `ThumbnailGenerator.generate_thumbnail()` in `src/generator/thumbnails.py`
- [X] T018 [US1] Add cache checking and mtime comparison in `ThumbnailGenerator.generate_thumbnail()` in `src/generator/thumbnails.py`
- [X] T019 [US1] Implement `ThumbnailGenerator.generate_batch()` method in `src/generator/thumbnails.py` with progress tracking
- [X] T020 [US1] Add thumbnail generation integration to `build_gallery()` in `src/generator/build_html.py`
- [X] T021 [US1] Update thumbnail attachment to Image objects after generation in `src/generator/build_html.py`
- [X] T022 [US1] Update `index.html.j2` template in `src/templates/index.html.j2` to serve thumbnails in gallery view with `<picture>` element
- [X] T023 [US1] Add WebP source with JPEG fallback in gallery grid in `src/templates/index.html.j2`
- [X] T024 [US1] Add error handling for corrupt images in `ThumbnailGenerator.generate_thumbnail()` in `src/generator/thumbnails.py`
- [X] T025 [US1] Add logging for thumbnail generation summary in `src/generator/build_html.py`

**Checkpoint**: At this point, User Story 1 should be fully functional - build generates thumbnails and gallery loads with optimized images

---

## Phase 4: User Story 2 - Full-Resolution Modal Display (Priority: P1) 🎯 MVP

**Goal**: Display original uncompressed images at full resolution when user clicks thumbnail in modal view

**Independent Test**: Click any thumbnail in gallery, verify modal opens with full-resolution original image (not thumbnail)

### Implementation for User Story 2

- [X] T026 [US2] Update `fullscreen.html.j2` template in `src/templates/fullscreen.html.j2` to serve original images in modal view
- [X] T027 [US2] Ensure modal uses `image.image_url` (original) not `image.thumbnail_url` in `src/templates/fullscreen.html.j2`
- [X] T028 [US2] Add progressive loading hint for large original images in modal in `src/templates/fullscreen.html.j2`
- [X] T029 [US2] Verify Image model thumbnail/original URL separation works correctly in templates

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - gallery shows thumbnails, modal shows originals

---

## Phase 5: User Story 3 - Modern Format Optimization (Priority: P2)

**Goal**: Generate WebP thumbnails with JPEG fallback for optimal compression and browser compatibility

**Independent Test**: Build gallery, inspect output directory, verify WebP thumbnails exist and are 25-35% smaller than JPEG fallbacks

### Implementation for User Story 3

- [X] T030 [US3] Add WebP encoding with quality setting in `ThumbnailGenerator.generate_thumbnail()` in `src/generator/thumbnails.py`
- [X] T031 [US3] Add JPEG encoding with quality setting for fallback in `ThumbnailGenerator.generate_thumbnail()` in `src/generator/thumbnails.py`
- [X] T032 [US3] Implement file size tracking for WebP and JPEG in `ThumbnailImage` creation in `src/generator/thumbnails.py`
- [X] T033 [US3] Add WebP savings calculation to `ThumbnailImage.webp_savings_percent` property in `src/generator/model.py`
- [X] T034 [US3] Add logging of compression metrics (WebP vs JPEG savings) in `src/generator/build_html.py`

**Checkpoint**: All modern format optimization complete - WebP with JPEG fallback generated and served

---

## Phase 6: User Story 4 - Automated Thumbnail Sizing (Priority: P2)

**Goal**: Automatically scale thumbnails to optimal 800px max dimension while preserving aspect ratio

**Independent Test**: Build gallery with images of varying sizes, measure thumbnail dimensions, verify all fit within 800px max dimension with aspect ratios preserved

### Implementation for User Story 4

- [X] T035 [US4] Implement aspect ratio preservation in `calculate_thumbnail_dimensions()` in `src/generator/thumbnails.py`
- [X] T036 [US4] Add LANCZOS resampling filter application in `ThumbnailGenerator.generate_thumbnail()` in `src/generator/thumbnails.py`
- [X] T037 [US4] Add edge case handling for images smaller than max_dimension (no upscaling) in `src/generator/thumbnails.py`
- [X] T038 [US4] Add dimension validation in `ThumbnailImage` model in `src/generator/model.py`
- [X] T039 [US4] Add width/height attributes to `<img>` tags in `src/templates/index.html.j2` to prevent layout shift

**Checkpoint**: Thumbnail sizing automated and working correctly for all image sizes and orientations

---

## Phase 7: User Story 5 - Build-Time Processing (Priority: P3)

**Goal**: Process all images at build time with incremental caching to skip unchanged images

**Independent Test**: Run build twice without changes, verify second build skips thumbnail regeneration and completes in <10 seconds

### Implementation for User Story 5

- [X] T040 [US5] Implement cache entry creation and update in `BuildCache.update_entry()` in `src/generator/model.py`
- [X] T041 [US5] Implement `BuildCache.should_regenerate()` with mtime comparison in `src/generator/model.py`
- [X] T042 [US5] Add cache persistence (JSON serialization) in `ThumbnailGenerator.save_cache()` in `src/generator/thumbnails.py`
- [X] T043 [US5] Add cache loading with error recovery in `ThumbnailGenerator.load_cache()` in `src/generator/thumbnails.py`
- [X] T044 [US5] Integrate cache checking before thumbnail generation in `src/generator/thumbnails.py`
- [X] T045 [US5] Add cache save after batch processing in `ThumbnailGenerator.generate_batch()` in `src/generator/thumbnails.py`
- [X] T046 [US5] Add cache statistics logging (X generated, Y cached, Z failed) in `src/generator/build_html.py`

**Checkpoint**: Incremental builds working - unchanged images skipped, only modified images regenerated

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final documentation

- [X] T047 [P] Add unit tests for `calculate_thumbnail_dimensions()` in `tests/unit/test_thumbnails.py`
- [X] T048 [P] Add unit tests for `generate_content_hash()` in `tests/unit/test_thumbnails.py`
- [X] T049 [P] Add unit tests for `apply_exif_orientation()` in `tests/unit/test_thumbnails.py`
- [X] T050 [P] Add unit tests for ThumbnailConfig validation in `tests/unit/test_model.py`
- [X] T051 [P] Add unit tests for ThumbnailImage derived properties in `tests/unit/test_model.py`
- [X] T052 [P] Add unit tests for BuildCache operations in `tests/unit/test_model.py`
- [X] T053 [P] Add integration test for end-to-end thumbnail generation in `tests/integration/test_end_to_end.py`
- [X] T054 [P] Add integration test for incremental builds in `tests/integration/test_end_to_end.py`
- [X] T055 [P] Update reproducibility test to verify thumbnail hashing in `tests/integration/test_reproducibility.py`
- [X] T056 [P] Add performance benchmark test for 100 images in `tests/integration/test_asset_budgets.py`
- [X] T057 [P] Add file size reduction validation test (90%+ reduction) in `tests/integration/test_asset_budgets.py`
- [X] T058 [P] Update accessibility tests to verify thumbnail HTML in `tests/accessibility/test_axe_a11y.py`
- [X] T059 Update README.md with thumbnail feature documentation and configuration examples
- [X] T060 [P] Add ADR document `docs/decisions/008-image-preprocessing-approach.md` explaining thumbnail strategy
- [X] T061 [P] Update CHANGELOG.md with thumbnail feature description
- [X] T062 [P] Add environment variable documentation for thumbnail configuration to README.md
- [X] T063 Run through quickstart.md scenarios to validate all workflows
- [X] T064 Final build and deployment verification with sample gallery

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Fast Gallery Loading**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1) - Full-Resolution Modal**: Can start after Foundational (Phase 2) - Independent but logically follows US1 for complete flow
- **User Story 3 (P2) - Modern Format Optimization**: Can start after Foundational (Phase 2) - Enhances US1 but independently testable
- **User Story 4 (P2) - Automated Thumbnail Sizing**: Can start after Foundational (Phase 2) - Core sizing logic, integrates with US1
- **User Story 5 (P3) - Build-Time Processing**: Can start after Foundational (Phase 2) - Independent caching system, enhances all stories

### Within Each User Story

- Core implementation before integration
- Models and services before templates
- Error handling after core functionality
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: All model additions (T002-T005) can run in parallel
**Phase 2 (Foundational)**: Helper functions (T010, T011) and cache methods (T013, T014) can run in parallel
**Phase 8 (Polish)**: All documentation (T059-T062) and most tests (T047-T058) can run in parallel

**Cross-Story Parallelization** (if multiple developers):
- After Foundational phase completes, different developers can work on different user stories simultaneously
- US1, US3, US4, US5 can all be developed in parallel (different files)
- US2 should coordinate with US1 for template consistency

---

## Parallel Example: Foundational Phase

```bash
# Launch all parallel helper functions together:
Task T010: "Implement generate_content_hash() helper function in src/generator/thumbnails.py"
Task T011: "Implement apply_exif_orientation() helper function in src/generator/thumbnails.py"

# Launch all parallel cache methods together (after T012):
Task T013: "Implement ThumbnailGenerator.load_cache() method in src/generator/thumbnails.py"
Task T014: "Implement ThumbnailGenerator.save_cache() method in src/generator/thumbnails.py"
```

---

## Parallel Example: User Story 1

```bash
# Core thumbnail generation (sequential dependency chain):
Task T016 → T017 → T018 (must be done in order in same file)

# Then parallel integration:
Task T020: "Add thumbnail generation integration to build_html.py"
Task T022: "Update index.html.j2 template to serve thumbnails"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (all model definitions)
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (thumbnail generation in gallery)
4. Complete Phase 4: User Story 2 (original images in modal)
5. **STOP and VALIDATE**: Test complete gallery flow end-to-end
6. Deploy/demo if ready - working gallery with thumbnails and full-res modal

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 + 2 → Test independently → Deploy/Demo (MVP with thumbnails!)
3. Add User Story 3 → Test independently → Deploy/Demo (WebP optimization)
4. Add User Story 4 → Test independently → Deploy/Demo (improved sizing)
5. Add User Story 5 → Test independently → Deploy/Demo (fast incremental builds)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (gallery thumbnails)
   - Developer B: User Story 2 (modal originals)
   - Developer C: User Story 5 (caching system)
3. Then:
   - Developer A: User Story 3 (WebP optimization)
   - Developer B: User Story 4 (sizing refinements)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies, safe for parallel execution
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are optional per spec - focus on implementation
- MVP = User Stories 1 & 2 (gallery thumbnails + modal originals)
- Incremental builds (US5) can be added later without breaking existing functionality

---

## Total Task Count

- **Total Tasks**: 64
- **Setup Phase**: 8 tasks
- **Foundational Phase**: 7 tasks
- **User Story 1**: 10 tasks
- **User Story 2**: 4 tasks
- **User Story 3**: 5 tasks
- **User Story 4**: 5 tasks
- **User Story 5**: 7 tasks
- **Polish Phase**: 18 tasks

**Parallel Opportunities**: 24 tasks marked [P] for parallel execution

**MVP Scope**: Setup + Foundational + US1 + US2 = 29 tasks for complete working gallery with thumbnails

**Recommended First Milestone**: Complete through Phase 4 (US2) for full MVP functionality
