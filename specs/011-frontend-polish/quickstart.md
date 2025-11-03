# Quickstart: Frontend Polish & Mobile Improvements

**Feature**: 011-frontend-polish
**Branch**: `011-frontend-polish`
**Date**: November 3, 2025

## Overview

This guide helps developers test and validate the frontend polish improvements: mobile layout fixes, touch swipe gestures, progressive image loading, optimized overlay layout, and refined loading animations.

---

## Prerequisites

- Python 3.11+ with uv installed
- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- Mobile device or browser DevTools for mobile emulation

---

## Quick Setup

```bash
# 1. Checkout the feature branch
git checkout 011-frontend-polish

# 2. Install dependencies (if not already installed)
uv sync

# 3. Build the gallery
uv run exposure

# 4. Serve locally (use any static file server)
python -m http.server 8000 -d dist/

# Open browser to http://localhost:8000
```

---

## Testing Guide

### Test 1: Mobile Layout (No Horizontal Scroll)

**What to test**: Banner and gallery should fit within viewport width on all mobile sizes.

**Steps**:
1. Open DevTools → Toggle device toolbar (Cmd/Ctrl + Shift + M)
2. Test these viewport widths:
   - 320px (iPhone SE)
   - 375px (iPhone 12/13 Mini)
   - 414px (iPhone 12/13 Pro Max)
   - 360px (Samsung Galaxy)
3. Scroll through entire page
4. Check for horizontal scrollbar (should be none)

**Expected**:
- ✅ No horizontal scrollbar at any viewport width
- ✅ Banner extends edge-to-edge (no white borders)
- ✅ All content stays within viewport
- ✅ No black line in top-left corner of banner

**How to verify**:
```javascript
// In browser console:
document.body.scrollWidth === window.innerWidth  // Should be true
```

---

### Test 2: Touch Swipe Navigation (Mobile Overlay)

**What to test**: Swipe left/right in fullscreen overlay to navigate images.

**Steps (Physical Device)**:
1. Open gallery on mobile device
2. Tap any image to open overlay
3. Swipe left (next image) or right (previous image)
4. Try multiple swipes in a row

**Steps (DevTools Emulation)**:
1. Open DevTools → Device toolbar → Select mobile device
2. Enable "Touch" in sensors (if available)
3. Click and drag left/right on overlay image
4. Note: Emulation may not perfectly replicate touch behavior

**Expected**:
- ✅ Swipe left → Shows next image in same category
- ✅ Swipe right → Shows previous image in same category
- ✅ Vertical swipe → Ignored (doesn't trigger navigation)
- ✅ Diagonal swipe → Ignored (unless primarily horizontal)
- ✅ Swipe at first image → No navigation (subtle feedback)
- ✅ Swipe at last image → No navigation (subtle feedback)

**Manual verification**:
- Swipe should feel natural (not too sensitive, not too sluggish)
- 50px minimum swipe distance required
- Angle must be within 30° of horizontal

---

### Test 3: Progressive Image Loading

**What to test**: Thumbnail appears immediately, original loads in background.

**Steps**:
1. Open DevTools → Network tab → Throttling: "Fast 3G"
2. Click any image to open overlay
3. Observe loading sequence

**Expected**:
- ✅ Thumbnail displays immediately (<100ms)
- ✅ Overlay opens without blank screen
- ✅ Original image loads in background (see network waterfall)
- ✅ Smooth transition from thumbnail to original (300ms fade)
- ✅ If you navigate before original loads, new image shows immediately

**Performance verification**:
```javascript
// In fullscreen.js, temporary debug code:
const startTime = performance.now();
// ... after thumbnail display ...
console.log(`Thumbnail latency: ${performance.now() - startTime}ms`); // Should be <100ms
```

**Network throttling test**:
- Fast 3G: Original should load within 2-3 seconds, thumbnail visible immediately
- Slow 3G: Original may take 5-10 seconds, thumbnail remains visible
- Offline: Original fails, thumbnail stays (check console warning)

---

### Test 4: Optimized Overlay Layout

**What to test**: Image is larger in overlay, category label is less prominent.

**Steps**:
1. Open overlay with any image (desktop)
2. Measure image height visually
3. Compare to current version (if available)

**Expected**:
- ✅ Desktop: Image up to 80% of viewport height (increased from 70vh)
- ✅ Mobile: Image up to 75% of viewport height (increased from 60vh)
- ✅ Category label: Smaller font, reduced opacity
- ✅ Visual hierarchy: Title > Description > Category
- ✅ Adequate spacing below image for metadata (≥1rem)

**Visual measurement** (browser console):
```javascript
const img = document.querySelector('#modal-image');
const computedStyle = getComputedStyle(img);
console.log('Max height:', computedStyle.maxHeight);
// Desktop: Should be "80vh"
// Mobile: Should be "75vh"

const category = document.querySelector('.modal-category');
console.log('Category font size:', getComputedStyle(category).fontSize);
// Should be "12px" (0.75rem)
console.log('Category opacity:', getComputedStyle(category).opacity);
// Should be "0.7"
```

---

### Test 5: Subtle Loading Animation

**What to test**: Shimmer animation on lazy-loaded images is slower and less flashy.

**Steps**:
1. Clear browser cache (Cmd/Ctrl + Shift + Delete)
2. Reload page with DevTools Network tab open
3. Scroll through gallery slowly
4. Observe shimmer animation on images as they load

**Expected**:
- ✅ Animation duration: 2.0 seconds (slower than before)
- ✅ Animation easing: Smooth (ease-in-out)
- ✅ Contrast: Subtle gradient (not high contrast)
- ✅ Dark mode: Even more subtle (barely visible)
- ✅ prefers-reduced-motion: Animation disabled

**Visual inspection**:
- Compare to current version (if available)
- Should feel "professional" not "loading-indicator"
- Multiple loading images shouldn't feel overwhelming

---

## Automated Testing

### Run Unit Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file (NEW)
uv run pytest tests/integration/test_responsive_layout.py
uv run pytest tests/e2e/test_fullscreen_overlay.py
```

### Run Accessibility Tests

```bash
# Requires Playwright browsers installed
uv run playwright install chromium

# Run accessibility scan
uv run pytest tests/integration/test_accessibility.py -v
```

**Expected**: All axe tests pass, no critical violations

### Run Asset Budget Tests

```bash
# Verify CSS/JS size limits
uv run pytest tests/integration/test_asset_budgets.py -v
```

**Expected**:
- ✅ HTML ≤30KB uncompressed
- ✅ CSS ≤25KB uncompressed
- ✅ JS ≤75KB uncompressed (should be ~30KB with changes)

---

## Manual Testing Checklist

### Desktop (1920x1080)
- [ ] No horizontal scroll
- [ ] Banner edge-to-edge
- [ ] Keyboard navigation works (arrow keys, Esc, Tab)
- [ ] Overlay image uses 80vh height
- [ ] Category label de-emphasized
- [ ] Progressive loading: thumbnail → original

### Tablet (768x1024)
- [ ] No horizontal scroll
- [ ] Banner responsive (30vh height)
- [ ] Touch overlay navigation works
- [ ] Overlay image appropriate size
- [ ] Loading animation subtle

### Mobile (375x667 - iPhone)
- [ ] No horizontal scroll (critical)
- [ ] Banner edge-to-edge, no white borders
- [ ] No black line near banner (top-left)
- [ ] Swipe left/right works smoothly
- [ ] Overlay image uses 75vh height
- [ ] Thumbnail appears instantly
- [ ] Can navigate while original loading

### Mobile (320x568 - iPhone SE)
- [ ] No horizontal scroll (critical)
- [ ] All content readable
- [ ] Swipe gestures reliable
- [ ] Metadata not cramped in overlay

---

## Debugging Tips

### Horizontal Scroll Issue

```javascript
// Find elements wider than viewport
Array.from(document.querySelectorAll('*')).forEach(el => {
  if (el.scrollWidth > document.documentElement.clientWidth) {
    console.log('Overflowing element:', el, 'Width:', el.scrollWidth);
  }
});
```

### Touch Gesture Not Working

```javascript
// Check touch event listeners
window.fullscreenDebug.getCurrentIndex(); // Should return index when overlay open

// Check browser console for errors
// Verify TouchEvent is available:
console.log('TouchEvent' in window); // Should be true on mobile
```

### Progressive Loading Not Working

```javascript
// Check data attributes present
document.querySelector('.image-item').dataset;
// Should have: thumbnailSrc, originalSrc, title, category

// Check Image() preloading
// See Network tab → Filter: "Img" → Look for duplicate requests (thumbnail + original)
```

### Performance Issues

```javascript
// Measure fullscreen open latency
performance.mark('overlay-start');
// ... openFullscreen() called ...
performance.mark('overlay-thumbnail-shown');
performance.measure('Overlay Latency', 'overlay-start', 'overlay-thumbnail-shown');
console.log(performance.getEntriesByName('Overlay Latency')[0].duration); // Should be <100ms
```

---

## Browser Compatibility Testing

### Required Browsers

1. **Chrome 90+** (Desktop + Mobile)
   - Full feature support
   - Touch gesture testing via DevTools emulation

2. **Safari 14+** (iOS)
   - Critical for touch gesture testing
   - Test on physical iPhone if possible

3. **Firefox 88+** (Desktop)
   - Verify layout consistency
   - Check CSS compatibility

4. **Edge 90+** (Desktop)
   - Chromium-based, should match Chrome

### Known Limitations

- **Safari 13.3 and below**: TouchEvent API limited (not supported)
- **IE11**: Not supported (project targets modern browsers only)
- **DevTools touch emulation**: May not perfectly replicate physical touch behavior

---

## Performance Benchmarks

### Target Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Thumbnail display latency | <100ms | `performance.now()` before/after |
| Swipe gesture recognition | <16ms (60fps) | Touch event handler execution time |
| Original image load cancellation | <50ms | Navigation during load |
| Modal open animation | 250ms | CSS transition duration |
| Thumbnail → original transition | 300ms | CSS opacity transition |
| Horizontal scroll | 0px | `body.scrollWidth === innerWidth` |

### Lighthouse Scores

```bash
# Run Lighthouse audit (Chrome DevTools)
# Or use CLI:
npx lighthouse http://localhost:8000 --view --throttling-method=simulate
```

**Expected**:
- Performance: ≥90
- Accessibility: ≥90
- Best Practices: ≥90
- SEO: ≥90

---

## Troubleshooting

### "Thumbnail not showing immediately"

**Possible causes**:
- `data-thumbnail-src` attribute missing or incorrect
- Network slow (check DevTools Network tab)
- Browser cache disabled (thumbnails should be cached)

**Fix**: Verify Jinja2 template generates correct data attributes

### "Swipe not working on iOS Safari"

**Possible causes**:
- Touch event listeners not attached
- JavaScript error in console
- Angle threshold too strict

**Fix**: Check browser console for errors, verify `touchstart`/`touchend` listeners active

### "Horizontal scroll still visible"

**Possible causes**:
- Banner width calculation incorrect
- Another element overflowing
- Browser-specific rendering quirk

**Fix**: Use debugging script (see "Debugging Tips") to find overflowing element

---

## Rollback Plan

If critical issues found:

```bash
# Revert changes
git checkout main
uv run exposure
```

Or revert specific files:
```bash
# Revert CSS only
git checkout main -- src/static/css/gallery.css src/static/css/fullscreen.css

# Revert JS only
git checkout main -- src/static/js/fullscreen.js
```

---

## Next Steps After Validation

1. ✅ All manual tests pass → Commit changes
2. ✅ All automated tests pass → Push to remote
3. ✅ Create pull request with test evidence (screenshots/videos)
4. ✅ Request review from maintainer
5. ✅ Merge to main after approval
6. ✅ Update CHANGELOG.md with user-facing improvements

---

## Support

- **Feature spec**: `specs/011-frontend-polish/spec.md`
- **Research notes**: `specs/011-frontend-polish/research.md`
- **Data model**: `specs/011-frontend-polish/data-model.md`
- **Contracts**: `specs/011-frontend-polish/contracts/javascript-interfaces.md`

---

**Last Updated**: November 3, 2025
**Author**: Generated by /speckit.plan command
