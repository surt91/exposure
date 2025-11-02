# Implementation Plan: Library Modernization and Internationalization

**Branch**: `005-library-refactor-i18n` | **Date**: 2025-11-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-library-refactor-i18n/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Refactor the fotoview static gallery generator to use modern Python libraries for improved maintainability, type safety, and internationalization. Replace dataclass models with Pydantic v2 for validation, migrate HTML string concatenation to Jinja2 templates, adopt Python's standard logging module, and implement i18n support for English and German locales. This is an internal refactoring focused on code quality—all existing tests must pass and generated output should remain functionally equivalent, though perfect backward compatibility is not required since there are no production users yet.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**:
- Current: PyYAML (6.0+), Pillow (10.0+)
- New: Pydantic (v2), Jinja2, pydantic-settings (optional for P3)
**Storage**: File-based (YAML for metadata, local images)
**Testing**: pytest (7.4+), pytest-cov, playwright (accessibility tests), axe-playwright-python
**Target Platform**: Build tool - cross-platform (Linux, macOS, Windows)
**Project Type**: Single project (static site generator CLI)
**Performance Goals**:
- Build time should remain reasonable (moderate slowdown acceptable for pre-production tool)
- Generated HTML size must remain within constitution limits (≤30KB)
- CSS/JS bundle sizes must remain within limits (CSS ≤25KB, JS ≤75KB)
**Constraints**:
- YAML compatibility: existing YAML files should work without migration (but breaking changes acceptable if needed)
- Output equivalence: generated HTML should be functionally similar (minor differences acceptable)
- No new runtime dependencies for end users (static output only)
- Constitution compliance: maintain static-first, no backend runtime
**Scale/Scope**:
- Refactoring ~5 Python modules (model, build_html, yaml_sync, scan, assets)
- ~10-20 translatable strings initially
- Support for 2 locales (English, German) in MVP

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The following MUST be affirmed (from `constitution.md`):

1. ✅ **Static-first approach confirmed**: This is a build-tool refactor only. No backend runtime introduced. Generated output remains pure static HTML/CSS/JS.

2. ✅ **Performance budget accepted**: Refactoring maintains existing asset sizes. Jinja2 templates generate same HTML. No new client-side JS. Pydantic runs at build time only.

3. ✅ **Accessibility commitment**: Existing axe tests continue to run. No changes to generated HTML structure or semantics. i18n translations improve accessibility for German users.

4. ✅ **Content integrity**: Existing reproducible build with asset fingerprinting (hash-based filenames) remains unchanged. Build process continues to be deterministic.

5. ✅ **Security/privacy**: No new third-party scripts. All libraries are build-time only (Pydantic, Jinja2). No runtime dependencies. Existing CSP/header strategy documented in `docs/hosting.md` is unaffected.

6. ✅ **Documentation**: Will create ADR for library choices. README quickstart remains valid (same CLI interface). CHANGELOG entry planned for this refactor.

7. ✅ **CI gates enumerated**: All existing gates continue (performance, accessibility via axe, reproducibility, asset sizes). Test suite must pass without modifications per SC-001.

**Status**: All constitution requirements satisfied. This is a pure internal refactoring that improves maintainability while preserving all external contracts.

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
├── __init__.py
├── generator/
│   ├── __init__.py
│   ├── assets.py           # Asset copying with hash-based filenames
│   ├── build_html.py        # Main build logic (to migrate to Jinja2)
│   ├── model.py             # Data models (to migrate to Pydantic)
│   ├── scan.py              # Image discovery and validation
│   ├── yaml_sync.py         # YAML metadata handling (to use Pydantic)
│   └── i18n.py              # NEW: Translation management (P2)
├── static/
│   ├── css/
│   │   ├── fullscreen.css
│   │   └── gallery.css
│   └── js/
│       ├── a11y.js
│       ├── fullscreen.js
│       └── gallery.js
└── templates/
    ├── fullscreen.html.part
    ├── index.html.tpl       # To migrate to proper Jinja2 template
    ├── category_section.html.j2  # NEW: Jinja2 template for category
    └── image_item.html.j2   # NEW: Jinja2 template for image item

tests/
├── __init__.py
├── accessibility/
│   └── test_axe_a11y.py     # Existing axe tests (must continue passing)
├── integration/
│   ├── test_asset_budgets.py
│   ├── test_end_to_end.py
│   ├── test_fullscreen.py
│   └── test_reproducibility.py
└── unit/
    ├── test_build_html.py
    ├── test_model.py        # To update for Pydantic models
    ├── test_scan.py
    ├── test_yaml_sync.py    # To update for Pydantic models
    └── test_i18n.py         # NEW: i18n tests (P2)

config/
├── gallery.yaml             # User-managed metadata (backward compatible)
├── settings.yaml            # Build configuration (may add locale field)
└── locales/                 # NEW: Translation files (P2)
    ├── en.yaml              # English (default)
    └── de.yaml              # German

docs/
├── decisions/
│   └── 0005-library-modernization.md  # NEW: ADR for this refactor
└── hosting.md               # Existing hosting documentation
```

**Structure Decision**: Single project structure. This is a static site generator CLI tool with a single Python package (`src/generator/`). The refactoring adds new template files (Jinja2) and an i18n module, but maintains the existing flat module structure. No multi-tier architecture needed for a build tool.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. This refactoring maintains full constitution compliance.
