# Implementation Plan: Type Checking and Type Annotations

**Branch**: `002-type-checking` | **Date**: 2025-11-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-type-checking/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Introduce comprehensive static type checking to the fotoview Python codebase to catch type-related bugs during development. System will verify 100% type annotation coverage across all functions and parameters (excluding self/cls), enforce strict type checking through CI/CD gates, and provide developers immediate feedback on type errors within 5 seconds. Implementation will integrate with existing pyproject.toml configuration and development workflow without requiring runtime behavior changes.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: PyYAML, Pillow (existing); ty from Astral (type checker); types-PyYAML>=6.0, types-Pillow>=10.0 (type stubs)
**Storage**: N/A (development tooling only)
**Testing**: pytest (existing); type checking will integrate as additional validation layer
**Target Platform**: Linux development environment; CI/CD (existing)
**Project Type**: Single project (static site generator)
**Performance Goals**: Type checking must complete in <10 seconds for full codebase analysis; <5 seconds for developer feedback (ty's Rust implementation expected to exceed these targets)
**Constraints**: Must not change runtime behavior; must work with Python 3.11+ syntax (list[str], X | Y unions); must handle optional PIL import gracefully
**Scale/Scope**: ~500-1000 lines of Python code in src/generator/; 5-6 modules; test coverage separate with relaxed rules

**Tool Choice Rationale**: Using ty from Astral as strategic bet on their ecosystem (uv, ruff). Experimental but aligned with project's existing Astral tooling. Provisionally configured; exact format subject to ty documentation.

**Research Complete**: All technical decisions documented in [research.md](research.md)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The following MUST be affirmed (from `constitution.md`):

1. ✅ **Static-first approach confirmed**: Type checking is a development-time tool only; no runtime code or backend introduced. Static assets remain unchanged.

2. ✅ **Performance budget accepted**: Type checking does not affect delivered assets. No changes to HTML/CSS/JS output. Build process extended but delivery unchanged.

3. ✅ **Accessibility commitment**: No accessibility impact. Type checking enforces code quality but does not modify user-facing features.

4. ✅ **Content integrity**: Reproducible builds maintained. Type checking configuration stored in version control (pyproject.toml). No generated content introduced.

5. ✅ **Security/privacy**: No security or privacy impact. Type checking is local development tooling. No third-party scripts or runtime changes.

6. ✅ **Documentation**: README will be updated with type checking commands. ADR will document tool selection rationale (ADR-0002-type-checking.md).

7. ✅ **CI gates enumerated**: Type checking will be added as new CI gate:
   - Existing gates: build reproducibility, axe accessibility, performance budget, asset sizes
   - New gate: Type checking must pass with zero errors
   - Gate failure blocks merge (non-zero exit code from type checker)

**Status**: All constitution requirements satisfied. No violations or exceptions needed.

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
# Single project structure (existing)
src/
├── __init__.py
└── generator/
    ├── __init__.py
    ├── assets.py          # Asset hashing/copying utilities
    ├── build_html.py      # Main gallery builder
    ├── model.py           # Data models (Image, Category, GalleryConfig, YamlEntry)
    ├── scan.py            # Image discovery and validation
    └── yaml_sync.py       # YAML metadata synchronization

tests/
├── __init__.py
├── unit/              # Type checking: strict mode
│   ├── test_build_html.py
│   ├── test_model.py
│   ├── test_scan.py
│   └── test_yaml_sync.py
├── integration/       # Type checking: strict mode
│   ├── test_asset_budgets.py
│   ├── test_end_to_end.py
│   ├── test_fullscreen.py
│   └── test_reproducibility.py
└── accessibility/     # Type checking: relaxed (playwright types complex)
    └── test_axe_a11y.py

# Configuration files affected
pyproject.toml         # Will add [tool.mypy] or similar section
pytest.ini             # No changes needed
.github/
└── workflows/         # CI workflow will add type checking step

# New documentation
docs/
└── decisions/
    └── 0002-type-checking.md  # ADR for tool selection
```

**Structure Decision**: Single project structure maintained. Type checking configuration added to existing pyproject.toml. All source files in src/generator/ will be type-checked with strict mode. Test files will have slightly relaxed rules (allow untyped decorators, test fixtures). No new source directories needed - this is purely a quality gate addition.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations. Type checking is purely additive development tooling with no impact on delivered static assets, performance budgets, or user-facing functionality.
