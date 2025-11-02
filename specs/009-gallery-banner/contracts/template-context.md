# Template Contract: Banner and Title

**Feature**: 009-gallery-banner
**Date**: 2025-11-02
**Contract Type**: Jinja2 Template Context

## Overview

This contract defines the data structure that `build_html.py` must provide to `index.html.j2` for banner and title rendering. This is an internal API contract between the build script and template.

---

## Template Context Extension

The existing template context is extended with the following fields:

### New Fields

```python
{
    # Existing fields (not shown for brevity)
    # ... gallery_title, categories, images, etc ...

    # NEW: Banner image URL (optional)
    "banner_image": Optional[str],

    # MODIFIED: Gallery title (now optional, was previously always set)
    "gallery_title": Optional[str],

    # NEW: Default title from i18n (fallback)
    "default_title": str,
}
```

---

## Field Specifications

### `banner_image`

**Type**: `Optional[str]`
**Required**: No
**Format**: Relative URL path
**Example**: `"images/banner/my-banner.jpg"`

**Contract**:
- MUST be `None` if no banner configured
- MUST be relative URL from gallery root if banner configured
- MUST point to existing file in output directory
- Path MUST match pattern: `images/banner/<filename>.<ext>`
- Supported extensions: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`

**Provider Responsibilities** (`build_html.py`):
1. Copy banner image from `config.banner_image` to `output_dir/images/banner/`
2. Generate relative URL path for template
3. Set to `None` if `config.banner_image` is `None`

**Consumer Responsibilities** (`index.html.j2`):
1. Check if `banner_image is not None` before rendering banner section
2. Use as `src` attribute for `<img>` element
3. Provide appropriate `alt` text (derived from `gallery_title`)

---

### `gallery_title`

**Type**: `Optional[str]`
**Required**: No
**Format**: Plain text (pre-escaped for HTML)
**Example**: `"My 3D Printing Gallery"`

**Contract**:
- MAY be `None` (indicates no custom title configured)
- MUST be properly escaped for HTML if provided
- MUST NOT exceed 200 characters
- MUST NOT be empty string or whitespace-only

**Provider Responsibilities** (`build_html.py`):
1. Pass through `config.gallery_title` as-is (Jinja2 auto-escapes)
2. Set to `None` if not configured in settings

**Consumer Responsibilities** (`index.html.j2`):
1. Use in banner title overlay if banner present
2. Fall back to `default_title` if `None`
3. Maintain proper heading hierarchy (`<h1>`)

---

### `default_title`

**Type**: `str`
**Required**: Yes (always provided)
**Format**: Localized text string
**Example**: `"Gallery"` (en) or `"Galerie"` (de)

**Contract**:
- MUST always be non-empty string
- MUST be localized according to `config.locale`
- MUST be suitable for use as gallery heading

**Provider Responsibilities** (`build_html.py`):
1. Load from i18n translations based on `config.locale`
2. Always provide fallback value ("Gallery" if translation missing)

**Consumer Responsibilities** (`index.html.j2`):
1. Use as fallback when `gallery_title is None`
2. Use for `alt` text construction

---

## Template Rendering Contract

### Scenario 1: No Banner, No Custom Title

**Input**:
```python
{
    "banner_image": None,
    "gallery_title": None,
    "default_title": "Gallery",
}
```

**Expected Output**:
```html
<header>
    <h1>Gallery</h1>
</header>
```

---

### Scenario 2: Banner Only, No Custom Title

**Input**:
```python
{
    "banner_image": "images/banner/banner.jpg",
    "gallery_title": None,
    "default_title": "Gallery",
}
```

**Expected Output**:
```html
<header>
    <div class="gallery-banner">
        <img src="images/banner/banner.jpg" alt="Gallery banner" class="banner-image">
    </div>
</header>
```

---

### Scenario 3: Banner with Custom Title

**Input**:
```python
{
    "banner_image": "images/banner/banner.jpg",
    "gallery_title": "My 3D Printing Gallery",
    "default_title": "Gallery",
}
```

**Expected Output**:
```html
<header>
    <div class="gallery-banner">
        <img src="images/banner/banner.jpg" alt="Banner for My 3D Printing Gallery" class="banner-image">
        <h1 class="banner-title">My 3D Printing Gallery</h1>
    </div>
</header>
```

---

### Scenario 4: No Banner, Custom Title Only

**Input**:
```python
{
    "banner_image": None,
    "gallery_title": "My 3D Printing Gallery",
    "default_title": "Gallery",
}
```

**Expected Output**:
```html
<header>
    <h1>My 3D Printing Gallery</h1>
</header>
```

---

## Template Logic Contract

The template MUST implement the following logic:

```jinja2
<header role="banner">
    {% if banner_image %}
    {# Banner present: render banner section #}
    <div class="gallery-banner">
        <img
            src="{{ banner_image }}"
            alt="{% if gallery_title %}Banner for {{ gallery_title }}{% else %}{{ default_title }} banner{% endif %}"
            class="banner-image"
        >
        {% if gallery_title %}
        {# Title as overlay on banner #}
        <h1 class="banner-title">{{ gallery_title }}</h1>
        {% endif %}
    </div>
    {% else %}
    {# No banner: simple header with title #}
    <h1>{{ gallery_title if gallery_title else default_title }}</h1>
    {% endif %}
</header>
```

---

## CSS Contract

The template relies on CSS classes that MUST be defined in `style.css`:

### Required Classes

| Class Name | Purpose | Contract |
|-----------|---------|----------|
| `.gallery-banner` | Container for banner image and title overlay | Position: relative; width: 100% |
| `.banner-image` | Banner image styling | Display: block; width: 100%; object-fit: cover; height: 40vh (responsive) |
| `.banner-title` | Title overlay on banner | Position: absolute; bottom: 2rem; font-size: 3rem (responsive) |

### CSS Contract Example

```css
.gallery-banner {
    position: relative;
    width: 100%;
}

.banner-image {
    display: block;
    width: 100%;
    height: 40vh;
    object-fit: cover;
    object-position: center center;
}

.banner-title {
    position: absolute;
    bottom: 2rem;
    left: 2rem;
    right: 2rem;
    font-size: 3rem;
    font-weight: 700;
    color: white;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
    margin: 0;
}

/* Gradient overlay for text readability */
.gallery-banner::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 50%;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.6), transparent);
    pointer-events: none;
    z-index: 1;
}

/* Title must be above gradient */
.banner-title {
    position: relative;
    z-index: 2;
}
```

---

## Backward Compatibility Contract

### Invariant 1: Existing Templates Continue Working
If template is NOT updated to use new `banner_image` field, existing behavior is preserved:
- `gallery_title` still renders as before (now uses `default_title` fallback)
- No visual changes if banner not configured

### Invariant 2: Field Presence Guarantees
- `default_title` is ALWAYS present (never `None`)
- `banner_image` and `gallery_title` MAY be `None`
- Template MUST check for `None` before using these fields

---

## Validation Contract

### Build-Time Validation

The build script MUST validate:
1. ✅ If `banner_image` provided, file exists at `config.banner_image`
2. ✅ If `banner_image` provided, output directory `images/banner/` is created
3. ✅ If `banner_image` provided, file is successfully copied to output
4. ✅ `gallery_title` does not exceed 200 characters
5. ✅ `default_title` is never empty

### Template Validation

The template MUST handle:
1. ✅ `banner_image` being `None` (render simple header)
2. ✅ `gallery_title` being `None` (use `default_title`)
3. ✅ Both `banner_image` and `gallery_title` being `None` (simple header with default title)
4. ✅ Special characters in `gallery_title` (Jinja2 auto-escapes)

---

## Error Handling Contract

### Provider Errors (Build Script)

| Error Condition | Build Behavior | Template Impact |
|----------------|----------------|-----------------|
| Banner file not found | Raise error, stop build | N/A (build fails) |
| Banner copy fails | Raise error, stop build | N/A (build fails) |
| Invalid banner path | Raise error, stop build | N/A (build fails) |
| Title validation fails | Raise error, stop build | N/A (build fails) |

### Consumer Errors (Template)

| Error Condition | Template Behavior | Fallback |
|----------------|------------------|----------|
| `banner_image` not in context | Render without banner | Use simple header |
| `gallery_title` not in context | Use `default_title` | Never fails (default always present) |
| `default_title` not in context | **Should never happen** | Fail gracefully with "Gallery" hardcoded |

---

## Testing Contract

### Unit Tests

Mock `build_html.py` providing various context combinations:
1. Test all 4 scenarios documented above
2. Test HTML output matches expected structure
3. Test CSS classes are correctly applied
4. Test alt text generation logic

### Integration Tests

Test full build pipeline:
1. Build with banner configured → verify banner appears in output
2. Build without banner → verify simple header in output
3. Build with title only → verify title in simple header
4. Build with neither → verify default title in simple header

### Accessibility Tests

Verify accessibility requirements:
1. `<header>` has implicit `banner` landmark role
2. `<h1>` is present and contains expected title
3. Banner `<img>` has descriptive `alt` text
4. Title text has sufficient contrast (>7:1 white on gradient)

---

## Version Compatibility

| Template Version | Required Context Fields | Optional Context Fields |
|-----------------|------------------------|------------------------|
| Pre-009 | `gallery_title` (non-null string) | (none) |
| 009+ | `default_title` (non-null string) | `banner_image` (optional str), `gallery_title` (optional str) |

**Migration**:
- Old templates receive `gallery_title` as before (now with `default_title` fallback)
- New templates can use `banner_image` for enhanced display
- No breaking changes to existing template contracts

---

## Summary

This contract ensures:
- ✅ Type safety: All fields properly typed and documented
- ✅ Nullability: Clear rules for when fields can be `None`
- ✅ Validation: Both provider and consumer responsibilities defined
- ✅ Error handling: Failure modes and fallbacks documented
- ✅ Backward compatibility: Existing behavior preserved
- ✅ Testing: Clear test scenarios for all cases

The template contract serves as the interface between the build system and presentation layer, ensuring reliable and predictable rendering of the banner feature.
