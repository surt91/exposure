# Research: Image Metadata Privacy and Build Progress Logging

**Feature**: `010-metadata-privacy` | **Date**: 2025-11-02

## Research Questions

### 1. How does Pillow handle EXIF/IPTC/XMP metadata stripping?

**Decision**: Use Pillow's selective metadata preservation via `img.save()` parameters

**Rationale**:
- Pillow provides fine-grained control over metadata retention during image save operations
- For JPEG: `exif` parameter in `save()` allows passing filtered EXIF data
- For PNG: Metadata stored in `info` dict can be selectively copied
- WebP: Limited metadata support, making stripping simpler

**Implementation approach**:
```python
# Extract EXIF data
exif = img.getexif()

# Create filtered EXIF with only safe fields
safe_exif = Image.Exif()
for tag_id in SAFE_EXIF_TAGS:
    if tag_id in exif:
        safe_exif[tag_id] = exif[tag_id]

# Save with filtered metadata
img.save(path, "JPEG", exif=safe_exif.tobytes())
```

**Alternatives considered**:
- **piexif library** - More powerful EXIF manipulation but adds dependency; overkill for our needs
- **exiftool command-line** - Requires external binary, not cross-platform, harder to integrate
- **Complete metadata removal** - Too aggressive; breaks color profiles and orientation

**References**:
- [Pillow EXIF documentation](https://pillow.readthedocs.io/en/stable/reference/ExifTags.html)
- [EXIF tag reference](https://exiv2.org/tags.html)

---

### 2. Which EXIF/IPTC/XMP fields must be removed for privacy?

**Decision**: Remove GPS, serial numbers, creator info, software details; preserve display-critical fields

**Sensitive fields to REMOVE**:
- **EXIF GPS tags** (0x0000-0x001F GPS IFD): GPSLatitude, GPSLongitude, GPSAltitude, GPSTimeStamp, etc.
- **Camera serial numbers**: BodySerialNumber (0xA431), LensSerialNumber (0xA435), InternalSerialNumber
- **Creator/copyright**: Artist (0x013B), Copyright (0x8298), XPAuthor (0x9C9D)
- **Software metadata**: Software (0x0131), ProcessingSoftware (0x000B), CreatorTool
- **Editing history**: XMP History, Photoshop metadata, ImageHistory
- **Embedded thumbnails**: ThumbnailImage (0x0201), JPEGInterchangeFormat (0x0201)
- **Location names**: LocationName, City, Country (IPTC fields)

**Safe fields to PRESERVE**:
- **Display-critical**: Orientation (0x0112), ColorSpace (0xA001), ICC Profile
- **Image properties**: Width, Height, BitDepth, SamplesPerPixel
- **Timestamps**: DateTimeOriginal (0x9003), DateTimeDigitized (0x9004) - useful for display sorting
- **Camera/lens info**: Make (0x010F), Model (0x0110), LensModel (0xA434), LensMake (0xA433)
- **Exposure data**: FNumber, ExposureTime, ISO, FocalLength (useful for photographers, non-identifying)

**Rationale**:
- GPS coordinates reveal exact shooting locations (privacy risk)
- Serial numbers enable camera/lens tracking (stolen equipment databases)
- Creator names and copyright info contain personal information
- Software metadata reveals workflow and licenses
- Timestamps are benign (no location data) and aid photo organization
- Camera/lens info requested by user for display purposes (FR-008a)

**IPTC/XMP considerations**:
- Pillow has limited IPTC/XMP support
- These are typically stored in APP13 (IPTC) and APP1 (XMP) JPEG markers
- Simplest approach: strip all APP markers except APP0 (JFIF), APP1 (EXIF), APP2 (ICC)
- For WebP: Metadata support is minimal, stripping easier

**References**:
- [EXIF privacy guide](https://www.eff.org/deeplinks/2020/02/your-photos-are-watching-you)
- [IPTC photo metadata standard](https://www.iptc.org/standards/photo-metadata/)

---

### 3. How to implement real-time progress logging during batch processing?

**Decision**: Add per-image logging after each thumbnail generation with filename and size reduction

**Implementation approach**:
```python
def generate_thumbnail(self, source_path: Path) -> Optional[ThumbnailImage]:
    # ... existing thumbnail generation ...

    # Calculate reduction
    reduction_pct = (
        (metadata.file_size_bytes - thumbnail.webp_size_bytes)
        / metadata.file_size_bytes * 100
    )

    # Log progress immediately
    self.logger.info(
        f"✓ {source_path.name} → "
        f"{self._format_size(metadata.file_size_bytes)} → "
        f"{self._format_size(thumbnail.webp_size_bytes)} "
        f"({reduction_pct:.1f}% reduction)"
    )
```

**Logging levels**:
- `INFO`: Successful processing with size reduction
- `WARNING`: Metadata stripping failures (use "⚠ WARNING:" prefix per FR-022)
- `DEBUG`: Cache hits, detailed metrics

**Format considerations**:
- Use Unicode symbols (✓, ⚠) for visual distinction
- Human-readable sizes (5.2MB not 5242880 bytes)
- Fixed precision percentages (92.3% not 92.34567%)
- Include arrow (→) for before/after clarity

**Alternatives considered**:
- **Progress bars** (tqdm) - Too heavy for simple logging, harder to test
- **Batched logging** - Rejected per FR-012 (must be real-time)
- **Separate log files** - Adds complexity, users expect console output

**References**:
- Python `logging` module standard library
- Existing `ThumbnailGenerator` logging patterns

---

### 4. How to handle metadata stripping failures gracefully?

**Decision**: Continue build on failures, log warnings with distinct format, include image in output

**Implementation approach**:
```python
def _strip_metadata(self, img: PILImage.Image) -> PILImage.Image:
    try:
        # Attempt metadata filtering
        exif = img.getexif()
        safe_exif = self._filter_sensitive_exif(exif)
        # ... apply safe_exif ...
        return img
    except Exception as e:
        self.logger.warning(
            f"⚠ WARNING: Metadata stripping failed for {img.filename}: {e}"
        )
        # Return image unchanged
        return img
```

**Error handling strategy**:
- Wrap metadata operations in try/except
- Log warning with "⚠ WARNING:" prefix (per FR-022)
- Return unmodified image to allow build to continue (per FR-021)
- Don't propagate exceptions to `generate_thumbnail()`
- No summary report needed (per FR-024)

**Failure scenarios**:
- Corrupted EXIF data
- Unsupported metadata format
- Pillow version incompatibilities
- Memory errors during metadata manipulation

**Rationale**:
- Build should never fail due to metadata issues (FR-021)
- User gets functional gallery even with metadata failures
- Distinct warning format makes failures visible (FR-022)
- Inline warnings sufficient for troubleshooting (FR-024)

---

### 5. How to integrate metadata stripping into existing thumbnail pipeline?

**Decision**: Add metadata stripping step after thumbnail creation, before save

**Integration point**:
```python
def _save_thumbnails(self, thumb: PILImage.Image, ...) -> tuple[Path, Path]:
    # NEW: Strip metadata before saving
    thumb = self._strip_metadata(thumb)

    # Existing save logic
    thumb.save(webp_path, "WEBP", quality=...)
    thumb.save(jpeg_path, "JPEG", quality=...)
```

**Why this location**:
- After `_create_thumbnail()` ensures metadata from source isn't copied
- Before `save()` ensures both WebP and JPEG get stripped
- Minimal changes to existing flow
- Easy to test in isolation

**Cache integration**:
- Build cache already tracks `content_hash` and timestamps
- Metadata stripping is deterministic (same input → same output)
- No new cache fields needed
- Incremental builds automatically benefit

**Performance impact**:
- Metadata filtering adds ~1-5ms per image
- Negligible compared to thumbnail resize (~50-100ms)
- Total build time increase <10% for typical galleries

**Alternatives considered**:
- **Strip before thumbnail creation** - Unnecessary, wastes processing
- **Strip only JPEG, not WebP** - Inconsistent, WebP can have EXIF too
- **Separate metadata stripping pass** - Requires re-opening files, slower

---

### 6. How to verify metadata removal in tests?

**Decision**: Use Pillow to read metadata from generated thumbnails and assert sensitive fields absent

**Test approach**:
```python
def test_gps_metadata_removed():
    # Generate thumbnail from GPS-tagged source
    thumbnail = generator.generate_thumbnail(source_with_gps)

    # Open generated thumbnail and check EXIF
    with Image.open(thumbnail.webp_path) as img:
        exif = img.getexif()

        # Assert GPS tags not present
        for gps_tag in GPS_TAG_IDS:
            assert gps_tag not in exif

        # Assert safe tags preserved
        assert ORIENTATION_TAG in exif
```

**Test fixtures needed**:
- Sample images with GPS data (can create with PIL)
- Sample images with serial numbers in EXIF
- Sample images with creator/copyright metadata

**Test coverage**:
- GPS coordinates removed (FR-001)
- Serial numbers removed (FR-003)
- Creator info removed (FR-004)
- Color profiles preserved (FR-006)
- Orientation preserved (FR-007)
- Timestamps preserved (FR-008)
- Camera/lens info preserved (FR-008a)

**Integration test**:
- Full build with real images
- Verify thumbnails with `exiftool` command-line
- Compare before/after metadata counts

**References**:
- Existing test patterns in `tests/unit/`
- Pillow's `getexif()` method for reading

---

## Summary of Technical Decisions

1. **Metadata Stripping**: Use Pillow's `save()` with filtered EXIF; remove GPS, serial numbers, creator info, software metadata, embedded thumbnails
2. **Preserved Metadata**: Keep orientation, color profiles, timestamps, camera/lens info per requirements
3. **Progress Logging**: Add INFO-level logs after each image with filename and size reduction percentage
4. **Error Handling**: Continue build on failures, log warnings with "⚠ WARNING:" prefix, no summary needed
5. **Integration**: Strip metadata in `_save_thumbnails()` method before save operations
6. **Testing**: Use Pillow `getexif()` to verify sensitive fields removed and safe fields preserved

## Open Questions

None - all clarifications resolved.
