# Fotoview

Modern static image gallery generator - build responsive, accessible galleries from a simple YAML configuration.

## Features

- 📸 Scrollable image gallery with category organization
- 🔍 Fullscreen image viewer with keyboard navigation
- 🔄 Automatic YAML stub generation for new images
- ♿ Accessibility-first design (semantic HTML, ARIA, keyboard support)
- ⚡ Performance-optimized (strict asset budgets)
- 🔒 Security-focused (no third-party scripts, CSP ready)

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd fotoview

# Install dependencies with uv
uv sync

# Add your images
mkdir -p content
cp /path/to/your/images/* content/

# Generate the gallery
uv run python -m src.generator.build_html

# Open dist/index.html in your browser
```

### Development Commands

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Lint code
uv run ruff check .

# Format code
uv run ruff format .
```

## Configuration

Edit `config/settings.yaml` to customize paths and behavior:

```yaml
content_dir: content           # Source images directory
gallery_yaml_path: config/gallery.yaml  # Metadata file
default_category: Uncategorized         # Default for new images
enable_thumbnails: false               # Enable Pillow metadata
output_dir: dist                       # Generated site output
```

## Image Metadata

Images are organized via `config/gallery.yaml`. The generator automatically creates stub entries for new images:

```yaml
categories:
  - Landscapes
  - Portraits

images:
  - filename: sunrise.jpg
    category: Landscapes
    title: "Mountain Sunrise"
    description: "Early morning light over the peaks"
```

## Performance & Accessibility

Fotoview enforces strict budgets to ensure fast, accessible galleries:

### Performance Budgets
- HTML: ≤30KB per page (enforced in CI)
- Critical CSS: ≤25KB (enforced in CI)
- Initial JS: ≤75KB (enforced in CI)
- First image visible: ≤2s
- Fullscreen open latency: ≤300ms
- Smooth scrolling with 500+ images

### Accessibility Standards
- Zero critical accessibility violations (axe-core tested)
- Semantic HTML with ARIA landmarks
- Full keyboard navigation (Tab, Enter, Escape, Arrow keys)
- Screen reader compatible
- Alt text for all images
- Focus management in modal dialogs
- WCAG 2.1 AA compliant

All standards are automatically enforced via CI with Playwright + axe-core integration tests.

## Architecture

Fotoview uses a build-time generation approach:

1. **Scan**: Discover images in `content/`
2. **Merge**: Match images with YAML metadata
3. **Stub**: Create entries for new images
4. **Build**: Generate static HTML/CSS/JS
5. **Hash**: Fingerprint assets for cache busting

All output is static - no server or database required.

## License

[Add your license here]
