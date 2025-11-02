# Data Model: Image Preprocessing

**Feature**: `008-image-preprocessing`
**Date**: 2025-11-02
**Status**: Draft

## Overview

This document defines the data structures for image preprocessing, including thumbnail generation, metadata extraction, and build caching. Entities extend existing models from `src/generator/model.py` and introduce new models for thumbnail management.

---

## Core Entities

### 1. ThumbnailConfig

Configuration parameters for thumbnail generation process.

**Fields**:
- `max_dimension: int` - Maximum width or height for thumbnails (default: 800)
- `webp_quality: int` - WebP compression quality 0-100 (default: 85)
- `jpeg_quality: int` - JPEG fallback compression quality 0-100 (default: 90)
- `output_dir: Path` - Directory for generated thumbnails (default: `build/images/thumbnails/`)
- `enable_cache: bool` - Whether to use incremental build cache (default: True)
- `cache_file: Path` - Path to build cache JSON (default: `build/.build-cache.json`)

**Validation Rules**:
- `max_dimension`: Must be >= 100 and <= 4000
- `webp_quality`: Must be >= 1 and <= 100
- `jpeg_quality`: Must be >= 1 and <= 100
- `output_dir`: Must be writable directory
- `cache_file`: Parent directory must exist

**Relationships**:
- Referenced by `GalleryConfig` to control thumbnail generation
- Used by `ThumbnailGenerator` service

**State Transitions**: Immutable after validation

---

### 2. ThumbnailImage

Represents a generated thumbnail with both WebP and JPEG fallback formats.

**Fields**:
- `source_filename: str` - Original image filename
- `source_path: Path` - Full path to original image file
- `webp_path: Path` - Path to generated WebP thumbnail
- `jpeg_path: Path` - Path to generated JPEG fallback thumbnail
- `width: int` - Thumbnail width in pixels
- `height: int` - Thumbnail height in pixels
- `webp_size_bytes: int` - WebP file size
- `jpeg_size_bytes: int` - JPEG file size
- `source_size_bytes: int` - Original image file size
- `content_hash: str` - SHA-256 hash of source image (first 8 chars)
- `generated_at: datetime` - Timestamp of thumbnail generation

**Validation Rules**:
- `source_filename`: Must not be empty
- `width`, `height`: Must be > 0
- File sizes: Must be > 0
- Paths: Must be valid Path objects
- `content_hash`: Must be 8 hexadecimal characters

**Relationships**:
- Links to `Image` entity via `source_filename`
- Multiple `ThumbnailImage` instances can reference same source if regenerated
- Referenced by `BuildCache` to track generation history

**State Transitions**:
1. Created → Validated → Persisted to disk
2. Immutable after creation (regeneration creates new instance)

**Derived Properties**:
```python
@property
def size_reduction_percent(self) -> float:
    """Calculate percentage reduction in file size (WebP vs original)."""
    return ((self.source_size_bytes - self.webp_size_bytes) / self.source_size_bytes) * 100

@property
def webp_savings_percent(self) -> float:
    """Calculate percentage savings of WebP vs JPEG fallback."""
    return ((self.jpeg_size_bytes - self.webp_size_bytes) / self.jpeg_size_bytes) * 100

@property
def aspect_ratio(self) -> float:
    """Calculate thumbnail aspect ratio."""
    return self.width / self.height
```

---

### 3. ImageMetadata

Extended metadata extracted from source images during thumbnail generation.

**Fields**:
- `filename: str` - Image filename
- `file_path: Path` - Full path to image file
- `format: str` - Image format (JPEG, PNG, GIF, WEBP)
- `width: int` - Original image width
- `height: int` - Original image height
- `file_size_bytes: int` - File size in bytes
- `color_mode: str` - Color mode (RGB, RGBA, L, CMYK, etc.)
- `has_transparency: bool` - Whether image has alpha channel
- `exif_orientation: Optional[int]` - EXIF orientation tag (1-8)
- `is_animated: bool` - Whether image is animated (GIF)
- `frame_count: int` - Number of frames (1 for static images)
- `dpi: Optional[tuple[int, int]]` - Image DPI if available

**Validation Rules**:
- `filename`: Must not be empty
- `format`: Must be one of supported formats
- Dimensions and sizes: Must be > 0
- `color_mode`: Must be valid PIL mode string
- `exif_orientation`: If present, must be 1-8

**Relationships**:
- Extracted from source `Image` entities
- Used by `ThumbnailGenerator` to determine processing strategy
- Can be cached separately from thumbnails for metadata-only queries

**State Transitions**: Immutable snapshot of image at scan time

---

### 4. BuildCache

Tracks processed images and their modification times for incremental builds.

**Fields**:
- `entries: dict[str, CacheEntry]` - Map of source file path to cache entry
- `cache_version: str` - Cache format version (for future compatibility)
- `last_updated: datetime` - When cache was last updated

**Nested Type - CacheEntry**:
- `source_path: str` - Absolute path to source image
- `source_mtime: float` - File modification timestamp
- `webp_path: str` - Path to generated WebP thumbnail
- `jpeg_path: str` - Path to generated JPEG thumbnail
- `content_hash: str` - Hash of source image
- `thumbnail_generated_at: datetime` - When thumbnail was created

**Validation Rules**:
- `cache_version`: Must match current version (e.g., "1.0")
- `source_path`: Must be valid absolute path
- `source_mtime`: Must be valid Unix timestamp
- Thumbnail paths: Must exist if cache entry present

**Relationships**:
- One cache per build output directory
- Contains entries for all processed images
- Used by `ThumbnailGenerator` to determine if regeneration needed

**State Transitions**:
1. Loaded from disk → Checked against current file system → Updated → Saved
2. Entries added/updated incrementally during build
3. Entries removed if source image deleted

**Methods**:
```python
def should_regenerate(self, source_path: Path) -> bool:
    """Check if thumbnail needs regeneration based on mtime."""
    entry = self.entries.get(str(source_path))
    if entry is None:
        return True
    current_mtime = source_path.stat().st_mtime
    return current_mtime > entry.source_mtime

def update_entry(self, source_path: Path, thumbnail: ThumbnailImage) -> None:
    """Update or add cache entry for processed image."""
    self.entries[str(source_path)] = CacheEntry(
        source_path=str(source_path),
        source_mtime=source_path.stat().st_mtime,
        webp_path=str(thumbnail.webp_path),
        jpeg_path=str(thumbnail.jpeg_path),
        content_hash=thumbnail.content_hash,
        thumbnail_generated_at=thumbnail.generated_at
    )
    self.last_updated = datetime.now()
```

---

## Modified Entities

### Image (Extended)

Existing `Image` model from `src/generator/model.py` extended with thumbnail references.

**New Fields**:
- `thumbnail: Optional[ThumbnailImage]` - Reference to generated thumbnail (None if not generated)

**New Methods**:
```python
@property
def thumbnail_url(self) -> str:
    """Get relative URL to thumbnail WebP for HTML templates."""
    if self.thumbnail:
        return f"images/thumbnails/{self.thumbnail.webp_path.name}"
    return self.image_url  # Fallback to original

@property
def thumbnail_fallback_url(self) -> str:
    """Get relative URL to JPEG fallback thumbnail."""
    if self.thumbnail:
        return f"images/thumbnails/{self.thumbnail.jpeg_path.name}"
    return self.image_url  # Fallback to original
```

---

### GalleryConfig (Extended)

Existing `GalleryConfig` model extended with thumbnail configuration.

**Modified Fields**:
- `enable_thumbnails: bool` - Changed from placeholder to active feature
- `thumbnail_config: ThumbnailConfig` - New nested configuration object

**Backward Compatibility**:
- `enable_thumbnails=False` maintains existing behavior (no thumbnail generation)
- Default thumbnail config values ensure safe defaults if not explicitly configured

---

## Entity Relationships Diagram

```
┌─────────────────┐
│  GalleryConfig  │
│  ──────────────  │
│  thumbnail_config├────┐
└─────────────────┘    │
                       │
                       ▼
           ┌──────────────────────┐
           │  ThumbnailConfig     │
           │  ────────────────────  │
           │  max_dimension       │
           │  webp_quality        │
           │  jpeg_quality        │
           └──────────────────────┘
                       │
                       │ used by
                       ▼
┌─────────────────┐  ┌──────────────────────┐
│  Image          │  │  ThumbnailGenerator  │
│  ──────────────  │  │  ────────────────────  │
│  filename       │◄─┤  generate()          │
│  file_path      │  │  load_cache()        │
│  thumbnail  ────┼──┤  save_cache()        │
└─────────────────┘  └──────────────────────┘
         │                    │
         │                    │ produces
         ▼                    ▼
┌─────────────────┐  ┌──────────────────────┐
│ ThumbnailImage  │  │  BuildCache          │
│ ──────────────   │  │  ────────────────────  │
│ webp_path       │  │  entries{}           │
│ jpeg_path       │◄─┤  should_regenerate() │
│ content_hash    │  │  update_entry()      │
└─────────────────┘  └──────────────────────┘
```

---

## Data Validation Examples

### ThumbnailConfig Validation

```python
from pydantic import ValidationError

# Valid configuration
config = ThumbnailConfig(
    max_dimension=800,
    webp_quality=85,
    jpeg_quality=90,
    output_dir=Path("build/images/thumbnails"),
    enable_cache=True
)

# Invalid: quality out of range
try:
    config = ThumbnailConfig(webp_quality=150)  # Raises ValidationError
except ValidationError as e:
    print(e)  # "webp_quality: must be <= 100"
```

### ThumbnailImage Creation

```python
thumbnail = ThumbnailImage(
    source_filename="photo.jpg",
    source_path=Path("content/photo.jpg"),
    webp_path=Path("build/images/thumbnails/photo-a1b2c3d4.webp"),
    jpeg_path=Path("build/images/thumbnails/photo-a1b2c3d4.jpg"),
    width=800,
    height=600,
    webp_size_bytes=45_000,
    jpeg_size_bytes=65_000,
    source_size_bytes=2_500_000,
    content_hash="a1b2c3d4",
    generated_at=datetime.now()
)

# Check metrics
assert thumbnail.size_reduction_percent > 90  # 98.2% reduction
assert thumbnail.webp_savings_percent > 25    # 30.8% WebP savings
```

---

## Storage Format

### Build Cache JSON Structure

```json
{
  "cache_version": "1.0",
  "last_updated": "2025-11-02T14:30:00Z",
  "entries": {
    "/path/to/content/photo1.jpg": {
      "source_path": "/path/to/content/photo1.jpg",
      "source_mtime": 1699012345.678,
      "webp_path": "build/images/thumbnails/photo1-a1b2c3d4.webp",
      "jpeg_path": "build/images/thumbnails/photo1-a1b2c3d4.jpg",
      "content_hash": "a1b2c3d4",
      "thumbnail_generated_at": "2025-11-02T14:25:00Z"
    }
  }
}
```

---

## Migration Strategy

### Phase 1: Add Models (Non-Breaking)
1. Add new models to `src/generator/model.py`
2. Existing code continues to work without thumbnails
3. Tests validate model definitions

### Phase 2: Extend Image Model (Non-Breaking)
1. Add optional `thumbnail` field to `Image`
2. Default `None` maintains backward compatibility
3. Add property methods for thumbnail URLs

### Phase 3: Integrate Generator (Feature Flag)
1. Check `enable_thumbnails` config flag
2. Generate thumbnails only if enabled
3. Existing builds unaffected if disabled

### Phase 4: Update Templates (Graceful Fallback)
1. Templates check if `thumbnail` exists
2. Use thumbnail URLs if available
3. Fall back to original image URLs if not

---

## Performance Considerations

### Memory Management
- Process images one at a time to limit memory usage
- Close PIL Image objects immediately after processing
- BuildCache loaded once, updated incrementally

### Disk I/O Optimization
- Cache checks use stat() for fast mtime comparison
- Thumbnail generation writes directly to final location (no temp files)
- JSON cache written once at end of build

### Scalability Limits
- Cache size: ~1KB per image entry, 100KB for 100 images
- Thumbnail directory: 2 files per source image
- Build time: Linear with number of changed images

---

## Error Handling Strategy

### Recoverable Errors
- Corrupt source image → Log warning, skip thumbnail, continue build
- Missing source file → Remove from cache, continue
- Disk space exhausted → Log error, skip remaining thumbnails, complete build

### Fatal Errors
- Output directory not writable → Fail build with clear error
- Cache file corrupted → Delete cache, regenerate all thumbnails
- Invalid configuration → Fail validation before build starts

### Error Reporting
- Per-image errors logged at WARNING level with filename
- Fatal errors logged at ERROR level with remediation guidance
- Build summary reports: X successful, Y skipped, Z failed
