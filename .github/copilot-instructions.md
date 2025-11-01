# fotoview Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-31

## Active Technologies
- Python 3.11 (build tooling), HTML5/CSS3/ES Modules (delivery assets)
- Pydantic v2 (data models with validation), Jinja2 (HTML templating), Babel (i18n), pydantic-settings (configuration)
- PyYAML (YAML parsing), Pillow (image metadata), axe-core (accessibility testing)
- Static file generation - no runtime storage
- Git repository (LICENSE file, source file headers tracked in version control)

## Project Structure

```text
src/
tests/
```

## Commands

```bash
# Build gallery
uv run python -m src.generator.build_html

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Lint
uv run ruff check .

# i18n workflow
uv run pybabel extract -F babel.cfg -o locales/messages.pot .
uv run pybabel update -i locales/messages.pot -d locales
uv run pybabel compile -d locales
```

## Code Style

Python 3.11: Follow standard conventions

## Recent Changes
- 005-library-refactor-i18n: Migrated to Pydantic v2 data models, Jinja2 templating, standard Python logging, Babel i18n support, pydantic-settings for configuration management
- 004-apache-license: Added Apache 2.0 license with SPDX headers
- 003-dark-mode-ui-polish: Added dark mode support with CSS custom properties
- 002-type-checking: Added type checking with ty


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
