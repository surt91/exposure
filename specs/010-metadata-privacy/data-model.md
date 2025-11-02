# Data Model: Image Metadata Privacy and Build Progress Logging

**Feature**: `010-metadata-privacy` | **Date**: 2025-11-02

## Overview

This feature extends the existing thumbnail generation data model to track metadata stripping and enhance progress logging. No new top-level entities are introduced; instead, we enhance existing models and add utility structures.

## Entity: SensitiveMetadataFields

**Purpose**: Define which EXIF/IPTC/XMP metadata fields must be removed for privacy

**Type**: Constants/Configuration (not a runtime model)

**Structure**:

```python
# src/generator/constants.py

# EXIF tags to REMOVE (privacy-sensitive)
SENSITIVE_EXIF_TAGS: set[int] = {
    # GPS tags (IFD GPS)
    0x0000,  # GPSVersionID
    0x0001,  # GPSLatitudeRef
    0x0002,  # GPSLatitude
    0x0003,  # GPSLongitudeRef
    0x0004,  # GPSLongitude
    0x0005,  # GPSAltitudeRef
    0x0006,  # GPSAltitude
    0x0007,  # GPSTimeStamp
    # ... (all GPS tags 0x0000-0x001F)

    # Camera/lens serial numbers
    0xA431,  # BodySerialNumber
    0xA435,  # LensSerialNumber
    0xFDE8,  # LensInfo (may contain serial)

    # Creator/copyright information
    0x013B,  # Artist
    0x8298,  # Copyright
    0x9C9D,  # XPAuthor
    0x9C9E,  # XPComment

    # Software/editing metadata
    0x0131,  # Software
    0x000B,  # ProcessingSoftware

    # Embedded thumbnails
    0x0201,  # JPEGInterchangeFormat (thumbnail offset)
    0x0202,  # JPEGInterchangeFormatLength (thumbnail length)
    0x0103,  # Compression (thumbnail)
}

# EXIF tags to PRESERVE (display-critical or useful)
SAFE_EXIF_TAGS: set[int] = {
    # Orientation
    0x0112,  # Orientation

    # Color management
    0xA001,  # ColorSpace
    # ICC profile preserved via Pillow's info dict

    # Timestamps (non-sensitive, useful for display)
    0x9003,  # DateTimeOriginal
    0x9004,  # DateTimeDigitized
    0x0132,  # DateTime (modification)

    # Camera/lens information (per FR-008a)
    0x010F,  # Make
    0x0110,  # Model
    0xA434,  # LensModel
    0xA433,  # LensMake

    # Image properties
    0xA002,  # PixelXDimension
    0xA003,  # PixelYDimension
    0xA210,  # FocalPlaneResolutionUnit

    # Exposure information (useful, non-identifying)
    0x829D,  # FNumber
    0x829A,  # ExposureTime
    0x8827,  # ISO
    0x920A,  # FocalLength
}
```

**Validation Rules**:
- Sets must be disjoint (no tag in both SENSITIVE and SAFE)
- GPS tag range (0x0000-0x001F) must be fully covered in SENSITIVE
- Orientation (0x0112) must be in SAFE (required for correct display)

**Relationships**:
- Used by `_strip_metadata()` method in `ThumbnailGenerator`
- Referenced in tests to verify removal/preservation

---

## Entity Enhancement: ThumbnailImage

**Purpose**: Track whether metadata was successfully stripped from thumbnail

**Existing Model** (`src/generator/model.py`):

```python
class ThumbnailImage(BaseModel):
    source_filename: str
    source_path: Path
    webp_path: Path
    jpeg_path: Path
    width: int
    height: int
    webp_size_bytes: int
    jpeg_size_bytes: int
    source_size_bytes: int
    content_hash: str
    generated_at: datetime
```

**Enhancement** (NEW field):

```python
class ThumbnailImage(BaseModel):
    # ... existing fields ...

    metadata_stripped: bool = True  # NEW: Whether sensitive metadata was successfully removed
    metadata_strip_warning: Optional[str] = None  # NEW: Error message if stripping failed
```

**Validation Rules**:
- `metadata_stripped`: Defaults to `True` (assume success unless error occurs)
- `metadata_strip_warning`: Populated only when `metadata_stripped=False`
- Must track independently for WebP and JPEG? NO - both use same `_strip_metadata()` call

**Why these fields**:
- Enables tracking which images have metadata issues
- Supports potential future features (e.g., "show unstripped images" admin view)
- Preserves history in build cache
- Allows testing to verify stripping occurred

---

## Entity: MetadataStripResult

**Purpose**: Internal structure for metadata stripping operation result

**Type**: Dataclass (not Pydantic model - internal only)

**Structure**:

```python
# src/generator/thumbnails.py

from dataclasses import dataclass

@dataclass
class MetadataStripResult:
    """Result of metadata stripping operation."""
    success: bool
    image: PILImage.Image  # Image with metadata stripped (or original if failed)
    warning: Optional[str] = None  # Error message if failed
    sensitive_fields_removed: int = 0  # Count of removed tags (for logging)
    safe_fields_preserved: int = 0  # Count of preserved tags (for logging)
```

**Usage**:

```python
def _strip_metadata(self, img: PILImage.Image) -> MetadataStripResult:
    try:
        # ... stripping logic ...
        return MetadataStripResult(
            success=True,
            image=img_with_safe_metadata,
            sensitive_fields_removed=removed_count,
            safe_fields_preserved=preserved_count
        )
    except Exception as e:
        return MetadataStripResult(
            success=False,
            image=img,  # Return original
            warning=str(e)
        )
```

**Validation Rules**:
- If `success=True`, `warning` must be `None`
- If `success=False`, `warning` must be populated
- Counts are informational only (no validation)

---

## Entity: ProgressLogEntry

**Purpose**: Define structure of progress log messages

**Type**: Conceptual (not a stored entity - just logging format)

**Structure**:

```python
# Not a Python class - just a logging pattern

# Success format:
"✓ {filename} → {source_size} → {thumbnail_size} ({reduction_pct}% reduction)"

# Warning format (metadata stripping failed):
"⚠ WARNING: Metadata stripping failed for {filename}: {error_message}"

# Cache hit format (debug level):
"Skipping {filename} (cached, unchanged)"
```

**Components**:
- `filename`: Source image filename (not full path)
- `source_size`: Human-readable size (e.g., "5.2MB")
- `thumbnail_size`: Human-readable size (e.g., "420KB")
- `reduction_pct`: Float formatted to 1 decimal place (e.g., "92.3")
- `error_message`: Exception message or description

**Validation Rules**:
- Sizes must be human-readable (MB/KB/bytes, not raw bytes)
- Percentages formatted to 1 decimal place
- Success logs use INFO level
- Warning logs use WARNING level with "⚠ WARNING:" prefix
- Cache hits use DEBUG level

**Format Helpers**:

```python
def _format_size(self, bytes: int) -> str:
    """Format bytes as human-readable size."""
    if bytes >= 1_000_000:
        return f"{bytes / 1_000_000:.1f}MB"
    elif bytes >= 1_000:
        return f"{bytes / 1_000:.0f}KB"
    else:
        return f"{bytes}B"
```

---

## Entity Enhancement: BuildCache

**Purpose**: Track metadata stripping state for incremental builds

**Existing Model** (`src/generator/cache.py`):

```python
class CacheEntry(BaseModel):
    source_path: str
    content_hash: str
    source_modified_time: float
    webp_path: str
    jpeg_path: str
    thumbnail_generated_at: datetime
```

**Enhancement** (NEW field):

```python
class CacheEntry(BaseModel):
    # ... existing fields ...

    metadata_stripped: bool = True  # NEW: Whether metadata was stripped in this build
```

**Validation Rules**:
- Defaults to `True` for new entries
- If `CACHE_VERSION` changes, entire cache invalidated anyway
- No migration needed from old cache (version mismatch triggers rebuild)

**Cache Invalidation**:
- Already handled by existing `content_hash` comparison
- If source image changes, `content_hash` changes → rebuild triggered
- If stripping logic changes, bump `CACHE_VERSION` → full rebuild

---

## Data Flow

### Thumbnail Generation with Metadata Stripping

```
1. generate_thumbnail(source_path)
   ↓
2. Check cache (existing logic)
   ↓
3. Open image with Pillow
   ↓
4. _prepare_image() - orientation, color conversion
   ↓
5. _create_thumbnail() - resize
   ↓
6. _strip_metadata(thumb) → MetadataStripResult  [NEW]
   ↓
7. _save_thumbnails(result.image, ...)
   ↓
8. Build ThumbnailImage with metadata_stripped field  [ENHANCED]
   ↓
9. Update cache with metadata_stripped=True  [ENHANCED]
   ↓
10. Log progress (filename + size reduction)  [ENHANCED]
```

### Metadata Stripping Process

```
1. _strip_metadata(img)
   ↓
2. Extract EXIF: img.getexif()
   ↓
3. Filter tags:
   - Keep tags in SAFE_EXIF_TAGS
   - Remove tags in SENSITIVE_EXIF_TAGS
   - Remove all other tags (default deny)
   ↓
4. Create new EXIF: Image.Exif()
   ↓
5. Populate with safe tags only
   ↓
6. Return MetadataStripResult
   - success=True if no errors
   - success=False if exception
```

---

## State Transitions

### MetadataStripResult States

```
[Image with metadata]
        ↓
  _strip_metadata()
        ↓
    ┌───────┴──────┐
    ↓              ↓
[SUCCESS]      [FAILURE]
    ↓              ↓
safe metadata   original
only            unchanged
```

### ThumbnailImage Metadata State

```
[New thumbnail]
        ↓
metadata_stripped=True (default)
metadata_strip_warning=None
        ↓
   if stripping fails:
        ↓
metadata_stripped=False
metadata_strip_warning="Error message"
```

---

## Constraints & Invariants

### System Constraints

1. **No File Corruption**: Metadata stripping must never corrupt image visual content
2. **Deterministic**: Same source image + same code = same stripped metadata (reproducible builds)
3. **Original Preservation**: Source images in `content_dir` must remain unchanged
4. **Format Support**: Stripping must work for JPEG, PNG, GIF (primary formats)

### Data Invariants

1. **Tag Disjointness**: `SENSITIVE_EXIF_TAGS ∩ SAFE_EXIF_TAGS = ∅`
2. **Orientation Preservation**: `0x0112 ∈ SAFE_EXIF_TAGS` (always true)
3. **GPS Removal**: `∀ tag ∈ [0x0000..0x001F] → tag ∈ SENSITIVE_EXIF_TAGS`
4. **Warning Consistency**: `metadata_stripped=False ⟺ metadata_strip_warning≠None`
5. **Result Validity**: `MetadataStripResult.success=True ⟺ warning=None`

### Performance Constraints

1. **Metadata Stripping Time**: ≤5ms per image (negligible vs 50-100ms resize)
2. **Total Build Impact**: ≤10% increase in total build time
3. **Memory Overhead**: Metadata structures must fit in available RAM (≤10KB per image)

---

## Testing Considerations

### Unit Test Data

**Test fixtures needed**:

```python
# tests/fixtures/images_with_metadata.py

def create_image_with_gps(path: Path):
    """Create test JPEG with GPS coordinates."""
    img = Image.new("RGB", (800, 600), color="blue")
    exif = Image.Exif()
    exif[0x0002] = [(40, 1), (44, 1), (54, 1)]  # GPSLatitude
    exif[0x0004] = [(74, 1), (0, 1), (21, 1)]   # GPSLongitude
    img.save(path, "JPEG", exif=exif.tobytes())

def create_image_with_serial(path: Path):
    """Create test JPEG with camera serial number."""
    img = Image.new("RGB", (800, 600), color="red")
    exif = Image.Exif()
    exif[0xA431] = "SERIAL123456"  # BodySerialNumber
    img.save(path, "JPEG", exif=exif.tobytes())
```

### Validation Tests

**Test cases**:

1. **Sensitive field removal**: GPS tags absent in output
2. **Safe field preservation**: Orientation tag present in output
3. **Timestamp preservation**: DateTimeOriginal present in output
4. **Camera info preservation**: Make/Model present in output (FR-008a)
5. **Error handling**: Corrupted EXIF → warning logged, build continues
6. **Progress logging**: Output contains filename and reduction percentage
7. **Cache behavior**: Unchanged images skip stripping, cached result used

---

## Migration Strategy

### Existing Data

**No migration needed**:
- Feature is additive (no breaking changes to existing models)
- Old cache entries without `metadata_stripped` field use default value `True`
- Pydantic handles missing fields gracefully with defaults

### Cache Version Bump

```python
# src/generator/constants.py

CACHE_VERSION = "2.0"  # Bump from 1.0 to force rebuild with metadata stripping
```

**Effect**:
- All existing cache entries invalidated
- All thumbnails regenerated with metadata stripping
- Users see one-time full rebuild after upgrade

### Backward Compatibility

**No backward compatibility needed**:
- Feature is for new builds only
- Old thumbnails (with metadata) remain until rebuild
- Users can manually trigger rebuild with `exposure` command

---

## Summary

**New Entities**: `MetadataStripResult` (internal dataclass), `SensitiveMetadataFields` (constants)

**Enhanced Entities**: `ThumbnailImage` (+2 fields), `CacheEntry` (+1 field)

**Key Relationships**:
- `ThumbnailGenerator._strip_metadata()` uses `SENSITIVE_EXIF_TAGS` / `SAFE_EXIF_TAGS`
- `ThumbnailImage.metadata_stripped` populated from `MetadataStripResult.success`
- `CacheEntry.metadata_stripped` mirrors `ThumbnailImage.metadata_stripped`
- Progress logs formatted from `ThumbnailImage` size fields

**Validation Focus**: Ensure tag sets are disjoint, orientation always preserved, GPS tags always removed, warnings logged on failures.
