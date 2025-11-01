# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
