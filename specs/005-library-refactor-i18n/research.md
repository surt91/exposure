# Research: Library Modernization and Internationalization

**Feature**: 005-library-refactor-i18n
**Date**: 2025-11-01
**Purpose**: Research and validate library choices for refactoring dataclasses to Pydantic, string templates to Jinja2, print to logging, and implementing i18n

## Research Questions

1. Should we use Pydantic v2 BaseModel or pydantic-settings for configuration?
2. How should we structure Jinja2 templates for the HTML generation?
3. What's the best approach for simple i18n with YAML-based translations?
4. How to configure Python logging to maintain current console output format?

---

## 1. Pydantic for Data Models and Configuration

### Decision: Use Pydantic v2 BaseModel for all models; evaluate pydantic-settings for GalleryConfig

### Rationale

**For Data Models (Image, Category, YamlEntry):**
- Pydantic v2 provides automatic validation with clear error messages (FR-002)
- Built-in serialization for YAML round-tripping via `model_dump()` and `model_validate()`
- Field validators handle complex constraints (e.g., Path validation, non-empty strings)
- Backward compatible with existing YAML structure through field aliases and validators
- Better IDE support and type checking than dataclasses

**For Configuration (GalleryConfig):**
- **Option A**: Use regular Pydantic BaseModel - simpler, sufficient for YAML-only config
- **Option B**: Use pydantic-settings - adds environment variable support, but more complex

**Recommendation**: Start with BaseModel for P1 (simpler). Pydantic-settings is optional for P3 (FR-020).

### Alternatives Considered

1. **Keep dataclasses + add manual validation** - Rejected: More boilerplate, no automatic validation
2. **attrs library** - Rejected: Less popular, less validation features than Pydantic
3. **marshmallow** - Rejected: Separate schema/object model, more complex

### Implementation Notes

```python
# Example migration pattern
from pydantic import BaseModel, Field, field_validator
from pathlib import Path

class Image(BaseModel):
    filename: str = Field(min_length=1)
    file_path: Path
    category: str = Field(min_length=1)
    width: int | None = None
    height: int | None = None
    title: str = ""
    description: str = ""

    @property
    def alt_text(self) -> str:
        return self.title if self.title else Path(self.filename).stem.replace("_", " ").title()

    class Config:
        # Allow Path objects
        arbitrary_types_allowed = True
```

**Key compatibility patterns:**
- Use `model_validate(dict)` instead of `from_dict()` class method
- Use `model_dump()` instead of `to_dict()` method
- Field aliases for backward compatibility if YAML keys differ
- Custom validators for complex Path/file existence checks

---

## 2. Jinja2 for HTML Templating

### Decision: Use Jinja2 with template inheritance and macros for reusable components

### Rationale

- Industry-standard Python templating (used by Flask, Django, Ansible)
- Separates presentation from logic (FR-005, FR-006)
- Template inheritance reduces duplication
- Auto-escaping prevents XSS (security benefit)
- Fast and mature (stable API since 2008)
- Better maintainability than string concatenation

### Alternatives Considered

1. **Python string formatting (current approach)** - Rejected: Hard to maintain, no auto-escaping, logic mixed with presentation
2. **Mako templates** - Rejected: Less popular, no auto-escaping by default
3. **Chameleon** - Rejected: XML-based, overkill for HTML generation

### Implementation Notes

**Template Structure:**
```
templates/
├── base.html.j2              # Base layout with head, body structure
├── index.html.j2             # Main gallery page (extends base)
├── macros/
│   ├── category_section.j2   # Category section macro
│   └── image_item.j2         # Image item macro
└── fullscreen.html.part      # Fullscreen modal (can be included)
```

**Key patterns:**
```jinja2
{# base.html.j2 #}
<!DOCTYPE html>
<html lang="{{ locale }}">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="{{ css_href }}">
</head>
<body>
    {% block content %}{% endblock %}
    <script src="{{ js_href }}"></script>
</body>
</html>

{# macros/image_item.j2 #}
{% macro render_image(image, category_name) %}
<div class="image-item"
     data-category="{{ category_name }}"
     data-filename="{{ image.filename }}"
     {% if image.title %}data-title="{{ image.title }}"{% endif %}
     {% if image.description %}data-description="{{ image.description }}"{% endif %}>
    <img src="images/{{ image.hashed_filename }}"
         alt="{{ image.alt_text }}"
         loading="lazy" />
    {% if image.title %}
    <div class="image-caption">{{ image.title }}</div>
    {% endif %}
</div>
{% endmacro %}
```

**Migration strategy:**
1. Convert `index.html.tpl` to proper Jinja2 with inheritance
2. Extract image grid HTML generation into macros
3. Replace string concatenation in `build_html.py` with Jinja2 rendering
4. Verify output equivalence with tests (FR-007, SC-005)

**Jinja2 Environment Configuration:**
```python
from jinja2 import Environment, FileSystemLoader, select_autoescape

template_dir = Path(__file__).parent.parent / "templates"
env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True
)
```

---

## 3. Internationalization (i18n) Approach

### Decision: Use Babel with Jinja2 integration for professional i18n

### Rationale

**Why Babel + Jinja2:**
- **Native Jinja2 integration**: Babel has built-in support via `jinja2.ext.i18n` extension
- **Industry standard**: Used by Flask, Pyramid, and other major Python frameworks
- **Extraction tools**: `pybabel extract` automatically finds translatable strings in templates
- **Compilation**: `.po` files compile to fast `.mo` binary format
- **Future-proof**: Supports pluralization, context, and complex cases if needed later
- **Tooling ecosystem**: GUIs like Poedit for translators, no Python knowledge needed

**Why not simpler approaches:**
- Spec has only ~10-20 strings NOW, but i18n is a P2 feature worth doing properly
- Babel's complexity is mostly in setup; daily use is simple
- Having professional tooling encourages proper i18n practices

### Alternatives Considered

1. **Simple YAML dictionary** - Considered but rejected:
   - No Jinja2 integration (need to pass translation function everywhere)
   - Manual extraction of strings (error-prone)
   - No tooling for translators (YAML is code, not translation format)
   - Would need custom solution for future features (pluralization)

2. **gettext directly (without Babel)** - Rejected:
   - Manual catalog management
   - No good Jinja2 integration
   - Babel is the standard wrapper around gettext for Python

3. **fluent (Mozilla's i18n)** - Rejected:
   - Too new, smaller ecosystem
   - Complex for simple needs
   - No established Jinja2 integration

4. **JSON translation files** - Rejected:
   - Same limitations as YAML approach
   - No translator tooling

### Implementation Notes

**Setup Workflow:**

1. **Install Babel**: `pip install babel`

2. **Configure Babel** (`babel.cfg` in project root):
```ini
[python: src/**.py]
[jinja2: src/templates/**.j2]
extensions=jinja2.ext.i18n
```

3. **Configure Jinja2 with i18n extension**:
```python
from jinja2 import Environment, FileSystemLoader
from babel.support import Translations

# Setup Jinja2 environment with i18n
env = Environment(
    loader=FileSystemLoader("src/templates"),
    extensions=['jinja2.ext.i18n']
)

# Load translations
locale = config.locale  # e.g., "de" or "en"
translations_dir = Path(__file__).parent.parent.parent / "locales"

if locale != "en":
    translations = Translations.load(translations_dir, [locale])
else:
    translations = Translations.load(translations_dir, [])  # NullTranslations

env.install_gettext_translations(translations)
```

4. **Mark strings for translation in templates**:
```jinja2
{# index.html.j2 #}
<h1>{{ _('Image Gallery') }}</h1>
<h2>{{ _('Category') }}</h2>

{# With variables #}
<p>{{ _('Found %(count)s images', count=image_count) }}</p>
```

5. **Mark strings in Python code**:
```python
from babel import _

logger.info(_("Scanning images in %s..."), config.content_dir)
logger.warning(_("%d invalid images skipped"), count)
```

6. **Extract translatable strings**:
```bash
pybabel extract -F babel.cfg -o locales/messages.pot .
```

7. **Initialize German catalog**:
```bash
pybabel init -i locales/messages.pot -d locales -l de
```

8. **Edit translations** (`locales/de/LC_MESSAGES/messages.po`):
```po
msgid "Image Gallery"
msgstr "Bildergalerie"

msgid "Category"
msgstr "Kategorie"

msgid "Scanning images in %s..."
msgstr "Scanne Bilder in %s..."

msgid "Found %(count)s images"
msgstr "%(count)s Bilder gefunden"
```

9. **Compile translations**:
```bash
pybabel compile -d locales
```

10. **Update translations** (when strings change):
```bash
pybabel extract -F babel.cfg -o locales/messages.pot .
pybabel update -i locales/messages.pot -d locales
# Edit .po files, then:
pybabel compile -d locales
```

**Directory Structure:**
```
config/
  settings.yaml           # Add locale: de/en
babel.cfg                 # Babel extraction config
locales/
  messages.pot           # Template (source)
  de/
    LC_MESSAGES/
      messages.po        # German translations (human-readable)
      messages.mo        # Compiled (binary, fast)
  en/                    # Optional (English is source language)
```

**Python i18n helper** (`src/generator/i18n.py`):
```python
from pathlib import Path
from babel.support import Translations, NullTranslations

_translations = None

def setup_i18n(locale: str = "en", locales_dir: Path = None):
    """Setup i18n for the given locale."""
    global _translations

    if locales_dir is None:
        locales_dir = Path(__file__).parent.parent.parent / "locales"

    if locale == "en":
        _translations = NullTranslations()
    else:
        try:
            _translations = Translations.load(locales_dir, [locale])
        except Exception:
            # Fallback to English if locale not found
            _translations = NullTranslations()

def _(message: str) -> str:
    """Get translated message."""
    if _translations is None:
        return message
    return _translations.gettext(message)

# For parameterized messages
def gettext(message: str, **kwargs) -> str:
    """Get translated message with parameter substitution."""
    translated = _(message)
    if kwargs:
        return translated % kwargs
    return translated
```

**Configuration (add to `settings.yaml`):**
```yaml
# Locale for UI strings (default: en)
locale: en  # or "de"
```

---

## 4. Python Logging Configuration

### Decision: Use standard logging module with StreamHandler and custom formatter for backward-compatible console output

### Rationale

- Standard library - no new dependencies
- Configurable log levels (FR-010)
- Structured logging for future enhancements (file output, etc.)
- Can maintain current console format (FR-011)
- Better than print for library code (can be silenced/redirected)

### Alternatives Considered

1. **Keep using print()** - Rejected: Not configurable, can't be disabled, no levels
2. **Rich library** - Rejected: Adds dependency for formatting we don't need yet
3. **structlog** - Rejected: Overkill for simple CLI tool
4. **loguru** - Rejected: Non-standard, adds dependency

### Implementation Notes

**Logger Configuration (`src/generator/__init__.py` or main entry point):**
```python
import logging
import sys

def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configure logging for the gallery generator.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("fotoview")
    logger.setLevel(getattr(logging, level.upper()))

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    # Formatter that matches current output style
    # Current: "Scanning images in content/..."
    # Logger: same format, no timestamp by default
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger

# Create module-level logger
logger = logging.getLogger("fotoview")
```

**Migration Pattern:**
```python
# Old code:
print(f"Scanning images in {config.content_dir}...")
print(f"Warning: {count} invalid images skipped")
print("Error: Duplicate filenames detected:", file=sys.stderr)

# New code:
logger.info("Scanning images in %s...", config.content_dir)
logger.warning("%d invalid images skipped", count)
logger.error("Duplicate filenames detected")
```

**Log Levels Mapping:**
- `print("✓ ...")` → `logger.info("✓ ...")`
- `print("Warning: ...")` → `logger.warning(...)`
- `print("Error: ...", file=sys.stderr)` → `logger.error(...)`
- Debug info (if added) → `logger.debug(...)`

**Configuration via settings.yaml (optional for P3):**
```yaml
# Log level (DEBUG, INFO, WARNING, ERROR)
log_level: INFO
```

**Logging + i18n integration:**
```python
logger.info(i18n.t("messages.scanning_images", path=config.content_dir))
logger.warning(i18n.t("messages.invalid_images_skipped", count=invalid_count))
```

---

## Summary of Decisions

| Component | Library/Approach | Rationale |
|-----------|-----------------|-----------|
| Data Models | Pydantic v2 BaseModel | Automatic validation, serialization, backward compatible |
| Configuration | Pydantic BaseModel (P1), pydantic-settings optional (P3) | Simple for YAML, extensible to env vars |
| HTML Templates | Jinja2 with inheritance & macros | Industry standard, auto-escaping, maintainable |
| i18n | Babel + gettext (.po/.mo files) | Professional tooling, Jinja2 integration, translator-friendly |
| Logging | Python standard logging | No new deps, configurable, backward-compatible output |

---

## Dependencies to Add

```toml
# Add to pyproject.toml dependencies:
dependencies = [
    "pyyaml>=6.0",
    "pillow>=10.0",
    "pydantic>=2.0",        # NEW: Data validation
    "jinja2>=3.1",          # NEW: Templating
    "babel>=2.13",          # NEW: i18n with Jinja2 integration
]

# Optional for P3:
# "pydantic-settings>=2.0",  # For environment variable config
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Pydantic validation breaks existing YAML | Medium | High | Comprehensive tests, field validators for backward compat |
| Jinja2 output differs from current HTML | Low | High | Byte-for-byte comparison tests, careful migration |
| i18n fallback fails | Low | Medium | Unit tests for missing translations, always load English |
| Logging format changes break scripts | Low | Low | Custom formatter maintains current format |
| Performance regression | Low | Medium | Benchmark build times, Pydantic is fast in practice |

All risks have mitigations in place. Test suite (SC-001) is critical safety net.
