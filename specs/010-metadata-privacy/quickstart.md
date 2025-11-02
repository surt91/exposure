# Quickstart: Image Metadata Privacy and Build Progress Logging

**Feature**: `010-metadata-privacy` | **Date**: 2025-11-02

## What This Feature Does

When you build your gallery with `exposure`, the build process now:

1. **Strips sensitive metadata** from all published images - both thumbnails (gallery grid) and full-size copies (modal/lightbox view)
2. **Removes privacy-sensitive data** including GPS coordinates, camera serial numbers, personal information, software metadata
3. **Preserves useful metadata** that enhances display (color profiles, orientation, timestamps, camera/lens info)
4. **Shows real-time progress** with size reduction statistics for each image processed

**Your original source images remain unchanged** - only the published copies in the `dist/` directory have metadata removed.

---

## Quick Example

### Before This Feature

```bash
$ uv run exposure
INFO     Starting gallery build...
INFO     Generated 50 thumbnails
INFO     Build complete
```

No visibility into which images were processed or how much space was saved.

### After This Feature

```bash
$ uv run exposure
INFO     Starting gallery build...
INFO     ✓ landscape01.jpg → 5.2MB → 420KB (92.0% reduction)
INFO     ✓ portrait02.jpg → 3.8MB → 380KB (90.0% reduction)
INFO     ✓ sunset03.jpg → 6.1MB → 510KB (91.6% reduction)
⚠ WARNING: Metadata stripping failed for corrupted04.jpg: Invalid EXIF header
INFO     ✓ beach05.jpg → 4.5MB → 405KB (91.0% reduction)
...
INFO     Thumbnails: 48 generated, 0 cached, 1 failed
INFO     Build complete
```

Clear progress with size reduction stats and warnings for problematic images.

---

## What Metadata Is Removed

### Privacy-Sensitive (REMOVED from thumbnails)

- **GPS coordinates** - Exact latitude, longitude, altitude where photo was taken
- **Location names** - City, country, place names embedded in photos
- **Camera serial numbers** - Unique identifiers for your camera and lenses
- **Personal information** - Photographer name, copyright holder, contact details
- **Software metadata** - Photoshop, Lightroom versions and editing history
- **Embedded thumbnails** - Small preview images that may contain GPS data

### Useful Information (PRESERVED in thumbnails)

- **Orientation** - Ensures photos display right-side-up
- **Color profiles** - Maintains accurate colors
- **Timestamps** - Date and time photo was taken (useful for sorting)
- **Camera/lens info** - Camera make, model, lens used (helpful for display)
- **Exposure settings** - F-stop, shutter speed, ISO (useful for photographers)

---

## How to Use

### Default Behavior (Automatic)

**No configuration needed** - metadata privacy is enabled by default:

```bash
# Just run the build command as usual
uv run exposure
```

Thumbnails are automatically stripped of sensitive metadata during generation.

### Verify Metadata Removal

After building your gallery, verify metadata removal with `exiftool`:

```bash
# Install exiftool (if not already installed)
# macOS: brew install exiftool
# Ubuntu/Debian: apt install libimage-exiftool-perl
# Windows: Download from https://exiftool.org/

# Check a source image (has GPS data)
exiftool content/landscape01.jpg | grep GPS
# Output: GPSLatitude, GPSLongitude, GPSAltitude, etc.

# Check generated thumbnail (no GPS data)
exiftool dist/thumbnails/landscape01-abc123.webp | grep GPS
# Output: (empty - GPS data removed)
```

### Check Progress Logs

Progress logs show each image processed with size reduction:

```bash
# Run build and see progress
uv run exposure

# Save logs to file
uv run exposure 2>&1 | tee build.log

# Filter for warnings only
uv run exposure 2>&1 | grep WARNING
```

---

## Understanding Progress Messages

### Success Format

```
✓ filename.jpg → source_size → thumbnail_size (reduction_percentage% reduction)
```

**Example**:
```
INFO     ✓ sunset.jpg → 5.2MB → 420KB (92.0% reduction)
```

**Components**:
- `✓` - Success indicator
- `filename.jpg` - Source image filename
- `5.2MB` - Original file size
- `420KB` - Thumbnail size (WebP format)
- `92.0%` - File size reduction achieved

### Warning Format

```
⚠ WARNING: Metadata stripping failed for filename.jpg: error_message
```

**Example**:
```
⚠ WARNING: Metadata stripping failed for corrupted.jpg: Invalid EXIF header
```

**What this means**:
- Thumbnail was generated successfully
- Metadata stripping encountered an error
- Thumbnail may contain original metadata (not stripped)
- Build continues normally (image included in gallery)

**Common causes**:
- Corrupted EXIF data in source image
- Unsupported metadata format
- File format edge cases

### Cache Hit Format (Debug Level)

```
DEBUG    Skipping filename.jpg (cached, unchanged)
```

**What this means**:
- Image hasn't changed since last build
- Using cached thumbnail (skipping regeneration)
- Metadata was already stripped in previous build

---

## Configuration

### Thumbnail Settings

Control thumbnail quality and size in `config/settings.yaml`:

```yaml
thumbnail_config:
  max_dimension: 800      # Max width/height in pixels
  webp_quality: 85        # WebP quality (1-100)
  jpeg_quality: 90        # JPEG fallback quality (1-100)
  enable_cache: true      # Skip unchanged images
```

### Logging Verbosity

Control log detail level:

```yaml
# config/settings.yaml
log_level: INFO  # Options: DEBUG, INFO, WARNING, ERROR
```

**Log levels**:
- `DEBUG` - Show cache hits and detailed metrics
- `INFO` - Show progress for each image (default)
- `WARNING` - Show only warnings and errors
- `ERROR` - Show only errors

**Examples**:

```bash
# Verbose logging (includes cache hits)
EXPOSURE_LOG_LEVEL=DEBUG uv run exposure

# Quiet logging (warnings/errors only)
EXPOSURE_LOG_LEVEL=WARNING uv run exposure
```

---

## Troubleshooting

### "Metadata stripping failed" Warnings

**Problem**: You see warnings like:
```
⚠ WARNING: Metadata stripping failed for photo.jpg: Invalid EXIF header
```

**Solution**:
1. Image is still included in gallery (build continues)
2. Try re-exporting image from photo editing software
3. If persistent, image may have corrupted metadata (not critical)

**Note**: Warnings don't prevent gallery from working. Original source images remain unchanged, so you can always re-export and rebuild.

### No GPS Data to Remove

**Problem**: Progress shows images processed, but source images had no GPS data anyway.

**Solution**: This is normal. Metadata stripping is defensive - it removes GPS data if present, but works fine on images without it. No action needed.

### Orientation Issues

**Problem**: Some photos appear rotated incorrectly in gallery.

**Solution**: Orientation metadata is preserved by default. If rotation is wrong:
1. Check source image orientation in photo viewer
2. Rotate source image correctly before building
3. Rebuild gallery with `uv run exposure`

### Checking What Metadata Remains

**Problem**: Want to verify what metadata is in thumbnails.

**Solution**: Use `exiftool` to inspect:

```bash
# View all metadata in thumbnail
exiftool dist/thumbnails/photo-abc123.webp

# Check for specific tags
exiftool dist/thumbnails/photo-abc123.webp | grep -E "(GPS|Serial|Artist|Copyright)"

# Compare source vs thumbnail metadata
exiftool content/photo.jpg > source.txt
exiftool dist/thumbnails/photo-abc123.webp > thumb.txt
diff source.txt thumb.txt
```

---

## Privacy FAQ

### Q: Are my original photos modified?

**A**: No. Original files in `content/` remain completely unchanged with all metadata intact. Only generated thumbnails (in `dist/thumbnails/`) have metadata removed.

### Q: Can visitors still see my location?

**A**: Not from the thumbnails. GPS coordinates are removed from all published images. However, visitors can still see:
- Location names you manually added in `gallery.yaml` (if you added them)
- General location inferred from photo content (landscapes, landmarks)

### Q: What about the full-size images in modal view?

**A**: Full-size modal images shown in the lightbox are also automatically stripped of sensitive metadata during the build process. Both thumbnails (gallery grid) and full-size copies (modal view) have privacy protection applied.

Your original source files in `content/` remain unchanged with all metadata intact for your personal records.

### Q: Is timestamp removal a privacy concern?

**A**: Timestamps (date/time) are preserved because:
- They don't reveal location (only when, not where)
- Useful for chronological sorting and display
- Commonly expected in photo galleries

If you want to remove timestamps too, you would need to customize the `SAFE_EXIF_TAGS` set in the code (advanced).

### Q: What if I want to share my location?

**A**: Add location information manually in `gallery.yaml`:

```yaml
images:
  - filename: sunset.jpg
    title: "Sunset at Golden Gate Bridge"
    description: "San Francisco, California"
```

This gives you control over what location info is shared (city-level rather than exact GPS coordinates).

---

## Performance

### Build Time Impact

Metadata stripping adds minimal overhead:

- **Per thumbnail**: ~2-8ms for metadata processing (negligible compared to 50-100ms resize)
- **Per full-size copy**: ~10-20ms for metadata processing (varies with file size)
- **Total build**: <15% increase for typical galleries
- **500 images**: ~3-6 seconds additional time

### Incremental Builds

Build cache tracks metadata stripping state:

- **Unchanged images**: Skipped completely (cache hit)
- **Changed images**: Regenerated with fresh metadata stripping
- **First build after upgrade**: All images rebuilt once

**Example**:
```bash
# First build after feature enabled (all images regenerated)
uv run exposure
# Output: "50 generated, 0 cached, 0 failed"

# Second build with no changes (all cached)
uv run exposure
# Output: "0 generated, 50 cached, 0 failed"

# Edit one image, rebuild (only one regenerated)
cp new_photo.jpg content/photo01.jpg
uv run exposure
# Output: "1 generated, 49 cached, 0 failed"
```

---

## What's Next

This feature enhances the thumbnail generation pipeline with privacy protections and progress visibility. Future enhancements might include:

- Configuration to customize which metadata fields to remove/preserve
- Summary report at end of build showing total space saved
- Option to strip metadata from full-size modal images too

For now, enjoy automatic privacy protection with clear progress feedback!

---

## Technical Details

For developers wanting to understand or extend this feature:

- **Implementation**: See `src/generator/thumbnails.py` - `_strip_metadata()` method
- **Metadata fields**: See `src/generator/constants.py` - `SENSITIVE_EXIF_TAGS`, `SAFE_EXIF_TAGS`
- **Data model**: See `specs/010-metadata-privacy/data-model.md`
- **API contract**: See `specs/010-metadata-privacy/contracts/metadata-stripping-api.md`
- **Testing**: See `tests/unit/test_metadata_stripping.py` and `tests/integration/test_thumbnail_privacy.py`
