# exposure Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-02

## Active Technologies
- Python 3.11 (build tooling), HTML5/CSS3/ES Modules (delivery assets)
- Pydantic v2 (data models with validation), Jinja2 (HTML templating), Babel (i18n), pydantic-settings (configuration)
- PyYAML (YAML parsing), Pillow (image metadata), axe-core (accessibility testing)
- Static file generation - no runtime storage
- Git repository (LICENSE file, source file headers tracked in version control)
- Python 3.11+ + PyYAML 6.0+, Pillow 10.0+, Pydantic 2.0+, Jinja2 3.1+, Babel 2.13+, pydantic-settings 2.0+ (006-tool-rename-cli)
- File-based (YAML configuration, static assets, no database) (006-tool-rename-cli)
- Python 3.11+ (build tooling), HTML5/CSS3/ES Modules (delivery assets) + Pydantic v2 (data models), Jinja2 (templating), Pillow (image metadata), PyYAML (config), Babel (i18n) (007-flexible-layout)

## Project Structure

```text
src/
tests/
```

## Commands

```bash
# Build gallery
uv run exposure

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
- 007-flexible-layout: Added Python 3.11+ (build tooling), HTML5/CSS3/ES Modules (delivery assets) + Pydantic v2 (data models), Jinja2 (templating), Pillow (image metadata), PyYAML (config), Babel (i18n)
- 006-tool-rename-cli: Added Python 3.11+ + PyYAML 6.0+, Pillow 10.0+, Pydantic 2.0+, Jinja2 3.1+, Babel 2.13+, pydantic-settings 2.0+
- 005-library-refactor-i18n: Migrated to Pydantic v2 data models, Jinja2 templating, standard Python logging, Babel i18n support, pydantic-settings for configuration management


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
