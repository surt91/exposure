# API Contract: Configuration Interface

**Version**: 1.0.0
**Module**: `src.generator.model`
**Status**: Draft

## Overview

This contract defines the configuration interface extensions for thumbnail preprocessing. It extends the existing `GalleryConfig` model to include thumbnail-specific settings.

---

## Configuration Schema

### ThumbnailConfig

Configuration model for thumbnail generation parameters.

```python
class ThumbnailConfig(BaseModel):
    """
    Configuration for thumbnail generation.

    All fields have sensible defaults based on research findings.
    Configuration loaded from YAML or environment variables.
    """

    max_dimension: int = Field(
        default=800,
        ge=100,
        le=4000,
        description="Maximum width or height for thumbnails in pixels"
    )

    webp_quality: int = Field(
        default=85,
        ge=1,
        le=100,
        description="WebP compression quality (1-100, higher = better quality)"
    )

    jpeg_quality: int = Field(
        default=90,
        ge=1,
        le=100,
        description="JPEG fallback compression quality (1-100, higher = better quality)"
    )

    output_dir: Path = Field(
        default=Path("build/images/thumbnails"),
        description="Directory for generated thumbnail files"
    )

    enable_cache: bool = Field(
        default=True,
        description="Enable incremental build caching to skip unchanged images"
    )

    cache_file: Path = Field(
        default=Path("build/.build-cache.json"),
        description="Path to build cache JSON file"
    )

    resampling_filter: str = Field(
        default="LANCZOS",
        pattern="^(LANCZOS|BICUBIC|BILINEAR|NEAREST)$",
        description="PIL resampling filter for thumbnail generation"
    )
```

**Validation**:
- `max_dimension`: Must be reasonable size (100-4000px)
- Quality values: Standard range for image compression (1-100)
- Paths: Converted to Path objects, validated at build time
- `resampling_filter`: Must be valid PIL filter name

**Configuration Sources** (priority order):
1. Environment variables: `EXPOSURE_THUMBNAIL_MAX_DIMENSION`, `EXPOSURE_THUMBNAIL_WEBP_QUALITY`, etc.
2. YAML file: `config/settings.yaml`
3. Default values

---

### GalleryConfig Extension

Existing configuration model extended with thumbnail settings.

```python
class GalleryConfig(BaseSettings):
    """Gallery configuration with thumbnail support."""

    # ... existing fields ...

    enable_thumbnails: bool = Field(
        default=False,
        description="Enable thumbnail generation during build"
    )

    thumbnail_config: ThumbnailConfig = Field(
        default_factory=ThumbnailConfig,
        description="Thumbnail generation configuration"
    )
```

**Backward Compatibility**:
- `enable_thumbnails=False` (default): Maintains existing behavior, no thumbnails generated
- Existing builds continue to work without any configuration changes
- New field `thumbnail_config` instantiated with defaults if not provided

---

## YAML Configuration Format

### config/settings.yaml

```yaml
# Gallery configuration
content_dir: content/
gallery_yaml_path: config/gallery.yaml
default_category: Uncategorized
output_dir: build/
locale: en
log_level: INFO

# Thumbnail configuration (NEW)
enable_thumbnails: true

thumbnail_config:
  max_dimension: 800
  webp_quality: 85
  jpeg_quality: 90
  output_dir: build/images/thumbnails
  enable_cache: true
  cache_file: build/.build-cache.json
  resampling_filter: LANCZOS
```

**Minimal Configuration** (uses defaults):
```yaml
# Enable thumbnails with default settings
enable_thumbnails: true
```

**Custom Configuration**:
```yaml
# Enable with custom quality settings
enable_thumbnails: true
thumbnail_config:
  max_dimension: 1200  # Larger thumbnails
  webp_quality: 80     # More compression
  jpeg_quality: 85     # Match WebP quality
```

---

## Environment Variable Configuration

### Variable Names

All thumbnail configuration accessible via environment variables:

```bash
# Enable thumbnails
export EXPOSURE_ENABLE_THUMBNAILS=true

# Override thumbnail settings
export EXPOSURE_THUMBNAIL_CONFIG__MAX_DIMENSION=1200
export EXPOSURE_THUMBNAIL_CONFIG__WEBP_QUALITY=80
export EXPOSURE_THUMBNAIL_CONFIG__JPEG_QUALITY=85
export EXPOSURE_THUMBNAIL_CONFIG__OUTPUT_DIR=dist/thumbnails
export EXPOSURE_THUMBNAIL_CONFIG__ENABLE_CACHE=false
```

**Naming Convention**:
- Prefix: `EXPOSURE_`
- Nested config: Double underscore `__` separator
- Example: `EXPOSURE_THUMBNAIL_CONFIG__MAX_DIMENSION`

**Type Conversion**:
- Booleans: `true`, `false`, `1`, `0`, `yes`, `no` (case-insensitive)
- Integers: String to int conversion
- Paths: String to Path object conversion

---

## Configuration Loading Flow

```python
def load_config() -> GalleryConfig:
    """
    Load configuration with thumbnail settings.

    Priority order:
    1. Environment variables (highest)
    2. .env file
    3. YAML settings file
    4. Default values (lowest)
    """

    # Pydantic-settings handles priority automatically
    config = GalleryConfig()

    # Validate paths exist
    config.validate_paths()

    return config
```

**Validation Steps**:
1. Pydantic field validation (types, ranges)
2. Path existence checks
3. Output directory writability check
4. Cache file parent directory check

---

## Configuration Validation

### Valid Configuration Examples

```python
# Minimal valid configuration
config = ThumbnailConfig()
assert config.max_dimension == 800
assert config.webp_quality == 85

# Custom configuration
config = ThumbnailConfig(
    max_dimension=1200,
    webp_quality=80,
    output_dir=Path("custom/thumbnails")
)
assert config.max_dimension == 1200
```

### Invalid Configuration Examples

```python
from pydantic import ValidationError

# Quality out of range
try:
    config = ThumbnailConfig(webp_quality=150)
except ValidationError as e:
    assert "webp_quality" in str(e)
    assert "less than or equal to 100" in str(e)

# Dimension too small
try:
    config = ThumbnailConfig(max_dimension=50)
except ValidationError as e:
    assert "max_dimension" in str(e)
    assert "greater than or equal to 100" in str(e)

# Invalid resampling filter
try:
    config = ThumbnailConfig(resampling_filter="INVALID")
except ValidationError as e:
    assert "resampling_filter" in str(e)
```

---

## Configuration Migration

### Phase 1: Add Configuration (Non-Breaking)

```python
# Existing configs continue to work
config = GalleryConfig(
    content_dir="content/",
    gallery_yaml_path="config/gallery.yaml",
    default_category="Uncategorized"
)

# enable_thumbnails defaults to False
assert config.enable_thumbnails is False
```

### Phase 2: Enable Thumbnails

```yaml
# Add to settings.yaml
enable_thumbnails: true
# Uses default thumbnail_config
```

### Phase 3: Customize Settings

```yaml
# Override defaults
enable_thumbnails: true
thumbnail_config:
  max_dimension: 1200
  webp_quality: 80
```

---

## Integration with CLI

### Command-Line Arguments

```python
# In src/generator/build_html.py

def main():
    """Build gallery with thumbnail support."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-thumbnails",
        action="store_true",
        help="Disable thumbnail generation (override config)"
    )
    parser.add_argument(
        "--thumbnail-size",
        type=int,
        metavar="PIXELS",
        help="Override max thumbnail dimension"
    )

    args = parser.parse_args()

    # Load config
    config = GalleryConfig()

    # Apply CLI overrides
    if args.no_thumbnails:
        config.enable_thumbnails = False

    if args.thumbnail_size:
        config.thumbnail_config.max_dimension = args.thumbnail_size

    # Build gallery
    build_gallery(config)
```

**CLI Examples**:
```bash
# Build with thumbnails (from config)
exposure

# Build without thumbnails (override config)
exposure --no-thumbnails

# Build with custom thumbnail size
exposure --thumbnail-size 1200

# Override via environment
EXPOSURE_THUMBNAIL_CONFIG__MAX_DIMENSION=1200 exposure
```

---

## Configuration Testing

### Test: Default Configuration

```python
def test_thumbnail_config_defaults():
    """Verify default configuration values."""
    config = ThumbnailConfig()

    assert config.max_dimension == 800
    assert config.webp_quality == 85
    assert config.jpeg_quality == 90
    assert config.output_dir == Path("build/images/thumbnails")
    assert config.enable_cache is True
    assert config.resampling_filter == "LANCZOS"
```

### Test: YAML Loading

```python
def test_load_from_yaml(tmp_path):
    """Verify YAML configuration loading."""
    yaml_file = tmp_path / "settings.yaml"
    yaml_file.write_text("""
enable_thumbnails: true
thumbnail_config:
  max_dimension: 1200
  webp_quality: 80
""")

    # Load config
    config = GalleryConfig(_yaml_settings_file=yaml_file)

    assert config.enable_thumbnails is True
    assert config.thumbnail_config.max_dimension == 1200
    assert config.thumbnail_config.webp_quality == 80
```

### Test: Environment Variables

```python
def test_env_override(monkeypatch):
    """Verify environment variable overrides."""
    monkeypatch.setenv("EXPOSURE_ENABLE_THUMBNAILS", "true")
    monkeypatch.setenv("EXPOSURE_THUMBNAIL_CONFIG__MAX_DIMENSION", "1200")

    config = GalleryConfig()

    assert config.enable_thumbnails is True
    assert config.thumbnail_config.max_dimension == 1200
```

### Test: Validation Errors

```python
def test_invalid_quality_range():
    """Verify quality validation."""
    with pytest.raises(ValidationError) as exc:
        ThumbnailConfig(webp_quality=150)

    assert "webp_quality" in str(exc.value)

def test_invalid_dimension_range():
    """Verify dimension validation."""
    with pytest.raises(ValidationError) as exc:
        ThumbnailConfig(max_dimension=50)

    assert "max_dimension" in str(exc.value)
```

---

## Configuration Documentation

### README Update

```markdown
## Configuration

### Thumbnail Generation

Enable optimized thumbnail generation for faster gallery loading:

```yaml
# config/settings.yaml
enable_thumbnails: true
```

Customize thumbnail settings:

```yaml
thumbnail_config:
  max_dimension: 800      # Max width/height in pixels (default: 800)
  webp_quality: 85        # WebP quality 1-100 (default: 85)
  jpeg_quality: 90        # JPEG fallback quality 1-100 (default: 90)
  output_dir: build/images/thumbnails
  enable_cache: true      # Skip unchanged images (default: true)
```

### Environment Variables

Override configuration via environment variables:

```bash
export EXPOSURE_ENABLE_THUMBNAILS=true
export EXPOSURE_THUMBNAIL_CONFIG__MAX_DIMENSION=1200
```
```

---

## Appendix: Full Configuration Example

### Complete settings.yaml

```yaml
# Gallery Configuration
content_dir: content/
gallery_yaml_path: config/gallery.yaml
default_category: Uncategorized
output_dir: build/
locale: en
log_level: INFO

# Thumbnail Configuration
enable_thumbnails: true

thumbnail_config:
  # Maximum dimension (width or height) for thumbnails
  # Recommended: 800 for standard galleries, 1200 for high-quality displays
  max_dimension: 800

  # WebP compression quality (1-100)
  # Recommended: 85 for balanced quality/size
  webp_quality: 85

  # JPEG fallback compression quality (1-100)
  # Recommended: 90 to match WebP visual quality
  jpeg_quality: 90

  # Output directory for generated thumbnails
  output_dir: build/images/thumbnails

  # Enable incremental builds (skip unchanged images)
  enable_cache: true

  # Build cache file location
  cache_file: build/.build-cache.json

  # Resampling filter for thumbnail generation
  # Options: LANCZOS (best quality), BICUBIC, BILINEAR, NEAREST
  resampling_filter: LANCZOS
```

### Complete .env Example

```bash
# Gallery settings
EXPOSURE_CONTENT_DIR=content/
EXPOSURE_GALLERY_YAML_PATH=config/gallery.yaml
EXPOSURE_DEFAULT_CATEGORY=Uncategorized
EXPOSURE_OUTPUT_DIR=build/
EXPOSURE_LOCALE=en
EXPOSURE_LOG_LEVEL=INFO

# Thumbnail settings
EXPOSURE_ENABLE_THUMBNAILS=true
EXPOSURE_THUMBNAIL_CONFIG__MAX_DIMENSION=800
EXPOSURE_THUMBNAIL_CONFIG__WEBP_QUALITY=85
EXPOSURE_THUMBNAIL_CONFIG__JPEG_QUALITY=90
EXPOSURE_THUMBNAIL_CONFIG__OUTPUT_DIR=build/images/thumbnails
EXPOSURE_THUMBNAIL_CONFIG__ENABLE_CACHE=true
EXPOSURE_THUMBNAIL_CONFIG__CACHE_FILE=build/.build-cache.json
EXPOSURE_THUMBNAIL_CONFIG__RESAMPLING_FILTER=LANCZOS
```
