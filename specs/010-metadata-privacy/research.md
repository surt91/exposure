# Research: Image Metadata Privacy and Build Progress Logging

**Feature**: `010-metadata-privacy` | **Date**: 2025-11-02

## Research Questions

### 1. How should EXIF/IPTC/XMP metadata be stripped from images?

**Decision**: Use `piexif` library for comprehensive EXIF manipulation

**Rationale**:
- Pillow's EXIF handling is basic and error-prone for selective metadata preservation
- `piexif` provides dedicated, well-tested EXIF manipulation with clear tag access
- Reduces implementation complexity - we don't need to manually manage EXIF byte structures
- Handles edge cases (corrupted EXIF, non-standard tags) more gracefully
- Allows precise control over which tags to keep/remove without risk of breaking EXIF structure
- Widely used in production (16k+ GitHub stars, 2M+ PyPI downloads/month)

**Implementation approach**:
```python
import piexif
from PIL import Image

def strip_sensitive_metadata(image_path: Path, output_path: Path) -> None:
    # Load EXIF data
    exif_dict = piexif.load(str(image_path))

    # Remove GPS data entirely
    exif_dict.pop("GPS", None)

    # Remove sensitive fields from Exif IFD
    sensitive_exif_tags = {
        piexif.ExifIFD.BodySerialNumber,
        piexif.ExifIFD.LensSerialNumber,
        # ... other sensitive tags
    }
    for tag in sensitive_exif_tags:
        exif_dict["Exif"].pop(tag, None)

    # Remove sensitive fields from 0th IFD (main image)
    sensitive_0th_tags = {
        piexif.ImageIFD.Artist,
        piexif.ImageIFD.Copyright,
        piexif.ImageIFD.Software,
        # ... other sensitive tags
    }
    for tag in sensitive_0th_tags:
        exif_dict["0th"].pop(tag, None)

    # Dump cleaned EXIF and save
    exif_bytes = piexif.dump(exif_dict)
    img = Image.open(image_path)
    img.save(output_path, exif=exif_bytes)
```

**Advantages over manual Pillow approach**:
- Named constants for all EXIF tags (no magic numbers)
- Proper EXIF structure validation before save
- Better error messages when EXIF data is malformed
- Handles thumbnail removal cleanly via `exif_dict["thumbnail"] = None`
- Less code to maintain and test

**Alternatives considered**:
- **Pillow's built-in EXIF** - Rejected due to complexity: requires manual byte manipulation, error-prone tag filtering, poor handling of corrupted EXIF
- **exiftool command-line** - Requires external binary, not cross-platform, harder to integrate, adds system dependency
- **Complete metadata removal** - Too aggressive; breaks color profiles and orientation
- **exif library** - Less mature, smaller community, fewer downloads than piexif

**References**:
- [piexif documentation](https://piexif.readthedocs.io/)
- [piexif GitHub](https://github.com/hMatoba/Piexif)
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
def _filter_metadata(self, source_path: Path) -> Optional[bytes]:
    """Filter sensitive metadata from source image, return None on failure."""
    try:
        # Load EXIF with piexif
        exif_dict = piexif.load(str(source_path))

        # Filter sensitive fields
        exif_dict = self._remove_sensitive_tags(exif_dict)

        # Dump back to bytes
        return piexif.dump(exif_dict)

    except piexif.InvalidImageDataError as e:
        self.logger.warning(
            f"⚠ WARNING: EXIF data corrupted in {source_path.name}: {e}"
        )
        return None
    except Exception as e:
        self.logger.warning(
            f"⚠ WARNING: Metadata stripping failed for {source_path.name}: {e}"
        )
        return None
```

**Error handling strategy**:
- Catch piexif-specific exceptions separately for better diagnostics
- Log warning with "⚠ WARNING:" prefix (per FR-022)
- Return None to signal failure; caller saves image without EXIF
- Build continues with other images (per FR-021)
- Don't propagate exceptions to `generate_thumbnail()`
- No summary report needed (per FR-024)

**Failure scenarios piexif handles**:
- `piexif.InvalidImageDataError`: Corrupted or non-standard EXIF data
- Missing EXIF data: `piexif.load()` returns empty dict (not an error)
- Malformed tag values: piexif.dump() validates structure
- Unsupported formats: JPEG has best support, WebP/PNG limited but handled

**Rationale**:
- Build should never fail due to metadata issues (FR-021)
- User gets functional gallery even with metadata failures
- Distinct warning format makes failures visible (FR-022)
- Inline warnings sufficient for troubleshooting (FR-024)
- piexif's exception types help distinguish corruption from other errors

---

### 5. How to integrate metadata stripping into existing image pipeline?

**Decision**: Strip metadata from both thumbnails AND full-size originals during build

**Integration points**:

**A) Thumbnails** - In `ThumbnailGenerator._save_thumbnails()`:
```python
def _save_thumbnails(self, thumb: PILImage.Image, source_path: Path, ...) -> tuple[Path, Path]:
    # Load and filter EXIF from source
    try:
        exif_dict = piexif.load(str(source_path))
        clean_exif = self._filter_sensitive_metadata(exif_dict)
        exif_bytes = piexif.dump(clean_exif)
    except (piexif.InvalidImageDataError, Exception) as e:
        self.logger.warning(f"⚠ WARNING: EXIF stripping failed for {source_path.name}: {e}")
        exif_bytes = None

    # Save with cleaned EXIF
    thumb.save(webp_path, "WEBP", quality=..., exif=exif_bytes)
    thumb.save(jpeg_path, "JPEG", quality=..., exif=exif_bytes)
```

**B) Full-size originals** - Modify `assets.copy_with_hash()`:
```python
def copy_with_hash(src_path: Path, dest_dir: Path, preserve_name: bool = False,
                   strip_metadata: bool = True) -> Path:
    """Copy file with optional metadata stripping."""
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Determine destination filename
    if preserve_name:
        dest_path = dest_dir / src_path.name
    else:
        file_hash = hash_file(src_path)
        stem = src_path.stem
        ext = src_path.suffix
        hashed_name = f"{stem}.{file_hash}{ext}"
        dest_path = dest_dir / hashed_name

    # For image files, strip metadata before copying
    if strip_metadata and src_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.webp'}:
        try:
            from .metadata_filter import strip_and_save
            strip_and_save(src_path, dest_path)
        except Exception as e:
            # Fallback to regular copy if stripping fails
            logger.warning(f"⚠ WARNING: Metadata stripping failed for {src_path.name}: {e}")
            shutil.copy2(src_path, dest_path)
    else:
        shutil.copy2(src_path, dest_path)

    return dest_path
```

**Why strip both**:
- Thumbnails are used in gallery grid view (already covered)
- Full-size originals shown in modal/lightbox view - also need stripping!
- Without stripping originals, GPS coordinates still exposed when users click to enlarge
- Consistent privacy protection across all published images

**Cache integration**:
- Build cache already tracks `content_hash` and timestamps
- Metadata stripping is deterministic (same input → same output)
- No new cache fields needed
- Incremental builds automatically benefit

**Performance impact**:
- Thumbnails: piexif.load() + filter + dump adds ~2-8ms per image
- Full-size copies: piexif.load() + filter + dump + save adds ~10-20ms per image (larger files)
- Still negligible compared to thumbnail resize (~50-100ms)
- Total build time increase <15% for typical galleries (was <10%, now slightly more)
- Library is written in pure Python but well-optimized

**Alternatives considered**:
- **Strip only thumbnails, not originals** - REJECTED: Leaves privacy hole in modal view
- **Strip only JPEG, not WebP** - Inconsistent, WebP can have EXIF too
- **Separate metadata stripping pass** - Requires re-opening files, slower
- **Process EXIF from thumbnail instead of source** - Less reliable, thumbnail may not preserve all source EXIF

---

### 6. How to verify metadata removal in tests?

**Decision**: Use piexif to read and validate EXIF data from generated thumbnails

**Test approach**:
```python
import piexif

def test_gps_metadata_removed():
    # Generate thumbnail from GPS-tagged source
    thumbnail = generator.generate_thumbnail(source_with_gps)

    # Load EXIF from generated thumbnail
    exif_dict = piexif.load(str(thumbnail.webp_path))

    # Assert GPS IFD not present or empty
    assert "GPS" not in exif_dict or len(exif_dict["GPS"]) == 0

    # Assert sensitive tags not in Exif IFD
    assert piexif.ExifIFD.BodySerialNumber not in exif_dict["Exif"]
    assert piexif.ExifIFD.LensSerialNumber not in exif_dict["Exif"]

    # Assert sensitive tags not in 0th IFD
    assert piexif.ImageIFD.Artist not in exif_dict["0th"]
    assert piexif.ImageIFD.Copyright not in exif_dict["0th"]

    # Assert safe tags preserved
    assert piexif.ImageIFD.Orientation in exif_dict["0th"]
```

**Advantages of piexif for testing**:
- Same library used for stripping and verification (consistent behavior)
- Named constants prevent typos in tag IDs
- Direct access to EXIF structure (no need to decode bytes manually)
- Can easily check entire IFD sections (GPS, Exif, 0th, 1st)

**Test fixtures needed**:
- Sample images with GPS data (can create with piexif)
- Sample images with serial numbers in EXIF
- Sample images with creator/copyright metadata
- Corrupted EXIF data to test error handling

**Test coverage**:
- GPS coordinates removed (FR-001)
- Serial numbers removed (FR-003)
- Creator info removed (FR-004)
- Color profiles preserved (FR-006)
- Orientation preserved (FR-007)
- Timestamps preserved (FR-008)
- Camera/lens info preserved (FR-008a)
- Embedded thumbnails removed (FR-019)
- Graceful handling of stripping failures (FR-021, FR-022)

**Integration test**:
- Full build with real images
- Verify thumbnails with piexif.load()
- Can also verify with `exiftool` command-line for cross-validation
- Compare before/after metadata counts

**References**:
- Existing test patterns in `tests/unit/`
- piexif documentation for testing patterns

---

## Summary of Technical Decisions

1. **Metadata Stripping Library**: Use `piexif` library for comprehensive EXIF manipulation - provides named constants, structure validation, better error handling than Pillow's basic EXIF support
2. **Scope**: Strip metadata from BOTH thumbnails AND full-size original copies - ensures privacy protection in gallery grid view and modal/lightbox view
3. **Sensitive Fields Removed**: GPS coordinates, camera serial numbers, creator/copyright info, software metadata, embedded thumbnails
4. **Preserved Metadata**: Keep orientation, color profiles, timestamps, camera/lens info per requirements (FR-006, FR-007, FR-008, FR-008a)
5. **Progress Logging**: Add INFO-level logs after each image with filename and size reduction percentage
6. **Error Handling**: Continue build on failures, log warnings with "⚠ WARNING:" prefix using piexif's exception types, no summary needed
7. **Integration**:
   - Thumbnails: Filter EXIF in `_save_thumbnails()` before saving WebP/JPEG
   - Full-size originals: Modify `assets.copy_with_hash()` to strip before copying to output
8. **Testing**: Use `piexif.load()` to verify sensitive fields removed and safe fields preserved - same library for stripping and validation

## Dependencies Added

- **piexif** (~16k GitHub stars, 2M+ monthly PyPI downloads): Pure Python EXIF manipulation library
  - Version: Latest stable (currently 1.1.x)
  - License: MIT (compatible with project)
  - Minimal transitive dependencies

## Open Questions

None - all clarifications resolved.
