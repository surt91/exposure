# JavaScript Module Contracts

**Feature**: 011-frontend-polish
**Date**: November 3, 2025
**Type**: Frontend JavaScript Interfaces

## Overview

This document defines the public interfaces and contracts for JavaScript modules modified in this feature. Since this is a static site with vanilla JavaScript (no TypeScript, no module bundler), these contracts serve as documentation for the expected behavior and integration points.

---

## Module 1: fullscreen.js

**Purpose**: Manage fullscreen image overlay with progressive loading and touch navigation

**Exports**: None (IIFE pattern, attaches to window for debugging)

**Public Debug Interface** (window.fullscreenDebug):
```javascript
{
  getCurrentIndex: () => number,    // Returns current image index (-1 if closed)
  getImagesCount: () => number,     // Returns total number of images
  close: () => void                 // Programmatically close overlay
}
```

**DOM Dependencies**:
```javascript
// Required elements (must exist on page):
#fullscreen-modal                 // Modal container element
.modal-close                       // Close button
.modal-prev                        // Previous image button
.modal-next                        // Next image button
#modal-image                       // Image element for display
#modal-title                       // Title heading element
#modal-description                 // Description paragraph element
#modal-category                    // Category label element
.image-item                        // All gallery image items (NodeList)
```

**Data Attribute Requirements** (on .image-item):
```javascript
{
  'data-category': string,         // Category name (required)
  'data-thumbnail-src': string,    // Thumbnail URL (required)
  'data-original-src': string,     // Original image URL (required)
  'data-title': string,            // Image title (required)
  'data-description': string,      // Image description (optional, can be empty)
  'data-filename': string          // Original filename (optional, for debugging)
}
```

**i18n Data Attribute** (on #fullscreen-modal):
```javascript
{
  'data-i18n-category': string     // Translated "Category:" label (e.g., "Kategorie:")
}
```

**Event Handlers**:
```javascript
// Click events:
.image-item.click → openFullscreen(globalIndex)
.modal-close.click → closeFullscreen()
.modal-prev.click → showPreviousImage()  // Crosses category boundaries seamlessly
.modal-next.click → showNextImage()      // Crosses category boundaries seamlessly
#fullscreen-modal.click (on backdrop) → closeFullscreen()

// Keyboard events (document-level):
Escape → closeFullscreen()
ArrowLeft → showPreviousImage()   // Crosses category boundaries seamlessly
ArrowRight → showNextImage()      // Crosses category boundaries seamlessly
Tab → trapFocus(event) // Keep focus within modal

// Touch events (NEW - on #fullscreen-modal):
touchstart → Record touch coordinates
touchend → Validate and process swipe gesture  // Crosses category boundaries seamlessly
```

**New Functions** (internal, documented for maintainability):

### handleTouchStart(event: TouchEvent)
```javascript
/**
 * Record initial touch coordinates when user touches overlay
 * @param {TouchEvent} event - Browser touch event
 * @returns {void}
 */
function handleTouchStart(event) {
  touchStartX = event.changedTouches[0].screenX;
  touchStartY = event.changedTouches[0].screenY;
  touchStartTime = performance.now();
}
```

### handleTouchEnd(event: TouchEvent)
```javascript
/**
 * Process touch end and determine if swipe gesture occurred
 * @param {TouchEvent} event - Browser touch event
 * @returns {void}
 */
function handleTouchEnd(event) {
  touchEndX = event.changedTouches[0].screenX;
  touchEndY = event.changedTouches[0].screenY;
  touchEndTime = performance.now();
  handleSwipeGesture();
}
```

### handleSwipeGesture()
```javascript
/**
 * Calculate swipe direction and trigger navigation if valid
 * Validates:
 * - Minimum distance (50px)
 * - Horizontal angle (within 30° of horizontal)
 * - Maximum duration (500ms for responsive feel)
 * @returns {void}
 */
function handleSwipeGesture() {
  const deltaX = touchEndX - touchStartX;
  const deltaY = touchEndY - touchStartY;
  const distance = Math.abs(deltaX);
  const angle = Math.abs(Math.atan2(deltaY, deltaX) * 180 / Math.PI);

  // Only process if primarily horizontal and sufficient distance
  if ((angle < 30 || angle > 150) && distance > 50) {
    if (deltaX > 0) {
      showPreviousImage(); // Swipe right
    } else {
      showNextImage(); // Swipe left
    }
  }
}
```

### Modified: openFullscreen(globalIndex: number)
```javascript
/**
 * Open fullscreen overlay with progressive image loading
 * CHANGED: Now displays thumbnail immediately, loads original in background
 * CHANGED: Now uses flat globalIndex across ALL categories
 *
 * @param {number} globalIndex - Index of image in flat allImages array
 * @returns {void}
 *
 * Performance Requirements:
 * - Thumbnail display: <50ms
 * - Modal open animation: 250ms (CSS transition)
 * - Original load: Variable (network-dependent), non-blocking
 *
 * Progressive Loading Strategy:
 * 1. Display thumbnail immediately from data-thumbnail-src
 * 2. Create new Image() object for original
 * 3. On original.onload: Swap src and add 'loaded' class
 * 4. On original.onerror: Keep thumbnail, log warning
 * 5. Cancel previous load if user navigates before completion
 *
 * Cross-Category Navigation:
 * - globalIndex spans ALL categories (flattened array)
 * - Category label updates when image.category changes
 * - No special boundary handling needed (seamless wrapping)
 */
function openFullscreen(globalIndex) {
  // ... existing validation and setup ...

  const imageItem = allImages[globalIndex];  // From flat array

  // NEW: Cancel previous image load
  if (currentImageLoader) {
    currentImageLoader = null;
  }

  // NEW: Display thumbnail immediately
  const thumbnailSrc = imageItem.thumbnailSrc;
  const originalSrc = imageItem.originalSrc;
  modalImg.src = thumbnailSrc;
  modalImg.classList.remove('loaded');

  // NEW: Update category label (may have crossed category boundary)
  modalCategory.textContent = imageItem.categoryName;

  // NEW: Preload original in background
  currentImageLoader = new Image();
  currentImageLoader.onload = function() {
    if (currentImageLoader === this) { // Still current image
      modalImg.src = originalSrc;
      modalImg.classList.add('loaded');
    }
  };
  currentImageLoader.onerror = function() {
    console.warn(`Failed to load original: ${originalSrc}`);
  };
  currentImageLoader.src = originalSrc;

  // ... existing modal display logic ...
}
```

### Modified: showNextImage()
```javascript
/**
 * Navigate to next image in flat array (crosses category boundaries)
 * CHANGED: Uses modulo arithmetic for seamless wrapping
 */
function showNextImage() {
  if (!isOpen) return;
  currentImageIndex = (currentImageIndex + 1) % allImages.length;
  openFullscreen(currentImageIndex);
}
```

### Modified: showPreviousImage()
```javascript
/**
 * Navigate to previous image in flat array (crosses category boundaries)
 * CHANGED: Uses modulo arithmetic for seamless wrapping
 */
function showPreviousImage() {
  if (!isOpen) return;
  currentImageIndex = (currentImageIndex - 1 + allImages.length) % allImages.length;
  openFullscreen(currentImageIndex);
}
```

**Performance Guarantees**:
- Thumbnail display latency: <100ms (target: <50ms)
- Swipe gesture recognition: <16ms (60fps)
- Image load cancellation: Immediate (next frame)
- Focus trap: No delay (synchronous)

**Error Handling**:
- Missing DOM elements: Silent fail (function guards with early return)
- Invalid image index: Silent fail (boundary checks)
- Original image load failure: Keep thumbnail, log warning
- Invalid touch coordinates: Ignore gesture

**Browser Compatibility**:
- TouchEvent API: iOS Safari 13.4+, Android Chrome 90+
- Image() preloading: Universal (IE6+)
- dataset API: Universal (IE11+)
- Performance API: Universal (IE10+)

---

## Module 2: gallery.css

**Purpose**: Visual styles for gallery layout and banner

**Modified Selectors**:

### body
```css
/* CONTRACT: Remove padding, prevent horizontal scroll */
body {
  /* ... existing styles ... */
  padding: 0;                                        /* CHANGED: Remove padding */
  overflow-x: hidden;                                /* NEW: Prevent horizontal scroll */
  max-width: 100vw;                                  /* NEW: Constrain to viewport */
}
```

**Guarantees**:
- No global padding (content sections define their own spacing)
- No horizontal scrollbar under any conditions
- Vertical scrolling unaffected

### .gallery
```css
/* CONTRACT: Content container with horizontal padding */
.gallery {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 var(--spacing-unit);                    /* NEW: Add horizontal padding */
}
```

**Guarantees**:
- Content has proper spacing on sides (1rem)
- Centered container for wide viewports
- Banner can extend edge-to-edge outside this container

### .gallery-banner
```css
/* CONTRACT: Full-width banner extending edge-to-edge */
.gallery-banner {
  position: relative;
  width: 100%;                                       /* SIMPLIFIED: Just 100%, no calculations */
  overflow: hidden;                                  /* ENSURE: No content overflow */
  margin-bottom: calc(var(--spacing-unit) * 2);
  /* No negative margins needed */
}
```

**Guarantees**:
- Banner width = full viewport width (naturally, due to body padding: 0)
- No horizontal scrollbar on any viewport size (320px - 2560px)
- No negative margins (eliminates sub-pixel rendering artifacts)
- No black line bug (simpler layout, no margin escaping)

### .image-item img[loading="lazy"]
```css
/* CONTRACT: Subtle loading animation */
.image-item img[loading="lazy"] {
  background: linear-gradient(
    90deg,
    var(--color-bg-elevated) 0%,
    rgba(255, 255, 255, 0.3) 50%,              /* CHANGED: Reduced contrast */
    var(--color-bg-elevated) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 2.0s ease-in-out infinite;  /* CHANGED: Slower, smoother */
}
```

**Guarantees**:
- Animation duration: 2.0s (slower than current 1.5s)
- Contrast reduction: rgba(255, 255, 255, 0.3) vs previous #f8f8f8
- Dark mode: Even more subtle (rgba(255, 255, 255, 0.05))
- Respects prefers-reduced-motion (disables animation)



---

## Module 3: fullscreen.css

**Purpose**: Fullscreen overlay modal styles

**Modified Selectors**:

### .modal-content img
```css
/* CONTRACT: Larger image display in overlay */
.modal-content img {
  max-width: 100%;
  max-height: 80vh;                                /* CHANGED: Increased from 70vh */
  width: auto;
  height: auto;
  object-fit: contain;
  /* ... existing styles ... */
}

@media (max-width: 768px) {
  .modal-content img {
    max-height: 75vh;                              /* CHANGED: Increased from 60vh */
  }
}
```

**Guarantees**:
- Desktop: Image occupies up to 80% of viewport height (increased from 70%)
- Mobile: Image occupies up to 75% of viewport height (increased from 60%)
- Aspect ratio always maintained (object-fit: contain)
- Minimum metadata space: ~15-20vh remaining

### .modal-category
```css
/* CONTRACT: De-emphasized category label */
.modal-category {
  font-size: 0.75rem;                              /* CHANGED: Reduced from 0.875rem */
  opacity: 0.7;                                    /* CHANGED: Reduced from 0.8 */
  font-style: italic;
  /* ... existing styles ... */
}
```

**Guarantees**:
- Font size: 12px at default 16px root (WCAG AA minimum)
- Contrast: ~14:1 (white text at 0.7 opacity on dark overlay)
- Visual hierarchy: Category < Description < Title

### #modal-image (NEW class-based styling)
```css
/* CONTRACT: Smooth transition from thumbnail to original */
#modal-image {
  transition: opacity 0.3s ease;                   /* NEW: Smooth fade-in */
}

#modal-image:not(.loaded) {
  opacity: 0.95;                                   /* NEW: Subtle hint loading */
}

#modal-image.loaded {
  opacity: 1;                                      /* NEW: Full opacity when original loaded */
}
```

**Guarantees**:
- Transition duration: 300ms (smooth but not slow)
- Loading state visible: 95% opacity (subtle, not distracting)
- Loaded state: 100% opacity (crisp original image)

---

## CSS Custom Properties Contract

**Existing** (unchanged):
```css
:root {
  --spacing-unit: 1rem;
  --banner-height-desktop: 40vh;
  --banner-height-tablet: 30vh;
  --banner-height-mobile: 25vh;
  --transition-fast: 150ms;
  --transition-normal: 250ms;
  --transition-slow: 400ms;
  --easing-smooth: cubic-bezier(0.4, 0.0, 0.2, 1);
}
```

**Guarantees**:
- All components use these variables consistently
- Changing these values updates all dependent styles
- Media queries respect breakpoints (768px, 1024px)

---

## Integration Contract

**Initialization Order**:
1. HTML parsed → DOM ready
2. CSS loaded → Styles applied
3. `fullscreen.js` executes → Event listeners attached
4. `gallery.js` executes → Justified layout calculated
5. `layout.js` executes → Image positions finalized
6. `a11y.js` executes → Accessibility features enabled

**Event Flow (User Opens Image)**:
```
1. User clicks .image-item
   ↓
2. fullscreen.js → openFullscreen(index)
   ↓
3. Modal aria-hidden="false", display: flex
   ↓
4. Thumbnail displayed (<50ms)
   ↓
5. CSS transition: opacity 0 → 1 (250ms)
   ↓
6. Image() preload started (background, non-blocking)
   ↓
7. Focus moved to .modal-close button
   ↓
8. (Later) Original loads → Smooth swap (300ms transition)
```

**Event Flow (User Swipes on Mobile)**:
```
1. User touches #fullscreen-modal
   ↓
2. touchstart event → Record coordinates
   ↓
3. User moves finger
   ↓
4. User lifts finger
   ↓
5. touchend event → Calculate angle/distance
   ↓
6. If valid swipe: showNextImage() / showPreviousImage()
   ↓
7. openFullscreen(newIndex) → Repeat thumbnail → original flow
```

---

## Testing Contracts

**Unit Tests** (JavaScript):
- Mock TouchEvent for swipe detection
- Mock Image() constructor for load simulation
- Verify gesture validation logic (angle, distance)
- Verify load cancellation on navigation

**Integration Tests** (Playwright):
- Verify thumbnail displays <100ms on slow network (Fast 3G throttle)
- Verify swipe left/right navigates images
- Verify no horizontal scroll on mobile (320px, 375px, 414px)
- Verify overlay image size increase (measure computed height)

**Accessibility Tests** (axe-playwright):
- Verify modal focus trap still works
- Verify keyboard navigation unchanged
- Verify ARIA attributes correct
- Verify contrast ratios (category label at 0.7 opacity)

**Visual Regression Tests** (Manual):
- Banner edge-to-edge on mobile (no white borders)
- No black line in top-left corner
- Category label less prominent than title
- Shimmer animation slower and more subtle

---

## Deprecations

**None**. This feature is purely additive. All existing public interfaces remain unchanged.

---

## Future Considerations

**Not in Scope** (potential future enhancements):
- Pinch-to-zoom gesture detection (requires more complex touch tracking)
- Real-time swipe visual feedback (drag image left/right during gesture)
- Preloading adjacent images (optimize network usage)
- Service Worker caching strategy (offline support)
- WebP/AVIF format detection (progressive enhancement)

These are intentionally excluded to maintain simplicity and avoid violating constitution principles (minimal dependencies, static-first architecture).

---

## Summary

This contract defines the public interfaces and guarantees for frontend polish improvements. All changes maintain backward compatibility, zero external dependencies, and static-first architecture. Performance budgets respected (≤5KB additional JS, negligible CSS change). Accessibility maintained (keyboard navigation, ARIA, contrast ratios). Browser compatibility: Modern browsers only (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+).
