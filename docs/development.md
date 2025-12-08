# Development Guide

## Setup

```bash
# Clone and install
git clone <repo-url>
cd exposure
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Install Playwright browsers (for accessibility tests)
uv run playwright install --with-deps chromium
```

## Common Commands

```bash
# Build gallery
uv run exposure

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Skip accessibility tests
uv run pytest -m "not a11y"

# Type check
uv run ty check src/

# Lint
uv run ruff check .

# Format
uv run ruff format .

# i18n workflow
uv run pybabel extract -F babel.cfg -o locales/messages.pot .
uv run pybabel update -i locales/messages.pot -d locales
# Edit locales/*/LC_MESSAGES/messages.po
uv run pybabel compile -d locales
```

## Code Style

- **Python 3.11+** features allowed
- **Type hints**: All functions must have type annotations
- **Docstrings**: Public functions need docstrings with Args/Returns/Raises
- **Line length**: 100 characters (Ruff enforced)
- **Imports**: Auto-sorted by Ruff

### Example Function
```python
def generate_thumbnail(
    source_path: Path,
    output_dir: Path,
    max_dimension: int = 800
) -> ThumbnailImage:
    """
    Generate optimized thumbnail from source image.

    Args:
        source_path: Path to source image file
        output_dir: Directory to write thumbnail files
        max_dimension: Maximum width/height in pixels

    Returns:
        ThumbnailImage object with paths and dimensions

    Raises:
        ValueError: If source image is invalid or unreadable
    """
    # Implementation...
```

## Development Workflow

1. Create a feature branch
2. Write tests first (TDD encouraged)
3. Implement the change
4. Run tests: `uv run pytest`
5. Type check: `uv run ty check src/`
6. Format: `uv run ruff format .`
7. Commit (pre-commit hooks auto-run)

## Configuration Override

Override settings via environment variables:

```bash
# Change locale to German
EXPOSURE_LOCALE=de uv run exposure

# Enable debug logging
EXPOSURE_LOG_LEVEL=DEBUG uv run exposure

# Custom output directory
EXPOSURE_OUTPUT_DIR=/tmp/my-gallery uv run exposure
```

## Testing Strategy

### Unit Tests (`tests/unit/`)
- Test individual functions/classes
- Fast, minimal I/O
- Use fixtures for test data

```bash
# Run single test file
uv run pytest tests/unit/test_thumbnails.py -v

# Run single test
uv run pytest tests/unit/test_thumbnails.py::test_calculate_dimensions -v
```

### Integration Tests (`tests/integration/`)
- Full build pipeline with real images
- Asset budget enforcement
- Reproducibility checks

```bash
# Run integration tests only
uv run pytest tests/integration/ -v
```

### Accessibility Tests (`tests/accessibility/`)
- Playwright + axe-core
- WCAG 2.1 AA compliance
- Requires Playwright browsers

```bash
# Install browsers first
uv run playwright install --with-deps chromium

# Run a11y tests
uv run pytest tests/accessibility/ -v

# Skip a11y tests
uv run pytest -m "not a11y"
```

## Debugging Tips

### Enable Debug Logging
```bash
EXPOSURE_LOG_LEVEL=DEBUG uv run exposure
```

### Inspect Build Cache
```bash
cat dist/.build-cache.json | python -m json.tool
```

### Test Thumbnail Generation
```python
from pathlib import Path
from src.generator.thumbnails import ThumbnailGenerator
from src.generator.model import ThumbnailConfig, BlurPlaceholderConfig

config = ThumbnailConfig()
blur_config = BlurPlaceholderConfig()
gen = ThumbnailGenerator(config, blur_config)

thumbnail = gen.generate_thumbnail(Path("content/test.jpg"))
print(f"WebP: {thumbnail.webp_path}")
print(f"JPEG: {thumbnail.jpeg_path}")
```

### Validate YAML
```python
from pathlib import Path
from src.generator.yaml_sync import load_gallery_yaml

categories, entries = load_gallery_yaml(Path("config/gallery.yaml"))
print(f"Categories: {categories}")
print(f"Entries: {len(entries)}")
```

### Check Type Coverage
```bash
uv run ty check src/ --show-error-codes
```

## Common Issues

### Issue: "Playwright browsers not installed"
**Solution:** `uv run playwright install --with-deps chromium`

### Issue: Type checking fails
**Solution:** `uv sync --dev`

### Issue: Thumbnails not regenerating
**Solution:** Delete `.build-cache.json`: `rm dist/.build-cache.json`

### Issue: YAML stubs not generated
**Solution:** Check images are in `content_dir` with valid extensions (.jpg, .png, .gif, .webp)

### Issue: Import errors
**Solution:** Run via `uv run` (not bare `python`)

## Adding Features

### Add New Image Format
1. Update `SUPPORTED_EXTENSIONS` in `src/generator/constants.py`
2. Ensure Pillow supports the format
3. Add test image to `tests/fixtures/`
4. Add tests in `tests/unit/test_scan.py`

### Add New Configuration Option
1. Add field to `GalleryConfig` in `src/generator/model.py`
2. Add to `config/settings.yaml` (with comment)
3. Document in README.md
4. Add test in `tests/unit/test_model.py`

### Add New Template Variable
1. Update context in `build_html.py:generate_gallery_html()`
2. Use in `src/templates/*.j2`
3. Add integration test

### Modify CSS/JS
1. Edit files in `src/static/css/` or `src/static/js/`
2. Files are bundled at build time (no build step needed)
3. Test in browser: `uv run exposure && open dist/index.html`
4. Run asset budget tests: `uv run pytest tests/integration/test_asset_budgets.py`

## Performance Guidelines

### Asset Budgets (enforced by tests)
- HTML: < 100KB
- CSS: < 30KB
- JS: < 50KB

### Image Optimization
- Thumbnails: Max 800px dimension
- WebP quality: 85
- JPEG quality: 85
- Blur placeholders: 16px max dimension

### Best Practices
- Lazy load below-fold images
- Specify width/height to prevent layout shift
- Use content hashing for cache busting
- Minimize inline styles/scripts

## Documentation

### When to Update Documentation

- **README.md**: User-facing features, commands, quick start
- **architecture.md**: System design, data flow, core components
- **development.md**: This file - dev workflow, debugging
- **ADRs** (`docs/decisions/`): Architectural decisions with context
- **Docstrings**: All public functions/classes

### Writing ADRs

See existing ADRs in `docs/decisions/` for format:
- Context
- Decision
- Consequences
- Alternatives Considered

## Contributing

### PR Checklist
- [ ] Tests added/updated
- [ ] Type checking passes (`uv run ty check src/`)
- [ ] Linting passes (`uv run ruff check .`)
- [ ] All tests pass (`uv run pytest`)
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md updated (if applicable)

### Commit Messages
- Use imperative mood: "Add feature" not "Added feature"
- First line < 72 chars
- Reference issues: "Fix #123"

### Branch Naming
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation only
- `refactor/description` - Code refactoring

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run full test suite: `uv run pytest`
4. Tag release: `git tag v0.x.0`
5. Push: `git push origin main --tags`

## Learning Resources

### Start Here
1. **README.md**: Feature overview
2. **architecture.md**: System design
3. **This file**: Development workflow

### Deep Dives
- **ADR 0001**: Templating (Jinja2 choice)
- **ADR 0002**: Type checking (ty choice)
- **ADR 0003**: Dark mode (CSS-only approach)
- **ADR 0007**: Layout algorithm (justified-layout)
- **ADR 0010**: Banner cropping
- **ADR 0012**: Blur placeholders

### Key Files to Understand
1. `build_html.py:main()` - Entry point
2. `model.py` - Data structures
3. `thumbnails.py:ThumbnailGenerator` - Image processing
4. `templates/index.html.j2` - HTML output

## Getting Help

- **Issues**: Open a GitHub issue for bugs
- **Discussions**: GitHub Discussions for questions
- **Documentation**: Check `docs/` folder first
