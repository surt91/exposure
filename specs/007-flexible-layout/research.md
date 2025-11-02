# Research: Flexible Aspect-Ratio Image Layout

**Feature**: 007-flexible-layout
**Date**: 2025-11-02
**Status**: Complete

## Research Questions

1. What layout algorithms exist for displaying mixed aspect ratio images?
2. What JavaScript libraries are available for flexible image layout?
3. What is the performance and bundle size impact of various approaches?
4. Should layout calculations happen client-side (JS) or build-time (Python)?
5. How can we achieve zero cumulative layout shift (CLS=0.0)?

---

## Q1: Layout Algorithms for Mixed Aspect Ratio Images

### Findings

**Justified Layout Algorithm** (Flickr/SmugMug approach)
- Arranges images in rows with consistent heights
- Adjusts row height to fit container width perfectly
- Algorithm: For each row, calculate height that makes images fit exactly within container width
- Benefits: No gaps between rows, efficient space usage, visually balanced
- Used by: Flickr, SmugMug, Google Photos

**Masonry Layout** (Pinterest approach)
- Vertical stacking in columns
- Images maintain aspect ratio, columns fill top-to-bottom
- Benefits: No cropping, works well for varying heights
- Drawbacks: Less control over visual weight, irregular bottom edge, requires JS for column balancing

**Flex Grid with Fixed Aspect Ratio**
- CSS Grid with `aspect-ratio` property
- All items same aspect ratio, variable content cropped
- Current implementation in exposure - simple but crops images

**Packing Algorithm** (Knuth-Plass inspired)
- Optimal line breaking adapted for image layout
- Minimizes "badness" metric (whitespace penalty)
- Complex implementation, requires dynamic programming
- Benefits: Mathematically optimal spacing
- Drawbacks: Computationally expensive, overkill for typical galleries

### Decision: Justified Layout Algorithm

**Rationale**:
- Best balance of visual consistency and space efficiency
- Industry proven (used by major photo sites)
- Relatively simple to implement (~200-300 lines)
- Natural reading flow (left-to-right, top-to-bottom)
- Handles extreme aspect ratios gracefully

**Alternatives Considered**:
- Masonry: Rejected due to irregular layout and poor mobile experience
- Packing: Rejected due to implementation complexity and performance concerns
- Fixed aspect: Current approach, rejected due to cropping requirement

---

## Q2: JavaScript Libraries for Flexible Layout

### Findings

**flickr/justified-layout** (npm: justified-layout)
- Official library from Flickr
- Pure calculation function: takes dimensions, returns positions
- ~5KB minified + gzipped
- No DOM manipulation, just math
- TypeScript definitions available
- Well tested, actively maintained
- MIT license

**Masonry.js**
- ~7KB minified + gzipped
- Includes DOM manipulation
- More than needed (vertical stacking not our goal)
- jQuery dependency in older versions (removed in v4+)

**Packery**
- Commercial license ($25)
- Bin-packing algorithm
- Overkill for our use case

**PhotoSwipe**
- Full gallery with lightbox (~20KB)
- Includes layout but also viewer, touch gestures, etc.
- Too heavy, duplicates existing fullscreen functionality

**Custom Implementation**
- ~2-3KB estimated (minimal justified layout)
- Full control over algorithm details
- No external dependencies
- Maintenance burden

### Decision: Use flickr/justified-layout library

**Rationale**:
- Minimal size impact (5KB, within budget: 15KB current + 5KB = 20KB < 75KB limit)
- Battle-tested algorithm used by millions of images on Flickr
- Pure function design fits our static generation approach
- No dependencies or DOM manipulation
- MIT license compatible with project
- TypeScript support available
- Active maintenance (last update 2023)

**Alternatives Considered**:
- Custom implementation: Rejected due to maintenance burden and risk of edge case bugs. 5KB cost is acceptable for proven, tested solution.
- Masonry.js: Rejected as layout pattern doesn't match requirements (vertical vs horizontal organization)
- PhotoSwipe: Rejected as it includes unnecessary features and duplicates existing fullscreen viewer

---

## Q3: Performance and Bundle Size Impact

### Findings

**Current State**:
- JS: ~15KB uncompressed (gallery.js + fullscreen.js)
- CSS: ~8KB uncompressed
- HTML: ~25KB for 30 images

**With Justified Layout Library**:
- Library: 5KB minified + gzipped (~15KB uncompressed)
- Integration code: ~2KB (initialization, responsive handlers)
- Total JS: ~32KB uncompressed → ~12KB gzipped
- Still well under 75KB budget

**Performance Benchmarks** (from flickr/justified-layout docs):
- 100 images: <5ms calculation time
- 500 images: ~20ms calculation time
- 1000 images: ~40ms calculation time
- Memory: O(n) where n = number of images

**Layout Shift Prevention**:
- Pre-calculate all positions before render
- Set explicit width/height/position via inline styles or CSS variables
- Images reserve space with skeleton/placeholder
- Cumulative Layout Shift (CLS) = 0.0 achievable

### Decision: Client-side calculation with pre-render

**Performance Strategy**:
1. Inline image dimensions in HTML (width/height attributes)
2. Run layout calculation in `<script>` tag before closing `</head>`
3. Apply positions via CSS custom properties
4. Images render in correct positions immediately
5. Zero layout shift as images load

**Alternatives Considered**:
- Build-time calculation (Python): Rejected because responsive layouts need recalculation on window resize. Would need breakpoint-specific calculations, adding complexity.
- Lazy layout calculation: Rejected due to visible layout shift, violates CLS=0.0 requirement

---

## Q4: Client-side vs Build-time Layout

### Findings

**Client-side (JavaScript)**:
- ✅ Responsive: Recalculates on window resize
- ✅ Simple build: Just pass dimensions to template
- ✅ Adaptive: Works for any viewport width
- ❌ Requires JavaScript enabled
- ❌ Small performance cost (5-20ms)

**Build-time (Python)**:
- ✅ No JS required for initial layout
- ✅ Faster initial render (no calculation)
- ❌ Fixed breakpoints only (e.g., mobile/tablet/desktop)
- ❌ Complex: Need multiple layouts per breakpoint
- ❌ No dynamic resize adaptation
- ❌ Larger HTML (inline styles for all breakpoints)

**Hybrid Approach**:
- Build-time: Generate default layout for common viewport (desktop)
- Client-side: Recalculate on resize or mobile viewport
- ✅ Progressive enhancement
- ❌ Most complex to implement and maintain

### Decision: Client-side layout calculation

**Rationale**:
- Modern web applications expect responsive behavior
- 5-20ms calculation time is negligible (<500ms requirement)
- Simpler implementation: single algorithm, no breakpoint management
- Progressive enhancement already handled (images display in grid without JS)
- Aligns with existing architecture (JS for interactivity)

**Graceful Degradation Strategy**:
- Without JS: CSS Grid fallback (current fixed aspect ratio)
- With JS: Justified layout algorithm
- Maintains accessibility and basic functionality

**Alternatives Considered**:
- Build-time: Rejected due to lack of responsive adaptation and increased build complexity
- Hybrid: Rejected as unnecessarily complex for minimal benefit

---

## Q5: Achieving Zero Cumulative Layout Shift (CLS=0.0)

### Findings

**Layout Shift Causes**:
1. Images loading without reserved space
2. Layout calculation happening after initial render
3. Font loading causing text reflow
4. Dynamic content injection

**Prevention Strategies**:

**Strategy 1: Inline Dimensions**
```html
<img src="image.jpg" width="800" height="600" alt="..." />
```
- Browser reserves space based on aspect ratio
- Works even without CSS
- Required for CLS=0.0

**Strategy 2: Pre-calculate Layout Before First Paint**
```html
<head>
  <script>
    // Calculate layout synchronously before DOM render
    const layout = calculateLayout(imageData);
    document.documentElement.style.setProperty('--layout-data', JSON.stringify(layout));
  </script>
</head>
```
- Execute before `</head>` closes
- Blocks rendering until complete (acceptable for <100ms)
- Positions available before images render

**Strategy 3: CSS Custom Properties for Positions**
```css
.image-item[data-index="0"] {
  width: var(--img-0-width);
  height: var(--img-0-height);
  transform: translate(var(--img-0-x), var(--img-0-y));
}
```
- Layout data passed via CSS variables
- No JavaScript required for positioning after initial calc
- Printable, inspector-friendly

**Strategy 4: Skeleton/Placeholder**
```html
<div class="image-item" style="width: 300px; height: 200px;">
  <img loading="lazy" ... />
</div>
```
- Container reserves space
- Image loads within reserved space
- No shift as image loads

### Decision: Hybrid approach with inline dimensions + synchronous pre-calculation

**Implementation Plan**:
1. **Build time**: Python extracts image dimensions (width, height) from files
2. **Template**: Include dimensions in HTML as data attributes and img attributes
3. **Pre-render script**: Synchronous JS calculates layout before `</head>` closes
4. **Apply layout**: Set container dimensions and positions via inline styles
5. **Image load**: Images fill pre-sized containers with lazy loading

**CLS=0.0 Guarantee**:
- ✅ Space reserved via width/height attributes
- ✅ Layout calculated before first paint
- ✅ Positions applied before images visible
- ✅ No dynamic content injection
- ✅ Font loading doesn't affect image layout

**Alternatives Considered**:
- Async layout calculation: Rejected - causes visible layout shift
- Build-time only: Rejected - not responsive
- Skeleton without dimensions: Rejected - still causes shift when layout applied

---

## Implementation Recommendations

### Phase 1: Foundation
1. Update Python image scanner to extract width/height using Pillow
2. Update Image model to store dimensions
3. Pass dimensions to Jinja2 template
4. Add width/height attributes to `<img>` tags

### Phase 2: Layout Algorithm
1. Add justified-layout library via npm/unpkg CDN (or bundle)
2. Create layout.js module
3. Implement pre-render calculation
4. Test with various aspect ratios and gallery sizes

### Phase 3: Styling
1. Update CSS Grid to flex container
2. Add positioning styles
3. Implement responsive resize handler
4. Add loading states and transitions

### Phase 4: Testing
1. Unit tests for dimension extraction
2. Layout algorithm tests (mock library)
3. Visual regression tests
4. Performance tests (layout calculation time)
5. Accessibility audit (no regressions)
6. CLS measurement (target: 0.0)

### Phase 5: Documentation
1. ADR for algorithm choice
2. Update README with new layout behavior
3. Add configuration options (if any)
4. Document browser compatibility

---

## Technical Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Layout Algorithm | Justified Layout | Industry proven, balanced visuals, efficient space usage |
| Implementation Library | flickr/justified-layout | Minimal size (5KB), battle-tested, pure calculation function |
| Calculation Timing | Client-side, pre-render | Responsive, simple build, zero layout shift achievable |
| Performance Budget | +5KB library + 2KB code | Total ~32KB JS uncompressed, within 75KB limit |
| CLS Prevention | Inline dimensions + sync calc | Guarantees CLS=0.0 with reserved space and pre-calculation |
| Fallback Strategy | CSS Grid (current) | Progressive enhancement, works without JS |
| Browser Support | ES6+ (2016+) | Aligns with current browser support policy |

---

## Open Questions / Risks

1. **Risk**: justified-layout library compatibility with future browsers
   - **Mitigation**: Pure math library, no browser APIs, unlikely to break

2. **Risk**: Performance on very large galleries (500+ images)
   - **Mitigation**: Benchmark shows 20ms for 500 images, acceptable. Could add virtual scrolling later if needed.

3. **Question**: Should we support SSR/pre-rendered layouts for SEO?
   - **Answer**: Not needed - static site already fully rendered, crawlers see all images with dimensions

4. **Question**: Configuration options for layout behavior (e.g., target row height)?
   - **Answer**: Start with sensible defaults, add configuration in future if users request it

---

## References

- [Flickr justified-layout library](https://github.com/flickr/justified-layout)
- [Web Vitals: CLS](https://web.dev/cls/)
- [Google Photos layout analysis](https://medium.com/google-design/google-photos-45b714dfbed1)
- [Masonry vs Justified Layout comparison](https://css-tricks.com/piecing-together-approaches-for-a-css-masonry-layout/)
- [Aspect ratio in CSS](https://developer.mozilla.org/en-US/docs/Web/CSS/aspect-ratio)

---

## Conclusion

The research strongly supports implementing a **justified layout algorithm using the flickr/justified-layout library** with **client-side calculation executed before first paint**. This approach:

- ✅ Meets all functional requirements (no cropping, consistent sizing, minimal whitespace)
- ✅ Satisfies performance constraints (<500ms, <75KB JS, CLS=0.0)
- ✅ Maintains constitution principles (static-first, accessible, reproducible)
- ✅ Provides responsive behavior across all viewport sizes
- ✅ Uses industry-proven, well-tested implementation
- ✅ Gracefully degrades without JavaScript

The implementation is straightforward with clear phases and testable milestones. Risk is minimal due to library maturity and simple integration pattern.
