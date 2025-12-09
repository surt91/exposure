# Exposure - LLM Assistant Guidelines

Static image gallery generator. Build-time Python pipeline → production-ready HTML/CSS/JS.

## Tech Stack

- **Python 3.11+**: Pydantic v2, Jinja2, Pillow, PyYAML, Babel, piexif, pydantic-settings
- **Type checking**: `ty` (Astral) - all code fully annotated
- **Testing**: pytest, Playwright+axe-core (WCAG 2.1 AA)
- **Frontend**: Vanilla ES modules, CSS-only dark mode
- **Layout**: Flickr's justified-layout (vendored)
- **Architecture**: Build-time processing, no runtime server, static output

## Project Structure

```
src/generator/          # Core build logic
├── build_html.py      # Entry point: main(), orchestration
├── model.py           # Pydantic models: GalleryConfig, Image, Category
├── scan.py            # Image discovery & validation
├── thumbnails.py      # WebP/JPEG thumbnails + blur placeholders
├── yaml_sync.py       # YAML parsing & stub generation
├── assets.py          # Asset copying with content hashing
├── i18n.py            # Babel i18n (en/de)
├── metadata_filter.py # EXIF stripping
└── constants.py       # Configuration defaults

src/templates/         # Jinja2 HTML templates
src/static/            # Frontend JavaScript + CSS
├── js/
│   ├── gallery.js               # Main gallery initialization, lazy loading
│   ├── fullscreen.js            # Fullscreen modal controller
│   ├── fullscreen-manager.js   # Fullscreen API wrapper (class)
│   ├── control-visibility-manager.js  # Auto-hide controls (class)
│   ├── a11y.js                  # Accessibility helpers (focus trap, announcements)
│   ├── layout.js                # Justified layout calculator
│   └── vendor/justified-layout.js  # Vendored Flickr layout library
└── css/
    ├── gallery.css              # Main gallery styles
    └── fullscreen.css           # Fullscreen modal styles

config/               # settings.yaml (global), gallery.yaml (images)
content/              # Source images
tests/                # Unit, integration, accessibility
docs/                 # architecture.md, development.md, ADRs
```

## Build Pipeline

1. Load config (`settings.yaml` + `EXPOSURE_*` env vars)
2. Scan images (discover, validate, dimensions)
3. Sync YAML (load metadata, generate stubs)
4. Generate thumbnails (WebP+JPEG, blur placeholders, strip EXIF)
5. Organize by categories
6. Copy assets (with content hash, strip metadata)
7. Render HTML (Jinja2 + i18n, bundle CSS/JS with hash)
8. Output `dist/index.html` + bundled assets

## Key Data Models

```python
GalleryConfig(BaseSettings):  # settings.yaml + env vars
    content_dir: Path
    gallery_yaml_path: Path
    output_dir: Path
    locale: str  # en or de
    banner_image: Optional[Path]
    gallery_title: Optional[str]
    thumbnail_config: ThumbnailConfig
    blur_placeholder_config: BlurPlaceholderConfig

Image(BaseModel):
    filename: str
    file_path: Path
    category: str
    width: Optional[int]  # Always handle None
    height: Optional[int]
    title: str
    description: str
    thumbnail: Optional[ThumbnailImage]

Category(BaseModel):
    name: str
    order_index: int
    images: list[Image]
```

## Commands

```bash
uv run exposure                              # Build gallery
uv run pytest                                # All tests
uv run pytest -m "not a11y"                  # Skip accessibility tests
uv run pytest --cov=src --cov-report=html   # Coverage
uv run ty check src/                         # Type check
uv run ruff check .                          # Lint
uv run ruff format .                         # Format

# i18n workflow
uv run pybabel extract -F babel.cfg -o locales/messages.pot .
uv run pybabel update -i locales/messages.pot -d locales
uv run pybabel compile -d locales

# Config override
EXPOSURE_LOCALE=de EXPOSURE_LOG_LEVEL=DEBUG uv run exposure
```

## Code Style

- Python 3.11+ features OK
- Full type hints required (`ty` enforced)
- Docstrings for public functions (Args/Returns/Raises)
- Line length: 100 chars (Ruff)
- Use `pathlib.Path`, not strings
- Relative imports within `generator/`

## Code Consistency Rules (Python)

**Imports:**
- Module-level imports only (no local imports in functions)
- Exception: `setup_logging` in `main()` to avoid circular dependencies
- Import order: stdlib → third-party → local modules

**Utilities:**
- Use `utils.py` for common operations: `hash_file()`, `hash_bytes()`, `hash_content()`
- Never duplicate hash/validation functions in other modules
- Single source of truth for reusable utilities

**Logging:**
- Always use module-level: `logger = logging.getLogger("exposure")`
- Never inject logger as constructor parameter
- No ad-hoc `logging.getLogger(__name__)` calls

## Code Consistency Rules (JavaScript)

**Module Pattern:**
- Use IIFE for non-class modules: `(function() { 'use strict'; ... })();`
- Use ES6 classes for stateful components: `class ComponentName { ... }`
- Always include `'use strict';` at top of IIFE

**Accessibility:**
- Use `window.a11y.FOCUSABLE_ELEMENTS_SELECTOR` for all focusable element queries
- Never create custom focusable selectors - ensures consistent `:not([disabled])` handling
- Include proper ARIA attributes for all interactive elements

**Global Exports:**
- Export public API via `window.moduleName = { ... };`
- Keep module internals private within IIFE
- Document exports with JSDoc comments

## Output Structure

```
dist/
├── index.html
├── gallery-<hash>.css
├── gallery-<hash>.js
└── images/
    ├── originals/      # Metadata stripped, content-hashed
    ├── thumbnails/     # WebP + JPEG fallback
    └── banner/         # Optional
```

## Performance Constraints (test-enforced)

- HTML < 100KB
- CSS < 30KB
- JS < 50KB
- Zero layout shift (dimensions specified)
- Incremental builds via `.build-cache.json` (in `output_dir`)

## Common Patterns

- **Paths**: Use `Path`, not strings
- **Dimensions**: Handle `Optional[int]` gracefully
- **Config override**: `EXPOSURE_*` env vars
- **Cache**: `.build-cache.json` in `output_dir`
- **YAML order**: Determines category display order
- **Run commands**: Via `uv run`, not bare `python`

## Extension Points

- **New image format**: Update `SUPPORTED_EXTENSIONS` in `constants.py`
- **New locale**: Use pybabel workflow (extract → init → translate → compile)
- **New config**: Add to `GalleryConfig` in `model.py` + `settings.yaml`
- **Template changes**: Edit `src/templates/*.j2`, update context in `build_html.py`

## Testing

- **Unit** (`tests/unit/`): Fast, isolated
- **Integration** (`tests/integration/`): Full pipeline, asset budgets, reproducibility
- **Accessibility** (`tests/accessibility/`): Playwright+axe (requires `playwright install --with-deps chromium`)

## Debugging

```bash
EXPOSURE_LOG_LEVEL=DEBUG uv run exposure  # Debug logging
rm dist/.build-cache.json                 # Clear cache
uv run ty check src/                      # Type check
```

## Documentation

- **docs/architecture.md**: Complete system design, data flow, components, commands
- **docs/development.md**: Dev workflow, debugging, contributing guidelines
- **docs/hosting.md**: Deployment & security configuration
- **docs/i18n-workflow.md**: Translation workflow
- **docs/decisions/**: Architecture Decision Records (ADRs)

## Security

- No third-party scripts (CSP-ready)
- EXIF metadata stripped from all outputs
- Content hashing for cache busting

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
