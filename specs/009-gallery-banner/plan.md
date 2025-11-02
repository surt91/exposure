````markdown
# Implementation Plan: Gallery Banner and Title

**Branch**: `009-gallery-banner` | **Date**: 2025-11-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/009-gallery-banner/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add configurable banner image and title display at the top of the gallery page. Banner spans full viewport width with appropriate cropping, title displays with enhanced styling. Both are optional and configured via YAML. Implementation extends existing Pydantic models, Jinja2 templates, and CSS with responsive design that matches current dark mode support.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: Pydantic 2.0+ (data models), Jinja2 3.1+ (templates), Pillow 10.0+ (image metadata), PyYAML 6.0+ (config), Babel 2.13+ (i18n)
**Storage**: File-based (YAML configuration files, static image assets)
**Testing**: pytest 7.4+ (unit/integration), playwright + axe-playwright-python (accessibility)
**Target Platform**: Static site generation (cross-platform, browser-based delivery)
**Project Type**: Single project (static generator with HTML/CSS/JS output)
**Performance Goals**: Banner image load <3s on 10 Mbps, LCP ≤2.5s (constitution requirement), HTML payload increase ≤5KB
**Constraints**: HTML ≤30KB total (constitution), CSS ≤25KB total (constitution), responsive 320px-3840px, dark mode support required
**Scale/Scope**: Single new configuration section (2 fields: banner_image, title), template modifications (header section), CSS additions (~50-100 lines for banner/title styling), backward compatible (galleries without banner/title continue working)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The following MUST be affirmed (from `constitution.md`):

1. ✅ **Static-first approach confirmed**: Banner and title are rendered at build time into static HTML. No backend runtime, no server-side processing. Banner image is a static asset copied to output directory.

2. ✅ **Performance budget accepted**:
   - HTML impact: +5-10 lines for banner section (~500 bytes), well within 30KB limit
   - CSS impact: ~50-100 lines for banner/title styling (~2-3KB), within 25KB limit
   - JS impact: No additional JavaScript required (uses existing fullscreen/gallery code)
   - Banner image: Existing image processing pipeline handles optimization, lazy loading not applicable to above-fold banner but image will be optimized via existing thumbnail generation if needed

3. ✅ **Accessibility commitment**:
   - Semantic HTML: `<header>` with `<h1>` for title, banner as `<img>` with proper alt text or decorative role
   - axe tests: Will extend existing accessibility test suite to verify banner/title region
   - Keyboard navigation: Banner is non-interactive, title maintains heading hierarchy
   - Screen reader: Banner alt text required in config validation, title properly marked up

4. ✅ **Content integrity**:
   - Reproducible build: Banner image path in YAML (version controlled), build output deterministic
   - Asset fingerprinting: Banner image goes through existing asset copying/fingerprinting pipeline
   - Version control: Configuration changes (banner/title) tracked in gallery.yaml commits
   - Build artifacts: Banner rendered consistently from same input YAML

5. ✅ **Security/privacy**:
   - No third-party scripts: Feature uses only existing Jinja2 templating
   - No tracking: Banner is static image, no external resources or tracking
   - CSP compliance: Banner served from same origin, no external resources
   - Headers: Existing hosting.md security headers apply (no changes needed)

6. ✅ **Documentation**:
   - README update: Will document banner/title configuration in existing config section
   - CHANGELOG: Entry prepared for 0.3.0 (Added: configurable gallery banner and title)
   - ADR: Will create decision record for banner cropping approach (center-crop vs alternatives)
   - Quickstart: Banner/title config example in quickstart.md (Phase 1)

7. ✅ **CI gates enumerated**:
   - Accessibility: Extend existing axe tests to verify banner region accessibility
   - Performance: Banner impact validated against existing Lighthouse CI thresholds
   - Reproducibility: Banner rendering included in existing build hash verification
   - Asset sizes: CSS budget verified in existing asset budget integration test
   - Backward compatibility: Existing unit tests verify galleries without banner still build

**All constitution requirements satisfied. No violations or exceptions needed.**

---

### Post-Phase 1 Design Review ✅

**Re-evaluation Date**: 2025-11-02
**Status**: PASSED - All constitution requirements remain satisfied after design phase.

**Design Verification**:
1. ✅ **Static-first maintained**: Design uses CSS object-fit (browser-native), no server-side image manipulation
2. ✅ **Performance budgets on track**:
   - Estimated CSS addition: 2-3KB (documented in research.md Q2)
   - Estimated HTML addition: 500 bytes (documented in data-model.md)
   - No JS additions required
3. ✅ **Accessibility integrated**: Template contract specifies semantic HTML, alt text, heading hierarchy (contracts/template-context.md)
4. ✅ **Build reproducibility preserved**: Banner asset copy uses deterministic file operations (data-model.md)
5. ✅ **No new security concerns**: No external resources, same-origin assets only (research.md Q7)
6. ✅ **Documentation complete**: README update planned, CHANGELOG entry drafted, quickstart.md created
7. ✅ **CI gates covered**: Test plan in quickstart.md covers accessibility, performance, backward compatibility

**Conclusion**: Design phase completed successfully. All constitution principles maintained. Ready to proceed to implementation (Phase 2: /speckit.tasks).

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
│   ├── model.py         # MODIFY: Add banner/title fields to GalleryConfig model
│   ├── build_html.py    # MODIFY: Pass banner/title data to templates
│   └── constants.py     # ADD: Banner height constants if needed
├── templates/
│   └── index.html.j2    # MODIFY: Add banner/title section in header
└── static/
    └── style.css        # MODIFY: Add banner/title styling with dark mode support

config/
├── gallery.yaml         # MODIFY: Document banner/title fields (example)
└── settings.yaml        # MODIFY: Add optional banner/title configuration schema

tests/
├── unit/
│   └── test_model.py    # ADD: Test banner/title config validation
├── integration/
│   └── test_build.py    # MODIFY: Test banner/title rendering
└── accessibility/
    └── test_a11y.py     # MODIFY: Test banner accessibility
```

**Structure Decision**: Single project structure. This is a pure static site generator with no frontend/backend split. All changes are within the existing `src/generator/` module for build logic, `src/templates/` for HTML rendering, and `src/static/` for CSS styling. Configuration extends existing YAML files. Tests follow established pattern of unit/integration/accessibility.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations.** All constitution requirements are satisfied. This feature maintains the static-first architecture, respects performance budgets, and requires no exceptions to established constraints.

````
