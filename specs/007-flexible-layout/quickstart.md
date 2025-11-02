# Quickstart: Flexible Aspect-Ratio Image Layout

**Feature**: 007-flexible-layout
**Date**: 2025-11-02
**Estimated Time**: 4-6 hours
**Difficulty**: Moderate

## Overview

This guide walks through implementing flexible aspect-ratio image layout that displays images without cropping while maintaining visual balance and minimizing whitespace.

---

## Prerequisites

- ✅ Python 3.11+ with uv installed
- ✅ Familiarity with Pydantic models
- ✅ Basic JavaScript/ES6 knowledge
- ✅ Understanding of CSS Grid and positioning
- ✅ Git branch `007-flexible-layout` checked out

---

## Implementation Phases

### Phase 1: Extract Image Dimensions (Python) - 1 hour

**Goal**: Update scanner to extract width and height from image files.

#### 1.1 Update Image Model

**File**: `src/generator/model.py`

Add dimension fields to the `Image` class:

```python
class Image(BaseModel):
    filename: str = Field(min_length=1)
    file_path: Path
    category: str = Field(min_length=1)
    width: Optional[int] = None      # NEW
    height: Optional[int] = None     # NEW
    title: str = ""
    description: str = ""

    @property
    def aspect_ratio(self) -> Optional[float]:  # NEW
        """Calculate aspect ratio if dimensions available."""
        if self.width and self.height:
            return self.width / self.height
        return None
```

**Test**: Run existing model tests to ensure backward compatibility.

```bash
uv run pytest tests/unit/test_model.py -v
```

---

#### 1.2 Update Scanner

**File**: `src/generator/scan.py`

Modify the image scanning function to extract dimensions using Pillow:

```python
from PIL import Image as PILImage
import logging

logger = logging.getLogger(__name__)

def extract_dimensions(file_path: Path) -> tuple[Optional[int], Optional[int]]:
    """Extract width and height from image file.

    Args:
        file_path: Path to image file

    Returns:
        Tuple of (width, height) or (None, None) if extraction fails
    """
    try:
        with PILImage.open(file_path) as img:
            return img.size  # Returns (width, height)
    except Exception as e:
        logger.warning(f"Failed to extract dimensions from {file_path}: {e}")
        return None, None

# Update the existing scan logic to call extract_dimensions
# and pass width/height when creating Image objects
```

**Test**: Add unit test for dimension extraction.

```python
# tests/unit/test_scan.py
def test_extract_dimensions_jpg():
    """Test dimension extraction from JPEG file."""
    # Create test image or use fixture
    width, height = extract_dimensions(test_image_path)
    assert width == 1920
    assert height == 1080

def test_extract_dimensions_invalid_file():
    """Test handling of invalid image file."""
    width, height = extract_dimensions(Path("nonexistent.jpg"))
    assert width is None
    assert height is None
```

Run tests:
```bash
uv run pytest tests/unit/test_scan.py::test_extract_dimensions_jpg -v
```

---

#### 1.3 Update Build Process

**File**: `src/generator/build_html.py`

Pass extracted dimensions to Image model instances:

```python
# When creating Image objects, include dimensions
for file_path in image_files:
    width, height = extract_dimensions(file_path)

    image = Image(
        filename=file_path.name,
        file_path=file_path,
        category=category,
        width=width,      # NEW
        height=height,    # NEW
        title=yaml_entry.title if yaml_entry else "",
        description=yaml_entry.description if yaml_entry else ""
    )
```

**Test**: Run end-to-end test to verify dimensions in generated HTML.

```bash
uv run pytest tests/integration/test_end_to_end.py -v
```

---

### Phase 2: Update Templates (Jinja2) - 30 minutes

**Goal**: Add dimension data to HTML output.

#### 2.1 Update Image Template

**File**: `src/templates/index.html.j2`

Modify the image container to include dimensions:

```jinja
<div
    class="image-item"
    data-filename="{{ image['filename'] }}"
    data-category="{{ image['category'] }}"
    data-title="{{ image['title'] }}"
    data-description="{{ image['description'] }}"
    {% if image['width'] and image['height'] %}
    data-width="{{ image['width'] }}"
    data-height="{{ image['height'] }}"
    {% endif %}
>
    <img
        src="{{ image['src'] }}"
        alt="{{ image['alt_text'] }}"
        {% if image['width'] and image['height'] %}
        width="{{ image['width'] }}"
        height="{{ image['height'] }}"
        {% endif %}
        loading="lazy"
        decoding="async"
    />
{% if image['title'] %}
    <div class="image-caption">{{ image['title'] }}</div>
{% endif %}
</div>
```

**Key Changes**:
- Added `data-width` and `data-height` attributes (for JS)
- Added `width` and `height` attributes on `<img>` (for browser CLS prevention)
- Added `decoding="async"` for better performance
- Conditional rendering for backward compatibility

**Test**: Build gallery and verify HTML output.

```bash
uv run exposure
# Inspect build/index.html for data-width and width attributes
```

---

### Phase 3: Install Layout Library (JavaScript) - 15 minutes

**Goal**: Add justified-layout library for calculations.

#### 3.1 Add Vendored Library

The justified-layout library is vendored locally in `src/static/js/vendor/`:
- `justified-layout.js` - The library code
- `justified-layout.LICENSE` - License file

This approach:
- Ensures offline functionality
- Eliminates external CDN dependencies
- Provides better privacy (no third-party requests)
- Allows bundling with other assets during build

#### 3.2 Verify Library in Template

The library is automatically included during the asset bundling process. The bundled JavaScript will include the justified-layout library alongside the gallery code.

**Test**: Open built gallery in browser, check console:
```javascript
console.log(typeof justifiedLayout); // Should output "function"
```

---

### Phase 4: Implement Layout Algorithm (JavaScript) - 2 hours

**Goal**: Create layout calculation and application logic.

#### 4.1 Create Layout Module

**File**: `src/static/js/layout.js` (new file)

```javascript
/**
 * Flexible Image Layout
 * Calculates and applies justified layout to image gallery
 */

(function() {
  'use strict';

  /**
   * Initialize layout system
   */
  function init() {
    const galleries = document.querySelectorAll('.image-grid');

    galleries.forEach(gallery => {
      // Extract image data from DOM
      const imageData = extractImageData(gallery);

      if (imageData.length === 0) {
        console.warn('No images with dimensions found');
        return;
      }

      // Calculate initial layout
      const layout = calculateLayout(gallery, imageData);

      // Apply layout
      applyLayout(gallery, layout);

      // Setup resize handler
      setupResizeHandler(gallery, imageData);
    });
  }

  /**
   * Extract image dimensions from DOM
   */
  function extractImageData(gallery) {
    const items = gallery.querySelectorAll('.image-item');
    const data = [];

    items.forEach((item, index) => {
      const width = parseInt(item.dataset.width);
      const height = parseInt(item.dataset.height);

      if (width && height) {
        data.push({
          index: index,
          width: width,
          height: height,
          aspectRatio: width / height,
          element: item
        });
      }
    });

    return data;
  }

  /**
   * Calculate layout using justified-layout library
   */
  function calculateLayout(gallery, imageData) {
    const containerWidth = gallery.clientWidth;

    // Prepare input for justified-layout library
    const input = imageData.map(img => ({
      width: img.width,
      height: img.height
    }));

    // Calculate layout
    const geometry = justifiedLayout(input, {
      containerWidth: containerWidth,
      targetRowHeight: containerWidth < 640 ? 200 : 320,
      boxSpacing: 8,
      containerPadding: 0
    });

    return {
      geometry: geometry,
      imageData: imageData
    };
  }

  /**
   * Apply layout to DOM
   */
  function applyLayout(gallery, layout) {
    const { geometry, imageData } = layout;

    // Update gallery container
    gallery.style.position = 'relative';
    gallery.style.height = `${geometry.containerHeight}px`;
    gallery.classList.add('layout-calculated');

    // Position each image
    geometry.boxes.forEach((box, index) => {
      const item = imageData[index].element;

      item.style.position = 'absolute';
      item.style.left = `${box.left}px`;
      item.style.top = `${box.top}px`;
      item.style.width = `${box.width}px`;
      item.style.height = `${box.height}px`;
    });
  }

  /**
   * Setup responsive resize handler
   */
  function setupResizeHandler(gallery, imageData) {
    let resizeTimeout;

    window.addEventListener('resize', () => {
      clearTimeout(resizeTimeout);

      resizeTimeout = setTimeout(() => {
        const layout = calculateLayout(gallery, imageData);
        applyLayout(gallery, layout);
      }, 150); // Debounce 150ms
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
```

**Test**: Build and open gallery in browser. Images should arrange in justified layout.

---

#### 4.2 Add Layout Script to Template

**File**: `src/templates/index.html.j2`

Add layout.js after gallery.js:

```html
<script src="{{ js_href }}"></script>
<script src="js/layout.js"></script>
```

**Note**: Need to update build process to copy layout.js to output directory.

---

### Phase 5: Update Styles (CSS) - 1 hour

**Goal**: Update CSS to support positioned layout.

#### 5.1 Update Gallery Styles

**File**: `src/static/css/gallery.css`

Add/modify styles:

```css
/* Image Grid - Base (CSS Grid fallback) */
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: var(--gap);
  margin-bottom: var(--spacing-unit);
}

/* Image Grid - Enhanced with JS */
.image-grid.layout-calculated {
  display: block;
  position: relative;
  /* height set dynamically by JS */
}

/* Image Item - Base */
.image-item {
  position: relative;
  aspect-ratio: 4 / 3; /* Fallback */
  overflow: hidden;
  border-radius: var(--border-radius);
  background-color: var(--color-bg-elevated);
  cursor: pointer;
  transition: transform var(--transition-fast) var(--easing-smooth),
              box-shadow var(--transition-fast) var(--easing-smooth);
}

/* Image Item - Enhanced with JS */
.layout-calculated .image-item {
  aspect-ratio: auto; /* Let dimensions control aspect */
  /* position, left, top, width, height set by JS */
}

/* Image Element */
.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* Image Element - Enhanced with JS */
.layout-calculated .image-item img {
  object-fit: contain; /* Show full image without cropping */
}
```

**Key Changes**:
- `.layout-calculated` class added by JS when layout is applied
- Positioned layout only when JS is active
- Graceful fallback to CSS Grid without JS
- Changed `object-fit` from `cover` to `contain` to prevent cropping

---

### Phase 6: Testing - 1 hour

**Goal**: Verify functionality across different scenarios.

#### 6.1 Unit Tests

**File**: `tests/unit/test_scan.py`

```python
def test_extract_dimensions_multiple_formats():
    """Test dimension extraction from various image formats."""
    test_cases = [
        ('test.jpg', 1920, 1080),
        ('test.png', 800, 600),
        ('test.webp', 1600, 900)
    ]

    for filename, expected_width, expected_height in test_cases:
        width, height = extract_dimensions(fixtures_path / filename)
        assert width == expected_width
        assert height == expected_height
```

Run:
```bash
uv run pytest tests/unit/test_scan.py -v
```

---

#### 6.2 Integration Tests

**File**: `tests/integration/test_end_to_end.py`

Add test for dimensions in HTML:

```python
def test_generated_html_includes_dimensions(tmp_path):
    """Test that generated HTML includes image dimensions."""
    # Build gallery
    config = GalleryConfig(...)
    build_gallery(config)

    # Parse output HTML
    html_path = config.output_dir / "index.html"
    with open(html_path) as f:
        html = f.read()

    # Verify data attributes present
    assert 'data-width=' in html
    assert 'data-height=' in html

    # Verify img attributes present
    assert 'width=' in html
    assert 'height=' in html
```

---

#### 6.3 Visual Testing

**Manual Test Checklist**:

1. **Basic Layout**:
   - ✅ Images display without cropping
   - ✅ Rows have consistent heights
   - ✅ Minimal whitespace between images

2. **Mixed Aspect Ratios**:
   - ✅ Landscape images display correctly
   - ✅ Portrait images display correctly
   - ✅ Square images display correctly
   - ✅ Extreme ratios (panoramas) handled gracefully

3. **Responsive Behavior**:
   - ✅ Layout recalculates on window resize
   - ✅ Mobile layout (320px) works correctly
   - ✅ Desktop layout (1920px) works correctly

4. **Performance**:
   - ✅ Initial layout appears within 500ms
   - ✅ No visible layout shift (CLS = 0.0)
   - ✅ Smooth resize behavior

5. **Fallback**:
   - ✅ CSS Grid works without JavaScript
   - ✅ Images still clickable for fullscreen
   - ✅ Accessibility maintained

---

#### 6.4 Accessibility Testing

Run existing accessibility tests:

```bash
uv run pytest tests/accessibility/test_axe_a11y.py -v
```

Verify:
- ✅ Zero critical violations
- ✅ Images have alt text
- ✅ Keyboard navigation works
- ✅ Focus management maintained

---

#### 6.5 Performance Testing

**File**: `tests/integration/test_asset_budgets.py`

Verify JS size stays under budget:

```python
def test_javascript_budget():
    """Test that total JavaScript size is under 75KB."""
    js_files = list(Path("dist").glob("**/*.js"))
    total_size = sum(f.stat().st_size for f in js_files)

    # Should be well under 75KB
    assert total_size < 75 * 1024, f"JS size {total_size} exceeds 75KB budget"
```

Run:
```bash
uv run pytest tests/integration/test_asset_budgets.py -v
```

---

### Phase 7: Documentation - 30 minutes

**Goal**: Document the new feature and decision rationale.

#### 7.1 Create ADR

**File**: `docs/decisions/0007-flexible-layout-algorithm.md`

```markdown
# ADR 0007: Flexible Layout Algorithm

## Status
Accepted

## Context
The gallery currently uses CSS Grid with fixed 4:3 aspect ratio, which crops images. Users need to see complete images without cropping while maintaining visual balance.

## Decision
Implement justified layout algorithm using flickr/justified-layout library with client-side calculation executed before first paint.

## Consequences
### Positive
- Images display without cropping
- Visually balanced layout
- Industry-proven algorithm
- Responsive across all viewports
- Zero cumulative layout shift

### Negative
- Requires JavaScript for optimal layout (CSS Grid fallback available)
- Additional 5KB library size
- Slight calculation overhead (<20ms for 500 images)

## Alternatives Considered
- Masonry layout: Rejected due to irregular layout pattern
- Build-time calculation: Rejected due to lack of responsive behavior
- Custom algorithm: Rejected due to maintenance burden vs. proven solution
```

---

#### 7.2 Update README

**File**: `README.md`

Add section about flexible layout:

```markdown
### Flexible Layout

Exposure uses a justified layout algorithm that displays images at their original aspect ratios without cropping. Images are arranged in rows with consistent heights, creating a visually balanced and space-efficient gallery.

**Features**:
- No image cropping - see the complete composition
- Consistent visual sizing across different aspect ratios
- Responsive layout recalculates on window resize
- Works from mobile (320px) to 4K (3840px) displays
- Zero layout shift (CLS = 0.0) for optimal performance

**Fallback**: Without JavaScript, gallery displays in CSS Grid with fixed aspect ratio (current behavior).
```

---

## Verification Checklist

Before marking feature complete, verify:

- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ Accessibility tests pass (zero critical violations)
- ✅ Asset budgets met (JS < 75KB, CSS < 25KB, HTML < 30KB)
- ✅ Manual visual testing complete
- ✅ Performance verified (layout < 500ms, CLS = 0.0)
- ✅ Documentation updated (ADR, README)
- ✅ Code reviewed and approved
- ✅ Branch merged to main

---

## Troubleshooting

### Issue: Images still appear cropped

**Solution**: Verify `object-fit: contain` is applied when `.layout-calculated` class is active.

```css
.layout-calculated .image-item img {
  object-fit: contain;
}
```

---

### Issue: Layout shifts when images load

**Solution**: Ensure `width` and `height` attributes are present on `<img>` tags:

```html
<img width="1920" height="1080" ... />
```

Verify in browser DevTools Elements panel.

---

### Issue: Layout calculation is slow

**Solution**: Check number of images. If > 500, consider:
- Pagination
- Virtual scrolling
- Lazy layout calculation (calculate only visible images)

---

### Issue: justifiedLayout is not defined

**Solution**: Verify library script loads before layout.js:

```html
<!-- justified-layout library is bundled with gallery.js -->
<script src="gallery.js"></script>
```

Check Network tab in DevTools for 404 errors.

---

## Next Steps

After basic implementation:

1. **Optimization**: Add virtual scrolling for very large galleries (1000+ images)
2. **Configuration**: Add user-configurable target row height
3. **Animation**: Add smooth transitions when layout changes
4. **Print**: Optimize layout for print media
5. **SEO**: Ensure search engine compatibility

---

## Estimated Timeline

| Phase | Task | Time |
|-------|------|------|
| 1 | Extract dimensions (Python) | 1h |
| 2 | Update templates (Jinja2) | 0.5h |
| 3 | Install layout library | 0.25h |
| 4 | Implement layout (JavaScript) | 2h |
| 5 | Update styles (CSS) | 1h |
| 6 | Testing | 1h |
| 7 | Documentation | 0.5h |
| **Total** | | **6.25h** |

---

## Resources

- [flickr/justified-layout documentation](https://github.com/flickr/justified-layout)
- [Web.dev: Cumulative Layout Shift](https://web.dev/cls/)
- [MDN: img width/height](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#attr-width)
- [Feature Spec](./spec.md)
- [Data Model](./data-model.md)
- [Layout Algorithm API Contract](./contracts/layout-algorithm-api.md)
- [HTML Template Contract](./contracts/html-template-data.md)
