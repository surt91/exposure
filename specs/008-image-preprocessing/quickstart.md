# Quickstart: Image Preprocessing with Thumbnails

**Feature**: `008-image-preprocessing`
**Version**: 1.0.0
**Status**: Draft

## Overview

This guide helps you enable and use the image preprocessing feature to generate optimized WebP thumbnails for your gallery. Thumbnails dramatically improve page load times while preserving full-resolution images for detailed viewing.

**Benefits**:
- ⚡ 85%+ reduction in bandwidth for gallery pages
- 🚀 3-second load time for galleries with 50+ images
- 📱 Improved mobile experience with smaller file sizes
- 🔄 Incremental builds: only regenerate changed images

---

## Quick Enable

Enable thumbnails with default settings (recommended for most users):

### 1. Update Configuration

Edit `config/settings.yaml`:

```yaml
# Add this line
enable_thumbnails: true
```

### 2. Build Gallery

```bash
uv run exposure
```

That's it! Thumbnails will be generated automatically during the build.

---

## What Happens During Build

When you run `uv run exposure` with thumbnails enabled:

1. **Scans** source images in your `content_dir`
2. **Checks cache** to skip unchanged images (fast incremental builds)
3. **Generates** two thumbnails per image:
   - `.webp` format (25-35% smaller than JPEG)
   - `.jpg` fallback (for older browsers)
4. **Updates** HTML to serve thumbnails in gallery view
5. **Preserves** original images for modal/fullscreen view

**Example output**:
```
INFO: Scanning images in content/
INFO: Found 50 images across 3 categories
INFO: Generating thumbnails...
INFO: Thumbnails: 5 generated, 45 cached, 0 failed
INFO: Gallery built successfully → build/index.html
```

---

## Verify Thumbnails

Check that thumbnails were generated:

```bash
# List generated thumbnails
ls -lh build/images/thumbnails/

# Example output:
# photo1-a1b2c3d4.webp  45K
# photo1-a1b2c3d4.jpg   65K
# photo2-e5f6g7h8.webp  52K
# photo2-e5f6g7h8.jpg   78K
```

Open `build/index.html` in a browser:
- Gallery grid should load quickly with thumbnails
- Click any image to see full-resolution original in modal

---

## Customization

### Change Thumbnail Size

For larger/smaller thumbnails, edit `config/settings.yaml`:

```yaml
enable_thumbnails: true

thumbnail_config:
  max_dimension: 1200  # Default: 800
```

**Common sizes**:
- `600`: Smaller thumbnails, faster loading, more compression
- `800`: **Default** - balanced quality and performance
- `1200`: Larger thumbnails, best for high-res displays

### Adjust Compression Quality

Trade off file size vs visual quality:

```yaml
thumbnail_config:
  webp_quality: 80  # Default: 85 (lower = smaller files, slightly lower quality)
  jpeg_quality: 85  # Default: 90 (for fallback images)
```

**Quality guidelines**:
- `75-80`: Aggressive compression, smaller files, minor artifacts
- `85-90`: **Recommended** - visually lossless at display sizes
- `95-100`: Minimal compression, larger files, marginal quality gain

### Custom Output Directory

```yaml
thumbnail_config:
  output_dir: dist/thumbnails  # Default: build/images/thumbnails
```

### Disable Caching (Force Regenerate All)

```yaml
thumbnail_config:
  enable_cache: false  # Default: true
```

Or via command line:
```bash
# Delete cache to force regeneration
rm build/.build-cache.json
uv run exposure
```

---

## Environment Variables

Override configuration without editing files:

```bash
# Enable thumbnails
export EXPOSURE_ENABLE_THUMBNAILS=true

# Custom size
export EXPOSURE_THUMBNAIL_CONFIG__MAX_DIMENSION=1200

# Custom quality
export EXPOSURE_THUMBNAIL_CONFIG__WEBP_QUALITY=80

# Build with overrides
uv run exposure
```

---

## Common Workflows

### Initial Setup (First Build)

```bash
# 1. Enable in config
echo "enable_thumbnails: true" >> config/settings.yaml

# 2. Build (generates all thumbnails)
uv run exposure

# 3. Check build time
# Expect: ~1-2 minutes for 100 images
```

### Regular Development (Incremental Builds)

```bash
# 1. Add/modify images in content/
cp new-photo.jpg content/

# 2. Build (only regenerates new/changed images)
uv run exposure

# 3. Check output
# Expect: ~5-10 seconds if only few images changed
```

### Testing Different Sizes

```bash
# Build with 600px thumbnails
EXPOSURE_THUMBNAIL_CONFIG__MAX_DIMENSION=600 uv run exposure

# Build with 1200px thumbnails
EXPOSURE_THUMBNAIL_CONFIG__MAX_DIMENSION=1200 uv run exposure

# Compare file sizes
du -sh build/images/thumbnails/
```

---

## Performance Benchmarks

Expected results with default settings (800px, quality 85/90):

| Metric | Before Thumbnails | With Thumbnails | Improvement |
|--------|------------------|-----------------|-------------|
| Gallery page size | 125 MB (50 images) | 15 MB | 88% smaller |
| Initial page load | 45s @ 10 Mbps | 3s @ 10 Mbps | 93% faster |
| Thumbnail file size | N/A (full-res) | 45-65 KB avg | 98% per image |
| Build time (100 images) | 5s | 2m (first), 10s (incremental) | Acceptable |

---

## Troubleshooting

### Problem: Thumbnails not generated

**Check 1**: Verify `enable_thumbnails` is `true`
```bash
grep enable_thumbnails config/settings.yaml
```

**Check 2**: Look for errors in build output
```bash
uv run exposure 2>&1 | grep -i error
```

**Check 3**: Verify Pillow is installed
```bash
uv run python -c "from PIL import Image; print('Pillow OK')"
```

---

### Problem: Build is slow

**Check 1**: Is caching enabled?
```bash
grep enable_cache config/settings.yaml
# Should show: enable_cache: true (or omitted for default)
```

**Check 2**: Does cache file exist?
```bash
ls -lh build/.build-cache.json
```

**Solution**: Ensure cache not deleted between builds

---

### Problem: Thumbnails look blurry

**Solution 1**: Increase thumbnail size
```yaml
thumbnail_config:
  max_dimension: 1200  # Was 800
```

**Solution 2**: Increase quality
```yaml
thumbnail_config:
  webp_quality: 95  # Was 85
  jpeg_quality: 95  # Was 90
```

---

### Problem: Thumbnails too large

**Solution 1**: Decrease size
```yaml
thumbnail_config:
  max_dimension: 600  # Was 800
```

**Solution 2**: More compression
```yaml
thumbnail_config:
  webp_quality: 75  # Was 85
  jpeg_quality: 80  # Was 90
```

---

### Problem: Some images fail to process

**Check build log for warnings**:
```
WARNING: Failed to process IMG_1234.jpg: cannot identify image file
```

**Common causes**:
- Corrupt image file → Re-export from original source
- Unsupported format → Convert to JPEG/PNG/WebP
- File permissions → Ensure images readable

**Build continues with other images** - fix problematic files and rebuild.

---

## Advanced Usage

### Disable Thumbnails for Specific Build

```bash
# One-time build without thumbnails (ignore config)
EXPOSURE_ENABLE_THUMBNAILS=false uv run exposure
```

### Check Thumbnail Metrics

```bash
# Count generated thumbnails
ls build/images/thumbnails/*.webp | wc -l

# Total size of thumbnails
du -sh build/images/thumbnails/

# Average file size
du -b build/images/thumbnails/*.webp | awk '{sum+=$1; n++} END {print sum/n/1024 " KB"}'
```

### Clean Thumbnails and Rebuild

```bash
# Remove all generated files
rm -rf build/images/thumbnails/
rm build/.build-cache.json

# Full rebuild
uv run exposure
```

---

## Testing Your Configuration

### Validate Settings

```bash
# Test configuration loads correctly
uv run python -c "
from src.generator.model import GalleryConfig
config = GalleryConfig()
print(f'Thumbnails enabled: {config.enable_thumbnails}')
print(f'Max dimension: {config.thumbnail_config.max_dimension}')
print(f'WebP quality: {config.thumbnail_config.webp_quality}')
"
```

### Verify Output Quality

1. Build with current settings
2. Open gallery in browser
3. Inspect thumbnails visually (should be sharp, no artifacts)
4. Check DevTools Network tab (should load quickly)
5. Open modal view (should show full-resolution original)

---

## Next Steps

### Production Deployment

1. **Build locally**:
   ```bash
   uv run exposure
   ```

2. **Deploy `build/` directory** to your static host:
   ```bash
   # GitHub Pages
   git add build/
   git commit -m "Update gallery with thumbnails"
   git push

   # Or Netlify
   netlify deploy --prod --dir build/
   ```

3. **Verify in production**:
   - Check page load speed (should be <3s)
   - Verify WebP served in modern browsers
   - Verify JPEG fallback in older browsers (Safari <14)

### CI/CD Integration

Add to your build pipeline:

```yaml
# .github/workflows/build.yml
- name: Generate Gallery
  run: |
    uv run exposure

- name: Verify Thumbnails
  run: |
    test -d build/images/thumbnails
    test $(ls build/images/thumbnails/*.webp | wc -l) -gt 0
```

---

## Configuration Reference

### Minimal Configuration

```yaml
# config/settings.yaml
enable_thumbnails: true
```

Uses all defaults:
- Max dimension: 800px
- WebP quality: 85
- JPEG quality: 90
- Output: `build/images/thumbnails/`
- Caching: Enabled

### Full Configuration

```yaml
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

---

## Getting Help

- **Issue**: Thumbnails not working? Check [Troubleshooting](#troubleshooting) section
- **Question**: How to optimize for mobile? See [Customization](#customization)
- **Bug**: Found a problem? Check build logs for error messages
- **Performance**: Build too slow? Ensure [caching enabled](#problem-build-is-slow)

---

## Summary

**To enable thumbnails**:
1. Add `enable_thumbnails: true` to `config/settings.yaml`
2. Run `uv run exposure`
3. Deploy the `build/` directory

**Key benefits**:
- 85%+ smaller gallery pages
- 3-second load time (vs 45s without thumbnails)
- Original quality preserved in modal view
- Incremental builds save time

**Default settings work great** - only customize if you have specific needs!
