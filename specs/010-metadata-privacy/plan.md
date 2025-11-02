# Implementation Plan: Image Metadata Privacy and Build Progress Logging

**Branch**: `010-metadata-privacy` | **Date**: 2025-11-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-metadata-privacy/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Extend the build pipeline to automatically strip sensitive metadata (GPS coordinates, camera serial numbers, creator information, software details, embedded thumbnails) from both generated thumbnails AND full-size original copies while preserving display-critical metadata (orientation, color profiles, timestamps, camera/lens info). Implement real-time progress logging during build to show per-image processing status and file size reduction. Use `piexif` library for robust EXIF manipulation instead of manual implementation to reduce complexity and improve error handling.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Pillow 10.0+ (image processing), Pydantic 2.0+ (data models), piexif 1.1+ (EXIF manipulation), PyYAML 6.0+ (config), Jinja2 3.1+ (templates), Babel 2.13+ (i18n)
**Storage**: File-based (source images, generated thumbnails, build cache JSON, no database)
**Testing**: pytest (unit/integration tests), axe-core (accessibility)
**Target Platform**: Cross-platform build tool (Linux, macOS, Windows)
**Project Type**: Single project - static site generator with preprocessing pipeline
**Performance Goals**: Metadata stripping adds <10% to build time; <10ms per image
**Constraints**: Must not corrupt images; must preserve display-critical metadata; build continues on metadata failures
**Scale/Scope**: Galleries with 100-1000 images; support JPEG/PNG/WebP/GIF formats

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The following MUST be affirmed (from `constitution.md`):

1. ✅ **Static-first approach confirmed**: No backend runtime introduced - metadata stripping happens during static build process
2. ✅ **Performance budget accepted**: No HTML/CSS/JS changes - this feature only affects build process
3. ✅ **Accessibility commitment**: No UI changes - build tool feature only
4. ✅ **Content integrity**: Reproducible builds maintained - metadata stripping is deterministic (same input → same output); build cache tracks content hashes
5. ✅ **Security/privacy**: This feature ENHANCES privacy by removing sensitive metadata (GPS, serial numbers, creator info) from published images
6. ✅ **Documentation**: Research completed; quickstart will be generated in Phase 1
7. ✅ **CI gates**: Existing tests remain; new tests will verify metadata removal without impacting existing gates

**No constitution violations** - this is a pure build-time enhancement that improves privacy without affecting the static delivery model.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
└── generator/
    ├── thumbnails.py          # MODIFY: Add metadata stripping to thumbnail generation
    ├── assets.py              # MODIFY: Add metadata stripping to copy_with_hash() for full-size originals
    ├── model.py               # MODIFY: Add file size tracking to ThumbnailImage model
    └── metadata_filter.py     # NEW: piexif-based metadata filtering logic (shared by thumbnails + originals)

tests/
├── unit/
│   └── test_metadata_filter.py  # NEW: Unit tests for metadata stripping
└── integration/
    ├── test_thumbnail_metadata.py  # NEW: Integration test for thumbnail metadata removal
    └── test_original_metadata.py   # NEW: Integration test for full-size original metadata removal

tests/fixtures/
└── metadata_samples/          # NEW: Test images with various EXIF configurations
```

**Structure Decision**: Single project structure - this is a build tool enhancement. Modified files are in the existing `src/generator/` module. New `metadata_filter.py` module encapsulates piexif usage for separation of concerns and testability - shared by both thumbnail generation (`thumbnails.py`) and full-size original copying (`assets.py`). Integration tests verify end-to-end metadata removal for both thumbnails and full-size originals.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - no complexity tracking needed.
