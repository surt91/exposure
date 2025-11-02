# Data Model: Tool Rename and CLI Simplification

**Feature**: 006-tool-rename-cli
**Date**: 2025-11-02
**Status**: Complete

## Overview

This feature is a refactoring that changes tool naming and invocation patterns. There are no new data entities, but several existing entities are modified to reflect the new name "exposure".

## Modified Entities

### 1. Package Metadata (pyproject.toml)

**Purpose**: Python package configuration that defines the installable package and CLI entry points

**Modified Attributes**:
- `name`: "fotoview" → "exposure"
- `scripts`: Add entry point mapping `exposure = "src.generator.build_html:main"`

**Relationships**:
- Defines entry point that references `build_html.main()` function
- Referenced by package managers (uv, pip) for installation
- Used by `uv run exposure` command resolution

**Validation Rules**:
- Package name must be valid Python identifier (lowercase, hyphens allowed)
- Entry point must reference existing module and function
- Script name must not conflict with system commands

**Example**:
```toml
[project]
name = "exposure"
version = "0.2.0"  # Bump minor for new feature

[project.scripts]
exposure = "src.generator.build_html:main"
```

---

### 2. GalleryConfig (src/generator/model.py)

**Purpose**: Pydantic settings model for loading configuration from YAML and environment variables

**Modified Attributes**:
- `env_prefix`: "FOTOVIEW_" → "EXPOSURE_"

**Relationships**:
- Loads from `config/settings.yaml`
- Overrides from environment variables with `EXPOSURE_*` prefix
- Used by `build_html.py` for all configuration

**Validation Rules**:
- All existing validation rules unchanged (paths must exist, locale must be valid, etc.)
- Environment variable names must be uppercase with underscores

**Example**:
```python
class GalleryConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="EXPOSURE_",
        yaml_file=_yaml_settings_file,
        # ... other settings
    )
```

---

### 3. Logger Instance (src/generator/*.py)

**Purpose**: Python logging instances for diagnostic output

**Modified Attributes**:
- Logger name: "fotoview" → "exposure" (affects all log output)

**Relationships**:
- Created via `logging.getLogger("exposure")`
- Used throughout `src/generator/` modules
- Output configured by `setup_logging()` in `src/generator/__init__.py`

**Validation Rules**:
- Logger name should be consistent across all modules
- Must match package name for clarity

**Example**:
```python
import logging

logger = logging.getLogger("exposure")
```

---

### 4. HTML Meta Generator Tag (src/templates/index.html.j2)

**Purpose**: HTML meta tag indicating the tool that generated the gallery

**Modified Attributes**:
- Content: "Fotoview" → "Exposure"

**Relationships**:
- Embedded in every generated HTML page
- Not used by any code logic (purely informational)
- May be read by web analytics or SEO tools

**Validation Rules**:
- Must be valid HTML meta tag
- Content should match package name (capitalized)

**Example**:
```html
<meta name="generator" content="Exposure">
```

---

### 5. Translation Strings (locales/*.po)

**Purpose**: Internationalized user-facing messages

**Modified Strings**:

| English (en) | German (de) | Context |
|--------------|-------------|---------|
| "Fotoview Gallery Generator" | "Fotoview Galerie-Generator" | Log banner |
| → "Exposure Gallery Generator" | → "Exposure Galerie-Generator" | |
| Examples: `FOTOVIEW_LOCALE=de` | Examples: `FOTOVIEW_LOCALE=de` | Help text |
| → `EXPOSURE_LOCALE=de` | → `EXPOSURE_LOCALE=de` | |

**Relationships**:
- Source: `locales/messages.pot` (template)
- Compiled to: `locales/*/LC_MESSAGES/messages.mo` (binary)
- Loaded by: `src/generator/i18n.py`

**Validation Rules**:
- All msgid strings must have corresponding msgstr translations
- .po files must compile without errors to .mo format
- Plural forms must be preserved

**Workflow**:
1. Extract: `uv run pybabel extract -F babel.cfg -o locales/messages.pot .`
2. Update: `uv run pybabel update -i locales/messages.pot -d locales`
3. Edit: Manually update msgstr in .po files
4. Compile: `uv run pybabel compile -d locales`

---

### 6. Copyright Notice (LICENSE)

**Purpose**: Apache 2.0 license copyright holder identification

**Modified Attributes**:
- Copyright holder: "fotoview contributors" → "exposure contributors"

**Relationships**:
- Referenced in SPDX headers in all source files
- Displayed in repository root
- May be referenced by LICENSE.txt in distributions

**Validation Rules**:
- Must follow Apache 2.0 license format
- Year should reflect original publication (2025)
- Holder name should be clear and consistent

**Example**:
```
Copyright 2025 exposure contributors

Licensed under the Apache License, Version 2.0...
```

---

## Unchanged Entities

The following entities are **not modified** by this feature:

- **Image**: Metadata model for gallery images (filename, title, description, etc.)
- **Category**: Grouping of images by category name
- **GalleryYAML**: Structure of gallery.yaml configuration file
- **AssetHash**: File fingerprinting for cache busting
- **BuildOutput**: Generated HTML/CSS/JS assets

These remain unchanged because the rename is purely about tool identity, not data structure or functionality.

## Entity Relationship Diagram

```
┌─────────────────────┐
│  pyproject.toml     │
│  name: "exposure"   │
└──────────┬──────────┘
           │ defines
           ▼
┌─────────────────────┐       ┌─────────────────────┐
│  CLI Entry Point    │       │  Environment Vars   │
│  exposure command   │◄──────│  EXPOSURE_*        │
└──────────┬──────────┘       └─────────────────────┘
           │ invokes
           ▼
┌─────────────────────┐       ┌─────────────────────┐
│  build_html.main()  │──────►│  GalleryConfig      │
│  Logger: "exposure" │       │  env_prefix: GALL…  │
└──────────┬──────────┘       └─────────────────────┘
           │ generates
           ▼
┌─────────────────────┐       ┌─────────────────────┐
│  index.html         │       │  Translation .po    │
│  meta: Exposure     │◄──────│  "Exposure…"        │
└─────────────────────┘       └─────────────────────┘
```

## Migration Path

For users upgrading from fotoview to exposure:

1. **Commands**: Change `uv run python -m src.generator.build_html` → `uv run exposure`
2. **Environment Variables**: Optionally change `FOTOVIEW_*` → `EXPOSURE_*` (old still works in v0.2.0)
3. **Scripts**: Update any automation/CI scripts to use new command
4. **Documentation**: No action needed (provided by project)

**Data Migration**: None required - gallery.yaml format unchanged.

## Validation Strategy

After implementation, verify:

1. **Command works**: `uv run exposure` builds gallery successfully
2. **Environment vars work**: `EXPOSURE_LOCALE=de uv run exposure` applies locale
3. **Old env vars work** (v0.2.0): `FOTOVIEW_LOCALE=de uv run exposure` still works
4. **Translations compile**: `uv run pybabel compile -d locales` succeeds
5. **Meta tag updated**: Generated index.html contains `<meta name="generator" content="Exposure">`
6. **Logger output correct**: Log messages show "exposure" logger name
7. **Tests pass**: Full test suite succeeds with no logic changes
8. **No stray references**: `grep -r "fotoview" .` (excluding git) returns only expected results

## Technical Debt

None introduced. This refactoring reduces confusion by aligning all naming consistently.
