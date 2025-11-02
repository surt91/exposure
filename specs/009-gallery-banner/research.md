# Research: Gallery Banner and Title

**Feature**: 009-gallery-banner
**Date**: 2025-11-02
**Status**: Complete

## Research Questions

This document consolidates research findings for all technical decisions required to implement the gallery banner and title feature.

---

## Q1: Banner Image Cropping Strategy

**Question**: What cropping approach should be used for banner images that are taller than the target display height?

### Decision
Use **CSS object-fit with center cropping** rather than server-side image preprocessing.

### Rationale
1. **Simplicity**: No additional image processing pipeline needed. Browser-native CSS handles cropping.
2. **Flexibility**: Gallery owners can adjust banner height via CSS without regenerating images.
3. **Performance**: Original banner image is already optimized by existing asset pipeline. CSS cropping is instantaneous.
4. **Responsive**: Different viewports can use different aspect ratios with media queries without multiple image versions.

### Implementation Approach
```css
.banner-image {
    width: 100%;
    height: 40vh; /* Responsive to viewport */
    object-fit: cover; /* Center crop */
    object-position: center center; /* Can be customized per image if needed */
}

@media (max-width: 768px) {
    .banner-image {
        height: 25vh; /* Shorter on mobile */
    }
}
```

### Alternatives Considered
- **Server-side pre-cropping**: Rejected because it requires additional build-time processing, reduces flexibility (fixed aspect ratio), and complicates incremental builds. Gallery owners would need to regenerate if they want different cropping.
- **Multiple image versions**: Rejected because it increases build complexity and storage. CSS object-fit is widely supported (97%+ browsers) and provides better UX.
- **Art direction with `<picture>`**: Rejected as over-engineering for this use case. Simple single image with CSS cropping is sufficient for most banner scenarios.

---

## Q2: Banner Height Specification

**Question**: Should banner height be fixed pixels, viewport-relative, or configurable?

### Decision
Use **viewport-relative height (vh units)** with responsive breakpoints as the default, with CSS custom properties to allow easy customization.

### Rationale
1. **Responsive**: Banner scales naturally with viewport size without requiring multiple breakpoints.
2. **Visual Balance**: Banner takes proportional space on all devices (40% on desktop, 25% on mobile provides good balance based on web design best practices).
3. **Customizable**: CSS custom properties allow gallery owners to override in their own stylesheets if needed.
4. **Accessible**: Viewport units work well with browser zoom and accessibility tools.

### Implementation Approach
```css
:root {
    --banner-height-desktop: 40vh;
    --banner-height-tablet: 30vh;
    --banner-height-mobile: 25vh;
}

.banner-image {
    height: var(--banner-height-desktop);
}

@media (max-width: 1024px) {
    .banner-image {
        height: var(--banner-height-tablet);
    }
}

@media (max-width: 768px) {
    .banner-image {
        height: var(--banner-height-mobile);
    }
}
```

### Alternatives Considered
- **Fixed pixel height**: Rejected because it doesn't scale well across different screen sizes and resolutions. 400px might be perfect on desktop but excessive on mobile.
- **Configurable in YAML**: Rejected as unnecessary complexity. This is a presentation concern best handled in CSS. Power users can override CSS custom properties.
- **Aspect ratio based**: Rejected because banner images have varying aspect ratios and this would result in inconsistent heights across the gallery.

---

## Q3: Title Typography and "Fancy" Styling

**Question**: What constitutes "fancy" title styling that matches the existing design while remaining maintainable?

### Decision
Use **enhanced typography with dark mode support** - larger font size, custom font weight, subtle text shadow, and optional gradient overlay on banner.

### Rationale
1. **Design Consistency**: Builds on existing CSS design system and dark mode implementation.
2. **Accessibility**: Maintains WCAG 2.1 AA contrast ratios in both light and dark modes.
3. **Performance**: Pure CSS, no external fonts or JavaScript. Zero additional HTTP requests.
4. **Maintainability**: Simple CSS that matches existing codebase patterns.

### Implementation Approach
```css
.gallery-banner {
    position: relative;
}

.banner-image {
    display: block;
    width: 100%;
    height: 40vh;
    object-fit: cover;
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

/* Optional gradient overlay for better text readability */
.gallery-banner::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 50%;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.6), transparent);
    pointer-events: none;
}

@media (max-width: 768px) {
    .banner-title {
        font-size: 2rem;
        bottom: 1rem;
        left: 1rem;
        right: 1rem;
    }
}

/* Dark mode: No changes needed - white text always on banner image */
```

### Alternatives Considered
- **Custom web font**: Rejected due to constitution requirement (no external dependencies, performance budget). System fonts are sufficient.
- **Animated text**: Rejected as unnecessary complexity and potential accessibility issue (motion sensitivity).
- **Text below banner**: Considered but rejected because overlay provides better visual integration and saves vertical space.
- **Configurable styling in YAML**: Rejected as scope creep. Styling is a presentation concern for CSS, not configuration.

---

## Q4: Configuration Schema Location

**Question**: Should banner/title configuration go in `gallery.yaml` (per-gallery metadata) or `settings.yaml` (generator settings)?

### Decision
Add banner and title fields to the **GalleryConfig model** which reads from `settings.yaml` (or environment variables via pydantic-settings).

### Rationale
1. **Architectural Consistency**: Banner/title are site-wide settings like `locale` and `output_dir`, not per-image metadata like the entries in `gallery.yaml`.
2. **Type Safety**: Pydantic model validation ensures banner image path is valid and title is properly typed.
3. **Flexibility**: pydantic-settings allows configuration via YAML, environment variables, or .env file.
4. **Documentation**: Settings are centralized in one model, making the API clear.

### Implementation Approach
```python
# src/generator/model.py
class GalleryConfig(BaseSettings):
    # ... existing fields ...

    banner_image: Optional[Path] = Field(
        default=None,
        description="Path to banner image (relative to content_dir or absolute)"
    )

    gallery_title: Optional[str] = Field(
        default=None,
        description="Title displayed on gallery (if not set, uses 'Gallery' or i18n default)"
    )

    @field_validator("banner_image", mode="before")
    @classmethod
    def validate_banner_image(cls, v, info):
        """Validate banner image path exists if provided."""
        if v is None:
            return None

        path = Path(v) if not isinstance(v, Path) else v

        # Check if absolute path exists
        if path.is_absolute() and path.exists():
            return path

        # Try relative to content_dir
        content_dir = info.data.get("content_dir")
        if content_dir:
            full_path = Path(content_dir) / path
            if full_path.exists():
                return full_path

        raise ValueError(f"Banner image not found: {v}")
```

### Alternatives Considered
- **gallery.yaml**: Rejected because this file contains per-image metadata. Banner is site-wide, not image-specific.
- **Separate banner.yaml**: Rejected as unnecessary file proliferation. Two settings files (gallery.yaml for images, settings.yaml for generator config) is sufficient.
- **Hardcoded in template**: Rejected because it's not configurable and defeats the purpose of the feature.

---

## Q5: Banner Image Asset Handling

**Question**: Should banner images go through the thumbnail generation pipeline or be handled as static assets?

### Decision
**Copy banner image as static asset** to output directory without thumbnail generation.

### Rationale
1. **Performance**: Banner is above-the-fold and should load quickly. Full resolution is appropriate for full-width display.
2. **Simplicity**: Reusing existing static asset copying logic (CSS, JS files) is simpler than extending thumbnail pipeline.
3. **Quality**: Banner deserves high quality. Thumbnail pipeline is optimized for grid display, not hero images.
4. **Lazy Loading**: Banner cannot be lazy-loaded (above fold), so thumbnail optimization benefit is minimal.

### Implementation Approach
```python
# In build_html.py
def copy_banner_image(config: GalleryConfig, output_dir: Path) -> Optional[str]:
    """
    Copy banner image to output directory.

    Returns relative URL for use in template, or None if no banner configured.
    """
    if not config.banner_image:
        return None

    banner_output_dir = output_dir / "images" / "banner"
    banner_output_dir.mkdir(parents=True, exist_ok=True)

    dest_path = banner_output_dir / config.banner_image.name
    shutil.copy2(config.banner_image, dest_path)

    return f"images/banner/{config.banner_image.name}"
```

### Alternatives Considered
- **Run through thumbnail pipeline**: Rejected because banner needs different optimization strategy (higher quality, no multi-format needed for single above-fold image).
- **Responsive images with srcset**: Rejected as over-engineering. Single optimized image with CSS object-fit is simpler and sufficient for most use cases.
- **External URL**: Considered allowing external URLs but rejected due to security (CSP violation) and performance (external dependency) concerns.

---

## Q6: Backward Compatibility Strategy

**Question**: How should galleries without banner/title configuration behave?

### Decision
**Optional fields with graceful degradation** - if banner/title not configured, render existing header without changes.

### Rationale
1. **Backward Compatibility**: Existing galleries continue working without modification.
2. **Progressive Enhancement**: New galleries can adopt banner/title incrementally.
3. **Zero Migration**: No breaking changes to existing configuration files.
4. **Clear Opt-in**: Feature is explicitly enabled by adding configuration, not a breaking default change.

### Implementation Approach
```jinja2
{# index.html.j2 #}
<header>
    {% if banner_image %}
    <div class="gallery-banner">
        <img src="{{ banner_image }}" alt="{{ gallery_title or 'Gallery' }}" class="banner-image">
        {% if gallery_title %}
        <h1 class="banner-title">{{ gallery_title }}</h1>
        {% endif %}
    </div>
    {% else %}
    <h1>{{ gallery_title or default_title }}</h1>
    {% endif %}
</header>
```

### Alternatives Considered
- **Required fields with defaults**: Rejected because it would force all users to configure banner/title even if they don't want the feature.
- **Separate template**: Rejected as template proliferation. Single template with conditional rendering is cleaner.
- **Feature flag**: Rejected as unnecessary. Optional fields provide natural feature gating.

---

## Q7: Dark Mode Banner Handling

**Question**: How should banner images work with dark mode theming?

### Decision
**No automatic dark mode adjustments** - banner images display as-is in both light and dark modes, with title text always readable via overlay gradient.

### Rationale
1. **User Control**: Gallery owners choose banner images appropriate for their content. Automatic adjustments could degrade image quality.
2. **Consistent Branding**: Banner is typically a branding element that should look the same regardless of theme.
3. **Technical Simplicity**: No image manipulation or multiple versions needed.
4. **Text Readability**: Overlay gradient ensures title text is readable regardless of banner colors or user theme.

### Implementation Approach
```css
/* No dark mode specific styles needed for banner image */
.banner-image {
    /* Same in light and dark mode */
}

/* Gradient overlay ensures title readability in all scenarios */
.gallery-banner::after {
    background: linear-gradient(to top, rgba(0, 0, 0, 0.6), transparent);
}

.banner-title {
    color: white; /* Always white on gradient overlay */
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
}
```

### Alternatives Considered
- **CSS filters in dark mode**: Rejected because automatic darkening/lightening of banner images could clash with the image content and reduce quality.
- **Separate dark mode banner**: Rejected as excessive complexity. One banner image is sufficient with proper text overlay.
- **Theme-aware title color**: Rejected because overlay gradient provides consistent background for white text in all scenarios.

---

## Q8: Accessibility Requirements for Banner

**Question**: What ARIA attributes and semantic HTML are needed for the banner to meet accessibility standards?

### Decision
Use **semantic `<header>` element with proper heading hierarchy** and `alt` text for banner image.

### Rationale
1. **Semantic HTML**: `<header>` landmark automatically communicates structure to screen readers.
2. **Heading Hierarchy**: Title remains `<h1>` (most important heading) whether in banner or standalone.
3. **Image Alt Text**: Banner image gets descriptive alt text from gallery_title or generic description.
4. **Keyboard Navigation**: Banner is non-interactive, so no focus management needed.

### Implementation Approach
```jinja2
<header role="banner">
    {% if banner_image %}
    <div class="gallery-banner">
        <img
            src="{{ banner_image }}"
            alt="{% if gallery_title %}Banner for {{ gallery_title }}{% else %}Gallery banner{% endif %}"
            class="banner-image"
        >
        {% if gallery_title %}
        <h1 class="banner-title">{{ gallery_title }}</h1>
        {% endif %}
    </div>
    {% else %}
    <h1>{{ gallery_title or default_title }}</h1>
    {% endif %}
</header>
```

### Accessibility Checklist
- ✅ Semantic `<header>` element (implicit `banner` landmark)
- ✅ Proper heading hierarchy (`<h1>` for title)
- ✅ Descriptive alt text for banner image
- ✅ Sufficient color contrast for title text (white on dark gradient = >7:1 ratio)
- ✅ Responsive text sizing (rem units, respects user font size preferences)
- ✅ No interactive elements in banner (no focus traps)

### Alternatives Considered
- **Banner as background-image**: Rejected because CSS background images are invisible to screen readers and couldn't have alt text.
- **ARIA label on banner div**: Rejected as unnecessary. The `<img>` alt text and `<h1>` already provide all needed context.
- **role="img" on banner div**: Rejected as semantically incorrect. The banner contains an image and heading, not itself an image.

---

## Q9: Subtitle Typography and Positioning

**Question**: How should the subtitle be styled and positioned relative to the title to maintain visual hierarchy?

### Decision
Use **smaller font size with lighter weight positioned directly below title** with reduced opacity for secondary emphasis.

### Rationale
1. **Visual Hierarchy**: Subtitle must be clearly secondary to title through size, weight, and opacity differences.
2. **Readability**: Still needs to be readable on banner gradient overlay, so white text with text-shadow like title.
3. **Spacing**: Minimal gap between title and subtitle creates visual grouping as a unit.
4. **Consistency**: Matches web design best practices for hero sections with title/subtitle pairs.

### Implementation Approach
```css
.banner-subtitle {
    position: absolute;
    bottom: 0.5rem; /* Just below title */
    left: 2rem;
    right: 2rem;
    font-size: 1.5rem;
    font-weight: 400; /* Normal weight vs title's 700 */
    line-height: 1.4;
    color: white;
    opacity: 0.9; /* Slightly transparent for secondary emphasis */
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.7);
    margin: 0;
    z-index: 2;
}

.banner-title {
    /* Adjust bottom positioning to make room for subtitle */
    bottom: 4rem; /* Was 2rem, increased for subtitle */
}

@media (max-width: 768px) {
    .banner-subtitle {
        font-size: 1.125rem;
        left: 1rem;
        right: 1rem;
    }

    .banner-title {
        bottom: 3rem; /* Less space on mobile */
    }
}
```

### Alternatives Considered
- **Same font size as title**: Rejected because it would compete with title and break visual hierarchy.
- **Different color (e.g., light gray)**: Rejected because on varying banner backgrounds, a single color wouldn't always have sufficient contrast. White with opacity maintains consistency.
- **Positioned above title**: Rejected as unconventional. Standard web pattern is title then subtitle.
- **Separate line with divider**: Rejected as unnecessarily complex. Simple spacing is sufficient.

---

## Q10: Subtitle Dependency on Title

**Question**: Should subtitle be displayable without a title, or should it require a title to be present?

### Decision
**Subtitle requires title to be present** - only display subtitle when gallery_title is also configured.

### Rationale
1. **Semantic Correctness**: A subtitle by definition is supplementary to a title. Displaying subtitle without title is semantically incorrect.
2. **Visual Hierarchy**: Subtitle styling (smaller, lighter) assumes presence of a larger, bolder title above it. Without title, subtitle would look oddly small.
3. **Configuration Clarity**: Makes the dependency explicit, preventing user confusion about why subtitle alone doesn't work.
4. **Simplified Logic**: Clear if/then: if title exists, check for subtitle. If no title, skip subtitle entirely.

### Implementation Approach
```jinja2
{% if banner_image %}
<div class="gallery-banner">
    <img src="{{ banner_image }}" alt="..." class="banner-image">
    {% if gallery_title %}
    <h1 class="banner-title">{{ gallery_title }}</h1>
    {% if gallery_subtitle %}
    <p class="banner-subtitle">{{ gallery_subtitle }}</p>
    {% endif %}
    {% endif %}
</div>
{% else %}
<h1>{{ gallery_title or default_title }}</h1>
{# No subtitle display in simple header - requires banner context #}
{% endif %}
```

### Alternatives Considered
- **Subtitle without title**: Rejected as semantically incorrect and visually awkward.
- **Promote subtitle to title if no title**: Rejected as it would confuse user intent. If they want a title, they should configure gallery_title.
- **Display subtitle in simple header**: Rejected because simple header should remain simple. Subtitle is a banner enhancement feature.

---

## Q11: Subtitle Configuration Validation

**Question**: What validation rules should apply to the subtitle field?

### Decision
Use **same validation as title** - optional field with length constraints and whitespace trimming.

### Rationale
1. **Consistency**: Subtitle and title are similar text fields, should have similar validation.
2. **Length Limit**: Subtitles should be concise (recommended 50-100 chars, max 300 for edge cases).
3. **Whitespace Handling**: Empty or whitespace-only subtitles should be treated as None (not configured).
4. **Type Safety**: Pydantic validator ensures clean string or None.

### Implementation Approach
```python
gallery_subtitle: Optional[str] = Field(
    default=None,
    description="Gallery subtitle displayed below title (requires gallery_title)"
)

@field_validator("gallery_subtitle", mode="before")
@classmethod
def validate_gallery_subtitle(cls, v):
    """
    Validate gallery subtitle if provided.

    Rules:
    - None is valid (no subtitle)
    - If string provided, must not be empty or whitespace-only
    - Length limit for reasonable display
    """
    if v is None:
        return None

    if isinstance(v, str):
        v = v.strip()
        if not v:
            return None  # Treat empty as None
        if len(v) > 300:
            raise ValueError("Gallery subtitle too long (max 300 characters)")

    return v
```

### Alternatives Considered
- **No validation**: Rejected because unlimited length could break layout.
- **Shorter max length (100 chars)**: Considered but rejected to allow flexibility for descriptive subtitles.
- **Error on empty**: Rejected because treating empty as None is more user-friendly (allows easy disabling).

---

## Summary of Technical Decisions

| Decision Area | Choice | Key Rationale |
|--------------|--------|---------------|
| Banner Cropping | CSS object-fit: cover | Simple, flexible, no build-time processing |
| Banner Height | Viewport-relative (vh) | Responsive, scales naturally across devices |
| Title Styling | Overlay on banner with gradient | Readable, no external fonts, dark mode compatible |
| Subtitle Styling | Smaller font, lighter weight, below title | Secondary visual hierarchy, maintains readability |
| Subtitle Dependency | Requires title to be present | Semantically correct, prevents awkward standalone subtitle |
| Subtitle Validation | Optional with 300 char limit | Same pattern as title, flexible but bounded |
| Configuration Location | GalleryConfig in settings.yaml | Site-wide setting, type-safe, flexible |
| Asset Handling | Static asset copy | Above-fold image needs quality, not thumbnails |
| Backward Compatibility | Optional fields | Existing galleries work without changes |
| Dark Mode | No special handling | Banner consistent across themes, overlay ensures readability |
| Accessibility | Semantic HTML + alt text | Meets WCAG 2.1 AA, screen reader friendly |

All decisions prioritize simplicity, maintainability, and adherence to the constitution's static-first, performance-focused principles.
