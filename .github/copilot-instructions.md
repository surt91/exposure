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
- Python 3.11 + Pillow 10.0+ (image processing), Pydantic 2.0+ (data models), Jinja2 3.1+ (HTML templating), PyYAML 6.0+ (config) (008-image-preprocessing)
- File-based (source images, generated thumbnails, build cache for incremental builds) (008-image-preprocessing)
- Python 3.11 + Pydantic 2.0+ (data models), Jinja2 3.1+ (templates), Pillow 10.0+ (image metadata), PyYAML 6.0+ (config), Babel 2.13+ (i18n) (009-gallery-banner)
- File-based (YAML configuration files, static image assets) (009-gallery-banner)

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
- 009-gallery-banner: Added Python 3.11 + Pydantic 2.0+ (data models), Jinja2 3.1+ (templates), Pillow 10.0+ (image metadata), PyYAML 6.0+ (config), Babel 2.13+ (i18n)
- 008-image-preprocessing: Added Python 3.11 + Pillow 10.0+ (image processing), Pydantic 2.0+ (data models), Jinja2 3.1+ (HTML templating), PyYAML 6.0+ (config)
- 007-flexible-layout: Added Python 3.11+ (build tooling), HTML5/CSS3/ES Modules (delivery assets) + Pydantic v2 (data models), Jinja2 (templating), Pillow (image metadata), PyYAML (config), Babel (i18n)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
