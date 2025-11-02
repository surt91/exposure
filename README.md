# Exposure

Modern static image gallery generator - build responsive, accessible galleries from a simple YAML configuration.

## Features

- 📸 Scrollable image gallery with category organization
- 🖼️ **Flexible layout** - Images displayed at original aspect ratios without cropping
- 🖼️ **Smart thumbnails** - Optimized WebP thumbnails with JPEG fallback for 90%+ file size reduction
- 🌙 **Dark mode** - Automatic theme switching based on system preference
- 🔍 Fullscreen image viewer with keyboard navigation
- 🔄 Automatic YAML stub generation for new images
- ♿ Accessibility-first design (semantic HTML, ARIA, keyboard support, WCAG 2.1 AA)
- ⚡ Performance-optimized (strict asset budgets, zero layout shift, incremental builds)
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
uv run exposure

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

Exposure uses [ty](https://github.com/astral-sh/ty) from Astral for fast, strict type checking:

- All source code is fully type-annotated
- Type checking enforced in CI pipeline
- Rust-based performance (<5 second feedback)
- See [ADR 0002](/docs/decisions/0002-type-checking.md) for tool choice rationale

## Dark Mode

Exposure automatically adapts to your system's dark mode preference:

- **Light mode** (default): Clean white background, optimal for bright environments
- **Dark mode** (automatic): Near-black background (#0f0f0f) reduces eye strain
- **System integration**: Respects OS-level dark mode setting (macOS, Windows, Linux, iOS, Android)
- **WCAG 2.1 AA compliant**: All text meets 4.5:1 contrast ratio
- **Smooth transitions**: Color changes animate smoothly when toggling system preference
- **Reduced motion support**: Respects `prefers-reduced-motion` accessibility setting
- **Zero JavaScript**: Pure CSS implementation, works without JS enabled

**Browser Support:** Chrome 76+, Firefox 67+, Safari 12.1+, Edge 79+ (2019+)

For implementation details, see [ADR 0003](/docs/decisions/0003-dark-mode-styling-approach.md)

## Flexible Layout

Exposure uses a justified layout algorithm that displays images at their original aspect ratios without cropping. Images are arranged in rows with consistent heights, creating a visually balanced and space-efficient gallery.

**Features:**
- **No cropping** - See the complete composition of every image
- **Visual balance** - Images appear roughly comparable in size despite different aspect ratios
- **Space efficient** - Minimal whitespace between images while maintaining clean spacing
- **Responsive** - Layout automatically recalculates on window resize
- **Zero layout shift (CLS = 0.0)** - Images reserve space before loading, preventing jarring shifts
- **Fast** - Layout calculation completes in <20ms for 500 images
- **Universal viewport support** - Works from mobile (320px) to 4K (3840px) displays

**Implementation:**
- Image dimensions automatically extracted using Pillow during build
- Justified layout algorithm powered by [flickr/justified-layout](https://github.com/flickr/justified-layout) library
- Client-side calculation ensures responsive behavior across all screen sizes
- Graceful degradation: Falls back to CSS Grid with fixed aspect ratio if JavaScript is disabled

**Browser Support:** Chrome 51+, Firefox 54+, Safari 10+, Edge 15+ (ES6+)

For algorithm choice rationale and implementation details, see [ADR 0007](/docs/decisions/0007-flexible-layout-algorithm.md)

## Configuration

Edit `config/settings.yaml` to customize paths and behavior:

```yaml
content_dir: content           # Source images directory
gallery_yaml_path: config/gallery.yaml  # Metadata file
default_category: Uncategorized         # Default for new images
output_dir: dist                       # Generated site output
locale: en                             # UI language (en=English, de=German)
log_level: INFO                        # Logging verbosity (DEBUG, INFO, WARNING, ERROR)
```

### Thumbnail Generation

Thumbnails are **always generated** during build for optimal gallery performance.

**Benefits:**
- 85%+ reduction in gallery page size (125MB → 15MB for 50 images)
- 3-second load time vs 45 seconds without thumbnails
- Original quality preserved in modal view
- Incremental builds save time (only regenerate changed images)

**Customize thumbnail settings:**

```yaml
thumbnail_config:
  max_dimension: 800      # Max width/height in pixels (default: 800)
  webp_quality: 85        # WebP quality 1-100 (default: 85)
  jpeg_quality: 90        # JPEG fallback quality 1-100 (default: 90)
  output_dir: build/images/thumbnails  # Output directory
  enable_cache: true      # Skip unchanged images (default: true)
```

**How it works:**
1. During build, generates WebP + JPEG thumbnails scaled to 800px max dimension
2. HTML uses `<picture>` element to serve WebP with JPEG fallback
3. Gallery displays thumbnails; modal displays full-resolution originals
4. Cache tracks file modification times to skip unchanged images

### Environment Variable Overrides

All configuration values can be overridden using environment variables with the `EXPOSURE_` prefix. This is useful for CI/CD pipelines, Docker deployments, or testing different configurations without modifying YAML files.

**Precedence (highest to lowest):**
1. Environment variables (`EXPOSURE_*`)
2. `.env` file (if present)
3. `config/settings.yaml`
4. Default values

**Examples:**

```bash
# Override locale for German UI
EXPOSURE_LOCALE=de uv run exposure

# Enable debug logging
EXPOSURE_LOG_LEVEL=DEBUG uv run exposure

# Use custom content directory
EXPOSURE_CONTENT_DIR=/path/to/images uv run exposure

# Multiple overrides
EXPOSURE_LOCALE=de EXPOSURE_OUTPUT_DIR=build uv run exposure
```

**Available Environment Variables:**

- `EXPOSURE_CONTENT_DIR` - Source images directory
- `EXPOSURE_GALLERY_YAML_PATH` - Path to metadata YAML file
- `EXPOSURE_DEFAULT_CATEGORY` - Default category for uncategorized images
- `EXPOSURE_OUTPUT_DIR` - Generated site output directory
- `EXPOSURE_LOCALE` - UI language code (en, de)
- `EXPOSURE_LOG_LEVEL` - Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `EXPOSURE_THUMBNAIL_CONFIG__MAX_DIMENSION` - Thumbnail max dimension in pixels (default: 800)
- `EXPOSURE_THUMBNAIL_CONFIG__WEBP_QUALITY` - WebP quality 1-100 (default: 85)
- `EXPOSURE_THUMBNAIL_CONFIG__JPEG_QUALITY` - JPEG quality 1-100 (default: 90)

**Note:** Environment variable names are case-insensitive on most systems, but uppercase is recommended for clarity.

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

Exposure enforces strict budgets to ensure fast, accessible galleries:

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

Exposure uses a build-time generation approach:

1. **Scan**: Discover images in `content/`
2. **Merge**: Match images with YAML metadata
3. **Stub**: Create entries for new images
4. **Build**: Generate static HTML/CSS/JS
5. **Hash**: Fingerprint assets for cache busting

All output is static - no server or database required.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
