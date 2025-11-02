# Implementation Plan: Image Metadata Privacy and Build Progress Logging

**Branch**: `010-metadata-privacy` | **Date**: 2025-11-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/010-metadata-privacy/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

**Primary Requirement**: Extend image preprocessing pipeline to (1) strip privacy-sensitive metadata (GPS coordinates, camera serial numbers, personal information) from generated thumbnails while preserving display-critical fields (color profiles, orientation, timestamps, camera/lens info), and (2) display real-time progress logging showing which images are processed with file size reduction percentages.

**Technical Approach**: Integrate metadata stripping into existing `ThumbnailGenerator` class using Pillow's metadata manipulation capabilities. After thumbnail generation, remove sensitive EXIF/IPTC/XMP fields before saving. Add progress logging to `generate_thumbnail()` method showing filename and size reduction. Preserve original source images unchanged. Enhance build cache to track metadata stripping state for incremental builds.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Pillow 10.0+ (image processing), Pydantic 2.0+ (data models), PyYAML 6.0+ (config), Jinja2 3.1+ (templates), Babel 2.13+ (i18n)
**Storage**: File-based (source images, generated thumbnails, build cache JSON, no database)
**Testing**: pytest 7.4+ with pytest-cov, Playwright + axe-core for accessibility, integration tests for build reproducibility and asset budgets
**Target Platform**: Build tooling runs on Linux/macOS/Windows; output is static HTML/CSS/JS for modern browsers (Chrome 76+, Firefox 67+, Safari 12.1+, Edge 79+)
**Project Type**: Single project - static site generator with build-time image processing
**Performance Goals**: Metadata stripping adds <10% to build time; thumbnail generation must remain incremental (only process changed images); build must handle 500+ images within reasonable time (<5 minutes)
**Constraints**: Thumbnail generation pipeline must not corrupt image files; metadata removal must work with JPEG, PNG, GIF formats; build must continue on individual image failures; no runtime dependencies (static output only)
**Scale/Scope**: Typical galleries have 50-500 images; metadata stripping must handle all standard EXIF/IPTC/XMP fields; logging must be real-time (not batched); cache must track which images have metadata stripping applied

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The following MUST be affirmed (from `constitution.md`):

1. **Static-first approach confirmed** ✅ - Feature enhances build-time preprocessing; no backend runtime introduced. Metadata stripping and logging occur during thumbnail generation (build phase only).

2. **Performance budget accepted** ✅ - No changes to delivered HTML/CSS/JS assets. Feature affects build time only (+<10% allowed). Thumbnail size may decrease slightly (metadata removal reduces file overhead by ~1-5KB per image).

3. **Accessibility commitment** ✅ - Feature does not modify UI or user-facing behavior. Existing axe tests remain valid. No new HTML/CSS/JS changes required.

4. **Content integrity** ✅ - Metadata removal is deterministic and reproducible. Same source image produces same stripped thumbnail across builds. Build cache tracks metadata stripping state. Asset fingerprinting (content hashing) already in place, unchanged.

5. **Security/privacy** ✅ - **ENHANCED** - Feature directly improves privacy by removing GPS coordinates, camera serial numbers, and personal information from published thumbnails. No third-party scripts involved. Original source images remain unchanged (user retains full metadata locally).

6. **Documentation** ✅ - This plan documents new behavior. README will be updated with metadata privacy information. Quickstart will explain what metadata is removed and preserved.

7. **CI gates enumerated** ✅ - Existing reproducibility and accessibility tests remain valid. New test coverage required: verify GPS/serial numbers removed from thumbnails, verify progress logging output format, verify build continues on metadata stripping failures.

**Result**: All constitution requirements satisfied. Feature enhances privacy (Principle IV) while maintaining static-first architecture (Principle I).

**Post-Phase 1 Re-evaluation** (2025-11-02):
- Research confirms Pillow's built-in metadata manipulation is sufficient (no new dependencies)
- Data model adds only 3 optional fields to existing models (minimal complexity)
- API contracts define clear boundaries with graceful error handling
- Test strategy validates all privacy guarantees without infrastructure changes
- **Constitution compliance reaffirmed** - All 7 principles satisfied after detailed design

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
├── generator/
│   ├── thumbnails.py        # Modified: Add metadata stripping logic
│   ├── model.py             # Modified: Add metadata tracking to ThumbnailImage
│   ├── utils.py             # Modified: Add metadata removal utilities
│   └── constants.py         # Modified: Add sensitive metadata field definitions

tests/
├── unit/
│   ├── test_metadata_stripping.py  # New: Unit tests for metadata removal
│   └── test_progress_logging.py    # New: Unit tests for progress output
└── integration/
    └── test_thumbnail_privacy.py   # New: E2E test verifying GPS removal
```

**Structure Decision**: Single project (static site generator). Feature adds metadata processing logic to existing `ThumbnailGenerator` class in `src/generator/thumbnails.py`. No new modules required - metadata stripping integrates into current thumbnail generation pipeline. Test files added to verify privacy guarantees.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations. Feature aligns with all principles.
