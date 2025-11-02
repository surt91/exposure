# API Contract: Metadata Stripping

**Feature**: `010-metadata-privacy` | **Date**: 2025-11-02

## Overview

Defines the programmatic interface for stripping sensitive metadata from image thumbnails while preserving display-critical fields. This contract specifies method signatures, input/output types, error handling, and behavioral guarantees.

---

## Method: `_strip_metadata`

### Signature

```python
def _strip_metadata(self, img: PILImage.Image) -> MetadataStripResult:
    """
    Remove sensitive EXIF/IPTC/XMP metadata from image while preserving
    display-critical fields.

    Strips GPS coordinates, camera serial numbers, creator information,
    and software metadata. Preserves orientation, color profiles, timestamps,
    and camera/lens information.

    Args:
        img: PIL Image object (typically a thumbnail after resize)

    Returns:
        MetadataStripResult with:
        - success: True if stripping completed without errors
        - image: PIL Image with filtered metadata (or original if failed)
        - warning: Error message if stripping failed (None otherwise)
        - sensitive_fields_removed: Count of tags removed
        - safe_fields_preserved: Count of tags preserved

    Raises:
        Never raises exceptions - all errors captured in result.warning

    Side Effects:
        - Modifies EXIF data in the PIL Image object in-place
        - Does not modify source file on disk
        - Does not write any files

    Performance:
        - Execution time: ≤5ms per image
        - Memory overhead: ≤10KB for metadata structures

    Thread Safety:
        - Method is thread-safe (no shared mutable state)
        - Each call operates on independent PIL Image object
    """
```

### Input Contract

**Type**: `PIL.Image.Image`

**Preconditions**:
- Image must be a valid PIL Image object (opened successfully)
- Image must be in-memory (not a lazy-loaded placeholder)
- Image format should be JPEG, PNG, or GIF (other formats handled gracefully)
- Image does not need to have EXIF data (handles absence gracefully)

**Invalid Inputs** (handled gracefully, not rejected):
- Image with no EXIF data → return success with 0 fields removed
- Image with corrupted EXIF data → return failure with warning
- Image in unsupported format → return success (no metadata to strip)

### Output Contract

**Type**: `MetadataStripResult` (dataclass)

**Structure**:
```python
@dataclass
class MetadataStripResult:
    success: bool
    image: PILImage.Image
    warning: Optional[str] = None
    sensitive_fields_removed: int = 0
    safe_fields_preserved: int = 0
```

**Postconditions**:

**On Success** (`success=True`):
- All tags in `SENSITIVE_EXIF_TAGS` removed from output image
- All tags in `SAFE_EXIF_TAGS` present in input are preserved in output
- `warning` is `None`
- `sensitive_fields_removed` ≥ 0 (count of removed tags)
- `safe_fields_preserved` ≥ 0 (count of preserved tags)
- Visual content of image unchanged (pixel data identical)
- Image file structure valid (can be saved without corruption)

**On Failure** (`success=False`):
- `warning` contains human-readable error message
- `image` is identical to input (no modifications applied)
- `sensitive_fields_removed` = 0
- `safe_fields_preserved` = 0
- Failure does not crash or raise exception

**Invariants**:
- `success=True ⟺ warning=None`
- `success=False ⟺ warning≠None`
- Output image must always be valid PIL Image object
- GPS tags (0x0000-0x001F) never present in success output
- Orientation tag (0x0112) always preserved if present in input

---

## Method: `_format_size`

### Signature

```python
def _format_size(self, bytes: int) -> str:
    """
    Format byte count as human-readable size string.

    Args:
        bytes: File size in bytes (non-negative integer)

    Returns:
        Human-readable size string:
        - "X.XMB" for sizes ≥ 1,000,000 bytes (1 decimal place)
        - "XXXKB" for sizes ≥ 1,000 bytes (no decimals)
        - "XB" for sizes < 1,000 bytes

    Raises:
        ValueError: If bytes is negative

    Examples:
        _format_size(5_242_880) → "5.2MB"
        _format_size(420_000) → "420KB"
        _format_size(512) → "512B"
    """
```

### Input Contract

**Type**: `int`

**Preconditions**:
- `bytes` ≥ 0 (non-negative)

**Invalid Inputs**:
- Negative values → raise `ValueError`

### Output Contract

**Type**: `str`

**Format Rules**:
- MB format: `"{value:.1f}MB"` (exactly 1 decimal place)
- KB format: `"{value:.0f}KB"` (no decimal places)
- Bytes format: `"{value}B"` (integer)
- Threshold for MB: ≥ 1,000,000 bytes
- Threshold for KB: ≥ 1,000 bytes

**Examples**:
```python
_format_size(0) → "0B"
_format_size(999) → "999B"
_format_size(1_000) → "1KB"
_format_size(1_500) → "2KB"  # Rounded
_format_size(999_999) → "1000KB"
_format_size(1_000_000) → "1.0MB"
_format_size(5_242_880) → "5.2MB"
```

---

## Method: `generate_thumbnail` (Enhanced)

### Signature Changes

**Existing signature** (unchanged):
```python
def generate_thumbnail(
    self,
    source_path: Path,
    metadata: Optional[ImageMetadata] = None
) -> Optional[ThumbnailImage]:
```

**Behavioral Changes**:

1. **Metadata Stripping** (NEW):
   - After thumbnail resize, before save
   - Calls `_strip_metadata()` on thumbnail
   - Populates `ThumbnailImage.metadata_stripped` field

2. **Progress Logging** (ENHANCED):
   - Logs INFO-level message after successful generation
   - Format: `"✓ {filename} → {source_size} → {thumb_size} ({reduction}% reduction)"`
   - Logs WARNING-level message if metadata stripping fails
   - Format: `"⚠ WARNING: Metadata stripping failed for {filename}: {error}"`

3. **Error Handling** (UNCHANGED):
   - Still returns `None` on fatal thumbnail generation errors
   - Metadata stripping failures do NOT cause `None` return
   - Build continues even if metadata stripping fails

### Enhanced Return Type

**ThumbnailImage additions**:
```python
class ThumbnailImage(BaseModel):
    # ... existing fields ...
    metadata_stripped: bool = True  # NEW
    metadata_strip_warning: Optional[str] = None  # NEW
```

**Postconditions**:

**If metadata stripping succeeds**:
- `metadata_stripped = True`
- `metadata_strip_warning = None`
- Thumbnail files contain no sensitive EXIF tags

**If metadata stripping fails**:
- `metadata_stripped = False`
- `metadata_strip_warning` contains error message
- Thumbnail files may contain original metadata
- WARNING log entry emitted
- Method still returns `ThumbnailImage` (not `None`)

---

## Constants: Metadata Field Definitions

### `SENSITIVE_EXIF_TAGS`

**Type**: `set[int]`

**Contract**:
- Contains all EXIF tag IDs that must be removed
- GPS tags: All tags in range 0x0000-0x001F
- Serial numbers: 0xA431 (BodySerialNumber), 0xA435 (LensSerialNumber)
- Creator info: 0x013B (Artist), 0x8298 (Copyright), 0x9C9D (XPAuthor)
- Software: 0x0131 (Software), 0x000B (ProcessingSoftware)
- Thumbnails: 0x0201, 0x0202, 0x0103

**Guarantees**:
- Disjoint with `SAFE_EXIF_TAGS` (no overlap)
- Comprehensive GPS coverage (all GPS IFD tags included)

### `SAFE_EXIF_TAGS`

**Type**: `set[int]`

**Contract**:
- Contains all EXIF tag IDs that must be preserved
- Orientation: 0x0112 (critical for correct display)
- Color: 0xA001 (ColorSpace)
- Timestamps: 0x9003 (DateTimeOriginal), 0x9004 (DateTimeDigitized)
- Camera info: 0x010F (Make), 0x0110 (Model), 0xA434 (LensModel), 0xA433 (LensMake)
- Exposure: 0x829D (FNumber), 0x829A (ExposureTime), 0x8827 (ISO), 0x920A (FocalLength)

**Guarantees**:
- Disjoint with `SENSITIVE_EXIF_TAGS` (no overlap)
- Orientation always included (0x0112 present)

---

## Error Handling Contract

### Error Classification

**Non-Fatal Errors** (logged, build continues):
- Metadata stripping failure (corrupted EXIF, unsupported format)
- Missing metadata (no EXIF data in source image)

**Fatal Errors** (return `None`, skip image):
- Thumbnail generation failure (corrupt source image, I/O error)
- File read/write errors

### Logging Contract

**INFO Level**:
```python
"✓ {filename} → {source_size} → {thumbnail_size} ({reduction_pct}% reduction)"
```
- Logged after successful thumbnail generation
- Includes metadata stripping success implicitly

**WARNING Level**:
```python
"⚠ WARNING: Metadata stripping failed for {filename}: {error_message}"
```
- Logged when metadata stripping fails
- Distinct format with "⚠ WARNING:" prefix (per FR-022)
- Includes error message for debugging

**DEBUG Level**:
```python
"Skipping {filename} (cached, unchanged)"
```
- Logged for cache hits (existing behavior)

---

## Performance Contract

### Execution Time

- **Metadata stripping**: ≤5ms per image (99th percentile)
- **Thumbnail generation** (total): ≤150ms per image (existing + stripping)
- **Build time impact**: ≤10% increase vs no metadata stripping

### Memory Overhead

- **Metadata structures**: ≤10KB per image
- **Peak memory**: No change from existing implementation (streaming processing)

### Throughput

- **Serial processing**: ≥6 images/second (150ms each)
- **Batch of 500 images**: ≤90 seconds (including all I/O)

---

## Thread Safety

### Safe Operations
- `_strip_metadata()`: Thread-safe (no shared mutable state)
- `_format_size()`: Thread-safe (pure function)
- Reading `SENSITIVE_EXIF_TAGS` / `SAFE_EXIF_TAGS`: Thread-safe (immutable sets)

### Unsafe Operations
- `generate_thumbnail()`: Not thread-safe (modifies `self.cache`)
- Batch generation: Sequential only (existing limitation)

**Note**: Current implementation is single-threaded; thread safety documented for future enhancements.

---

## Backward Compatibility

### API Stability

**No breaking changes**:
- `generate_thumbnail()` signature unchanged
- Return type enhanced (new optional fields default gracefully)
- Existing callers continue to work without modifications

**Cache Compatibility**:
- New `metadata_stripped` field has default value `True`
- Old cache entries without field use default (graceful degradation)
- Cache version bump triggers full rebuild (standard pattern)

---

## Testing Contract

### Unit Test Requirements

**Must verify**:
1. GPS tags removed from output (FR-001)
2. Orientation tag preserved in output (FR-007)
3. Timestamp tags preserved in output (FR-008)
4. Camera/lens tags preserved in output (FR-008a)
5. Serial number tags removed from output (FR-003)
6. Creator tags removed from output (FR-004)
7. Error handling: corrupted EXIF returns failure result
8. No-metadata images handled gracefully (success with 0 removed)

### Integration Test Requirements

**Must verify**:
1. Full build with GPS-tagged images produces clean thumbnails
2. Progress logs appear in real-time during build
3. Metadata stripping failures logged with WARNING prefix
4. Build completes successfully even if some images fail stripping

---

## Example Usage

### Successful Metadata Stripping

```python
# Inside generate_thumbnail()
thumb = self._create_thumbnail(img)

# Strip metadata
strip_result = self._strip_metadata(thumb)

if strip_result.success:
    # Save with clean metadata
    thumb = strip_result.image
    self.logger.debug(
        f"Removed {strip_result.sensitive_fields_removed} sensitive fields, "
        f"preserved {strip_result.safe_fields_preserved} safe fields"
    )
else:
    # Log warning but continue
    self.logger.warning(
        f"⚠ WARNING: Metadata stripping failed for {source_path.name}: "
        f"{strip_result.warning}"
    )
    # Use original thumbnail (with metadata)
    thumb = strip_result.image

# Save thumbnails (WebP + JPEG)
webp_path, jpeg_path = self._save_thumbnails(thumb, source_path, content_hash)

# Build result with metadata status
thumbnail = ThumbnailImage(
    # ... existing fields ...
    metadata_stripped=strip_result.success,
    metadata_strip_warning=strip_result.warning
)
```

### Progress Logging

```python
# After thumbnail generation
source_size_str = self._format_size(metadata.file_size_bytes)
thumb_size_str = self._format_size(thumbnail.webp_size_bytes)
reduction_pct = thumbnail.size_reduction_percent

self.logger.info(
    f"✓ {source_path.name} → {source_size_str} → {thumb_size_str} "
    f"({reduction_pct:.1f}% reduction)"
)
```

---

## Compliance Mapping

**Functional Requirements**:
- FR-001 to FR-008a: Metadata field removal/preservation → `_strip_metadata()`
- FR-009 to FR-012: Progress logging → Enhanced `generate_thumbnail()`
- FR-013: Error identification → Logging with filename
- FR-021: Continue on failure → Error handling in `_strip_metadata()`
- FR-022: Distinct warning format → "⚠ WARNING:" prefix
- FR-023: Include failed images → Return `ThumbnailImage` even on failure
- FR-024: No summary report → Inline warnings only

**Success Criteria**:
- SC-001: GPS data absent → Verified by `SENSITIVE_EXIF_TAGS` coverage
- SC-002: Serial/creator absent → Verified by tag filtering
- SC-003: Correct display → Orientation/color profiles preserved
- SC-005: Progress per image → INFO log after each `generate_thumbnail()`
- SC-006: Filename + reduction → Log format contract
