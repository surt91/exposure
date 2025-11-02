# API Contract: ThumbnailGenerator Service

**Version**: 1.0.0
**Module**: `src.generator.thumbnails`
**Status**: Draft

## Overview

The `ThumbnailGenerator` service provides the core API for generating optimized WebP and JPEG thumbnails from source images. It handles thumbnail creation, caching, and incremental build detection.

---

## Public API

### Class: ThumbnailGenerator

Primary service class for thumbnail generation operations.

#### Constructor

```python
class ThumbnailGenerator:
    """
    Service for generating optimized image thumbnails.

    Handles WebP and JPEG format generation, EXIF orientation correction,
    and incremental build caching.
    """

    def __init__(
        self,
        config: ThumbnailConfig,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """
        Initialize thumbnail generator with configuration.

        Args:
            config: Thumbnail generation configuration
            logger: Optional logger instance (creates default if None)

        Raises:
            ValueError: If config validation fails
            OSError: If output directory cannot be created
        """
```

**Preconditions**:
- `config.output_dir` parent directory must exist or be creatable
- `config` must pass Pydantic validation

**Postconditions**:
- Output directory exists and is writable
- Build cache loaded from disk if exists
- Logger configured for operation

---

### Method: generate_thumbnail

Generate thumbnail for a single source image.

```python
def generate_thumbnail(
    self,
    source_path: Path,
    metadata: Optional[ImageMetadata] = None
) -> Optional[ThumbnailImage]:
    """
    Generate WebP and JPEG thumbnails for source image.

    Automatically detects if regeneration is needed based on build cache.
    Applies EXIF orientation correction. Preserves aspect ratio.

    Args:
        source_path: Path to source image file
        metadata: Optional pre-extracted metadata (extracted if None)

    Returns:
        ThumbnailImage with paths to generated files, or None if generation
        failed or was skipped (cache hit).

    Raises:
        FileNotFoundError: If source_path does not exist
        ValueError: If source_path is not a supported image format
        OSError: If thumbnail files cannot be written

    Side Effects:
        - Creates WebP and JPEG files in output_dir
        - Updates build cache with generation timestamp and mtime
        - Logs warnings for recoverable errors
    """
```

**Preconditions**:
- `source_path` exists and is readable
- `source_path` is a supported image format (JPEG, PNG, GIF, WEBP)
- Sufficient disk space for output files

**Postconditions**:
- If regeneration needed:
  - Two files created: `{stem}-{hash}.webp` and `{stem}-{hash}.jpg`
  - Both files closed and flushed to disk
  - Build cache updated with new entry
  - Returns `ThumbnailImage` with file details
- If cache hit (no regeneration needed):
  - No files created
  - Returns `None`
  - Cache entry preserved

**Error Handling**:
- `Pillow.UnidentifiedImageError` → Log warning, return `None`
- `OSError` during write → Propagate to caller (fatal)
- Corrupt EXIF data → Log warning, proceed without correction

**Performance**:
- Single image: <500ms for 5MB source on standard laptop
- Cache check: <1ms per image

---

### Method: generate_batch

Generate thumbnails for multiple images with progress tracking.

```python
def generate_batch(
    self,
    source_paths: list[Path],
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> tuple[list[ThumbnailImage], list[Path]]:
    """
    Generate thumbnails for multiple source images.

    Processes images sequentially with optional progress reporting.
    Continues on individual failures.

    Args:
        source_paths: List of source image paths
        progress_callback: Optional callback(current, total) for progress

    Returns:
        Tuple of (successful_thumbnails, failed_paths)

    Side Effects:
        - Calls generate_thumbnail() for each source path
        - Saves build cache after all processing complete
        - Invokes progress_callback after each image if provided
        - Logs summary statistics (X succeeded, Y skipped, Z failed)
    """
```

**Preconditions**:
- All paths in `source_paths` are valid Path objects
- Generator initialized with valid config

**Postconditions**:
- All processable images have thumbnails generated
- Build cache saved to disk
- Summary logged at INFO level

**Error Handling**:
- Individual failures collected in `failed_paths` list
- Batch continues processing remaining images
- Cache saved even if some images failed

---

### Method: load_cache

Load build cache from disk.

```python
def load_cache(self) -> BuildCache:
    """
    Load build cache from configured cache file.

    Returns:
        BuildCache object with entries from disk, or empty cache if file
        does not exist or is invalid.

    Side Effects:
        - Reads cache file from disk
        - Logs warning if cache corrupted (returns empty cache)
        - Creates new cache if none exists
    """
```

**Preconditions**:
- `config.cache_file` parent directory exists

**Postconditions**:
- Returns valid `BuildCache` instance
- Cache version validated (must match current version)

**Error Handling**:
- JSON parse error → Log warning, return empty cache
- Version mismatch → Log warning, return empty cache
- File not found → Return empty cache (no warning)

---

### Method: save_cache

Save build cache to disk.

```python
def save_cache(self) -> None:
    """
    Save current build cache to configured cache file.

    Writes cache as formatted JSON with timestamp.

    Raises:
        OSError: If cache file cannot be written

    Side Effects:
        - Overwrites existing cache file
        - Updates cache.last_updated timestamp
        - Creates cache file if it doesn't exist
    """
```

**Preconditions**:
- `config.cache_file` parent directory exists and is writable

**Postconditions**:
- Cache file written to disk with current timestamp
- JSON formatted with 2-space indentation (human-readable)

---

### Method: extract_metadata

Extract image metadata without generating thumbnail.

```python
def extract_metadata(self, source_path: Path) -> ImageMetadata:
    """
    Extract comprehensive metadata from image file.

    Opens image, reads dimensions, format, color mode, EXIF data, and
    animation info. Does not modify source file.

    Args:
        source_path: Path to image file

    Returns:
        ImageMetadata with all extracted fields

    Raises:
        FileNotFoundError: If source_path does not exist
        Pillow.UnidentifiedImageError: If file is not a valid image

    Side Effects:
        - Opens and reads image file (closes after reading)
        - No disk writes
    """
```

**Preconditions**:
- `source_path` exists and is readable image file

**Postconditions**:
- Returns complete `ImageMetadata` instance
- Source file unchanged
- Image file closed

---

## Helper Functions

### Function: calculate_thumbnail_dimensions

Calculate target thumbnail dimensions preserving aspect ratio.

```python
def calculate_thumbnail_dimensions(
    source_width: int,
    source_height: int,
    max_dimension: int
) -> tuple[int, int]:
    """
    Calculate thumbnail dimensions to fit within max_dimension.

    Maintains aspect ratio. If source is smaller than max_dimension,
    returns original dimensions (no upscaling).

    Args:
        source_width: Source image width in pixels
        source_height: Source image height in pixels
        max_dimension: Maximum allowed dimension (width or height)

    Returns:
        Tuple of (thumbnail_width, thumbnail_height)

    Examples:
        >>> calculate_thumbnail_dimensions(4000, 3000, 800)
        (800, 600)
        >>> calculate_thumbnail_dimensions(600, 400, 800)
        (600, 400)  # No upscaling
    """
```

**Preconditions**:
- All dimensions > 0
- `max_dimension` > 0

**Postconditions**:
- Returned dimensions maintain aspect ratio within 0.01%
- Larger dimension == `max_dimension` (unless source smaller)
- No upscaling: returned dimensions <= source dimensions

---

### Function: generate_content_hash

Generate hash-based filename component from image content.

```python
def generate_content_hash(image_bytes: bytes) -> str:
    """
    Generate 8-character hash from image content.

    Uses SHA-256 for reproducibility and collision resistance.

    Args:
        image_bytes: Raw image file bytes

    Returns:
        First 8 characters of SHA-256 hex digest

    Examples:
        >>> generate_content_hash(Path("photo.jpg").read_bytes())
        'a1b2c3d4'
    """
```

**Preconditions**:
- `image_bytes` not empty

**Postconditions**:
- Returns exactly 8 hexadecimal characters
- Same bytes always produce same hash (reproducible)
- Different bytes produce different hashes (collision-resistant)

---

### Function: apply_exif_orientation

Apply EXIF orientation correction to PIL Image.

```python
def apply_exif_orientation(image: PILImage.Image) -> PILImage.Image:
    """
    Apply EXIF orientation transformation to image.

    Handles all 8 EXIF orientation values. No-op if no EXIF data.

    Args:
        image: PIL Image object

    Returns:
        New PIL Image with orientation applied (or same image if no EXIF)

    Side Effects:
        - May create new image object with rotated/flipped data
        - Original image unchanged
    """
```

**Preconditions**:
- `image` is valid PIL Image object

**Postconditions**:
- Returns image oriented for standard display
- Original image reference preserved (new image created if transform needed)

---

## Integration Points

### Integration with build_html.py

```python
# In src/generator/build_html.py

from src.generator.thumbnails import ThumbnailGenerator
from src.generator.model import ThumbnailConfig

def build_gallery(config: GalleryConfig) -> None:
    """Main build function."""

    # ... existing code ...

    if config.enable_thumbnails:
        # Initialize thumbnail generator
        thumb_gen = ThumbnailGenerator(config.thumbnail_config)

        # Extract image paths
        image_paths = [img.file_path for img in images]

        # Generate thumbnails
        successful, failed = thumb_gen.generate_batch(image_paths)

        # Attach thumbnails to Image objects
        thumbnail_map = {t.source_path: t for t in successful}
        for img in images:
            img.thumbnail = thumbnail_map.get(img.file_path)

        # Log results
        logger.info(
            f"Thumbnails: {len(successful)} generated, "
            f"{len(image_paths) - len(successful) - len(failed)} cached, "
            f"{len(failed)} failed"
        )
```

### Integration with Templates

```jinja2
{# In src/templates/index.html.j2 #}

{% for image in category.images %}
<div class="gallery-item">
  <picture>
    <source
      srcset="{{ image.thumbnail_url if image.thumbnail else image.image_url }}"
      type="image/webp">
    <img
      src="{{ image.thumbnail_fallback_url if image.thumbnail else image.image_url }}"
      alt="{{ image.alt_text }}"
      width="{{ image.thumbnail.width if image.thumbnail else image.width }}"
      height="{{ image.thumbnail.height if image.thumbnail else image.height }}"
      loading="lazy">
  </picture>
</div>
{% endfor %}
```

---

## Error Codes and Messages

### Error: ThumbnailGenerationError

```python
class ThumbnailGenerationError(Exception):
    """Raised when thumbnail generation fails for recoverable reasons."""
    pass
```

**Usage**: Wrap Pillow errors during individual image processing

### Error: BuildCacheError

```python
class BuildCacheError(Exception):
    """Raised when build cache operations fail."""
    pass
```

**Usage**: Wrap JSON parsing or file I/O errors during cache operations

### Standard Error Messages

```python
ERROR_MESSAGES = {
    "unsupported_format": "Image format not supported for {path}: {format}",
    "corrupt_image": "Unable to open image {path}: file may be corrupt",
    "write_failed": "Failed to write thumbnail to {path}: {error}",
    "cache_corrupt": "Build cache corrupted, regenerating all thumbnails",
    "insufficient_space": "Insufficient disk space for thumbnail generation",
}
```

---

## Performance Contracts

### generate_thumbnail()
- **Time**: <500ms per 5MB source image on standard laptop (Intel i5, SSD)
- **Memory**: Peak 50MB per image (2x source file size during processing)
- **Disk I/O**: 1 read (source), 2 writes (WebP + JPEG)

### generate_batch()
- **Time**: <2 minutes for 100 images (linear scaling)
- **Memory**: Constant (processes one image at a time)
- **Disk I/O**: Linear with image count

### load_cache()
- **Time**: <10ms for 100 entries
- **Memory**: ~1KB per cache entry

### save_cache()
- **Time**: <50ms for 100 entries
- **Disk I/O**: Single write to cache file

---

## Testing Contracts

### Unit Test Requirements

```python
def test_generate_thumbnail_creates_both_formats():
    """Verify WebP and JPEG files created."""

def test_generate_thumbnail_preserves_aspect_ratio():
    """Verify thumbnail dimensions maintain source aspect ratio."""

def test_generate_thumbnail_applies_exif_orientation():
    """Verify EXIF rotation applied correctly."""

def test_generate_thumbnail_skips_cached():
    """Verify cache hit returns None without regeneration."""

def test_generate_thumbnail_handles_corrupt_image():
    """Verify corrupt image logged and skipped gracefully."""

def test_calculate_thumbnail_dimensions_no_upscaling():
    """Verify small images not upscaled."""
```

### Integration Test Requirements

```python
def test_end_to_end_thumbnail_generation():
    """Verify full build pipeline generates thumbnails."""

def test_incremental_build_skips_unchanged():
    """Verify only modified images regenerated."""

def test_thumbnail_file_size_reduction():
    """Verify 90%+ size reduction achieved."""

def test_webp_savings_vs_jpeg():
    """Verify WebP 25-35% smaller than JPEG."""
```

---

## Versioning and Compatibility

### Cache Version Policy

- **Version format**: Semantic versioning (MAJOR.MINOR)
- **Breaking changes**: Increment MAJOR (e.g., 1.0 → 2.0)
  - Cache format structure changes
  - Hash algorithm changes
- **Non-breaking changes**: Increment MINOR (e.g., 1.0 → 1.1)
  - New optional fields
  - Additional metadata

### API Stability Guarantees

- **Stable**: Public methods and signatures (no breaking changes without major version)
- **Unstable**: Internal helper functions (may change between minor versions)
- **Deprecated**: Features marked deprecated for 2 minor versions before removal

---

## Example Usage

### Basic Usage

```python
from pathlib import Path
from src.generator.thumbnails import ThumbnailGenerator
from src.generator.model import ThumbnailConfig

# Configure thumbnail generation
config = ThumbnailConfig(
    max_dimension=800,
    webp_quality=85,
    jpeg_quality=90,
    output_dir=Path("build/images/thumbnails"),
    enable_cache=True
)

# Initialize generator
generator = ThumbnailGenerator(config)

# Generate single thumbnail
source = Path("content/photos/IMG_1234.jpg")
thumbnail = generator.generate_thumbnail(source)

if thumbnail:
    print(f"Generated: {thumbnail.webp_path}")
    print(f"Size reduction: {thumbnail.size_reduction_percent:.1f}%")
else:
    print("Thumbnail cached (no regeneration needed)")
```

### Batch Processing

```python
# Process multiple images
source_images = list(Path("content/photos").glob("*.jpg"))

def log_progress(current: int, total: int) -> None:
    print(f"Processing {current}/{total}...", end="\r")

successful, failed = generator.generate_batch(
    source_images,
    progress_callback=log_progress
)

print(f"\nCompleted: {len(successful)} successful, {len(failed)} failed")
```

---

## Security Considerations

### Input Validation

- All file paths validated as existing, readable files
- Image formats validated against allowlist (JPEG, PNG, GIF, WEBP)
- File size limits enforced (reject >50MB by default)

### Path Traversal Prevention

- All output paths constructed relative to configured `output_dir`
- No user-controlled path components in filename generation
- Hash-based naming prevents directory traversal in filenames

### Resource Limits

- Single-threaded processing prevents resource exhaustion
- Memory usage bounded by single image processing
- Disk space checked before write operations

---

## Appendix: Example Responses

### Successful Generation

```python
ThumbnailImage(
    source_filename="IMG_1234.jpg",
    source_path=Path("content/photos/IMG_1234.jpg"),
    webp_path=Path("build/images/thumbnails/IMG_1234-a1b2c3d4.webp"),
    jpeg_path=Path("build/images/thumbnails/IMG_1234-a1b2c3d4.jpg"),
    width=800,
    height=600,
    webp_size_bytes=45_123,
    jpeg_size_bytes=65_789,
    source_size_bytes=2_456_789,
    content_hash="a1b2c3d4",
    generated_at=datetime(2025, 11, 2, 14, 30, 0)
)
```

### Cache Hit (No Regeneration)

```python
generator.generate_thumbnail(source_path)
# Returns: None
# Log: "Skipping IMG_1234.jpg (cached, unchanged)"
```

### Error Case

```python
try:
    generator.generate_thumbnail(Path("corrupt.jpg"))
except ThumbnailGenerationError as e:
    # Logs: "WARNING: Unable to open image corrupt.jpg: file may be corrupt"
    # Returns: None (not raised, handled internally)
```
