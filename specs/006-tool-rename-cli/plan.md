# Implementation Plan: Tool Rename and CLI Simplification

**Branch**: `006-tool-rename-cli` | **Date**: 2025-11-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-tool-rename-cli/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Rename the static gallery generator from "fotoview" to "exposure" and simplify CLI invocation from `uv run python -m src.generator.build_html` to `uv run exposure`. This is a comprehensive refactoring that updates package metadata, environment variables, documentation, translations, and all user-facing strings while maintaining the same functionality. The technical approach involves: (1) adding a console_scripts entry point in pyproject.toml, (2) performing systematic search-and-replace across codebase, (3) updating i18n translation files via Babel workflow, (4) updating all documentation and configuration files, and (5) validating that all tests pass with the new naming.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PyYAML 6.0+, Pillow 10.0+, Pydantic 2.0+, Jinja2 3.1+, Babel 2.13+, pydantic-settings 2.0+
**Storage**: File-based (YAML configuration, static assets, no database)
**Testing**: pytest with pytest-cov, playwright + axe-playwright-python for accessibility
**Target Platform**: Cross-platform (Linux, macOS, Windows) - build tool only, output is static HTML/CSS/JS
**Project Type**: Single Python project - CLI tool for static site generation
**Performance Goals**: Gallery build time < 2 seconds for typical use case (50-100 images), generated HTML/CSS/JS within asset budgets
**Constraints**: Must maintain existing asset budgets (HTML ≤30KB, CSS ≤25KB, JS ≤75KB), all tests must pass, zero breaking changes to gallery.yaml format or generated output functionality
**Scale/Scope**: Single-package refactoring affecting ~50 files (Python source, tests, docs, translations, configs)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The following MUST be affirmed (from `constitution.md`):

1. ✅ **Static-first approach confirmed**: This is a pure refactoring - no changes to the static-first architecture. All output remains static HTML/CSS/JS.
2. ✅ **Performance budget accepted**: No changes to generated output size. The rename affects only tool invocation and branding, not asset generation.
3. ✅ **Accessibility commitment**: Existing axe tests and semantic HTML remain unchanged. Only string updates in test assertions needed.
4. ✅ **Content integrity**: Build reproducibility unchanged. Asset hashing and fingerprinting logic remains identical.
5. ✅ **Security/privacy**: No changes to security headers, CSP, or third-party scripts. Only documentation updates to reflect new tool name.
6. ✅ **Documentation**: README quickstart will be updated with new command. No new ADR needed (rename is documented in this spec/plan).
7. ✅ **CI gates enumerated**: All existing CI gates remain active. Tests updated to use new command syntax but gates unchanged.

**Result**: All constitution principles satisfied. This is a non-functional refactoring that preserves all architectural decisions while improving developer experience.

## Project Structure

### Documentation (this feature)

```text
specs/006-tool-rename-cli/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── cli-entrypoint.md  # Console script entry point contract
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Single Python project structure (existing)
src/
├── __init__.py
├── generator/
│   ├── __init__.py       # Module initialization, logging setup
│   ├── build_html.py     # Main build logic, CLI entry point
│   ├── model.py          # Pydantic models, GalleryConfig
│   ├── scan.py           # Image discovery
│   ├── yaml_sync.py      # YAML metadata management
│   ├── assets.py         # Asset hashing and copying
│   └── i18n.py           # Internationalization support
├── static/
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript modules
└── templates/
    └── *.j2              # Jinja2 templates

tests/
├── unit/                 # Unit tests for all modules
├── integration/          # End-to-end build tests
└── accessibility/        # Playwright + axe tests

config/
├── settings.yaml         # Build configuration
└── gallery.yaml          # Image metadata

locales/
├── messages.pot          # Translation template
└── de/LC_MESSAGES/       # German translations
    ├── messages.po
    └── messages.mo

docs/
├── decisions/            # ADRs
├── hosting.md            # Deployment guide
└── i18n-workflow.md      # Translation workflow

pyproject.toml            # Package metadata, dependencies, entry point
README.md                 # User documentation
CHANGELOG.md              # Version history
LICENSE                   # Apache 2.0 license
```

**Structure Decision**: Single Python project with static site generation. This rename affects primarily:
1. **pyproject.toml**: Package name and console_scripts entry point
2. **src/generator/**: Logger names, module docstrings
3. **src/generator/model.py**: Environment variable prefix in GalleryConfig
4. **src/templates/**: Meta generator tags
5. **locales/**: Translation strings
6. **docs/**: All documentation references
7. **tests/**: Test assertions and command invocations
8. **LICENSE**: Copyright holder name

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations**: All constitution principles are satisfied. This is a pure refactoring with zero functional changes.
