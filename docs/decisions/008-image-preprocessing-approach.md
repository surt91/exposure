# ADR 008: Image Preprocessing with WebP Thumbnails

**Status**: Accepted
**Date**: 2025-11-02
**Context**: Feature 008-image-preprocessing

## Context

Gallery pages were loading slowly (45+ seconds for 50 images) because full-resolution source images (2-5MB each) were served directly in the gallery grid. This created excessive bandwidth usage and poor user experience, especially on slower connections.

## Decision

Implement mandatory build-time image preprocessing to generate optimized WebP and JPEG thumbnails:

1. **Thumbnail Generation**
   - Always generate thumbnails during build (not optional)
   - Scale images to 800px maximum dimension during build
   - Generate WebP thumbnails (quality 85) for modern browsers
   - Generate JPEG fallbacks (quality 90) for older browsers
   - Use LANCZOS resampling for high-quality downscaling

2. **Format Strategy**
   - Serve WebP as primary format (25-35% smaller than JPEG)
   - Provide JPEG fallback for browser compatibility
   - Use HTML `<picture>` element for automatic format selection
   - No JavaScript required - browser handles format choice natively

3. **Build-Time Processing**
   - Generate all thumbnails during `exposure` build command
   - Store thumbnails in `build/images/thumbnails/` directory
   - Use content hash in filenames for cache busting
   - Track file modification times for incremental builds

4. **Caching Strategy**
   - Maintain build cache in `build/.build-cache.json`
   - Compare source image mtime against cache entries
   - Skip regeneration if source unchanged
   - Enable sub-second incremental builds

5. **Template Integration**
   - Gallery grid displays thumbnails via `<picture>` element
   - Modal view displays full-resolution originals
   - Original images moved to `images/originals/` subdirectory
   - Thumbnails reference source via `data-original-src` attribute

## Consequences

### Positive

- **Massive bandwidth reduction**: 85%+ smaller gallery pages (125MB → 15MB)
- **Fast load times**: 3 seconds vs 45 seconds for 50 images
- **Better UX**: Gallery usable immediately, originals load on-demand in modal
- **Modern formats**: WebP provides superior compression with good quality
- **Incremental builds**: Only changed images regenerated (10s vs 2min)
- **Static output**: No runtime dependencies, works on any static host
- **Browser compatibility**: JPEG fallback ensures universal support

### Negative

- **Build time increase**: First build takes 1-2 minutes for 100 images
- **Storage increase**: 2 additional files per image (WebP + JPEG thumbnails)
- **Dependency added**: Requires Pillow library for image processing
- **Complexity increase**: More moving parts in build pipeline

### Neutral

- **Cache file**: Build cache adds `build/.build-cache.json` (not version controlled)
- **Directory structure**: Output now has `images/originals/` and `images/thumbnails/`
- **Configuration**: Optional thumbnail quality settings in `config/settings.yaml`
- **Always enabled**: Thumbnail generation cannot be disabled (design decision)

## Technical Details

### Thumbnail Sizing

800px maximum dimension chosen because:
- Provides 2x resolution for typical 400px grid displays (HiDPI support)
- Achieves 90%+ file size reduction from typical 4000-6000px sources
- Maintains visual quality when displayed at gallery sizes
- Balances quality and performance for mobile/desktop

### Quality Settings

- **WebP quality 85**: Visually lossless at display sizes, good compression
- **JPEG quality 90**: Matches WebP visual quality for fallback consistency
- Settings based on research testing with sample images

### Resampling Filter

LANCZOS chosen over BICUBIC/BILINEAR because:
- Produces sharpest results when downscaling
- Avoids aliasing and blur artifacts
- Industry standard for professional image tools
- Pillow native support, no external dependencies

### Format Selection

HTML `<picture>` element chosen over JavaScript detection:
- Standards-based, no script required
- Browser automatically picks best supported format
- Works with screen readers and accessibility tools
- No extra bandwidth (only downloads chosen format)

## Alternatives Considered

### 1. Runtime Image Processing

**Rejected**: Violates static-first architecture, requires server infrastructure

### 2. Multiple Thumbnail Sizes (Responsive Images)

**Rejected**: Added complexity, storage overhead, marginal benefit for gallery use case

### 4. Client-Side Resizing

**Rejected**: Still requires downloading full-resolution images, defeats optimization goal

### 5. WebP Only (No JPEG Fallback)

**Rejected**: Breaks Safari <14 and older browsers, reduces compatibility

### 6. CDN Image Optimization

**Rejected**: Ties project to specific hosting provider, increases deployment complexity

### 7. Optional Thumbnail Generation

**Rejected**: Making thumbnails optional would:
- Require users to understand performance implications
- Lead to poor out-of-box experience if disabled
- Add unnecessary configuration complexity
- Result in suboptimal galleries by default

**Decision**: Always generate thumbnails as a core feature, not an option

## Implementation References

- **Specification**: `/specs/008-image-preprocessing/spec.md`
- **Data Model**: `/specs/008-image-preprocessing/data-model.md`
- **API Contracts**: `/specs/008-image-preprocessing/contracts/`
- **Research**: `/specs/008-image-preprocessing/research.md`
- **Tasks**: `/specs/008-image-preprocessing/tasks.md`

## Validation

Success metrics:
- ✅ Gallery page size reduced by 90%+
- ✅ Page load time <3 seconds for 50 images on 10Mbps
- ✅ WebP thumbnails 25-35% smaller than JPEG
- ✅ Incremental builds skip unchanged images (<10s)
- ✅ Modal displays full-resolution originals
- ✅ No accessibility regressions (axe-core passes)

## Related Decisions

- [ADR 0001: Jinja2 for HTML Templating](0001-templating.md) - Template integration
- [ADR 0002: Type Checking with ty](0002-type-checking.md) - Type safety for new models
- [ADR 0007: Flexible Layout Algorithm](0007-flexible-layout-algorithm.md) - Layout integration

## Notes

- Thumbnails are always generated (mandatory feature, not optional)
- Thumbnails are build artifacts, not version controlled
- Cache file format versioned for future compatibility
- Quality settings can be customized via configuration or environment variables
