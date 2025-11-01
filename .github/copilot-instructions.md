# fotoview Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-31

## Active Technologies
- N/A (development tooling only) (002-type-checking)
- Python 3.11 (build tooling), HTML5/CSS3/ES Modules (delivery assets) + PyYAML (YAML parsing), Pillow (image metadata), axe-core (accessibility testing) (003-dark-mode-ui-polish)
- Static file generation - no runtime storage (003-dark-mode-ui-polish)
- N/A (text files only - LICENSE, headers in Python/JS/CSS comments) + Apache Software Foundation (official Apache 2.0 license text), SPDX specification (004-apache-license)
- Git repository (LICENSE file, source file headers tracked in version control) (004-apache-license)

- Python 3.11 + PyYAML (YAML parsing), Pillow (optional thumbnail metadata), (axe [EXTRACTED FROM ALL PLAN.MD FILES] Lighthouse run via CI tooling outside Python scope) (001-image-gallery)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11: Follow standard conventions

## Recent Changes
- 004-apache-license: Added N/A (text files only - LICENSE, headers in Python/JS/CSS comments) + Apache Software Foundation (official Apache 2.0 license text), SPDX specification
- 003-dark-mode-ui-polish: Added Python 3.11 (build tooling), HTML5/CSS3/ES Modules (delivery assets) + PyYAML (YAML parsing), Pillow (image metadata), axe-core (accessibility testing)
- 002-type-checking: Added Python 3.11


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
