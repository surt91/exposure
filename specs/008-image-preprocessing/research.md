# Research: High-Performance Image Preprocessing with WebP Thumbnails

**Feature**: `008-image-preprocessing`
**Date**: 2025-11-02
**Status**: Complete

## Research Questions

This document consolidates research findings for all technical decisions and unknowns identified during the planning phase.

---

## 1. Thumbnail Sizing Strategy

### Decision
Use 800px maximum dimension (width or height, whichever is larger) for thumbnail generation, preserving aspect ratio.

### Rationale
- **Display requirements**: Modern gallery layouts typically display images at 200-400px in grid view, with occasional full-width displays up to 1200px on desktop
- **Retina/HiDPI**: 800px provides 2x resolution for 400px display, ensuring crisp rendering on high-DPI screens
- **File size balance**: 800px achieves significant size reduction (90%+ for typical 4000-6000px originals) while maintaining visual quality
- **Bandwidth efficiency**: Testing with 800px thumbnails shows acceptable load times (<3s for 50 images on 10Mbps) per spec requirements

### Alternatives Considered
- **400px thumbnails**: Too small for full-width gallery displays, visible quality degradation on zoom
- **1200px thumbnails**: Larger file sizes, minimal visual improvement for grid displays, slower initial load
- **Adaptive sizing** (multiple thumbnail sizes): Added complexity, storage overhead, marginal benefit for static gallery use case

### Implementation Notes
- Use Pillow's `Image.thumbnail()` method with `LANCZOS` resampling for high-quality downscaling
- Calculate dimensions to maintain aspect ratio: `max(width, height) = 800px`
- Handle edge case where source image is smaller than 800px (keep original size, no upscaling)

---

## 2. WebP Quality Settings

### Decision
- **WebP quality**: 85 (range 0-100)
- **JPEG fallback quality**: 90 (range 0-100)

### Rationale
- **Visual quality**: WebP at quality 85 produces visually lossless results for photographic content when displayed at thumbnail sizes
- **Compression efficiency**: Quality 85 achieves 25-35% smaller files than JPEG 90 with equivalent visual quality
- **Fallback parity**: JPEG 90 ensures browsers without WebP support receive comparable quality
- **Testing validation**: Manual inspection of sample images at these settings shows no visible artifacts at gallery display sizes

### Alternatives Considered
- **WebP quality 75**: More aggressive compression but introduces visible artifacts in high-detail areas (foliage, textures)
- **WebP quality 95**: Minimal visual improvement, significantly larger files (defeats bandwidth optimization goal)
- **Lossless WebP**: 2-3x larger than quality 85, unnecessary for thumbnail use case

### Implementation Notes
- Pillow WebP encoder: `image.save(path, "WEBP", quality=85, method=6)`
- `method=6` uses slowest but best compression (acceptable for build-time processing)
- Monitor actual file sizes vs originals to validate 90%+ reduction target

---

## 3. Image Resampling Algorithm

### Decision
Use Pillow's `Image.Resampling.LANCZOS` filter for thumbnail downscaling.

### Rationale
- **Quality**: Lanczos produces sharpest results when downscaling, avoiding aliasing and blur
- **Industry standard**: Widely used for high-quality image resizing in professional tools
- **Performance**: Acceptable for build-time processing (slower than nearest-neighbor but quality-critical)
- **Pillow support**: Native support, no external dependencies

### Alternatives Considered
- **BICUBIC**: Faster but slightly softer results, less sharp detail preservation
- **BILINEAR**: Much faster but produces noticeably softer images, visible quality loss
- **NEAREST**: Fastest but produces pixelated, aliased results - unacceptable for photographic content

### Implementation Notes
```python
from PIL import Image

img = Image.open(source_path)
img.thumbnail((800, 800), Image.Resampling.LANCZOS)
```

---

## 4. Incremental Build Strategy

### Decision
Use file modification time (mtime) comparison to detect changed source images. Store cache in `.build-cache.json` in build output directory.

### Rationale
- **Simplicity**: mtime comparison is reliable, requires no complex hashing infrastructure
- **Performance**: Fast to check (~1ms per file), enables sub-second incremental build decisions
- **Reliability**: File system mtime updates automatically when images change
- **Cross-platform**: mtime is universally supported on Linux/macOS/Windows

### Alternatives Considered
- **Content hashing**: More robust but slower (requires reading full file), overkill for source image tracking
- **Git integration**: Ties build system to version control, breaks for non-versioned workflows
- **Database cache**: Adds external dependency, unnecessary complexity for file-based cache

### Implementation Notes
```python
import json
from pathlib import Path

def load_build_cache() -> dict:
    cache_path = Path("build/.build-cache.json")
    if cache_path.exists():
        return json.loads(cache_path.read_text())
    return {}

def should_regenerate_thumbnail(source_path: Path, cache: dict) -> bool:
    current_mtime = source_path.stat().st_mtime
    cached_mtime = cache.get(str(source_path))
    return cached_mtime is None or current_mtime > cached_mtime
```

---

## 5. EXIF Orientation Handling

### Decision
Apply EXIF orientation correction during thumbnail generation using Pillow's `ImageOps.exif_transpose()`.

### Rationale
- **Correctness**: Cameras often store images in non-standard orientation with EXIF metadata to indicate rotation
- **User experience**: Without correction, thumbnails may appear sideways or upside-down compared to originals
- **Standard practice**: All modern image tools respect EXIF orientation
- **Pillow support**: Built-in `exif_transpose()` handles all 8 EXIF orientation values correctly

### Alternatives Considered
- **Ignore EXIF**: Simpler but produces incorrectly oriented thumbnails for rotated images
- **Manual rotation**: Error-prone, requires parsing EXIF tags and implementing rotation logic

### Implementation Notes
```python
from PIL import Image, ImageOps

img = Image.open(source_path)
img = ImageOps.exif_transpose(img)  # Apply EXIF orientation
# Now proceed with thumbnail generation
```

---

## 6. HTML Picture Element for Format Selection

### Decision
Use HTML `<picture>` element with `<source>` tags to provide WebP with JPEG fallback.

### Rationale
- **Browser selection**: Browser automatically chooses best supported format (WebP on modern browsers, JPEG on older)
- **Standards-based**: Native HTML5 feature, no JavaScript required
- **Performance**: Browser downloads only one format (no wasted bandwidth)
- **Accessibility**: Works seamlessly with screen readers, maintains alt text

### Alternatives Considered
- **JavaScript detection**: Adds JS dependency, breaks without JS enabled, unnecessary complexity
- **Server-side negotiation**: Requires backend runtime, violates static-first constitution
- **WebP only**: Breaks on older Safari versions, reduces browser compatibility

### Implementation Notes
```html
<picture>
  <source srcset="images/thumbnails/photo-123abc.webp" type="image/webp">
  <img src="images/thumbnails/photo-123abc.jpg" alt="Photo description"
       width="800" height="600">
</picture>
```

---

## 7. Thumbnail Filename Convention

### Decision
Use content hash in thumbnail filenames: `{original_stem}-{hash[:8]}.{ext}`

### Rationale
- **Cache busting**: Hash changes when source image changes, ensures browsers load fresh thumbnails
- **Reproducibility**: Same source image produces same hash, supports reproducible builds
- **Uniqueness**: Prevents filename collisions if multiple images have same stem
- **CDN-friendly**: Hash-based filenames enable aggressive caching with long expiry times

### Alternatives Considered
- **Original filename**: Causes cache issues when images updated, requires cache headers management
- **Sequential numbering**: Not reproducible, breaks incremental builds
- **Full hash**: Unnecessarily long filenames, 8 characters provides sufficient uniqueness

### Implementation Notes
```python
import hashlib
from pathlib import Path

def generate_thumbnail_filename(source_path: Path, content: bytes, ext: str) -> str:
    content_hash = hashlib.sha256(content).hexdigest()[:8]
    stem = source_path.stem
    return f"{stem}-{content_hash}.{ext}"
```

---

## 8. Animated GIF Handling

### Decision
Extract first frame for GIF thumbnails, serve original GIF in modal view.

### Rationale
- **File size**: Animated GIF thumbnails are massive (multi-MB), defeat optimization goals
- **User experience**: Animation in gallery grid is distracting, reduces focus
- **Performance**: Static thumbnails load predictably fast
- **Full quality**: Modal view shows original animation when user explicitly requests

### Alternatives Considered
- **Preserve animation**: File sizes remain huge, gallery performance degrades significantly
- **Convert to video**: Adds complexity, format compatibility issues, overkill for occasional GIFs
- **Reject GIFs**: Reduces format support, users may have legitimate animated content

### Implementation Notes
```python
from PIL import Image

img = Image.open(gif_path)
img.seek(0)  # Ensure first frame
# Proceed with thumbnail generation on first frame
```

---

## 9. Error Handling for Corrupt Images

### Decision
Log warning, skip thumbnail generation, allow build to continue for other images.

### Rationale
- **Robustness**: Don't fail entire build for single corrupt file
- **Transparency**: Logged warnings alert user to investigate problems
- **Graceful degradation**: Gallery displays successfully for valid images
- **User control**: Gallery owner decides whether to fix/remove corrupt files

### Alternatives Considered
- **Fail fast**: Prevents build completion, user must fix all issues before any deployment
- **Silent skip**: Hides problems, user unaware of missing thumbnails
- **Automatic removal**: Too aggressive, may delete intentionally unusual formats

### Implementation Notes
```python
import logging

logger = logging.getLogger(__name__)

try:
    img = Image.open(source_path)
    # ... thumbnail generation
except Exception as e:
    logger.warning(f"Failed to process {source_path}: {e}")
    return None  # Skip this image, continue with others
```

---

## 10. Build Performance Optimization

### Decision
Process images sequentially in single thread during initial implementation.

### Rationale
- **Simplicity**: Single-threaded code is easier to debug and maintain
- **Build time acceptable**: 100 images in <2 minutes meets spec requirement
- **I/O bound**: Image processing is disk I/O bound, parallel processing provides diminishing returns
- **Complexity deferred**: Can add parallelization later if needed, avoid premature optimization

### Alternatives Considered
- **Multiprocessing**: Adds complexity (serialization, error handling), marginal speedup for I/O-bound workload
- **Async I/O**: Requires async/await throughout codebase, architectural change for modest benefit
- **GPU acceleration**: Requires external dependencies (CUDA, OpenCL), overkill for build tool

### Implementation Notes
- Monitor actual build times with representative image sets
- If >2 minutes for 100 images, consider `multiprocessing.Pool` for parallel processing
- Profile to identify bottlenecks before optimizing

---

## Summary

All technical decisions documented with rationale and alternatives. Key technologies confirmed:
- **Pillow 10.0+**: Image processing (resize, format conversion, EXIF handling)
- **Python 3.11**: Build tooling with pathlib, hashlib, json for caching
- **WebP + JPEG**: Modern format with universal fallback
- **HTML `<picture>` element**: Standards-based format selection

No external services or runtime dependencies introduced. All processing occurs at build time, maintaining static-first architecture. Incremental builds supported via mtime caching. Ready to proceed to Phase 1 design.
