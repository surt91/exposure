# Implementation Plan: Apache 2.0 License

**Branch**: `004-apache-license` | **Date**: 2025-11-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-apache-license/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add Apache 2.0 license to fotoview project including LICENSE file in repository root, SPDX license headers in all source files (Python, JavaScript, CSS), and license metadata in project files (README.md, pyproject.toml). Technical approach uses official Apache 2.0 license text from Apache Software Foundation, standard SPDX header format for machine-readable license detection, and manual file updates (no automated tools needed for one-time license addition).

## Technical Context

**Language/Version**: N/A (text files only - LICENSE, headers in Python/JS/CSS comments)
**Primary Dependencies**: Apache Software Foundation (official Apache 2.0 license text), SPDX specification
**Storage**: Git repository (LICENSE file, source file headers tracked in version control)
**Testing**: Manual verification (file existence, header presence, GitHub badge), optional: licensee/FOSSA scanners
**Target Platform**: All platforms (license is platform-agnostic)
**Project Type**: Documentation/meta-files (applies to existing single-project structure)
**Performance Goals**: N/A (license files do not affect runtime performance)
**Constraints**: Must use exact Apache 2.0 text, SPDX-compliant headers, no license headers in JSON/YAML
**Scale/Scope**: ~25 source files requiring headers (Python, JS, CSS), 1 LICENSE file, 2 metadata files (README, pyproject.toml)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The following MUST be affirmed (from `constitution.md`):

1. ✅ Static-first approach confirmed - License files are text/metadata only, no runtime code
2. ✅ Performance budget accepted - License headers add ~200 bytes per file (comments), negligible impact
3. ✅ Accessibility commitment - License changes do not affect UI/accessibility
4. ✅ Content integrity - LICENSE file and headers tracked in git, reproducible builds unaffected
5. ✅ Security/privacy - No third-party scripts, license clarifies usage terms (enhances transparency)
6. ✅ Documentation - README.md will include License section, ADR not needed (standard practice)
7. ✅ CI gates enumerated - Existing gates unaffected, optional: add license header verification

**Decision**: Standard Apache 2.0 licensing approach fully complies with constitution.
**Rationale**: License addition is administrative/legal metadata with zero impact on technical architecture, performance, or accessibility. Enhances project transparency per constitution principle V (Documentation & Traceability).

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
# New files to create
LICENSE                         # NEW: Apache 2.0 license text (361 lines)
README.md                       # MODIFY: Add License section

# Modified files (add license headers)
pyproject.toml                  # MODIFY: Add license = "Apache-2.0" field

src/
├── __init__.py                 # ADD HEADER
├── generator/
│   ├── __init__.py             # ADD HEADER
│   ├── assets.py               # ADD HEADER
│   ├── build_html.py           # ADD HEADER
│   ├── model.py                # ADD HEADER
│   ├── scan.py                 # ADD HEADER
│   └── yaml_sync.py            # ADD HEADER
└── static/
    ├── css/
    │   ├── gallery.css         # ADD HEADER
    │   └── fullscreen.css      # ADD HEADER
    └── js/
        ├── a11y.js             # ADD HEADER
        ├── fullscreen.js       # ADD HEADER
        └── gallery.js          # ADD HEADER

tests/
├── __init__.py                 # ADD HEADER
├── accessibility/
│   ├── __init__.py             # ADD HEADER
│   └── test_axe_a11y.py        # ADD HEADER
├── integration/
│   ├── test_asset_budgets.py   # ADD HEADER
│   ├── test_end_to_end.py      # ADD HEADER
│   ├── test_fullscreen.py      # ADD HEADER
│   └── test_reproducibility.py # ADD HEADER
└── unit/
    ├── test_build_html.py      # ADD HEADER
    ├── test_model.py           # ADD HEADER
    ├── test_scan.py            # ADD HEADER
    └── test_yaml_sync.py       # ADD HEADER

# Files explicitly excluded (no headers)
config/                         # User configuration (YAML)
content/                        # User content (images)
docs/                           # Documentation (Markdown)
specs/                          # Specifications (Markdown)
.github/                        # GitHub config (YAML)
output/                         # Generated files
__pycache__/                    # Build artifacts
```

**Structure Decision**: Single-project structure with ~25 source files requiring license headers. LICENSE file added to repository root per Apache 2.0 standard. Headers follow language-specific comment syntax: Python (#), CSS/JS (/* */). Configuration and documentation files excluded per spec edge cases.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. License addition is administrative metadata with zero constitutional impact.
