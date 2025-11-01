# Research: Tool Rename and CLI Simplification

**Feature**: 006-tool-rename-cli
**Date**: 2025-11-02
**Status**: Complete

## Overview

This document consolidates research findings for renaming the static gallery generator from "fotoview" to "galleria" and simplifying CLI invocation. Since this is primarily a refactoring task with well-established patterns, research focuses on Python packaging best practices and comprehensive renaming strategies.

## Research Questions

### 1. How to create a simple CLI command with Python packaging?

**Decision**: Use setuptools `console_scripts` entry point in `pyproject.toml`

**Rationale**:
- Standard Python packaging approach for creating CLI commands
- Works seamlessly with `uv run` and other package managers
- Automatically creates executable scripts in the virtual environment
- No additional dependencies required (uses existing hatchling build backend)
- Well-documented and widely adopted pattern

**Implementation Pattern**:
```toml
[project.scripts]
exposure = "src.generator.build_html:main"
```

**Alternatives Considered**:
- **Click/Typer framework**: Rejected - overkill for single command, adds dependency
- **Custom wrapper script**: Rejected - not installable, requires manual PATH management
- **Poetry scripts**: Rejected - project uses uv/hatchling, not Poetry

**References**:
- [Python Packaging User Guide - Entry Points](https://packaging.python.org/en/latest/specifications/entry-points/)
- [Setuptools Documentation - console_scripts](https://setuptools.pypa.io/en/latest/userguide/entry_point.html)

---

### 2. Best practices for comprehensive package renaming?

**Decision**: Systematic search-and-replace with validation at each layer

**Rationale**:
- Minimizes risk of missing references
- Allows incremental verification (run tests after each layer)
- Clear audit trail of what changed where
- Prevents subtle bugs from inconsistent naming

**Renaming Layers** (in order):
1. **Package metadata** (pyproject.toml, README badges)
2. **Source code internals** (logger names, module docstrings)
3. **Configuration** (environment variable prefix in model.py, settings.yaml comments)
4. **User-facing strings** (log messages, HTML meta tags)
5. **Translations** (Babel i18n workflow: extract → update → compile)
6. **Documentation** (README, docs/, specs/)
7. **Tests** (assertions, command invocations)
8. **License** (copyright holder name)

**Validation Strategy**:
- Run `grep -r "fotoview" .` after each layer (excluding git history)
- Run full test suite after each layer
- Check i18n compilation: `uv run pybabel compile -d locales`
- Verify command works: `uv run exposure`

**Alternatives Considered**:
- **Automated refactoring tools**: Rejected - no standard tool for cross-language rename (Python + YAML + Markdown + PO files)
- **Single big-bang replace**: Rejected - high risk of breaking something, hard to debug
- **Keep old name internally**: Rejected - creates confusion, defeats purpose of clarity

**References**:
- [Refactoring: Improving the Design of Existing Code](https://refactoring.com/) (Martin Fowler)
- [Python Packaging: Renaming and Deprecating](https://packaging.python.org/en/latest/guides/package-name-normalization/)

---

### 3. How to handle environment variable prefix changes?

**Decision**: Clean break - change prefix from `FOTOVIEW_*` to `EXPOSURE_*` without backward compatibility

**Rationale**:
- No existing users yet - clean slate opportunity
- Simpler implementation (no deprecation logic needed)
- Clearer code without conditional handling
- No technical debt from day one

**Implementation Approach**:
```python
class GalleryConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="EXPOSURE_",
        # ... other settings
    )
```

**Alternatives Considered**:
- **Support both prefixes**: Rejected - adds unnecessary complexity for zero users
- **Keep FOTOVIEW_***: Rejected - defeats purpose of rename

**References**:
- [Pydantic Settings - Environment Variables](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [The Twelve-Factor App - Config](https://12factor.net/config)

---

### 4. Babel workflow for updating translation strings?

**Decision**: Standard Babel extract-update-compile workflow

**Rationale**:
- Already in use (see docs/i18n-workflow.md)
- Preserves existing translations, only updates changed strings
- Fuzzy matching for similar strings reduces translator work
- Well-tested, industry-standard tooling

**Workflow Steps**:
```bash
# 1. Extract translatable strings from source code
uv run pybabel extract -F babel.cfg -o locales/messages.pot .

# 2. Update existing .po files with new strings
uv run pybabel update -i locales/messages.pot -d locales

# 3. Manually edit locales/de/LC_MESSAGES/messages.po
#    - Update "Fotoview" → "Exposure"
#    - Update "Fotoview Galerie-Generator" → "Exposure Galerie-Generator"

# 4. Compile .po to .mo binary format
uv run pybabel compile -d locales

# 5. Verify with German locale
EXPOSURE_LOCALE=de uv run exposure
```

**Changed Strings**:
- English: "Fotoview Gallery Generator" → "Exposure Gallery Generator"
- German: "Fotoview Galerie-Generator" → "Exposure Galerie-Generator"
- Environment variable examples in help text

**Alternatives Considered**:
- **Manual .po editing only**: Rejected - risks format corruption, loses metadata
- **New translation files**: Rejected - loses translation history, unnecessary work
- **Skip i18n update**: Rejected - inconsistent branding across locales

**References**:
- [Babel Documentation](https://babel.pocoo.org/en/latest/)
- [GNU gettext Manual](https://www.gnu.org/software/gettext/manual/)
- Project's existing i18n-workflow.md

---

### 5. Impact on existing gallery.yaml files and generated output?

**Decision**: Zero impact - YAML schema and HTML/CSS/JS output unchanged

**Rationale**:
- Rename is purely internal (tool name, not data format)
- gallery.yaml structure is part of user contract
- Generated galleries remain functionally identical
- Only meta generator tag changes (invisible to users)

**Unchanged Elements**:
- gallery.yaml schema (categories, images, titles, descriptions)
- Generated HTML structure (classes, IDs, semantic markup)
- CSS selectors and styling
- JavaScript module exports and event handlers
- Asset hashing algorithm
- Image file processing

**Changed Elements** (non-functional):
- `<meta name="generator" content="Exposure">` in HTML head
- Internal logger output (developer-facing only)
- CLI command name (documented user-facing change)

**Verification**:
- Run reproducibility test: build same gallery before/after rename, compare asset hashes
- Only changed files should be index.html (meta tag), CSS (if generator comment exists), JS (if generator comment exists)

**References**:
- Existing gallery.yaml contract: specs/001-image-gallery/contracts/gallery-yaml.schema.yaml
- Reproducibility test: tests/integration/test_reproducibility.py

---

## Summary of Decisions

| Question | Decision | Key Benefit |
|----------|----------|-------------|
| CLI invocation | setuptools console_scripts | Standard, no dependencies |
| Rename strategy | Layered search-replace | Incremental validation, low risk |
| Environment vars | Clean break to EXPOSURE_* | No technical debt, simpler code |
| i18n update | Standard Babel workflow | Preserves translations |
| gallery.yaml impact | No changes | Backward compatible |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Missed reference in obscure file | Medium | Low | Comprehensive grep search, full test suite |
| Translation compilation fails | Low | Medium | Test i18n workflow before code changes |
| Tests fail with new command | Medium | Medium | Run tests after each layer, fix incrementally |
| Breaking change for scripts | None | None | No existing users - clean slate |

## Next Steps

Proceed to Phase 1: Generate data-model.md and contracts for the CLI entry point contract.
