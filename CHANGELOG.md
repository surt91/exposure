# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Gallery banner and title** - Optional full-width banner image with styled title overlay
- Banner image displayed at top of gallery spanning full viewport width
- Responsive banner height: 40vh (desktop), 30vh (tablet), 25vh (mobile)
- Gallery title with enhanced typography: 3rem font, 700 weight, text shadow for readability
- **Gallery subtitle** - Optional descriptive text displayed below the title
- Subtitle styling: 1.5rem font, 400 weight, 0.9 opacity for secondary emphasis
- Subtitle requires title to be present (semantic correctness)
- Subtitle validation: max 300 characters, empty/whitespace treated as None
- Title overlay on banner with gradient background for contrast
- CSS custom properties for banner height customization
- Backward compatible - galleries without banner/title show simple header
- Banner validation: verifies image exists at build time
- Title validation: 1-200 characters, no empty/whitespace-only
- Support for relative (to content_dir) or absolute banner paths
- Semantic HTML with proper accessibility (alt text, heading hierarchy)
- Dark mode compatible - no special handling needed
- i18n support for default gallery title
- **Image preprocessing with optimized thumbnails** - Always generate WebP and JPEG thumbnails at build time
- Thumbnail generation scales images to 800px maximum dimension with aspect ratio preservation
- WebP format with JPEG fallback using HTML `<picture>` element for automatic browser selection
- 90%+ file size reduction for gallery pages (125MB → 15MB for 50 images)
- Page load time improved from 45s to 3s for 50 images on 10Mbps connection
- Incremental build caching - only regenerate thumbnails for changed images
- Cache tracking via `build/.build-cache.json` with mtime comparison
- Full-resolution originals preserved and displayed in modal view
- EXIF orientation correction applied automatically during thumbnail generation
- Configurable quality settings for WebP (default: 85) and JPEG (default: 90)
- `thumbnail_config` nested configuration for advanced control
- Architecture decision record for image preprocessing approach (ADR 008)

### Changed
- Gallery grid now displays thumbnails instead of full-resolution images when enabled
- Original images moved to `images/originals/` subdirectory in build output
- Thumbnails stored in `images/thumbnails/` subdirectory
- Fullscreen modal updated to load original high-resolution images
- Image items now include `data-original-src` attribute for modal integration

## [0.2.0] - 2025-11-02

### Changed
- **Renamed project from "fotoview" to "exposure"**
- Simplified CLI command from `uv run python -m src.generator.build_html` to `uv run exposure`
- Environment variable prefix changed from `FOTOVIEW_*` to `EXPOSURE_*`
- Updated all documentation, translations, and meta tags to reflect new branding
- Logger name changed from "fotoview" to "exposure"
- Package name in pyproject.toml updated to "exposure"

### Added
- Console script entry point `exposure` for simplified command-line invocation

### Breaking Changes
- Environment variables with `FOTOVIEW_*` prefix are no longer recognized - use `EXPOSURE_*` instead
- Package name changed - reinstall with `uv sync` required

### Migration Guide
- Update any scripts or CI/CD pipelines to use `uv run exposure` instead of `uv run python -m src.generator.build_html`
- Replace `FOTOVIEW_*` environment variables with `EXPOSURE_*` equivalents
- The old module invocation `python -m src.generator.build_html` still works as a Python language feature

### Added
- Initial project structure
- Python package configuration with uv
- Basic README and quickstart documentation
- Configuration system (settings.yaml, gallery.yaml)
- MIT License
- **Dark mode support** with automatic system preference detection
- CSS custom properties for theming (18 variables: 7 colors, 4 timing, 7 typography)
- Smooth color transitions and visual flourishes
- Reduced motion support via `prefers-reduced-motion` media query
- Enhanced accessibility with WCAG 2.1 AA compliant contrast ratios
- Browser color scheme integration via `<meta name="color-scheme">`
- Architecture decision record for dark mode approach (ADR 0003)
- **Internationalization (i18n) support** with Babel/gettext
- German locale (de) translations for all UI strings
- `locale` configuration field in settings.yaml
- Automatic fallback to English for unsupported locales
- Translation infrastructure with pybabel workflow
- **Pydantic v2 data models** for automatic validation and type safety
- **Jinja2 templating** replacing string concatenation for HTML generation
- **Standard Python logging** replacing print() statements with configurable levels
- **Pydantic Settings** for enhanced configuration management
- Environment variable support for all settings (FOTOVIEW_* prefix)
- Architecture decision record for library modernization (ADR 0005)

### Changed
- Migrated all dataclass models to Pydantic BaseModel (Image, Category, YamlEntry, GalleryConfig)
- Replaced HTML string building with Jinja2 templates
- Replaced print() statements with logger calls throughout codebase
- Configuration now supports environment variable overrides with validation
- Improved error messages for configuration validation failures

### Deprecated

### Removed

### Fixed

### Security
