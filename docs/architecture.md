# Exposure Architecture

## System Overview

Exposure is a static image gallery generator with a build-time processing pipeline. No runtime server required.

```
Source Images + YAML Config → Python Generator → Static HTML/CSS/JS
```

## Tech Stack

- **Python 3.11+**: Pydantic v2 (models), Jinja2 (templates), Pillow (images), PyYAML (config), Babel (i18n), piexif (EXIF), pydantic-settings (config)
- **Type checking**: `ty` (Astral's Rust-based checker) - all code fully type-annotated
- **Frontend**: Vanilla ES modules, CSS-only dark mode via `@media (prefers-color-scheme: dark)`
- **Testing**: pytest (unit/integration), Playwright+axe-core (WCAG 2.1 AA accessibility)
- **Layout**: Flickr's justified-layout library (vendored, MIT)

## API Documentation

**All public functions and classes have complete docstrings** in the source code. This is the single source of truth for API documentation.

**To explore the API:**

```python
# In Python interpreter or IPython
from src.generator import build_html
help(build_html.main)

from src.generator.model import Image
help(Image)

# Or use your IDE's "Go to Definition" and documentation features
```

**Documentation standards:**
- All public functions have docstrings with Args/Returns/Raises
- All functions have complete type annotations (enforced by `ty`)
- Docstrings follow Google style (consistent with Pydantic)

**Why no separate API reference?** Maintaining separate API docs leads to drift. The code is the documentation.

## Project Structure

```
src/generator/          # Core Python build logic
├── build_html.py      # Entry point: main(), orchestration
├── model.py           # Pydantic models: GalleryConfig, Image, Category
├── scan.py            # Image discovery & validation
├── thumbnails.py      # WebP/JPEG thumbnail generation + blur placeholders
├── yaml_sync.py       # YAML parsing & stub generation
├── assets.py          # Asset copying with content hashing
├── cache.py           # Build cache management
├── i18n.py            # Babel internationalization (en/de)
├── metadata_filter.py # EXIF stripping for privacy
├── constants.py       # Defaults & configuration
└── utils.py           # Shared utilities

src/templates/         # Jinja2 HTML templates
├── index.html.j2      # Main gallery page
└── fullscreen.html.j2 # Fullscreen modal component

src/static/           # Frontend assets (bundled at build time)
├── css/              # Gallery and fullscreen styles
└── js/               # Vanilla ES modules + vendored justified-layout

config/               # YAML configuration
├── settings.yaml     # Global: paths, locale, banner, title
└── gallery.yaml      # Images: categories, titles, descriptions

content/              # Source images (auto-scanned)
tests/                # pytest: unit, integration, accessibility
docs/                 # Architecture, development, ADRs, workflows
```

## Build Pipeline

### Phase 1: Discovery & Validation
- **scan.py**: Discover images in `content_dir`, validate formats, check duplicates
- **Extract dimensions** from image files using Pillow

### Phase 2: YAML Synchronization
- **yaml_sync.py**: Load `gallery.yaml`, auto-generate stubs for new images
- Creates mapping: `filename → {category, title, description}`

### Phase 3: Thumbnail Generation
- **thumbnails.py**:
  - Check `.build-cache.json` for existing thumbnails
  - Generate WebP (primary) + JPEG (fallback)
  - Create 16px blur placeholders (base64 data URLs)
  - Strip EXIF metadata using `metadata_filter.py`
  - Save cache for incremental builds

### Phase 4: Asset Processing
- **assets.py**: Copy images to `dist/images/originals/` with:
  - Content-hash based filenames (cache busting)
  - Metadata stripping for privacy
- Copy banner image to `dist/images/banner/` (if configured)

### Phase 5: HTML Generation
- **build_html.py**:
  - Combine CSS files (`gallery.css` + `fullscreen.css`)
  - Combine JS files (justified-layout vendor + gallery modules)
  - Hash and write bundled assets
  - Render Jinja2 templates with i18n support
  - Output `dist/index.html`

## Data Flow

```
Image Files
    ↓
[scan.py] → valid_paths: list[Path]
    ↓
[yaml_sync.py] → categories: list[str], entry_map: dict[str, YamlEntry]
    ↓
[build_html.py] → images: list[Image]
    ↓
[thumbnails.py] → images with .thumbnail attached
    ↓
[build_html.py] → categories: list[Category]
    ↓
[Jinja2 + assets.py] → dist/index.html + bundled assets
```

## Key Components

### Core Modules

| Module | Responsibility | Key Functions |
|--------|---------------|---------------|
| `build_html.py` | Orchestration & entry point | `main()`, `generate_gallery_html()` |
| `model.py` | Pydantic data models | `Image`, `Category`, `GalleryConfig` |
| `scan.py` | Image discovery | `discover_images()`, `filter_valid_images()` |
| `yaml_sync.py` | YAML parsing & sync | `load_gallery_yaml()`, `append_stub_entries()` |
| `thumbnails.py` | Image processing | `ThumbnailGenerator.generate_batch()` |
| `assets.py` | Asset copying with hashing | `copy_with_hash()`, `write_with_hash()` |
| `i18n.py` | Internationalization | `setup_i18n()`, `_()` gettext wrapper |
| `metadata_filter.py` | EXIF stripping | `filter_metadata()` |
| `cache.py` | Build cache management | Cache serialization helpers |

### Data Models (Pydantic)

```python
class GalleryConfig(BaseSettings):
    """Loaded from settings.yaml + env vars (EXPOSURE_* prefix)"""
    content_dir: Path
    gallery_yaml_path: Path
    output_dir: Path
    locale: str  # en or de
    banner_image: Optional[Path]
    gallery_title: Optional[str]
    gallery_subtitle: Optional[str]
    thumbnail_config: ThumbnailConfig
    blur_placeholder_config: BlurPlaceholderConfig

class Image(BaseModel):
    """Single image with metadata"""
    filename: str
    file_path: Path
    category: str
    width: Optional[int]
    height: Optional[int]
    title: str
    description: str
    thumbnail: Optional[ThumbnailImage]

class Category(BaseModel):
    """Group of images"""
    name: str
    order_index: int
    images: list[Image]

class ThumbnailImage(BaseModel):
    """Generated thumbnail data"""
    source_path: Path
    webp_path: Path
    jpeg_path: Path
    width: int
    height: int
    blur_placeholder: Optional[BlurPlaceholder]
```

### Frontend Architecture

**Zero dependencies**: Pure vanilla ES modules

| Module | Responsibility | Key Functions/Features |
|--------|---------------|----------------------|
| `gallery.js` | Entry point & initialization | DOMContentLoaded event, gallery setup coordination |
| `layout.js` | Responsive image layout | `calculateFlexibleLayout()` using justified-layout, aspect ratio preservation |
| `fullscreen.js` | Fullscreen viewer controller | Keyboard nav (←/→/Esc), image preloading, caption display |
| `fullscreen-manager.js` | Image loading & display | Lazy loading, progressive enhancement, error handling |
| `control-visibility-manager.js` | UI control fade behavior | Auto-hide controls on idle, touch/mouse interaction detection |
| `a11y.js` | Accessibility helpers | ARIA live region announcements, screen reader support |
| `vendor/justified-layout.js` | Layout algorithm (Flickr) | Geometry calculation for justified rows (vendored, MIT license) |

**CSS Modules:**

| File | Responsibility | Key Features |
|------|---------------|--------------|
| `gallery.css` | Main gallery styles | Grid layout, responsive design, dark mode via `@media (prefers-color-scheme: dark)` |
| `fullscreen.css` | Fullscreen viewer styles | Modal overlay, image centering, control positioning |

**Architecture Notes:**
- **No build step**: Files bundled at Python build time, no webpack/rollup needed
- **ES modules**: Native browser imports, no transpilation
- **Progressive enhancement**: Core functionality works without JS
- **Dark mode**: Pure CSS via media query, no JavaScript toggle
- **Event-driven**: Module communication via custom events and shared DOM state

## Configuration System

### Settings Priority (highest to lowest)
1. Environment variables (`EXPOSURE_*` prefix)
2. `.env` file (if present)
3. `settings.yaml`

### Example Override
```bash
EXPOSURE_LOCALE=de EXPOSURE_LOG_LEVEL=DEBUG uv run exposure
```

## Build Cache

`.build-cache.json` structure:
```json
{
  "content/image.jpg": {
    "source_hash": "sha256...",
    "thumbnail_hash": "sha256...",
    "webp_path": "dist/images/thumbnails/image-hash.webp",
    "jpeg_path": "dist/images/thumbnails/image-hash.jpg",
    "width": 800,
    "height": 600
  }
}
```

Cache invalidation: Changes to source image hash or thumbnail config.

## Output Structure

```
dist/
├── index.html                    # Main gallery page
├── gallery-<hash>.css            # Bundled styles
├── gallery-<hash>.js             # Bundled JavaScript
└── images/
    ├── originals/                # Full-size (metadata stripped)
    │   └── image-<hash>.jpg
    ├── thumbnails/               # WebP + JPEG fallback
    │   ├── image-<hash>.webp
    │   └── image-<hash>.jpg
    └── banner/                   # Banner image (optional)
        └── banner.jpg
```

## Performance Constraints

Enforced by `tests/integration/test_asset_budgets.py`:

- HTML: < 100KB
- CSS: < 30KB
- JS: < 50KB
- Zero layout shift (dimensions specified for all images)
- Lazy loading for below-fold content

## Type Checking

- **Tool**: `ty` (Astral's Rust-based type checker)
- **Command**: `uv run ty check src/`
- **Strictness**: All source code fully type-annotated
- See ADR 0002 for rationale

## Testing Architecture

```
tests/
├── unit/              # Fast, isolated tests
│   ├── test_model.py
│   ├── test_thumbnails.py
│   ├── test_yaml_sync.py
│   └── ...
├── integration/       # End-to-end with real files
│   ├── test_end_to_end.py
│   ├── test_asset_budgets.py      # Performance enforcement
│   └── test_reproducibility.py    # Deterministic builds
└── accessibility/     # Playwright + axe-core
    └── test_a11y.py   # WCAG 2.1 AA compliance
```

Run: `uv run pytest` (skip a11y: `uv run pytest -m "not a11y"`)

## Commands

```bash
# Build gallery
uv run exposure

# Testing
uv run pytest                                # All tests
uv run pytest -m "not a11y"                  # Skip accessibility tests
uv run pytest --cov=src --cov-report=html   # With coverage

# Code quality
uv run ty check src/                         # Type check
uv run ruff check .                          # Lint
uv run ruff format .                         # Format

# i18n workflow
uv run pybabel extract -F babel.cfg -o locales/messages.pot .
uv run pybabel update -i locales/messages.pot -d locales
uv run pybabel compile -d locales

# Configuration override
EXPOSURE_LOCALE=de EXPOSURE_LOG_LEVEL=DEBUG uv run exposure
```

## Internationalization

- **Library**: Babel
- **Supported**: English (en), German (de)
- **Workflow**: See `i18n-workflow.md`
- **Files**: `locales/{locale}/LC_MESSAGES/messages.po`

## Common Patterns

### Path Handling
- Use `pathlib.Path`, not strings
- Relative imports within `generator/` package
- Always use absolute paths for file operations

### Image Dimensions
- Width/height are `Optional[int]` - gracefully handle None
- Extract dimensions during scan phase with Pillow
- Specify dimensions in HTML to prevent layout shift

### Cache Management
- `.build-cache.json` always stored in `output_dir`
- Cache key: source file hash + thumbnail config hash
- Invalidate on: source change, config change, or manual deletion

### Environment Variables
- Must use `EXPOSURE_` prefix
- Override any `settings.yaml` value
- Example: `EXPOSURE_LOCALE=de`, `EXPOSURE_OUTPUT_DIR=/tmp/gallery`

### YAML Order
- Category order in `gallery.yaml` determines display order
- Images within categories: YAML file order = display order
- Use YAML list order intentionally for gallery organization

## Security Features

- **No third-party scripts**: Zero external dependencies in frontend
- **CSP ready**: No inline scripts or styles
- **Metadata stripping**: EXIF data removed from all output images
- **Content hashing**: Cache busting prevents stale assets

- **No third-party scripts**: Zero external dependencies in frontend
- **CSP ready**: No inline scripts or styles
- **Metadata stripping**: EXIF data removed from all output images
- **Content hashing**: Cache busting prevents stale assets

## Extension Points

### Add New Image Format
1. Update `SUPPORTED_EXTENSIONS` in `constants.py`
2. Ensure Pillow supports format
3. Add tests

### Add New Locale
1. Extract messages: `pybabel extract -F babel.cfg -o locales/messages.pot .`
2. Initialize locale: `pybabel init -i locales/messages.pot -d locales -l <code>`
3. Translate `locales/<code>/LC_MESSAGES/messages.po`
4. Compile: `pybabel compile -d locales`

### Customize Layout Algorithm
Modify `src/static/js/layout.js` - uses Flickr's justified-layout library.

### Add New Template Variables
1. Update template context in `build_html.py:generate_gallery_html()`
2. Use in `src/templates/*.j2` files

## Common Gotchas

- **Import paths**: Use `from . import module` (relative imports within generator/)
- **Path types**: Always use `pathlib.Path`, not strings
- **Image dimensions**: Optional - gracefully handle None
- **YAML order matters**: Categories display in YAML order
- **Cache location**: Always in output_dir (`.build-cache.json`)
- **Environment variables**: Must use `EXPOSURE_` prefix

## Debugging

```bash
# Enable debug logging
EXPOSURE_LOG_LEVEL=DEBUG uv run exposure

# Clear build cache
rm dist/.build-cache.json

# Type check
uv run ty check src/

# Run specific test
uv run pytest tests/unit/test_thumbnails.py -v

# Coverage report
uv run pytest --cov=src --cov-report=html
```
