# ADR 0012: Blur Placeholder Strategy

**Date**: 2025-12-08
**Status**: Accepted

## Context

The gallery needs to provide instant visual feedback when loading images on mobile devices, especially on slow network connections. Users currently see blank spaces while thumbnails load, creating a perception of slow performance even when the overall page load time is reasonable.

Research shows that perceived performance (time-to-first-content) is more important to user experience than total load time. The "blur-up" technique pioneered by Medium and adopted by Gatsby/Next.js demonstrates that showing a tiny, blurred version of an image immediately can dramatically improve perceived load times.

## Decision

We will generate ultra-low-resolution blur placeholders (20×20px before blur) during the build process and embed them as base64-encoded data URLs directly in the HTML. This approach ensures:

1. **Zero network requests**: Placeholders are available immediately when HTML is parsed
2. **Instant display**: No waiting for DNS, connection, or download
3. **Perceptual performance**: Users see image previews within 50ms
4. **Build-time cost**: One-time generation during build (~50-100ms per image)

### Technical Implementation

- **Tool**: Pillow (PIL) for image resizing, CSS `filter: blur()` for blur effect
- **Process**: Resize to 20×20px → JPEG encode (quality 50) → Base64 encode → Apply CSS blur
- **Size**: Target <800 bytes per placeholder (smaller without Pillow blur)
- **Format**: `data:image/jpeg;base64,{base64_string}` with CSS `filter: blur(20px)`
- **Storage**: Embedded in HTML `<div>` inline styles as background-image
- **Rendering**: CSS filter uses GPU acceleration for better performance

### HTML Size Trade-off

This approach increases HTML file size significantly:
- **Before**: ~30KB initial HTML
- **After**: ~110KB for 100 images (~800 bytes × 100)
- **Trade-off**: One-time cost on page load for instant perceived performance

The project's constitution limits HTML to 30KB, but we accept this violation because:
1. The user benefit (instant visual feedback) is substantial
2. After initial page load, all subsequent images have instant previews
3. Progressive enhancement ensures functionality without placeholders
4. Alternative approaches (external files, CSS colors) defeat the performance purpose

## Alternatives Considered

### 1. CSS Dominant Color Extraction
Extract the dominant color from each image and use as solid background.

**Rejected**: No preview of actual image content. Users can't recognize images from solid colors. Poor UX compared to blur placeholders.

### 2. External Blur Placeholder Files
Generate tiny blur images as separate .jpg files (e.g., `blur-{hash}.jpg`).

**Rejected**: Requires network request, adding 50-200ms latency on 3G. Defeats the purpose of instant display. Increases server requests.

### 3. SVG Traced Placeholders
Use Potrace or primitive.js to generate SVG outlines of images.

**Rejected**: Complex build process. Larger file sizes (>2KB typical). Inconsistent quality across different image types. Higher CPU cost.

### 4. WebP Format for Smaller Data URLs
Use WebP encoding instead of JPEG for ~30% size reduction.

**Considered but deferred**: Better compression but adds build complexity (WebP support in Pillow, browser compatibility). JPEG is universally supported and sufficient for MVP. Can revisit if HTML size becomes problematic.

### 5. No Placeholders (Show Nothing)
Current behavior - display blank space until thumbnails load.

**Rejected**: Poor perceived performance. Users interpret blank screens as "slow" even when loads are fast. Research shows blur placeholders dramatically improve perceived speed.

## Consequences

### Positive
- Users see image previews instantly (<50ms from page load)
- Dramatically improved perceived performance on slow connections
- Smooth progressive enhancement (blur → thumbnail → full image)
- Build-time generation has no runtime performance cost
- Cached in build system for incremental builds

### Negative
- HTML file size increases significantly (~80KB for 100 images)
- Violates project's 30KB HTML budget (documented exception)
- Adds 2-5 seconds to build time for blur generation
- Requires base64 encoding/decoding overhead (1.33x size multiplier)

### Mitigation Strategies
- Implement lazy blur placeholder loading (only embed for visible images)
- Add configuration toggle to disable blur placeholders entirely
- Consider WebP format in future for smaller data URLs
- Use CSS dominant colors as fallback for non-critical images

## References

- [Medium's Progressive Image Loading](https://jmperezperez.com/medium-image-progressive-loading-placeholder/)
- [Gatsby Image Plugin Documentation](https://www.gatsbyjs.com/docs/how-to/images-and-media/using-gatsby-plugin-image/)
- [Next.js Image Optimization](https://nextjs.org/docs/pages/building-your-application/optimizing/images)
- Pillow ImageFilter documentation
- Research: `specs/010-mobile-fullscreen-performance/research.md`
