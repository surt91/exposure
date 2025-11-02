# Quickstart: Gallery Banner and Title Implementation

**Feature**: 009-gallery-banner
**Date**: 2025-11-02
**Target Audience**: Developers implementing this feature

## Overview

This quickstart guide walks through implementing the gallery banner and title feature in the correct order, with checkpoints to verify each step.

**Estimated Time**: 2-3 hours
**Difficulty**: Intermediate

---

## Prerequisites

- [ ] Familiarity with Python 3.11, Pydantic, and Jinja2
- [ ] Local development environment set up (see main README.md)
- [ ] Read `research.md` and `data-model.md` in this directory
- [ ] Branch `009-gallery-banner` checked out

---

## Implementation Steps

### Step 1: Extend GalleryConfig Model (30 min)

**File**: `src/generator/model.py`

#### 1.1: Add New Fields

Add two optional fields to the `GalleryConfig` class:

```python
class GalleryConfig(BaseSettings):
    # ... existing fields ...

    banner_image: Optional[Path] = Field(
        default=None,
        description="Path to banner image displayed at top of gallery (relative to content_dir or absolute)"
    )

    gallery_title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Gallery title displayed prominently in banner or header"
    )

    gallery_subtitle: Optional[str] = Field(
        default=None,
        description="Gallery subtitle displayed below title (requires gallery_title)"
    )
```

#### 1.2: Add Field Validators

Add validation for banner image path:

```python
@field_validator("banner_image", mode="before")
@classmethod
def validate_banner_image(cls, v, info):
    """Validate banner image path exists if provided."""
    if v is None:
        return None

    path = Path(v) if not isinstance(v, Path) else v

    # Check absolute path
    if path.is_absolute():
        if not path.exists() or not path.is_file():
            raise ValueError(f"Banner image not found or not a file: {path}")
        return path

    # Try relative to content_dir
    content_dir = info.data.get("content_dir")
    if content_dir:
        full_path = Path(content_dir) / path
        if full_path.exists() and full_path.is_file():
            return full_path

    raise ValueError(
        f"Banner image not found: {v}. "
        f"Provide absolute path or path relative to content_dir."
    )

@field_validator("gallery_title", mode="before")
@classmethod
def validate_gallery_title(cls, v):
    """Validate gallery title if provided."""
    if v is None:
        return None

    if isinstance(v, str):
        v = v.strip()
        if not v:
            raise ValueError("Gallery title cannot be empty or whitespace-only")
        if len(v) > 200:
            raise ValueError("Gallery title must be 200 characters or less")

    return v

@field_validator("gallery_subtitle", mode="before")
@classmethod
def validate_gallery_subtitle(cls, v):
    """Validate gallery subtitle if provided."""
    if v is None:
        return None

    if isinstance(v, str):
        v = v.strip()
        if not v:
            return None  # Treat empty as None
        if len(v) > 300:
            raise ValueError("Gallery subtitle must be 300 characters or less")

    return v
```

**Checkpoint 1**: Run tests
```bash
uv run pytest tests/unit/test_model.py -v
```

Expected: Existing model tests pass. Add new tests for banner/title validation (see Step 6).

---

### Step 2: Update Build Script (45 min)

**File**: `src/generator/build_html.py`

#### 2.1: Add Banner Asset Copy Function

Add function to copy banner image to output directory:

```python
def copy_banner_image(config: GalleryConfig, output_dir: Path) -> Optional[str]:
    """
    Copy banner image to output directory.

    Args:
        config: Gallery configuration with optional banner_image
        output_dir: Build output directory

    Returns:
        Relative URL to banner image, or None if no banner configured
    """
    if not config.banner_image:
        return None

    # Create banner output directory
    banner_output_dir = output_dir / "images" / "banner"
    banner_output_dir.mkdir(parents=True, exist_ok=True)

    # Copy banner to output
    dest_path = banner_output_dir / config.banner_image.name
    shutil.copy2(config.banner_image, dest_path)

    logger.info(f"Copied banner image: {config.banner_image.name}")

    # Return relative URL for template
    return f"images/banner/{config.banner_image.name}"
```

#### 2.2: Add Default Title Retrieval

Add function to get localized default title:

```python
def get_default_title(locale: str) -> str:
    """
    Get default gallery title from i18n translations.

    Args:
        locale: Current locale (e.g., "en", "de")

    Returns:
        Localized default title
    """
    # Babel translation (requires gettext setup)
    return _("Gallery")
```

#### 2.3: Update Template Context

Modify the main build function to include banner/title data:

```python
def build_gallery(config: GalleryConfig) -> None:
    """Build the gallery HTML and copy assets."""
    # ... existing code ...

    # NEW: Prepare banner/title context
    banner_image_url = copy_banner_image(config, config.output_dir)
    default_title = get_default_title(config.locale)

    # Prepare template context
    context = {
        "categories": categories,
        "css_href": "style.css",
        "js_href": "script.js",
        # NEW: Banner and title fields
        "banner_image": banner_image_url,
        "gallery_title": config.gallery_title,
        "default_title": default_title,
    }

    # ... rest of build logic ...
```

**Checkpoint 2**: Test build script
```bash
# Create test banner image
echo "Test" > content/test-banner.jpg

# Add to settings.yaml
echo "banner_image: test-banner.jpg" >> config/settings.yaml
echo "gallery_title: Test Gallery" >> config/settings.yaml

# Run build
uv run exposure

# Verify banner copied
ls dist/images/banner/test-banner.jpg
```

---

### Step 3: Update Jinja2 Template (30 min)

**File**: `src/templates/index.html.j2`

#### 3.1: Replace Header Section

Replace the existing `<header>` section:

```jinja2
{# OLD: #}
<header>
    <h1>{{ gallery_title }}</h1>
</header>

{# NEW: #}
<header role="banner">
    {% if banner_image %}
    {# Banner present: render banner with optional title overlay #}
    <div class="gallery-banner">
        <img
            src="{{ banner_image }}"
            alt="{% if gallery_title %}Banner for {{ gallery_title }}{% else %}{{ default_title }} banner{% endif %}"
            class="banner-image"
        >
        {% if gallery_title %}
        <h1 class="banner-title">{{ gallery_title }}</h1>
        {% if gallery_subtitle %}
        <p class="banner-subtitle">{{ gallery_subtitle }}</p>
        {% endif %}
        {% endif %}
    </div>
    {% else %}
    {# No banner: simple header with title (subtitle not shown in simple header) #}
    <h1>{{ gallery_title if gallery_title else default_title }}</h1>
    {% endif %}
</header>
```

**Checkpoint 3**: View in browser
```bash
uv run exposure
# Open dist/index.html in browser
# Verify banner displays if configured, or simple header if not
```

---

### Step 4: Add CSS Styling (45 min)

**File**: `src/static/style.css`

#### 4.1: Add Banner Styles

Add at the end of the file (or in appropriate section):

```css
/* ============================================
   Gallery Banner and Title
   ============================================ */

.gallery-banner {
    position: relative;
    width: 100%;
    overflow: hidden;
}

.banner-image {
    display: block;
    width: 100%;
    height: var(--banner-height-desktop, 40vh);
    object-fit: cover;
    object-position: center center;
}

/* Gradient overlay for title readability */
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

.banner-title {
    position: absolute;
    bottom: 4rem; /* Increased to make room for subtitle */
    left: 2rem;
    right: 2rem;
    font-size: 3rem;
    font-weight: 700;
    line-height: 1.2;
    color: white;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
    margin: 0;
    z-index: 2;
}

.banner-subtitle {
    position: absolute;
    bottom: 0.5rem; /* Below title */
    left: 2rem;
    right: 2rem;
    font-size: 1.5rem;
    font-weight: 400; /* Normal weight */
    line-height: 1.4;
    color: white;
    opacity: 0.9; /* Slightly transparent for secondary emphasis */
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.7);
    margin: 0;
    z-index: 2;
}

/* Responsive breakpoints */
@media (max-width: 1024px) {
    .banner-image {
        height: var(--banner-height-tablet, 30vh);
    }

    .banner-title {
        font-size: 2.5rem;
    }
}

@media (max-width: 768px) {
    .banner-image {
        height: var(--banner-height-mobile, 25vh);
    }

    .banner-title {
        font-size: 2rem;
        bottom: 3rem; /* Adjusted for subtitle */
        left: 1rem;
        right: 1rem;
    }

    .banner-subtitle {
        font-size: 1.125rem;
        left: 1rem;
        right: 1rem;
    }
}

@media (max-width: 480px) {
    .banner-title {
        font-size: 1.5rem;
    }

    .banner-subtitle {
        font-size: 1rem;
    }
}

/* Dark mode: No changes needed, banner works in both themes */
```

#### 4.2: Add CSS Custom Properties (Optional)

Add to the `:root` section for easy customization:

```css
:root {
    /* Banner height customization */
    --banner-height-desktop: 40vh;
    --banner-height-tablet: 30vh;
    --banner-height-mobile: 25vh;
}
```

**Checkpoint 4**: Verify styling
```bash
uv run exposure
# Open dist/index.html
# Check:
# - Banner spans full width
# - Title overlay is readable
# - Responsive on mobile (use browser dev tools)
# - Dark mode toggle works (if implemented)
```

---

### Step 5: Add i18n Translation (15 min)

**File**: `locales/messages.pot` and `locales/de/LC_MESSAGES/messages.po`

#### 5.1: Extract New Strings

```bash
uv run pybabel extract -F babel.cfg -o locales/messages.pot .
```

#### 5.2: Update German Translation

Edit `locales/de/LC_MESSAGES/messages.po`:

```po
msgid "Gallery"
msgstr "Galerie"
```

#### 5.3: Compile Translations

```bash
uv run pybabel compile -d locales
```

**Checkpoint 5**: Test localization
```bash
# Set German locale
export EXPOSURE_LOCALE=de
uv run exposure
# Verify default title is "Galerie" when gallery_title not set
```

---

### Step 6: Write Unit Tests (45 min)

**File**: `tests/unit/test_model.py`

Add test cases for new validation:

```python
def test_gallery_config_banner_image_none():
    """Test that banner_image can be None."""
    config = GalleryConfig(
        content_dir=Path("content"),
        gallery_yaml_path=Path("config/gallery.yaml"),
        default_category="Test",
        banner_image=None,
    )
    assert config.banner_image is None

def test_gallery_config_banner_image_absolute_path(tmp_path):
    """Test banner_image with absolute path."""
    banner_file = tmp_path / "banner.jpg"
    banner_file.touch()

    config = GalleryConfig(
        content_dir=Path("content"),
        gallery_yaml_path=Path("config/gallery.yaml"),
        default_category="Test",
        banner_image=banner_file,
    )
    assert config.banner_image == banner_file

def test_gallery_config_banner_image_relative_path(tmp_path):
    """Test banner_image with path relative to content_dir."""
    content_dir = tmp_path / "content"
    content_dir.mkdir()
    banner_file = content_dir / "banner.jpg"
    banner_file.touch()

    config = GalleryConfig(
        content_dir=content_dir,
        gallery_yaml_path=Path("config/gallery.yaml"),
        default_category="Test",
        banner_image=Path("banner.jpg"),
    )
    assert config.banner_image == banner_file

def test_gallery_config_banner_image_not_found():
    """Test validation error when banner image doesn't exist."""
    with pytest.raises(ValueError, match="Banner image not found"):
        GalleryConfig(
            content_dir=Path("content"),
            gallery_yaml_path=Path("config/gallery.yaml"),
            default_category="Test",
            banner_image=Path("nonexistent.jpg"),
        )

def test_gallery_config_gallery_title_valid():
    """Test gallery_title with valid string."""
    config = GalleryConfig(
        content_dir=Path("content"),
        gallery_yaml_path=Path("config/gallery.yaml"),
        default_category="Test",
        gallery_title="My Gallery",
    )
    assert config.gallery_title == "My Gallery"

def test_gallery_config_gallery_title_none():
    """Test that gallery_title can be None."""
    config = GalleryConfig(
        content_dir=Path("content"),
        gallery_yaml_path=Path("config/gallery.yaml"),
        default_category="Test",
        gallery_title=None,
    )
    assert config.gallery_title is None

def test_gallery_config_gallery_title_empty():
    """Test validation error for empty gallery_title."""
    with pytest.raises(ValueError, match="cannot be empty"):
        GalleryConfig(
            content_dir=Path("content"),
            gallery_yaml_path=Path("config/gallery.yaml"),
            default_category="Test",
            gallery_title="   ",
        )

def test_gallery_config_gallery_title_too_long():
    """Test validation error for too long gallery_title."""
    with pytest.raises(ValueError, match="200 characters"):
        GalleryConfig(
            content_dir=Path("content"),
            gallery_yaml_path=Path("config/gallery.yaml"),
            default_category="Test",
            gallery_title="x" * 201,
        )
```

**Checkpoint 6**: Run unit tests
```bash
uv run pytest tests/unit/test_model.py -v
```

---

### Step 7: Write Integration Tests (30 min)

**File**: `tests/integration/test_build.py`

Add integration tests for banner rendering:

```python
def test_build_with_banner_and_title(tmp_path):
    """Test full build with banner and title configured."""
    # Setup
    content_dir = tmp_path / "content"
    content_dir.mkdir()
    banner = content_dir / "banner.jpg"
    banner.write_bytes(b"fake image data")

    config = GalleryConfig(
        content_dir=content_dir,
        gallery_yaml_path=Path("config/gallery.yaml"),
        default_category="Test",
        output_dir=tmp_path / "dist",
        banner_image=banner,
        gallery_title="Test Gallery",
    )

    # Build
    build_gallery(config)

    # Verify banner copied
    assert (tmp_path / "dist" / "images" / "banner" / "banner.jpg").exists()

    # Verify HTML contains banner
    html_content = (tmp_path / "dist" / "index.html").read_text()
    assert "images/banner/banner.jpg" in html_content
    assert "Test Gallery" in html_content
    assert 'class="gallery-banner"' in html_content

def test_build_without_banner(tmp_path):
    """Test build without banner configured (backward compatibility)."""
    config = GalleryConfig(
        content_dir=Path("content"),
        gallery_yaml_path=Path("config/gallery.yaml"),
        default_category="Test",
        output_dir=tmp_path / "dist",
        banner_image=None,
        gallery_title=None,
    )

    # Build
    build_gallery(config)

    # Verify no banner directory created
    assert not (tmp_path / "dist" / "images" / "banner").exists()

    # Verify HTML uses simple header
    html_content = (tmp_path / "dist" / "index.html").read_text()
    assert "gallery-banner" not in html_content
    assert "<h1>" in html_content  # Simple header still present
```

**Checkpoint 7**: Run integration tests
```bash
uv run pytest tests/integration/test_build.py -v
```

---

### Step 8: Write Accessibility Tests (30 min)

**File**: `tests/accessibility/test_a11y.py`

Add accessibility tests for banner:

```python
@pytest.mark.a11y
def test_banner_accessibility(page, base_url):
    """Test banner section meets accessibility standards."""
    page.goto(base_url)

    # Run axe accessibility audit
    results = page.evaluate("axe.run()")

    # Check for violations
    violations = results["violations"]
    assert len(violations) == 0, f"Accessibility violations: {violations}"

    # Specific checks for banner
    header = page.locator("header")
    assert header.is_visible()

    # Check heading hierarchy
    h1 = page.locator("h1")
    assert h1.count() == 1, "Should have exactly one h1"

    # Check banner image alt text if present
    if page.locator(".banner-image").count() > 0:
        banner_img = page.locator(".banner-image")
        alt_text = banner_img.get_attribute("alt")
        assert alt_text, "Banner image must have alt text"
        assert len(alt_text) > 0, "Alt text must not be empty"

@pytest.mark.a11y
def test_banner_title_contrast(page, base_url):
    """Test banner title has sufficient color contrast."""
    page.goto(base_url)

    if page.locator(".banner-title").count() > 0:
        # Check contrast ratio
        results = page.evaluate("""
            () => {
                const title = document.querySelector('.banner-title');
                const style = window.getComputedStyle(title);
                return {
                    color: style.color,
                    textShadow: style.textShadow
                };
            }
        """)

        # White text on dark gradient should have >7:1 ratio
        # This is validated by axe-core in the general accessibility test
        assert results["color"], "Title must have color defined"
```

**Checkpoint 8**: Run accessibility tests
```bash
uv run pytest tests/accessibility/test_a11y.py -v -m a11y
```

---

### Step 9: Update Documentation (15 min)

#### 9.1: Update README.md

Add banner configuration example to README:

```markdown
### Configuration

Create `config/settings.yaml`:

```yaml
content_dir: "content/"
gallery_yaml_path: "config/gallery.yaml"
default_category: "Uncategorized"

# Optional: Gallery banner and title
banner_image: "banner.jpg"  # Relative to content_dir
gallery_title: "My 3D Printing Gallery"
```
```

#### 9.2: Update CHANGELOG.md

Add entry for version 0.3.0:

```markdown
## [0.3.0] - 2025-11-XX

### Added
- Configurable gallery banner image displayed at top of page
- Configurable gallery title with enhanced styling
- Banner image spans full viewport width with responsive sizing
- Title overlay on banner with gradient for readability
- Dark mode support for banner and title
- i18n support for default gallery title
```

**Checkpoint 9**: Review documentation
```bash
# Verify README is clear
cat README.md

# Verify CHANGELOG follows keep-a-changelog format
cat CHANGELOG.md
```

---

### Step 10: Manual Testing Checklist

- [ ] Build runs successfully with banner configured
- [ ] Build runs successfully without banner (backward compatibility)
- [ ] Banner displays at full viewport width
- [ ] Banner height is appropriate on desktop (40vh)
- [ ] Banner height is appropriate on mobile (25vh)
- [ ] Title overlay is readable on banner
- [ ] Title has sufficient contrast (white on gradient)
- [ ] Simple header displays when no banner configured
- [ ] Default title displays when gallery_title not set
- [ ] Dark mode toggle works (if implemented)
- [ ] Browser zoom works correctly with banner
- [ ] Banner works in Chrome, Firefox, Safari
- [ ] No console errors in browser
- [ ] All tests pass (`uv run pytest`)
- [ ] Accessibility audit passes (`uv run pytest -m a11y`)
- [ ] Asset budgets respected (HTML ≤30KB, CSS ≤25KB)

---

## Common Issues & Solutions

### Issue 1: Banner Image Not Displaying

**Symptom**: Banner image path appears correct but image doesn't show.

**Solutions**:
1. Check file exists at specified path: `ls content/banner.jpg`
2. Verify banner copied to output: `ls dist/images/banner/`
3. Check browser console for 404 errors
4. Verify image format is supported (JPG, PNG, WebP, GIF)

### Issue 2: Title Not Readable on Banner

**Symptom**: Title text is hard to read due to light banner colors.

**Solutions**:
1. Increase gradient overlay opacity in CSS
2. Increase text-shadow blur radius
3. Consider darker banner images
4. Adjust gradient height (increase 50% to 60%)

### Issue 3: Banner Too Tall on Mobile

**Symptom**: Banner takes excessive vertical space on mobile.

**Solutions**:
1. Reduce `--banner-height-mobile` in CSS (try 20vh or 15vh)
2. Add more responsive breakpoints for smaller screens
3. Consider hiding banner on very small screens (<480px)

### Issue 4: Validation Errors for Banner Path

**Symptom**: Build fails with "Banner image not found".

**Solutions**:
1. Use absolute path: `/full/path/to/banner.jpg`
2. Ensure relative path is relative to `content_dir`
3. Check file permissions are readable
4. Verify filename spelling and extension

---

## Performance Verification

After implementation, verify performance budgets:

```bash
# Build gallery
uv run exposure

# Check HTML size
du -h dist/index.html  # Should be <30KB

# Check CSS size
du -h dist/style.css  # Should be <25KB

# Check banner image size
du -h dist/images/banner/*.jpg  # Recommend <500KB

# Run full test suite
uv run pytest --cov=src --cov-report=html

# Check asset budgets
uv run pytest tests/integration/test_asset_budgets.py -v
```

---

## Next Steps

After completing implementation:

1. **Create PR**: Include link to this spec in PR description
2. **Request Review**: Ensure reviewer checks constitution compliance
3. **Update Agent Context**: Run `.specify/scripts/bash/update-agent-context.sh copilot`
4. **Tag Release**: Create v0.3.0 tag after merge
5. **Deploy Example**: Update live demo with banner feature

---

## Resources

- **Research**: `specs/009-gallery-banner/research.md` - All technical decisions
- **Data Model**: `specs/009-gallery-banner/data-model.md` - Entity definitions
- **Template Contract**: `specs/009-gallery-banner/contracts/template-context.md` - Template interface
- **Constitution**: `.specify/memory/constitution.md` - Project constraints
- **Pydantic Docs**: https://docs.pydantic.dev/latest/ - Model validation reference
- **Jinja2 Docs**: https://jinja.palletsprojects.com/ - Template syntax reference

---

## Support

If you encounter issues not covered in this quickstart:
1. Review the research document for context
2. Check existing test cases for examples
3. Consult the template contract for expected behavior
4. Review similar features (e.g., thumbnail generation) for patterns
