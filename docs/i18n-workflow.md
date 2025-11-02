# Internationalization (i18n) Workflow

Exposure uses [Babel](https://babel.pocoo.org/) and [gettext](https://www.gnu.org/software/gettext/) for internationalization support. This document describes the workflow for managing translations.

## Overview

The i18n system consists of:
- **Source strings**: Marked with `_()` function in Python code and Jinja2 templates
- **Message catalog**: `.pot` template file containing all extractable strings
- **Translations**: `.po` files for each locale (human-readable)
- **Compiled translations**: `.mo` files (binary, fast to load)

## Directory Structure

```
locales/
├── messages.pot              # Master template (generated)
├── de/
│   └── LC_MESSAGES/
│       ├── messages.po       # German translations (editable)
│       └── messages.mo       # Compiled German (generated)
└── en/                       # Optional (English is source language)
```

## Workflow

### 1. Mark Strings for Translation

In Jinja2 templates, wrap strings with `_()`:

```jinja2
<h1>{{ _('Image Gallery') }}</h1>
<p>{{ _('Found %(count)s images', count=image_count) }}</p>
```

In Python code, use the `_()` function from `src.generator.i18n`:

```python
from src.generator.i18n import _

logger.info(_("Scanning images in %s..."), path)
logger.warning(_("%d invalid images skipped"), count)
```

### 2. Extract Translatable Strings

Extract all marked strings to the message catalog template:

```bash
uv run pybabel extract -F babel.cfg -o locales/messages.pot .
```

This scans:
- Python files: `src/**/*.py`
- Jinja2 templates: `src/templates/**/*.j2`

### 3. Initialize a New Locale

To add support for a new language (e.g., French):

```bash
uv run pybabel init -i locales/messages.pot -d locales -l fr
```

This creates `locales/fr/LC_MESSAGES/messages.po`.

### 4. Translate Strings

Edit the `.po` file with a text editor or translation tool like [Poedit](https://poedit.net/):

```po
# locales/de/LC_MESSAGES/messages.po

msgid "Image Gallery"
msgstr "Bildergalerie"

msgid "Found %(count)s images"
msgstr "%(count)s Bilder gefunden"

msgid "Scanning images in %s..."
msgstr "Scanne Bilder in %s..."
```

**Important**: Keep variable placeholders (`%s`, `%(name)s`) unchanged in translations.

### 5. Compile Translations

Compile `.po` files to fast binary `.mo` format:

```bash
uv run pybabel compile -d locales
```

This generates `locales/{locale}/LC_MESSAGES/messages.mo` files.

### 6. Update Translations

When source strings change (new strings added, existing modified), update translation catalogs:

```bash
# 1. Extract new/changed strings
uv run pybabel extract -F babel.cfg -o locales/messages.pot .

# 2. Update existing translations
uv run pybabel update -i locales/messages.pot -d locales

# 3. Edit .po files to translate new/changed strings
# (Use text editor or Poedit)

# 4. Compile updated translations
uv run pybabel compile -d locales
```

The `update` command merges new strings into existing `.po` files while preserving existing translations.

## Configuration

### Babel Configuration

`babel.cfg` defines which files to scan for translatable strings:

```ini
[python: src/**.py]
[jinja2: src/templates/**.j2]
extensions=jinja2.ext.i18n
```

### Locale Selection

Users select their locale in `config/settings.yaml`:

```yaml
locale: de  # Options: en (English), de (German)
```

Or via environment variable:

```bash
EXPOSURE_LOCALE=de uv run exposure
```

### Fallback Behavior

- If a translation is missing for the selected locale, the system falls back to English
- If an unsupported locale is specified (e.g., `fr` when only `en` and `de` exist), English is used

## Testing Translations

### Test German Locale

```bash
# Set locale in config
echo "locale: de" >> config/settings.yaml

# Build gallery
uv run python -m src.generator.build_html

# Check generated HTML for German strings
grep -i "Kategorie" dist/index.html
```

### Test Fallback

```bash
# Try unsupported locale
EXPOSURE_LOCALE=fr uv run exposure

# Should use English with no errors
```

### Run i18n Tests

```bash
uv run pytest tests/unit/test_i18n.py -v
```

## Translation Guidelines

1. **Preserve formatting**: Keep HTML tags, placeholders (`%s`, `%(name)s`), and punctuation
2. **Context matters**: Consider where the string appears in the UI
3. **Keep it short**: UI labels should be concise
4. **Consistent terminology**: Use the same translation for repeated terms
5. **Formal vs informal**: German uses formal "Sie" form for user-facing messages
6. **Test in context**: Build the gallery and verify translations make sense in the UI

## Supported Locales

Current supported locales:
- **en** (English) - Default, source language
- **de** (German) - Fully translated

To request a new locale, create a GitHub issue with the locale code (ISO 639-1) and language name.

## Troubleshooting

### Translations not appearing

1. Check that `.mo` files are compiled: `ls locales/*/LC_MESSAGES/*.mo`
2. Verify locale setting: `grep locale config/settings.yaml`
3. Check for translation errors: Look for `msgstr ""` (empty translations) in `.po` files
4. Rebuild: `uv run pybabel compile -d locales`

### Extraction not finding strings

1. Verify `babel.cfg` paths match your file structure
2. Check that strings use `_()` function (not `gettext()` or other variants)
3. Ensure Jinja2 templates use `{{ _('string') }}` syntax
4. Run extract with verbose output: `uv run pybabel extract -F babel.cfg -o locales/messages.pot . -v`

### Compile errors

1. Check for syntax errors in `.po` files (unmatched quotes, missing line breaks)
2. Ensure placeholders match between `msgid` and `msgstr`
3. Use Poedit for validation - it catches common errors

## References

- [Babel Documentation](https://babel.pocoo.org/)
- [GNU gettext Manual](https://www.gnu.org/software/gettext/manual/)
- [Jinja2 i18n Extension](https://jinja.palletsprojects.com/en/3.1.x/extensions/#i18n-extension)
- [ISO 639-1 Language Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
