# Developer Quickstart: Mobile Full-Screen & Performance

**Feature**: 010-mobile-fullscreen-performance
**Date**: December 8, 2025
**Status**: Complete

## Quick Setup (5 minutes)

This guide gets you running with blur placeholder generation, mobile full-screen testing, and performance validation.

---

## Prerequisites

- Python 3.11+ installed
- [uv](https://github.com/astral-sh/uv) package manager
- Mobile device or browser DevTools mobile emulation
- Playwright browsers for accessibility testing (optional)

---

## 1. Install Dependencies

```bash
cd /home/surt91/code/exposure

# Install Python dependencies
uv sync

# Install Playwright browsers (for accessibility tests)
uv run playwright install --with-deps chromium
```

---

## 2. Test Blur Placeholder Generation

### Generate Gallery with Blur Placeholders

```bash
# Build gallery (blur placeholders auto-generated)
uv run exposure

# Check generated HTML for data URLs
grep -o 'data:image/jpeg;base64' dist/index.html | wc -l
# Should output number of images in gallery
```

### Verify Blur Placeholder Size

```bash
# Check HTML file size
ls -lh dist/index.html

# Measure data URL sizes (should be ~800 bytes each)
python -c "
import re
with open('dist/index.html') as f:
    html = f.read()
    data_urls = re.findall(r'data:image/jpeg;base64,[^\'\"]+', html)
    sizes = [len(url) for url in data_urls]
    print(f'Found {len(sizes)} blur placeholders')
    print(f'Average size: {sum(sizes)//len(sizes)} bytes')
    print(f'Max size: {max(sizes)} bytes')
"
```

### Inspect Build Cache

```bash
# Check blur placeholders in cache
cat .exposure-cache/build-cache.json | jq '.images[].blur_placeholder' | head -20
```

---

## 3. Test Mobile Full-Screen Mode

### Option A: Real Mobile Device

1. **Build and serve gallery**:
   ```bash
   uv run exposure
   cd dist
   python -m http.server 8000
   ```

2. **Open on mobile device**:
   - Connect phone to same WiFi network
   - Get computer's local IP: `hostname -I | awk '{print $1}'`
   - Open `http://<YOUR_IP>:8000` on mobile browser

3. **Test full-screen**:
   - Tap any image → should fill entire screen
   - Tap image again → controls appear for 3 seconds
   - Swipe left/right → navigate between images
   - Controls should auto-hide after 3 seconds

### Option B: Browser DevTools Emulation

1. **Open in Chrome DevTools**:
   ```bash
   # Serve locally
   cd dist && python -m http.server 8000
   ```
   - Open `http://localhost:8000` in Chrome
   - Press `F12` → Toggle device toolbar (Ctrl+Shift+M)
   - Select device: iPhone 12 Pro or Pixel 5

2. **Test full-screen**:
   - Click image → fullscreen overlay opens
   - Check if controls are hidden by default (mobile viewport)
   - Click image area → controls should appear
   - Wait 3 seconds → controls should auto-hide

3. **Test orientation change**:
   - In DevTools, rotate device (portrait ↔ landscape)
   - Verify image rescales correctly
   - Verify controls remain hidden after rotation

---

## 4. Verify Blur Placeholder Loading

### Test Progressive Load Sequence

1. **Throttle Network**:
   - Chrome DevTools → Network tab → Throttling: Slow 3G
   - Clear cache (Ctrl+Shift+Del)

2. **Open Gallery**:
   - Reload page
   - Observe loading sequence:
     1. Blur placeholders appear INSTANTLY (no delay)
     2. Thumbnails load and fade in (~500ms)
     3. Original images load when clicked (~2-3s)

3. **Verify Blur Visibility**:
   - Blur placeholders should be visible BEFORE any network requests complete
   - No "blank white boxes" during load
   - Smooth fade transitions (not jarring "pop-in")

### Measure Perceived Performance

```bash
# Use Lighthouse CI to measure time-to-first-content
npx lighthouse http://localhost:8000 \
  --preset=desktop \
  --throttling-method=simulate \
  --throttling.cpuSlowdownMultiplier=4 \
  --only-categories=performance

# Key metrics to check:
# - First Contentful Paint (FCP): < 1.5s
# - Largest Contentful Paint (LCP): < 2.5s
# - Cumulative Layout Shift (CLS): < 0.1
```

---

## 5. Test Control Visibility (Mobile)

### Manual Testing Checklist

**Mobile viewport (<768px)**:
- [ ] Controls hidden by default when image opens
- [ ] Tap on image → controls fade in (300ms animation)
- [ ] Wait 3 seconds → controls auto-hide
- [ ] Tap again → controls reappear
- [ ] Click next/previous button → controls stay visible for 3 more seconds
- [ ] Swipe to navigate → controls hide immediately
- [ ] Tab to focus button → controls become visible (keyboard accessibility)

**Desktop viewport (≥768px)**:
- [ ] Controls always visible (no auto-hide)
- [ ] Clicking image does not hide controls
- [ ] Hover states work correctly

### Automated Visibility Testing

```javascript
// Add to tests/integration/test_control_visibility.js
test('controls auto-hide on mobile', async () => {
  // Set mobile viewport
  await page.setViewportSize({ width: 375, height: 667 });

  // Open fullscreen
  await page.click('.image-thumbnail');

  // Check controls are visible initially
  const controls = await page.locator('.fullscreen-controls');
  expect(await controls.evaluate(el =>
    window.getComputedStyle(el).opacity
  )).toBe('1');

  // Wait for auto-hide
  await page.waitForTimeout(3500);

  // Check controls are hidden
  expect(await controls.evaluate(el =>
    window.getComputedStyle(el).opacity
  )).toBe('0');
});
```

---

## 6. Performance Validation

### Run Existing Tests

```bash
# Unit tests (Python)
uv run pytest tests/unit/test_thumbnails.py -v

# Integration tests (blur placeholders)
uv run pytest tests/integration/test_blur_placeholders.py -v

# Accessibility tests (keyboard navigation in fullscreen)
uv run pytest tests/accessibility/test_fullscreen_a11y.py -v -m a11y
```

### Asset Budget Checks

```bash
# Check HTML size budget
uv run pytest tests/integration/test_asset_budgets.py::test_html_size_budget -v

# Check individual blur placeholder sizes
uv run pytest tests/integration/test_blur_placeholders.py::test_placeholder_size_limit -v
```

### Lighthouse Performance Audit

```bash
# Build production gallery
uv run exposure

# Serve locally
cd dist && python -m http.server 8000 &

# Run Lighthouse
npx lighthouse http://localhost:8000 \
  --preset=desktop \
  --throttling-method=simulate \
  --output=html \
  --output-path=./lighthouse-report.html

# Open report
xdg-open lighthouse-report.html

# Target scores:
# - Performance: ≥ 90
# - Accessibility: ≥ 90
# - Best Practices: ≥ 90
```

---

## 7. Debug Common Issues

### Blur Placeholders Not Appearing

**Symptom**: Images show white background, no blur preview

**Debug**:
```bash
# Check if blur placeholders generated
cat .exposure-cache/build-cache.json | jq '.images[].blur_placeholder' | head

# Verify data URLs in HTML
grep 'data:image/jpeg;base64' dist/index.html

# Check build logs
uv run exposure 2>&1 | grep -i "blur\|placeholder"
```

**Solution**: Verify `BlurPlaceholderConfig.enabled = True` in settings

---

### Full-Screen Not Working on iOS

**Symptom**: Image overlay opens but browser UI remains visible

**Debug**:
```javascript
// Check if fallback mode active (in browser console)
console.log('Fullscreen mode:', fullscreenManager.mode);
// Should output: "fallback" on iOS
```

**Expected**: iOS Safari doesn't support Fullscreen API for images, fallback mode is correct behavior

---

### Controls Not Auto-Hiding

**Symptom**: Navigation controls remain visible permanently on mobile

**Debug**:
```javascript
// Check if mobile detection working (in browser console)
console.log('Is mobile:', controlManager.isMobile);
console.log('Viewport width:', window.innerWidth);

// Check CSS
const controls = document.querySelector('.fullscreen-controls');
console.log('Opacity:', window.getComputedStyle(controls).opacity);
```

**Solution**:
1. Verify viewport width < 768px
2. Check CSS media query: `@media (max-width: 767px)`
3. Verify `visible` class toggling correctly

---

### Slow Build Time

**Symptom**: Gallery build takes >5 minutes

**Debug**:
```bash
# Profile build time
time uv run exposure

# Check cache hit rate
cat .exposure-cache/build-cache.json | \
  jq '[.images[].blur_placeholder != null] | group_by(.) | map({key: .[0], count: length})'
```

**Solution**:
1. Ensure build cache is being used (incremental builds)
2. Reduce blur placeholder target size (default 20px)
3. Verify Pillow using optimized libraries (libjpeg-turbo)

---

## 8. Development Workflow

### Make Changes to Blur Placeholder Generation

```bash
# Edit thumbnail generator
vim src/generator/thumbnails.py

# Run tests
uv run pytest tests/unit/test_thumbnails.py -k blur -v

# Rebuild gallery
uv run exposure

# Verify changes
grep -c 'data:image/jpeg;base64' dist/index.html
```

### Make Changes to Frontend JavaScript

```bash
# Edit fullscreen or control visibility
vim src/static/js/fullscreen.js
vim src/static/js/gallery.js

# No rebuild needed (static files copied directly)
# Just refresh browser to see changes

# Run accessibility tests
uv run pytest tests/accessibility/test_fullscreen_a11y.py -v -m a11y
```

### Update CSS Transitions

```bash
# Edit styles
vim src/static/css/style.css

# Test in browser DevTools first
# Then copy finalized styles back to source

# Verify reduced motion support
# Chrome DevTools → Rendering → Emulate CSS prefers-reduced-motion
```

---

## 9. Testing Checklist (Before PR)

### Build & Unit Tests
- [ ] `uv run pytest tests/unit/ -v` (all pass)
- [ ] `uv run exposure` (builds without errors)
- [ ] Build time increase < 20% (for 100 images: +10s acceptable)

### Blur Placeholders
- [ ] All images have blur placeholders in HTML
- [ ] Each placeholder < 1.5KB
- [ ] Total HTML size increase < 100KB
- [ ] Blur visible BEFORE network requests

### Full-Screen Mode
- [ ] Works on Chrome Mobile (real device)
- [ ] Works on Safari iOS (fallback mode)
- [ ] Orientation changes handled correctly
- [ ] ESC key exits fullscreen

### Control Visibility
- [ ] Hidden by default on mobile
- [ ] Tap reveals controls (300ms fade-in)
- [ ] Auto-hide after 3 seconds
- [ ] Keyboard accessible (Tab to focus)
- [ ] Always visible on desktop

### Accessibility
- [ ] `uv run pytest -m a11y -v` (all pass)
- [ ] Keyboard navigation works in fullscreen
- [ ] Screen reader announcements correct
- [ ] WCAG 2.1 AA contrast maintained

### Performance
- [ ] Lighthouse Performance ≥ 90
- [ ] Lighthouse Accessibility ≥ 90
- [ ] FCP < 1.5s, LCP < 2.5s, CLS < 0.1
- [ ] No console errors or warnings

---

## 10. Useful Commands Reference

```bash
# Build gallery
uv run exposure

# Run all tests
uv run pytest -v

# Run specific test category
uv run pytest -m a11y -v                    # Accessibility only
uv run pytest tests/unit/ -v                # Unit tests only
uv run pytest tests/integration/ -v         # Integration tests only

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Type checking
uv run ty check src/

# Linting
uv run ruff check .
uv run ruff format .

# Serve gallery locally
cd dist && python -m http.server 8000

# Clear build cache (force regeneration)
rm -rf .exposure-cache/

# Check asset budgets
uv run pytest tests/integration/test_asset_budgets.py -v
```

---

## Next Steps

After completing this quickstart:

1. **Read contracts**: See `contracts/` for detailed API specifications
2. **Review data model**: See `data-model.md` for entity definitions
3. **Check tasks**: See `tasks.md` (generated by `/speckit.tasks` command)
4. **Implement feature**: Follow task breakdown in `tasks.md`

---

## Getting Help

**Common Resources**:
- Feature spec: `specs/010-mobile-fullscreen-performance/spec.md`
- Research findings: `specs/010-mobile-fullscreen-performance/research.md`
- API contracts: `specs/010-mobile-fullscreen-performance/contracts/`
- Existing code:
  - Thumbnail generation: `src/generator/thumbnails.py`
  - Fullscreen logic: `src/static/js/fullscreen.js`
  - Gallery layout: `src/static/js/gallery.js`

**Questions?**
- Check ADRs: `docs/decisions/`
- Review constitution: `.specify/memory/constitution.md`
- Read README: `README.md`

---

**Estimated Setup Time**: 5-10 minutes
**Estimated First Test Run**: 2-3 minutes
**Estimated End-to-End Validation**: 15-20 minutes
