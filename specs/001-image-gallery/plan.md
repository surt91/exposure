# Implementation Plan: Modern Image Gallery

**Branch**: `001-image-gallery` | **Date**: 2025-10-31 | **Spec**: ./spec.md
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Deliver a static, responsive, mobile-friendly image gallery with fullscreen
view, category ordering via YAML, and auto-stub generation for new images.
Implementation uses a lightweight Python script to (a) read image metadata and
YAML, (b) write missing stubs, (c) emit static HTML/CSS/JS assets into `dist/`.
No server/database; all runtime interaction is client-side JS for modal and
keyboard navigation.

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: PyYAML (YAML parsing), Pillow (optional thumbnail metadata), (axe & Lighthouse run via CI tooling outside Python scope)
**Storage**: N/A (filesystem only: images folder + YAML file)
**Testing**: pytest (unit + integration around generation), accessibility & performance via external CI scripts (non-Python)
**Target Platform**: Static site served via CDN (desktop + mobile browsers)
**Project Type**: single (static site generator + assets)
**Performance Goals**: First image visible ≤ 2s; fullscreen open ≤ 300ms; scroll latency < 100ms with 500 images
**Constraints**: HTML ≤30KB, critical CSS ≤25KB, initial JS ≤75KB uncompressed (constitution); no third-party scripts by default
**Scale/Scope**: Up to 500 images smoothly; stub mechanism handles batch additions efficiently

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Affirmed:
1. Static-first: Python used only for build-time generation; output is static.
2. Performance budgets adopted; build pipeline will enforce asset sizes.
3. Accessibility: semantic HTML structure + alt text + keyboard navigation; axe CI planned.
4. Content integrity: reproducible build (same input → identical dist/); asset hashing planned.
5. Security/privacy: CSP documented (restrict to self), no third-party scripts.
6. Documentation: README quickstart & initial ADR placeholders to be added in first commit.
7. CI gates: Will script checks for sizes, axe scan, Lighthouse run, reproducibility.

No violations at this stage.

### Post-Design Re-Evaluation
Design artifacts (data model, contracts, quickstart) maintain static-only
approach. Asset hashing & accessibility tests planned. No new dependencies
breach minimalism (PyYAML + optional Pillow only). Gates remain satisfied.

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
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/
├── generator/              # Python build-time scripts
│   ├── __init__.py
│   ├── scan.py             # Discover images
│   ├── yaml_sync.py        # Read/update YAML stubs
│   ├── build_html.py       # Emit HTML pages
│   ├── assets.py           # Hashing + asset copy
│   └── model.py            # Data classes (Image, Category, Config)
├── static/                 # Unprocessed static assets (css, base js)
│   ├── css/
│   └── js/
└── templates/             # HTML templates (Jinja2 or simple format strings)

dist/                      # Generated static site output

tests/
├── unit/
│   ├── test_scan.py
│   ├── test_yaml_sync.py
│   └── test_build_html.py
├── integration/
│   └── test_end_to_end.py  # Run generator & assert outputs
└── accessibility/          # Axe script harness (non-Python invocation placeholder)

content/                   # User-provided images (source)
config/
├── gallery.yaml           # Category + image metadata
└── settings.yaml          # Paths & config (folder overrides)
```

**Structure Decision**: Single static-site generator project; Python scripts produce assets in `dist/`. Separation of generator logic, user content, config, templates, and output ensures reproducibility and traceability.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
