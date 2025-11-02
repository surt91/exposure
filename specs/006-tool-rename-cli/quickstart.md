# Quickstart: Tool Rename and CLI Simplification

**Feature**: 006-tool-rename-cli
**Audience**: Developers implementing this feature
**Estimated Time**: 2-3 hours

## Overview

This quickstart guides you through renaming the gallery generator from "fotoview" to "exposure" and adding a simple CLI command. The work is organized in layers to enable incremental testing and minimize risk.

## Prerequisites

- Branch `006-tool-rename-cli` checked out
- All existing tests passing on current branch
- Familiarity with Python packaging (pyproject.toml)
- Babel/gettext tools installed (already in dev dependencies)

## Implementation Layers

### Layer 1: Package Metadata (15 min)

**Goal**: Update package name and add CLI entry point

**Files**:
- `pyproject.toml`

**Changes**:
1. Change `name = "fotoview"` → `name = "exposure"`
2. Bump version `0.1.0` → `0.2.0` (minor version for new CLI command)
3. Add scripts section:
   ```toml
   [project.scripts]
   exposure = "src.generator.build_html:main"
   ```

**Validation**:
```bash
# Reinstall package with new entry point
uv sync

# Test new command
uv run exposure

# Verify gallery builds successfully
ls dist/index.html
```

**Expected**: Gallery builds, output matches previous builds

---

### Layer 2: Source Code Internals (20 min)

**Goal**: Update logger names and module docstrings

**Files**:
- `src/generator/__init__.py`
- `src/generator/build_html.py`
- `src/generator/i18n.py`
- `src/generator/model.py`
- `src/generator/scan.py`
- `src/generator/yaml_sync.py`
- `src/generator/assets.py`

**Changes**:
1. Search for `logging.getLogger("fotoview")` → replace with `logging.getLogger("exposure")`
2. Update module docstrings if they mention "fotoview"
3. In `model.py`, change:
   ```python
   # Before
   env_prefix="FOTOVIEW_",

   # After
   env_prefix="EXPOSURE_",
   ```

**Validation**:
```bash
# Run tests
uv run pytest tests/unit/

# Check logger output
EXPOSURE_LOG_LEVEL=DEBUG uv run exposure | grep -i exposure
```

**Expected**: Tests pass, log messages show "exposure" logger name

---

### Layer 3: Configuration Files (10 min)

**Goal**: Update config file comments and examples

**Files**:
- `config/settings.yaml`

**Changes**:
1. Update header comment: `# Fotoview Gallery Configuration` → `# Exposure Gallery Configuration`

**Validation**:
```bash
# Verify config still loads
uv run exposure
```

**Expected**: No changes to behavior, just comments updated

---

### Layer 4: User-Facing Strings (15 min)

**Goal**: Update log messages and HTML meta tags

**Files**:
- `src/generator/build_html.py` (translatable strings)
- `src/templates/index.html.j2`
- `src/templates/index.html.tpl` (if exists)

**Changes**:

1. In build_html.py, update the welcome banner:
   ```python
   logger.info(_("Fotoview Gallery Generator"))
   # →
   logger.info(_("Exposure Gallery Generator"))
   ```

2. In templates, update meta tag:
   ```html
   <meta name="generator" content="Fotoview">
   <!-- → -->
   <meta name="generator" content="Exposure">
   ```

**Validation**:
```bash
# Rebuild gallery
uv run exposure

# Check meta tag
grep 'generator' dist/index.html
```

**Expected**: HTML contains `<meta name="generator" content="Exposure">`

---

### Layer 5: Translations (20 min)

**Goal**: Update i18n strings for English and German

**Files**:
- `locales/messages.pot`
- `locales/de/LC_MESSAGES/messages.po`
- `locales/de/LC_MESSAGES/messages.mo`

**Changes**:

1. Extract new strings:
   ```bash
   uv run pybabel extract -F babel.cfg -o locales/messages.pot .
   ```

2. Update .po files:
   ```bash
   uv run pybabel update -i locales/messages.pot -d locales
   ```

3. Manually edit `locales/de/LC_MESSAGES/messages.po`:
   ```po
   # Find and update:
   msgid "Fotoview Gallery Generator"
   msgstr "Fotoview Galerie-Generator"
   # →
   msgid "Exposure Gallery Generator"
   msgstr "Exposure Galerie-Generator"
   ```

4. Compile translations:
   ```bash
   uv run pybabel compile -d locales
   ```

**Validation**:
```bash
# Test English
uv run exposure | grep "Exposure Gallery Generator"

# Test German
EXPOSURE_LOCALE=de uv run exposure | grep "Exposure Galerie-Generator"
```

**Expected**: Correct translated strings in both locales

---

### Layer 6: Documentation (25 min)

**Goal**: Update all documentation files

**Files**:
- `README.md`
- `CHANGELOG.md`
- `docs/i18n-workflow.md`
- `docs/hosting.md`
- `docs/decisions/*.md`
- `.github/copilot-instructions.md`

**Changes**:

1. **README.md**:
   - Title: `# Fotoview` → `# Exposure`
   - All command examples: `uv run python -m src.generator.build_html` → `uv run exposure`
   - Environment variables: `FOTOVIEW_*` → `EXPOSURE_*`
   - Project description references

2. **CHANGELOG.md** (add new entry):
   ```markdown
   ## [0.2.0] - 2025-11-02

   ### Changed
   - Renamed project from "fotoview" to "exposure"
   - Simplified CLI command from `uv run python -m src.generator.build_html` to `uv run exposure`
   - Environment variable prefix changed from `FOTOVIEW_*` to `EXPOSURE_*`
   - Updated all documentation, translations, and meta tags

   ### Deprecated
   - `FOTOVIEW_*` environment variables (still work but will be removed in v0.3.0)
   ```

3. **docs/i18n-workflow.md**:
   - Update command examples with new env var names
   - Keep content about Babel workflow (unchanged)

4. **docs/hosting.md**:
   - Update any references to project name

5. **docs/decisions/*.md**:
   - Update references in ADRs if they mention "fotoview"

6. **.github/copilot-instructions.md**:
   - Update project title and references

**Validation**:
```bash
# Search for old name (excluding git history)
grep -r "fotoview" --exclude-dir=.git --exclude-dir=specs

# Should only find:
# - LICENSE (old copyright, update next)
# - specs/ directories (old feature specs, ok)
# - This quickstart guide (intentional)
```

---

### Layer 7: Tests (20 min)

**Goal**: Update test assertions and command invocations

**Files**:
- `tests/unit/test_build_html.py`
- `tests/unit/test_i18n.py`
- `tests/unit/test_model.py`
- `tests/integration/*.py`
- `tests/accessibility/*.py`

**Changes**:

1. Update environment variable tests:
   ```python
   # Before
   monkeypatch.setenv("FOTOVIEW_LOCALE", "de")
   # After
   monkeypatch.setenv("EXPOSURE_LOCALE", "de")
   ```

2. Update string assertions:
   ```python
   # Before
   assert result == "Fotoview Gallery Generator"
   # After
   assert result == "Exposure Gallery Generator"
   ```

3. Check logger name tests (if any)

**Validation**:
```bash
# Run full test suite
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term

# Run accessibility tests
uv run pytest tests/accessibility/ -m a11y
```

**Expected**: All tests pass with 100% of previous coverage

---

### Layer 8: License (10 min)

**Goal**: Update copyright holder name

**Files**:
- `LICENSE`
- All source files with SPDX headers (if they include project name)

**Changes**:

1. **LICENSE** (first line):
   ```
   Copyright 2025 fotoview contributors
   →
   Copyright 2025 exposure contributors
   ```

2. Check source files for SPDX headers:
   ```bash
   grep -r "Copyright.*fotoview" --include="*.py" --include="*.js" --include="*.css"
   ```
   If found, update to "exposure contributors"

**Validation**:
```bash
# Verify license file
head -5 LICENSE

# Check for old copyright notices
grep -r "fotoview contributors" --exclude-dir=.git
```

**Expected**: Only specs/ directories contain old name

---

## Final Verification

### Comprehensive Tests

```bash
# 1. Full test suite
uv run pytest --cov=src --cov-report=html

# 2. Type checking
uv run ty check src/

# 3. Linting
uv run ruff check .

# 4. Build gallery
uv run exposure

# 5. Test environment variables
EXPOSURE_LOCALE=de uv run exposure
EXPOSURE_OUTPUT_DIR=build uv run exposure

# 6. Verify generated output
grep -E '(Exposure|exposure)' dist/index.html
grep -E '(Fotoview|fotoview)' dist/index.html  # Should find nothing

# 7. Check for stray references
grep -r "fotoview" --exclude-dir=.git --exclude-dir=specs --exclude-dir=dist
# Expected: Only this quickstart and historical references
```

### Smoke Test Checklist

- [ ] `uv run exposure` builds gallery successfully
- [ ] Generated HTML has correct meta tag: `<meta name="generator" content="Exposure">`
- [ ] German locale works: `EXPOSURE_LOCALE=de uv run exposure`
- [ ] Environment overrides work: `EXPOSURE_OUTPUT_DIR=build uv run exposure`
- [ ] All tests pass: `uv run pytest`
- [ ] Type checking passes: `uv run ty check src/`
- [ ] Linting passes: `uv run ruff check .`
- [ ] README examples use new command
- [ ] CHANGELOG documents the change
- [ ] No "fotoview" in user-facing strings (except historical docs)

---

## Troubleshooting

### Command not found: exposure

**Cause**: Package entry point not installed

**Fix**:
```bash
uv sync  # Reinstall package with new entry point
```

### Tests fail: "FOTOVIEW_LOCALE" not recognized

**Cause**: Tests still use old environment variable names

**Fix**: Update test files to use `EXPOSURE_LOCALE`

### Translation compilation fails

**Cause**: Syntax error in .po file

**Fix**:
```bash
# Check .po syntax
uv run pybabel compile -d locales --statistics

# Fix errors in locales/de/LC_MESSAGES/messages.po
# Re-compile
```

### Old command still works

**Status**: Expected behavior

**Explanation**: `uv run python -m src.generator.build_html` is a Python language feature, not controlled by the package. This provides backward compatibility for users' scripts.

---

## Estimated Timeline

| Layer | Task | Time |
|-------|------|------|
| 1 | Package metadata | 15 min |
| 2 | Source code internals | 20 min |
| 3 | Configuration | 10 min |
| 4 | User-facing strings | 15 min |
| 5 | Translations | 20 min |
| 6 | Documentation | 25 min |
| 7 | Tests | 20 min |
| 8 | License | 10 min |
| **Final** | Verification & smoke tests | 20 min |
| **Total** | | **~2.5 hours** |

## Next Steps

After completing this quickstart:

1. Commit changes: `git add -A && git commit -m "Rename tool from fotoview to exposure"`
2. Run final verification suite (see above)
3. Push branch: `git push origin 006-tool-rename-cli`
4. Create pull request to main branch
5. Update PR description with before/after examples
6. Wait for CI to pass (all tests, type checking, linting)
7. Merge to main
8. Tag release: `git tag v0.2.0`
9. Update deployment documentation if needed

## Resources

- Feature Spec: [spec.md](spec.md)
- Implementation Plan: [plan.md](plan.md)
- Data Model: [data-model.md](data-model.md)
- CLI Contract: [contracts/cli-entrypoint.md](contracts/cli-entrypoint.md)
- Python Packaging Guide: https://packaging.python.org/
- Babel Documentation: https://babel.pocoo.org/
