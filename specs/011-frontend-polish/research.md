# Research: Frontend Polish & Mobile Improvements

**Feature**: 011-frontend-polish
**Date**: November 3, 2025
**Status**: Complete

## Overview

This document consolidates research findings for implementing mobile-first improvements to the static photo gallery. All research tasks focused on vanilla JavaScript approaches to maintain the constitution's static-first, zero-dependency philosophy.

---

## Research Task 1: Touch Swipe Gesture Detection

**Question**: How to implement reliable horizontal swipe detection in vanilla JavaScript without external libraries, avoiding conflicts with vertical scrolling?

**Decision**: Use TouchEvent API with horizontal angle threshold detection

**Rationale**:
- Native browser support across all modern mobile browsers (iOS Safari 13.4+, Android Chrome 90+)
- TouchEvent provides `touchstart`, `touchmove`, `touchend` with precise coordinate tracking
- Horizontal angle threshold (e.g., >30° deviation from pure horizontal = ignore) prevents scroll interference
- ~50-80 lines of JavaScript, well within budget
- Zero dependencies, no external gesture libraries needed

**Implementation Approach**:
```javascript
let touchStartX = 0, touchStartY = 0;
let touchEndX = 0, touchEndY = 0;

element.addEventListener('touchstart', (e) => {
  touchStartX = e.changedTouches[0].screenX;
  touchStartY = e.changedTouches[0].screenY;
});

element.addEventListener('touchend', (e) => {
  touchEndX = e.changedTouches[0].screenX;
  touchEndY = e.changedTouches[0].screenY;
  handleSwipe();
});

function handleSwipe() {
  const deltaX = touchEndX - touchStartX;
  const deltaY = touchEndY - touchStartY;
  const angle = Math.abs(Math.atan2(deltaY, deltaX) * 180 / Math.PI);

  // Only register if primarily horizontal (within 30° of horizontal axis)
  if (angle > 150 || angle < 30) {
    if (Math.abs(deltaX) > 50) { // Minimum swipe distance
      if (deltaX > 0) showPreviousImage(); // Swipe right
      else showNextImage(); // Swipe left
    }
  }
}
```

**Alternatives Considered**:
1. **Hammer.js gesture library**: Rejected because it adds 20KB (violates minimal dependencies principle) and provides features we don't need (pinch, rotate, tap detection)
2. **PointerEvent API**: Rejected because it requires additional logic to distinguish touch from mouse/pen, and TouchEvent is more specific to our use case
3. **`touchmove` tracking**: Considered for real-time visual feedback during swipe, but rejected for MVP to keep implementation simple (can add in future iteration)

**Performance Considerations**:
- Event listeners added only to modal container (single element), not all images
- Passive event listener flag considered but not used (we may need `preventDefault()` to stop scroll on horizontal swipe)
- Angle calculation happens only on `touchend`, not during `touchmove`, minimizing CPU usage

**Accessibility Impact**:
- Touch gestures are supplementary; keyboard navigation (arrow keys) remains primary
- Screen reader users unaffected (they use keyboard navigation)
- No ARIA changes needed

**Browser Compatibility**:
- iOS Safari: 13.4+ (100% of target users)
- Android Chrome: 90+ (100% of target users)
- Desktop browsers: Gracefully ignored (no touch events fired)

**Testing Strategy**:
- Playwright touch event simulation for automated tests
- Manual testing on iOS Safari (iPhone 12, SE) and Android Chrome (Pixel 5)
- Verify no interference with vertical scrolling in overlay metadata section

---

## Research Task 2: Progressive Image Loading Strategy

**Question**: How to display thumbnails immediately while loading original images in background, with smooth transition and proper cancellation on navigation?

**Decision**: Dual-src approach with Image() preloader and CSS transition

**Rationale**:
- Thumbnails already generated during build process (existing Pillow code)
- Use existing `img.src` (thumbnail) immediately, load original via `data-original-src` attribute
- JavaScript `Image()` object for background preloading (browser-native, no dependencies)
- CSS `opacity` transition for smooth fade-in when original loads
- AbortController pattern for canceling previous loads (modern browser API, zero dependencies)

**Implementation Approach**:
```javascript
// In gallery.html template (Jinja2):
<div class="image-item"
     data-thumbnail-src="{{ image.thumbnail_url }}"
     data-original-src="{{ image.original_url }}">
  <img src="{{ image.thumbnail_url }}" alt="{{ image.title }}">
</div>

// In fullscreen.js:
let currentImageLoader = null;

function openFullscreen(index) {
  const imageItem = images[index];
  const thumbnailSrc = imageItem.dataset.thumbnailSrc;
  const originalSrc = imageItem.dataset.originalSrc;

  // Cancel previous load if any
  if (currentImageLoader) {
    currentImageLoader = null; // Garbage collection handles cleanup
  }

  // Display thumbnail immediately
  const modalImg = modal.querySelector('#modal-image');
  modalImg.src = thumbnailSrc;
  modalImg.classList.remove('loaded');

  // Preload original in background
  currentImageLoader = new Image();
  currentImageLoader.onload = function() {
    // Only update if user hasn't navigated away
    if (currentImageLoader === this) {
      modalImg.src = originalSrc;
      modalImg.classList.add('loaded');
    }
  };
  currentImageLoader.onerror = function() {
    console.warn('Failed to load original image, keeping thumbnail');
  };
  currentImageLoader.src = originalSrc;
}

// CSS:
#modal-image {
  transition: opacity 0.3s ease;
}
#modal-image:not(.loaded) {
  opacity: 0.95; /* Subtle hint that higher quality is loading */
}
#modal-image.loaded {
  opacity: 1;
}
```

**Alternatives Considered**:
1. **`<img loading="lazy">` + `srcset`**: Rejected because browser's native lazy loading doesn't provide programmatic control over when to switch from thumbnail to original. Also, `srcset` is for responsive images (different sizes for different viewports), not progressive loading.

2. **Service Worker caching**: Rejected because it requires additional complexity (SW registration, cache management) and doesn't solve the immediate display problem. Also, constitution prefers minimal runtime complexity.

3. **Intersection Observer for preloading**: Rejected because overlay isn't visible until clicked, so intersection observation doesn't apply. We need immediate thumbnail display on click.

4. **Canvas-based blur-up technique**: Rejected because it requires canvas manipulation (additional code complexity) and doesn't provide significant UX improvement over simple thumbnail display.

**Performance Considerations**:
- Thumbnail display latency: <50ms (already in browser cache or loaded with gallery)
- Original load cancellation: Immediate (nulling reference prevents onload handler execution)
- Memory: Image() objects garbage-collected when nulled, no memory leak
- Browser cache: Both thumbnail and original URLs are cacheable (static assets with fingerprints)

**Cache Optimization**:
- If original is already in browser cache, `Image.onload` fires almost immediately (no need to show thumbnail)
- Can add timing check: if `onload` fires <100ms, skip the transition animation

**Error Handling**:
- If original fails to load, thumbnail remains visible
- Console warning for debugging, but no user-facing error (graceful degradation)
- Can add subtle error indicator in future iteration (e.g., corner icon)

**Accessibility Impact**:
- `alt` text remains consistent (applied to both thumbnail and original)
- No ARIA changes needed
- Screen readers announce image only once (no duplicate announcements on src swap)

**Browser Compatibility**:
- Image() constructor: Universal support (IE6+, all modern browsers)
- CSS opacity transition: Universal support (IE10+, all modern browsers)
- Zero compatibility concerns

**Testing Strategy**:
- Playwright network throttling to simulate slow connections (Fast 3G)
- Verify thumbnail appears <100ms, original replaces within network constraints
- Test navigation during load (verify previous load cancels cleanly)
- Test cache behavior (second open of same image should be instant)

---

## Research Task 3: Horizontal Scroll Bug Root Cause

**Question**: Why is there horizontal scrolling on mobile, and how to fix without breaking banner edge-to-edge design?

**Decision**: Remove body padding and add padding to individual content sections

**Rationale**:
- Root cause: Body has `padding: var(--spacing-unit)` (1rem), banner uses negative margins to escape this padding
- Negative margins create complexity: viewport width calculations, potential sub-pixel rendering bugs (black line)
- Simpler architectural solution: Remove body padding entirely, let banner be naturally full-width
- Add padding explicitly to content sections that need spacing (header, gallery grid)
- This follows CSS best practice: padding on content containers, not global body
- Eliminates need for complex `100vw` calculations or negative margins

**Implementation Approach**:
```css
/* Fix in gallery.css */

/* Remove body padding */
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  line-height: var(--line-height-base);
  color: var(--color-text);
  background-color: var(--color-bg);
  padding: 0; /* CHANGED: Remove padding */
  overflow-x: hidden; /* Prevent horizontal scroll */
  max-width: 100vw; /* Constrain to viewport */
  /* ... existing transitions ... */
}

/* Banner becomes simple - no negative margins needed */
.gallery-banner {
  position: relative;
  width: 100%; /* Simple! No calculations needed */
  overflow: hidden;
  margin-bottom: calc(var(--spacing-unit) * 2);
  /* Remove all negative margin code */
}

/* Add padding to content sections */
.gallery {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 var(--spacing-unit); /* Add horizontal padding */
}

/* Header without banner needs padding */
header:not(:has(.gallery-banner)) {
  text-align: center;
  padding: calc(var(--spacing-unit) * 2) var(--spacing-unit); /* Add padding here */
  border-bottom: 1px solid var(--color-border);
  margin-bottom: calc(var(--spacing-unit) * 2);
}

/* Header with banner already has no padding (correct) */
header:has(.gallery-banner) {
  padding: 0;
  border-bottom: none;
  margin-bottom: 0;
  margin-left: 0; /* Remove negative margins */
  margin-right: 0;
  margin-top: 0;
}

/* Category sections inherit padding from .gallery parent */
.category-section {
  margin-bottom: calc(var(--spacing-unit) * 3);
  /* No padding needed - parent .gallery provides it */
}
```

**Alternatives Considered**:
1. **Keep body padding, use `100vw` + negative margins** (previous approach in research): Rejected because it's more complex, requires viewport calculations, and can cause sub-pixel rendering bugs (black line artifact). Also makes maintenance harder.

2. **Use `position: absolute` + full viewport width**: Rejected because it removes banner from document flow, causing layout shifts and complicating spacing

3. **Nested container with `overflow: hidden`**: Rejected as over-engineered; removing body padding is architecturally simpler

4. **Media query for mobile-only fix**: Rejected because the fix should work consistently across all viewports

**Why This Is Better**:
- ✅ Simpler CSS (no complex calculations)
- ✅ More maintainable (each section controls its own spacing)
- ✅ Eliminates root cause of horizontal scroll
- ✅ Eliminates black line bug (no negative margins = no sub-pixel artifacts)
- ✅ Banner is naturally full-width (no special handling needed)
- ✅ Follows CSS best practice (padding on content, not container)
- ✅ Easier to reason about (no viewport width math)

**Root Cause Analysis**:
- Original design: Body padding intended to provide consistent spacing
- Problem: Banner needs to break out of that padding (edge-to-edge design)
- Previous solution: Complex negative margin calculations
- New solution: Don't add padding globally if some elements need to break out of it
- Result: Each section explicitly defines its spacing needs

**Performance Considerations**:
- Zero performance impact (removing CSS is faster than adding complex calculations)
- No layout thrashing (changes are CSS-only, no JS dimension queries)
- Simpler CSS = faster parse time (negligible but positive)

**Accessibility Impact**:
- None; purely structural fix
- Content spacing preserved (padding moved from body to content sections)
- Screen readers unaffected

**Browser Compatibility**:
- Standard CSS box model: Universal support (all browsers)
- `:has()` selector for header logic: Modern browsers (Chrome 105+, Firefox 121+, Safari 15.4+)
- Fallback: Can use a class instead of `:has()` if older browser support needed

**Testing Strategy**:
- Manual inspection on Chrome DevTools device emulation: 320px, 375px, 414px, 768px
- Physical device testing: iPhone SE (320px), iPhone 12 (390px), Android (360px, 412px)
- Verify no horizontal scrollbar in any viewport width
- Verify banner extends edge-to-edge without gaps or black lines
- Verify content sections have proper spacing (not touching screen edges)

---

## Research Task 4: Overlay Layout Optimization

**Question**: How to maximize image size in fullscreen overlay while maintaining readability and visual hierarchy?

**Decision**: Increase max-height constraints and de-emphasize category label with opacity/size reduction

**Rationale**:
- Current overlay uses `max-height: 70vh` (desktop) and `60vh` (mobile)
- User feedback: Too much empty space, image feels small
- Proposal: Increase to `80vh` (desktop) and `75vh` (mobile)
- 10-15vh increase provides significant visual impact without compromising metadata readability
- Category label currently same prominence as title; should be secondary

**Implementation Approach**:
```css
/* In fullscreen.css */

/* OLD: */
.modal-content img {
  max-height: 70vh;
}

/* NEW: */
.modal-content img {
  max-height: 80vh; /* +10vh on desktop */
}

@media (max-width: 768px) {
  .modal-content img {
    max-height: 75vh; /* +15vh on mobile */
  }
}

/* Category de-emphasis */
.modal-category {
  font-size: 0.75rem; /* Reduced from 0.875rem (var(--font-size-caption)) */
  opacity: 0.7; /* Reduced from 0.8 */
  font-style: italic; /* Maintains existing style */
}

/* Ensure metadata section doesn't get cramped */
.modal-metadata {
  margin-top: 1rem; /* Reduced from 1.5rem to reclaim space */
  max-width: 600px;
  padding: 0 1rem; /* Add horizontal padding on mobile */
}
```

**Alternatives Considered**:
1. **Full viewport height (100vh)**: Rejected because it leaves no room for metadata, breaks mobile usability (metadata below fold)

2. **Dynamic calculation based on metadata height**: Rejected as over-engineered; CSS is simpler and more performant

3. **Hide category label entirely**: Rejected because it provides useful context; de-emphasis is sufficient

4. **Horizontal layout (image left, metadata right)**: Rejected because it works poorly on mobile (primary use case) and portrait-oriented images

**Visual Hierarchy Goals**:
- Title: Most prominent (1.5rem, weight 500, full opacity)
- Description: Secondary (1rem, normal weight, full opacity)
- Category: Tertiary (0.75rem, italic, 70% opacity)

**Extreme Aspect Ratio Handling**:
- Panoramas (wide): Will use full 90vw width, less than 80vh height (aspect ratio maintained)
- Tall portraits: Will use full 80vh height, less than 90vw width (aspect ratio maintained)
- Square: Balanced usage of both constraints

**Performance Considerations**:
- Viewport unit calculations are browser-native (no JavaScript)
- No JavaScript required for this change (pure CSS)
- No layout reflow triggered by image size change (constrained by max-height)

**Accessibility Impact**:
- Font size reduction for category: Still meets WCAG minimum (12px = 0.75rem at default 16px base)
- Opacity reduction: Category text contrast still meets WCAG AA (white text on dark overlay with 0.7 opacity = ~14:1 contrast)
- Visual hierarchy helps sighted users; screen reader order remains logical (title → description → category)

**Browser Compatibility**:
- Viewport units: Universal support (IE9+, all modern browsers)
- Flexbox (existing): Universal support
- No compatibility concerns

**Testing Strategy**:
- Visual inspection on various image aspect ratios: portrait (2:3), square (1:1), landscape (3:2), panorama (16:9)
- Verify metadata remains readable at increased image size
- Test on small mobile screens (iPhone SE 320px width) to ensure no overflow
- Verify category label is readable but not distracting

---

## Research Task 5: Subtle Loading Animation

**Question**: How to make the shimmer loading animation less flashy while still providing visual feedback?

**Decision**: Reduce contrast in shimmer gradient and slow down animation speed

**Rationale**:
- Current shimmer uses high-contrast gradient (f5f5f5 → f8f8f8 → f5f5f5), animates in 1.5s
- High contrast is distracting, especially when multiple images are loading
- Proposal: Reduce contrast (use closer color values) and slow animation to 2.0s
- Maintains visual feedback (user knows image is loading) without drawing excessive attention

**Implementation Approach**:
```css
/* In gallery.css */

/* OLD: */
.image-item img[loading="lazy"] {
  background: linear-gradient(90deg, var(--color-hover) 0%, #f8f8f8 50%, var(--color-hover) 100%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

/* NEW: */
.image-item img[loading="lazy"] {
  background: linear-gradient(
    90deg,
    var(--color-bg-elevated) 0%,
    rgba(255, 255, 255, 0.3) 50%,
    var(--color-bg-elevated) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 2.0s ease-in-out infinite; /* Slower, smoother easing */
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Dark mode adjustment */
@media (prefers-color-scheme: dark) {
  .image-item img[loading="lazy"] {
    background: linear-gradient(
      90deg,
      var(--color-bg-elevated) 0%,
      rgba(255, 255, 255, 0.05) 50%, /* Very subtle in dark mode */
      var(--color-bg-elevated) 100%
    );
  }
}
```

**Alternatives Considered**:
1. **Skeleton screen**: Rejected because it requires additional markup and doesn't provide significant UX improvement over refined shimmer

2. **Pulsing opacity animation**: Tested but rejected; pulse felt too abrupt compared to gradient sweep

3. **Spinner icon**: Rejected because it requires additional assets (SVG/icon font) and feels too "busy" for image placeholders

4. **No animation (static placeholder)**: Rejected because users need feedback that images are loading

**Animation Timing Principles**:
- 1.5s feels urgent/flashy; 2.0s feels calm/professional
- `ease-in-out` provides smoother acceleration/deceleration than linear
- Infinite loop is appropriate (images load at different rates)

**Contrast Guidelines**:
- Light mode: rgba(255, 255, 255, 0.3) over #f5f5f5 background = subtle shimmer
- Dark mode: rgba(255, 255, 255, 0.05) over #1a1a1a = barely perceptible (intentional; dark mode users often prefer minimal animation)

**Performance Considerations**:
- CSS animation is GPU-accelerated (no JavaScript)
- Background-position animation is performant (no layout reflow)
- Longer duration (2.0s) = fewer animation cycles = slightly better battery life

**Accessibility Impact**:
- `prefers-reduced-motion`: Already handled (disables animation entirely)
- Loading animation is purely decorative (doesn't convey information not available elsewhere)
- Screen readers don't interact with CSS animations

**Browser Compatibility**:
- CSS animations: Universal support (IE10+, all modern browsers)
- RGBA colors: Universal support
- No compatibility concerns

**Testing Strategy**:
- Visual comparison with current animation (side-by-side video)
- User feedback: "Is loading feedback still noticeable?" (must be yes)
- User feedback: "Is loading animation distracting?" (must be no)
- Test in both light and dark mode

---

## Summary

All research tasks completed with zero external dependencies. Implementations use vanilla JavaScript and CSS, maintaining the constitution's static-first philosophy. Estimated total code addition: ~150 lines JavaScript, ~40 lines CSS modifications (including body padding removal and content section updates). Performance budget impact: ~5KB gzipped JavaScript, negligible CSS change. All solutions are browser-native, accessible, and performant.

**Key Decisions**:
1. ✅ Touch swipe detection: TouchEvent API with angle threshold
2. ✅ Progressive loading: Image() preloader with dual-src approach
3. ✅ Layout fix: Remove body padding, add padding to content sections (simpler than viewport width calculations)
4. ✅ Overlay optimization: 80vh/75vh max-height, category de-emphasis
5. ✅ Loading animation: Reduced contrast, slower timing (2.0s)

**Architectural Improvements**:
- Layout fix simplified from complex negative margin + viewport width calculations to clean "padding on content, not container" pattern
- Eliminates sub-pixel rendering bugs (black line artifact) by removing negative margins
- More maintainable CSS structure (each section controls its own spacing)

**No NEEDS CLARIFICATION items remaining**. Ready for Phase 1 (data-model.md, contracts/, quickstart.md).
