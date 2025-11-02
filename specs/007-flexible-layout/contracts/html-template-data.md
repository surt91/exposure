# HTML Template Data Contract

**Feature**: 007-flexible-layout
**Version**: 1.0.0
**Date**: 2025-11-02

## Overview

This contract defines the data structure passed from Python build system to Jinja2 templates and the expected HTML output format for flexible layout support.

---

## Template Input Contract

### Image Object (Enhanced)

The existing `Image` model passed to templates gains dimension fields.

**Python Type** (src/generator/model.py):
```python
class Image(BaseModel):
    filename: str
    file_path: Path
    category: str
    width: Optional[int] = None      # NEW
    height: Optional[int] = None     # NEW
    title: str = ""
    description: str = ""

    @property
    def alt_text(self) -> str:
        """Generate appropriate alt text for the image."""
        ...

    @property
    def aspect_ratio(self) -> Optional[float]:  # NEW
        """Calculate aspect ratio if dimensions available."""
        if self.width and self.height:
            return self.width / self.height
        return None
```

**Template Variable** (passed to index.html.j2):
```python
image_dict = {
    'filename': str,          # e.g., "IMG_1234.jpg"
    'category': str,          # e.g., "Landscapes"
    'title': str,             # e.g., "Mountain Sunrise"
    'description': str,       # e.g., "Early morning in the Alps"
    'alt_text': str,          # e.g., "Mountain Sunrise"
    'src': str,               # e.g., "images/IMG_1234.jpg"
    'width': int | None,      # NEW: e.g., 1920
    'height': int | None,     # NEW: e.g., 1080
}
```

**Validation Rules**:
- If `width` is not None, `height` must also be not None
- Both `width` and `height` must be positive integers when present
- Missing dimensions are acceptable for backward compatibility

---

## HTML Output Contract

### Image Container Element

Each image must be wrapped in a container with dimension data attributes.

**Required Structure**:
```html
<div
  class="image-item"
  data-filename="{{ image['filename'] }}"
  data-category="{{ image['category'] }}"
  data-title="{{ image['title'] }}"
  data-description="{{ image['description'] }}"
  data-width="{{ image['width'] }}"
  data-height="{{ image['height'] }}"
>
  <img
    src="{{ image['src'] }}"
    alt="{{ image['alt_text'] }}"
    width="{{ image['width'] }}"
    height="{{ image['height'] }}"
    loading="lazy"
    decoding="async"
  />
  {% if image['title'] %}
  <div class="image-caption">{{ image['title'] }}</div>
  {% endif %}
</div>
```

**Key Changes from Current**:
1. Added `data-width` and `data-height` attributes on container
2. Added `width` and `height` attributes on `<img>` tag (critical for CLS prevention)
3. Added `decoding="async"` for better performance

**Fallback for Missing Dimensions**:
```html
{% if image['width'] and image['height'] %}
  data-width="{{ image['width'] }}"
  data-height="{{ image['height'] }}"
{% endif %}
```

---

## Data Attribute Contract

### Purpose

Data attributes enable JavaScript to:
1. Read image dimensions without loading image files
2. Calculate layout before images are rendered
3. Associate layout data with DOM elements

### Attributes

| Attribute | Type | Required | Purpose |
|-----------|------|----------|---------|
| `data-filename` | string | Yes | Unique identifier for the image |
| `data-category` | string | Yes | Category grouping for filtering/navigation |
| `data-title` | string | No | Display title (may be empty) |
| `data-description` | string | No | Long description (may be empty) |
| `data-width` | integer | Yes* | Original image width in pixels |
| `data-height` | integer | Yes* | Original image height in pixels |

\* Required for flexible layout; optional for backward compatibility with fixed-aspect layout

---

## Image Element Attributes

### width and height

The `width` and `height` attributes on `<img>` are **critical** for preventing layout shift.

**Behavior**:
- Browser calculates aspect ratio: `aspect-ratio = width / height`
- Space is reserved before image loads
- Image scales to fit CSS dimensions while maintaining aspect ratio
- Results in Cumulative Layout Shift (CLS) = 0.0

**Example**:
```html
<img
  src="image.jpg"
  width="1920"
  height="1080"
  style="width: 400px; height: auto;"
/>
<!-- Browser calculates: aspect-ratio: 1.78 -->
<!-- Actual render: 400px × 225px (maintains ratio) -->
<!-- Space reserved: 400px × 225px (no shift when image loads) -->
```

**Reference**: [MDN: img width/height attributes](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#attr-width)

---

## Category Structure

The overall template structure remains unchanged:

```html
<main class="gallery">
  {% for category in categories %}
  <section class="category-section">
    <h2>{{ category['name'] }}</h2>
    <div class="image-grid">
      {% for image in category['images'] %}
      <!-- Image container as defined above -->
      {% endfor %}
    </div>
  </section>
  {% endfor %}
</main>
```

**Container Requirements**:
- `.image-grid` container must have measurable width for layout calculation
- Container must be block-level or flex container
- JavaScript will transform `.image-grid` from CSS Grid to positioned container

---

## CSS Grid Fallback

When JavaScript is disabled or layout calculation fails, CSS Grid provides fallback:

```css
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.image-item {
  aspect-ratio: 4 / 3; /* Fixed fallback */
  overflow: hidden;
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Enhanced with JS */
.image-grid.layout-calculated {
  display: block;
  position: relative;
}

.image-grid.layout-calculated .image-item {
  position: absolute;
  /* Positioned by JS */
}
```

---

## Build-Time Dimension Extraction

### Scanner Integration (src/generator/scan.py)

**Current Function**:
```python
def scan_images(content_dir: Path) -> list[Path]:
    """Scan directory for image files."""
    ...
```

**Enhanced Function**:
```python
def scan_images_with_dimensions(content_dir: Path) -> list[tuple[Path, int, int]]:
    """Scan directory and extract image dimensions.

    Returns:
        List of (file_path, width, height) tuples
    """
    from PIL import Image as PILImage

    images = []
    for file_path in content_dir.glob("**/*.{jpg,jpeg,png,gif,webp}"):
        try:
            with PILImage.open(file_path) as img:
                width, height = img.size
                images.append((file_path, width, height))
        except Exception as e:
            logger.warning(f"Failed to read dimensions for {file_path}: {e}")
            # Option 1: Skip image
            # Option 2: Add with None dimensions
            images.append((file_path, None, None))

    return images
```

**Integration Point** (src/generator/build_html.py):
```python
# Existing code creates Image objects
image = Image(
    filename=path.name,
    file_path=path,
    category=category,
    title=yaml_entry.title,
    description=yaml_entry.description,
    width=width,      # NEW: from dimension extraction
    height=height     # NEW: from dimension extraction
)
```

---

## Template Rendering Contract

### Input to Template

```python
context = {
    'gallery_title': str,
    'categories': [
        {
            'name': str,
            'images': [
                {
                    'filename': str,
                    'category': str,
                    'title': str,
                    'description': str,
                    'alt_text': str,
                    'src': str,
                    'width': int | None,   # NEW
                    'height': int | None   # NEW
                }
            ]
        }
    ],
    'css_href': str,
    'js_href': str
}
```

### Conditional Rendering

```jinja
{% if image['width'] and image['height'] %}
  <!-- Full flexible layout support -->
  <div
    class="image-item"
    data-width="{{ image['width'] }}"
    data-height="{{ image['height'] }}"
  >
    <img
      src="{{ image['src'] }}"
      width="{{ image['width'] }}"
      height="{{ image['height'] }}"
      alt="{{ image['alt_text'] }}"
      loading="lazy"
      decoding="async"
    />
  </div>
{% else %}
  <!-- Fallback: fixed aspect ratio -->
  <div class="image-item">
    <img
      src="{{ image['src'] }}"
      alt="{{ image['alt_text'] }}"
      loading="lazy"
      decoding="async"
    />
  </div>
{% endif %}
```

---

## Accessibility Requirements

### Semantic HTML

All existing semantic HTML must be preserved:

- ✅ `<main>` wrapper for gallery
- ✅ `<section>` for each category
- ✅ `<h2>` for category headings
- ✅ `alt` attributes on all images
- ✅ Keyboard navigation support

### ARIA Attributes

Optional enhancements for layout:

```html
<div
  class="image-grid"
  role="list"
  aria-label="Image gallery"
>
  <div class="image-item" role="listitem">
    ...
  </div>
</div>
```

### Focus Management

When layout is applied via JavaScript:
- Maintain tab order (left-to-right, top-to-bottom)
- Preserve focus visibility
- Ensure `tabindex` remains correct

---

## Performance Considerations

### Critical Data

The following must be available before first paint:
1. Image dimensions (width/height attributes)
2. Container width (measurable via DOM)

### Lazy Loading

Maintain existing lazy loading behavior:
```html
<img loading="lazy" ... />
```

Layout calculation happens before images load, so lazy loading is unaffected.

### Async Decoding

Add `decoding="async"` to prevent blocking:
```html
<img decoding="async" ... />
```

This allows browser to decode images off the main thread.

---

## Testing Contract

### Template Tests

1. **Dimension Attributes**: Verify data-width and data-height are present
2. **Image Attributes**: Verify width and height on img tag
3. **Fallback**: Verify CSS Grid works without dimensions
4. **Accessibility**: Verify alt text, semantic HTML maintained
5. **Valid HTML**: Verify output passes W3C validator

### Integration Tests

1. **Build Process**: Verify dimensions extracted from real images
2. **Template Rendering**: Verify correct data passed to template
3. **Output Validation**: Verify generated HTML matches contract

---

## Migration Strategy

### Phase 1: Backward Compatible (Current)
- Templates render with or without dimensions
- CSS Grid provides fallback layout
- No breaking changes

### Phase 2: Dimension Extraction (Next)
- Scanner extracts dimensions for all images
- Templates always receive dimensions
- Flexible layout becomes default

### Phase 3: Dimension Required (Future)
- Scanner fails if dimensions unavailable
- Templates assume dimensions always present
- CSS Grid fallback only for JS-disabled users

---

## Example Output

### Complete Example

```html
<main class="gallery">
  <section class="category-section">
    <h2>Landscapes</h2>
    <div class="image-grid">

      <div
        class="image-item"
        data-filename="mountain.jpg"
        data-category="Landscapes"
        data-title="Mountain Sunrise"
        data-description="Early morning light"
        data-width="1920"
        data-height="1080"
      >
        <img
          src="images/mountain.jpg"
          alt="Mountain Sunrise"
          width="1920"
          height="1080"
          loading="lazy"
          decoding="async"
        />
        <div class="image-caption">Mountain Sunrise</div>
      </div>

      <div
        class="image-item"
        data-filename="lake.jpg"
        data-category="Landscapes"
        data-title=""
        data-description=""
        data-width="800"
        data-height="1200"
      >
        <img
          src="images/lake.jpg"
          alt="lake"
          width="800"
          height="1200"
          loading="lazy"
          decoding="async"
        />
      </div>

    </div>
  </section>
</main>
```

---

## Changelog

### Version 1.0.0 (2025-11-02)
- Initial contract definition
- Added width/height to Image model
- Defined data attribute requirements
- Specified img element attributes
- Documented backward compatibility strategy

---

## References

- [MDN: Responsive Images](https://developer.mozilla.org/en-US/docs/Learn/HTML/Multimedia_and_embedding/Responsive_images)
- [Web.dev: Optimize CLS](https://web.dev/optimize-cls/)
- [HTML Standard: img element](https://html.spec.whatwg.org/multipage/embedded-content.html#the-img-element)
