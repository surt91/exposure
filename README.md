# Fotoview

Modern static image gallery generator - build responsive, accessible galleries from a simple YAML configuration.

## Features

- 📸 Scrollable image gallery with category organization
- 🌙 **Dark mode** - Automatic theme switching based on system preference
- 🔍 Fullscreen image viewer with keyboard navigation
- 🔄 Automatic YAML stub generation for new images
- ♿ Accessibility-first design (semantic HTML, ARIA, keyboard support, WCAG 2.1 AA)
- ⚡ Performance-optimized (strict asset budgets)
- 🔒 Security-focused (no third-party scripts, CSP ready)
- ✨ Smooth transitions and subtle visual flourishes

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

# Type check
uv run ty check src/

# Lint code
uv run ruff check .

# Format code
uv run ruff format .
```

### Type Checking

Fotoview uses [ty](https://github.com/astral-sh/ty) from Astral for fast, strict type checking:

- All source code is fully type-annotated
- Type checking enforced in CI pipeline
- Rust-based performance (<5 second feedback)
- See [ADR 0002](/docs/decisions/0002-type-checking.md) for tool choice rationale

## Dark Mode

Fotoview automatically adapts to your system's dark mode preference:

- **Light mode** (default): Clean white background, optimal for bright environments
- **Dark mode** (automatic): Near-black background (#0f0f0f) reduces eye strain
- **System integration**: Respects OS-level dark mode setting (macOS, Windows, Linux, iOS, Android)
- **WCAG 2.1 AA compliant**: All text meets 4.5:1 contrast ratio
- **Smooth transitions**: Color changes animate smoothly when toggling system preference
- **Reduced motion support**: Respects `prefers-reduced-motion` accessibility setting
- **Zero JavaScript**: Pure CSS implementation, works without JS enabled

**Browser Support:** Chrome 76+, Firefox 67+, Safari 12.1+, Edge 79+ (2019+)

For implementation details, see [ADR 0003](/docs/decisions/0003-dark-mode-styling-approach.md)

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

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
