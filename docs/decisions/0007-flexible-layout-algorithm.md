# ADR 0007: Flexible Layout Algorithm

## Status

Accepted

## Date

2025-11-02

## Context

The gallery currently uses CSS Grid with a fixed 4:3 aspect ratio, which crops images to fit the grid cells. Users need to see complete images without cropping while maintaining:
- Visual balance across different aspect ratios
- Efficient use of space
- Responsive behavior across all viewport sizes
- Zero cumulative layout shift (CLS = 0.0)
- Performance requirements (<500ms layout calculation for 100 images)

### Requirements

1. Display images at their original aspect ratios without cropping
2. Maintain consistent visual sizing (images should appear roughly comparable in size)
3. Minimize whitespace between images while maintaining clean spacing
4. Work responsively from mobile (320px) to 4K (3840px) displays
5. Achieve zero layout shift for optimal Core Web Vitals
6. Keep JavaScript bundle size under 75KB total

### Algorithm Options Considered

1. **Masonry Layout** (Pinterest-style)
   - Vertical stacking in columns
   - Pros: No cropping, simple to implement
   - Cons: Irregular bottom edge, less control over visual weight, poor mobile experience
   - Decision: Rejected

2. **Packing Algorithm** (Knuth-Plass inspired)
   - Optimal line breaking adapted for images
   - Pros: Mathematically optimal spacing
   - Cons: Computationally expensive, implementation complexity, overkill for typical galleries
   - Decision: Rejected

3. **Justified Layout Algorithm** (Flickr/SmugMug approach)
   - Arranges images in rows with consistent heights
   - Adjusts row height to fit container width perfectly
   - Pros: No gaps, efficient space usage, visually balanced, industry-proven
   - Cons: Requires JavaScript for calculation
   - Decision: **Selected**

## Decision

Implement **justified layout algorithm** using the **flickr/justified-layout** library with client-side calculation executed on page load.

### Technical Implementation

1. **Build-time**: Extract image dimensions (width, height) using Pillow
2. **Template**: Include dimensions in HTML as `data-width`, `data-height`, and `width`, `height` attributes
3. **Runtime**: JavaScript calculates optimal layout using justified-layout library
4. **Rendering**: Apply positions via absolute positioning within a container
5. **Responsive**: Recalculate layout on window resize (debounced 150ms)

### Library Choice

Use **flickr/justified-layout** (v4.1.0):
- Size: ~5KB minified + gzipped (~15KB uncompressed)
- Pure calculation function (no DOM manipulation)
- Battle-tested (used by Flickr for millions of images)
- MIT license
- TypeScript definitions available
- Active maintenance

Vendored locally to avoid external CDN dependency and ensure reproducible builds.

## Consequences

### Positive

✅ Images display at original aspect ratios without cropping
✅ Visually balanced layout across different aspect ratios
✅ Efficient space usage with minimal whitespace
✅ Responsive across all viewport sizes (320px to 3840px)
✅ Zero cumulative layout shift (CLS = 0.0) achieved
✅ Industry-proven algorithm (used by Flickr, SmugMug, Google Photos)
✅ Performant (<20ms calculation time for 500 images)
✅ JavaScript bundle size well within budget (~42KB total, <75KB limit)

### Negative

❌ Requires JavaScript for optimal layout (CSS Grid fallback available)
❌ Additional 15KB library size (5KB gzipped)
❌ Small calculation overhead on initial load and resize

### Neutral

⚪ Graceful degradation: Without JavaScript, falls back to CSS Grid with fixed aspect ratio
⚪ Maintains semantic HTML structure and accessibility

## Implementation Details

### Configuration

```javascript
justifiedLayout(imageData, {
  containerWidth: gallery.clientWidth,
  targetRowHeight: containerWidth < 640 ? 200 : 320, // Responsive
  maxRowHeight: targetRowHeight * 1.5,
  boxSpacing: 8,
  containerPadding: 0
});
```

### Performance Characteristics

- 10 images: <1ms
- 100 images: <5ms
- 500 images: ~20ms
- Memory: O(n) where n = number of images

### Browser Support

ES6+ (Chrome 51+, Firefox 54+, Safari 10+, Edge 15+)

## Alternatives Not Chosen

### Custom Implementation

- Estimated size: 2-3KB
- Pros: Full control, no dependencies, smaller size
- Cons: Maintenance burden, risk of edge case bugs, untested in production
- Reason rejected: 5KB cost is acceptable for proven, tested solution used by major photo sites

### Build-time Layout Calculation

- Calculate layout server-side for specific breakpoints
- Pros: No JavaScript required, faster initial render
- Cons: No responsive adaptation, complex multi-breakpoint management, larger HTML
- Reason rejected: Modern web expects responsive behavior; complexity outweighs benefits

## References

- [flickr/justified-layout GitHub](https://github.com/flickr/justified-layout)
- [Feature Specification](../../specs/007-flexible-layout/spec.md)
- [Research Document](../../specs/007-flexible-layout/research.md)
- [Layout Algorithm API Contract](../../specs/007-flexible-layout/contracts/layout-algorithm-api.md)
- [Web.dev: Cumulative Layout Shift](https://web.dev/cls/)
- [Google Photos Layout Analysis](https://medium.com/google-design/google-photos-45b714dfbed1)

## Validation

- ✅ All 103 unit/integration tests pass
- ✅ Zero accessibility violations (axe-core)
- ✅ Asset budget tests pass (JS: 42KB < 75KB limit)
- ✅ CLS = 0.0 achieved with inline dimensions + pre-calculation
- ✅ Performance: <20ms layout calculation for 82 images (test gallery)

## Future Considerations

1. **Virtual Scrolling**: For galleries with 1000+ images, implement virtual scrolling to only calculate/render visible images
2. **Configuration Options**: Add user-configurable target row height and spacing if needed
3. **Animation**: Add smooth transitions when layout changes (currently instant)
4. **Print Optimization**: Optimize layout calculation for print media
5. **Progressive Enhancement**: Consider server-side rendering of default layout for SEO (if needed)

## Changelog

- 2025-11-02: Initial implementation completed and validated
