# Research: Mobile Full-Screen Experience & Advanced Performance

**Feature**: 010-mobile-fullscreen-performance
**Date**: December 8, 2025
**Status**: Complete

## Phase 0: Research Findings

This document consolidates research findings for all technical unknowns identified in the Technical Context phase.

---

## 1. Blur Placeholder Generation Strategy

### Decision
Generate ultra-low-resolution blur placeholders (20x20px before blur) using Pillow during build process, apply Gaussian blur (radius 10-20px), encode as base64 data URLs, embed inline in HTML templates.

### Rationale
- **Instant Display**: Data URLs require zero network requests, placeholders visible immediately on page parse
- **Perceptual Performance**: Human perception of "fast" is dominated by time-to-first-content, not total load time
- **Proven Pattern**: Used by Medium (blur-up technique), Gatsby Image, Next.js Image Optimization
- **Build-Time Cost**: ~50-100ms per image acceptable (one-time cost during build, not runtime)
- **Size-Quality Tradeoff**: 20x20px provides enough color/structure information while keeping data URL <1KB

### Implementation Approach
```python
# Pillow implementation pseudocode
def generate_blur_placeholder(image_path: Path) -> str:
    """Generate ultra-low-res blurred data URL."""
    img = PILImage.open(image_path)

    # Step 1: Resize to 20x20 (maintain aspect ratio with padding)
    img.thumbnail((20, 20), PILImage.Resampling.LANCZOS)

    # Step 2: Apply Gaussian blur (radius 10)
    img = img.filter(ImageFilter.GaussianBlur(radius=10))

    # Step 3: Convert to JPEG (quality 50, size ~500-800 bytes)
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=50, optimize=True)

    # Step 4: Base64 encode
    b64 = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/jpeg;base64,{b64}"
```

### Alternatives Considered

**Alternative 1: CSS Dominant Color Extraction**
- Extract dominant color from image, use as solid background
- **Rejected**: No preview of actual image content, poor UX, users don't recognize images

**Alternative 2: External Blur Placeholder Files**
- Generate blur images as separate .jpg files
- **Rejected**: Requires network request (defeats instant-display purpose), adds latency

**Alternative 3: SVG Traced Placeholders**
- Use Potrace/primitive to generate SVG outlines
- **Rejected**: Complex build process, larger file sizes (>2KB), inconsistent quality

**Alternative 4: WebP Blur Placeholders**
- Use WebP format for smaller data URLs
- **Considered but deferred**: Better compression (~30% smaller) but adds build complexity, JPEG sufficient for MVP

### Research Sources
- [Medium blur-up technique article](https://jmperezperez.com/medium-image-progressive-loading-placeholder/)
- [Gatsby Image blur placeholders](https://www.gatsbyjs.com/docs/how-to/images-and-media/using-gatsby-plugin-image/)
- Pillow ImageFilter documentation
- Base64 encoding size analysis (1.33x overhead)

---

## 2. Browser Fullscreen API Best Practices

### Decision
Use standardized Fullscreen API (`element.requestFullscreen()`) with vendor prefix fallback, implement mobile-specific workarounds for iOS Safari (viewport-based fixed positioning + scroll-to-hide-UI), graceful degradation for unsupported browsers.

### Rationale
- **Wide Browser Support**: Chrome 71+, Firefox 64+, Safari 11.3+, Edge 79+ (covers 95%+ mobile browsers)
- **iOS Safari Limitations**: Doesn't support Fullscreen API for non-media elements, requires alternative approach
- **User Expectations**: Mobile users expect immersive viewing (no browser chrome)
- **Progressive Enhancement**: Feature detection ensures functionality without breaking older browsers

### Implementation Approach

**Desktop/Android (Fullscreen API)**:
```javascript
async function enterFullscreen(element) {
  try {
    if (element.requestFullscreen) {
      await element.requestFullscreen();
    } else if (element.webkitRequestFullscreen) {  // Safari
      element.webkitRequestFullscreen();
    } else if (element.msRequestFullscreen) {  // IE11
      element.msRequestFullscreen();
    }
  } catch (err) {
    console.warn('Fullscreen not supported, using fallback');
    applyFullscreenFallback(element);
  }
}
```

**iOS Safari Fallback**:
```javascript
function applyFullscreenFallback(element) {
  // Use fixed positioning + viewport units
  element.style.position = 'fixed';
  element.style.top = '0';
  element.style.left = '0';
  element.style.width = '100vw';
  element.style.height = '100vh';
  element.style.zIndex = '9999';

  // Scroll page to top to hide Safari address bar
  window.scrollTo(0, 1);

  // Prevent body scroll
  document.body.style.overflow = 'hidden';
}
```

### Mobile-Specific Considerations
- **Orientation Changes**: Listen for `orientationchange` / `resize` events, recalculate dimensions
- **Address Bar Hiding**: iOS Safari address bar auto-hides on scroll, calculate viewport height dynamically (`window.innerHeight`)
- **Safe Area Insets**: Use `env(safe-area-inset-*)` CSS for notched devices (iPhone X+)
- **Gesture Conflicts**: Disable pinch-zoom in fullscreen mode (`touch-action: none`)

### Alternatives Considered

**Alternative 1: Video Element Fullscreen Only**
- Only use native fullscreen for `<video>` elements (well-supported)
- **Rejected**: Doesn't apply to image galleries, limited scope

**Alternative 2: Custom Fullscreen Modal (No API)**
- Build pure CSS fullscreen modal without using Fullscreen API
- **Rejected**: Doesn't hide browser UI on mobile, suboptimal immersion

**Alternative 3: Open Images in New Tab**
- Simple `target="_blank"` for fullscreen viewing
- **Rejected**: Poor UX (breaks navigation flow), doesn't preserve gallery context

### Research Sources
- [MDN Fullscreen API](https://developer.mozilla.org/en-US/docs/Web/API/Fullscreen_API)
- [Can I Use: Fullscreen API](https://caniuse.com/fullscreen)
- iOS Safari viewport behavior analysis
- Photoswipe library implementation reference

---

## 3. Progressive Image Loading & Transition Strategy

### Decision
Implement three-stage loading with CSS transitions: blur placeholder (instant) → thumbnail (fast) → original (full quality). Use `<img>` element with JavaScript-managed `src` updates, CSS opacity transitions for smooth fading (300ms), intelligent skip logic for cached content.

### Rationale
- **Perceived Performance**: Users see *something* immediately (blur), then progressive quality improvement
- **Bandwidth Optimization**: Load appropriate quality for viewport (thumbnail sufficient for grid view)
- **Smooth Transitions**: Fade transitions prevent jarring "pop-in" effect
- **Cache-Aware**: Skip intermediate steps if high-quality version already cached (avoids unnecessary transitions)

### Implementation Approach

**HTML Structure**:
```html
<div class="image-container" data-blur="data:image/jpeg;base64,...">
  <img
    class="image-progressive"
    data-thumbnail="thumb.webp"
    data-original="original.jpg"
    alt="Image description"
  />
</div>
```

**CSS Transitions**:
```css
.image-container {
  position: relative;
  background-size: cover;
  background-position: center;
  background-image: var(--blur-placeholder); /* Inline style set from data-blur */
}

.image-progressive {
  opacity: 0;
  transition: opacity 300ms ease-in-out;
}

.image-progressive.loaded {
  opacity: 1;
}
```

**JavaScript Loading Logic**:
```javascript
function loadProgressiveImage(container) {
  const img = container.querySelector('.image-progressive');
  const thumbnailSrc = img.dataset.thumbnail;
  const originalSrc = img.dataset.original;

  // Set blur placeholder as background
  container.style.setProperty('--blur-placeholder',
    `url("${container.dataset.blur}")`);

  // Load thumbnail
  const thumbImg = new Image();
  thumbImg.onload = () => {
    img.src = thumbnailSrc;
    img.classList.add('loaded');

    // Preload original in background
    const originalImg = new Image();
    originalImg.onload = () => {
      // Only upgrade if not cached (check load time)
      if (originalImg.complete && originalImg.naturalWidth > 0) {
        img.src = originalSrc;
      }
    };
    originalImg.src = originalSrc;
  };
  thumbImg.src = thumbnailSrc;
}
```

### Skip Logic for Cached Content
```javascript
// Skip thumbnail if original loads fast (cached)
const startTime = performance.now();
const img = new Image();
img.onload = () => {
  const loadTime = performance.now() - startTime;
  if (loadTime < 100) {
    // Fast load = cached, skip thumbnail step
    element.src = originalSrc;
  } else {
    // Slow load = not cached, use thumbnail first
    element.src = thumbnailSrc;
    // ... then load original
  }
};
img.src = originalSrc;
```

### Alternatives Considered

**Alternative 1: IntersectionObserver Lazy Loading**
- Only load images when they enter viewport
- **Retained as complementary technique**: Combine with progressive loading for best results

**Alternative 2: `<picture>` Element with Multiple Sources**
- Use native responsive images (`<source>` tags)
- **Rejected**: Can't control blur placeholder step, no smooth transitions between sources

**Alternative 3: CSS `background-image` Only**
- Use background images instead of `<img>` tags
- **Rejected**: Poor accessibility (no alt text), SEO concerns, harder to implement progressive loading

**Alternative 4: Canvas-Based Blur Rendering**
- Draw blur placeholder on `<canvas>` for perfect blur control
- **Rejected**: Overengineered, data URL approach simpler and sufficient

### Research Sources
- [Progressive Image Loading Techniques](https://css-tricks.com/the-blur-up-technique-for-loading-background-images/)
- Native lazy loading browser support
- Intersection Observer API usage patterns
- Performance timing API for cache detection

---

## 4. Mobile Control Visibility & Auto-Hide Timer

### Decision
Hide navigation controls by default on mobile (<768px), show on tap with 3-second auto-hide timer, use CSS opacity transitions (300ms), reset timer on any user interaction, maintain keyboard accessibility regardless of visual visibility.

### Rationale
- **Unobstructed Viewing**: Hidden controls provide true full-screen experience, maximize image visibility
- **Discoverability**: Single tap reveals controls (intuitive mobile pattern)
- **Auto-Dismiss**: 3-second timer balances "don't get in the way" with "stay visible long enough to use"
- **Accessibility**: Controls remain focusable/keyboard-accessible even when visually hidden

### Implementation Approach

**CSS Implementation**:
```css
/* Mobile only (<768px) */
@media (max-width: 767px) {
  .fullscreen-controls {
    opacity: 0;
    pointer-events: none;
    transition: opacity 300ms ease-in-out;
  }

  .fullscreen-controls.visible {
    opacity: 1;
    pointer-events: auto;
  }

  /* Keep controls keyboard-accessible when hidden */
  .fullscreen-controls:focus-within {
    opacity: 1;
    pointer-events: auto;
  }
}

/* Desktop: always visible */
@media (min-width: 768px) {
  .fullscreen-controls {
    opacity: 1;
    pointer-events: auto;
  }
}
```

**JavaScript State Management**:
```javascript
class ControlVisibilityManager {
  constructor() {
    this.hideTimer = null;
    this.isVisible = false;
    this.isMobile = window.matchMedia('(max-width: 767px)').matches;
  }

  showControls() {
    if (!this.isMobile) return; // Desktop always visible

    const controls = document.querySelector('.fullscreen-controls');
    controls.classList.add('visible');
    this.isVisible = true;

    // Reset auto-hide timer
    this.resetHideTimer();
  }

  hideControls() {
    if (!this.isMobile) return;

    const controls = document.querySelector('.fullscreen-controls');
    controls.classList.remove('visible');
    this.isVisible = false;
  }

  resetHideTimer() {
    clearTimeout(this.hideTimer);
    this.hideTimer = setTimeout(() => this.hideControls(), 3000);
  }

  handleUserInteraction() {
    if (this.isVisible) {
      this.resetHideTimer(); // Extend visibility
    } else {
      this.showControls(); // Show controls
    }
  }
}

// Usage
const manager = new ControlVisibilityManager();

// Toggle on tap/click
overlay.addEventListener('click', (e) => {
  if (e.target.matches('.fullscreen-image')) {
    manager.handleUserInteraction();
  }
});

// Reset timer on button clicks
controls.addEventListener('click', () => {
  manager.resetHideTimer();
});

// Hide on swipe navigation
overlay.addEventListener('touchend', () => {
  manager.hideControls();
});
```

### Timer Duration Research
- **Instagram Stories**: 3-second auto-advance (taps pause timer)
- **YouTube Mobile**: Controls hide after 3 seconds
- **Native iOS Photos**: Controls hide after ~5 seconds
- **Decision: 3 seconds** - Industry standard, balances usability with immersion

### Alternatives Considered

**Alternative 1: Always-Visible Controls with Semi-Transparency**
- Show controls at 50% opacity permanently
- **Rejected**: Still obscures image content, defeats purpose of immersive viewing

**Alternative 2: Edge-Zone Tap Areas**
- Tap left/right edges only, center tap has no controls
- **Rejected**: Less discoverable, conflicts with swipe gestures

**Alternative 3: Double-Tap to Toggle Controls**
- Require double-tap instead of single tap
- **Rejected**: Less intuitive, conflicts with zoom gestures

**Alternative 4: Gesture-Based Show (Swipe Down from Top)**
- Swipe down from top edge to reveal controls
- **Retained as additional option**: Can complement tap-to-reveal

### Research Sources
- Mobile UX patterns in Instagram, YouTube, Google Photos
- [Material Design: Full-Screen Dialogs](https://material.io/components/dialogs#full-screen-dialog)
- iOS Human Interface Guidelines for full-screen content
- Accessibility best practices for hidden controls

---

## 5. Build Process Integration & Caching

### Decision
Extend existing `ThumbnailGenerator` class to generate blur placeholders alongside thumbnails, store blur data URLs in build cache JSON (same structure as thumbnail cache), add `blur_placeholder` field to `ImageMetadata` Pydantic model, pass blur placeholders to Jinja2 templates as inline style attributes.

### Rationale
- **Reuse Infrastructure**: Leverage existing thumbnail generation pipeline (EXIF handling, caching, parallelization)
- **Incremental Builds**: Cache blur placeholders to avoid regenerating on every build
- **Type Safety**: Pydantic models ensure data integrity
- **Template Integration**: Jinja2 already used for HTML generation, natural fit for inline styles

### Implementation Approach

**Extend Data Model** (`model.py`):
```python
from pydantic import BaseModel, Field

class BlurPlaceholder(BaseModel):
    """Ultra-low-resolution blur placeholder data."""
    data_url: str = Field(..., description="Base64-encoded data URL")
    size_bytes: int = Field(..., description="Size of data URL in bytes")
    generated_at: datetime
    source_hash: str = Field(..., description="Hash of source image")

class ImageMetadata(BaseModel):
    # ... existing fields ...
    blur_placeholder: Optional[BlurPlaceholder] = None
```

**Extend ThumbnailGenerator** (`thumbnails.py`):
```python
def generate_blur_placeholder(self, source_path: Path) -> BlurPlaceholder:
    """Generate ultra-low-res blur data URL."""
    # Check cache first
    cache_key = f"blur_{hash_file(source_path)}"
    if cache_key in self.cache:
        return BlurPlaceholder(**self.cache[cache_key])

    # Generate blur placeholder
    img = PILImage.open(source_path)
    img.thumbnail((20, 20), PILImage.Resampling.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(radius=10))

    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=50, optimize=True)
    b64 = base64.b64encode(buffer.getvalue()).decode()
    data_url = f"data:image/jpeg;base64,{b64}"

    placeholder = BlurPlaceholder(
        data_url=data_url,
        size_bytes=len(data_url),
        generated_at=datetime.now(),
        source_hash=hash_file(source_path)
    )

    # Cache for next build
    self.cache[cache_key] = placeholder.model_dump()
    return placeholder
```

**Template Integration** (`index.html.j2`):
```jinja2
{% for image in category.images %}
<div class="image-container"
     style="background-image: url('{{ image.blur_placeholder.data_url }}')">
  <img
    data-thumbnail="{{ image.thumbnail.webp_path }}"
    data-original="{{ image.original_path }}"
    alt="{{ image.title }}"
    loading="lazy"
  />
</div>
{% endfor %}
```

### Build Cache Structure
```json
{
  "version": "1.0.0",
  "images": {
    "photo001.jpg": {
      "thumbnail": { /* existing thumbnail data */ },
      "blur_placeholder": {
        "data_url": "data:image/jpeg;base64,/9j/4AAQ...",
        "size_bytes": 823,
        "generated_at": "2025-12-08T10:30:00",
        "source_hash": "sha256:abc123..."
      }
    }
  }
}
```

### Alternatives Considered

**Alternative 1: Separate Blur Placeholder Generation Script**
- Standalone CLI command for blur generation
- **Rejected**: Adds complexity, users must remember to run multiple commands

**Alternative 2: Generate Blur Placeholders On-Demand in Template**
- Use Jinja2 filter to generate blur URLs during template rendering
- **Rejected**: Slows down template rendering, no caching, not idiomatic

**Alternative 3: Store Blur Placeholders as Separate JSON File**
- Generate `blur-placeholders.json` alongside HTML
- **Rejected**: Requires extra HTTP request, defeats instant-display purpose

### Research Sources
- Existing `thumbnails.py` implementation
- Pydantic model validation patterns
- Jinja2 inline style generation best practices
- JSON cache file structure analysis

---

## Summary: All Unknowns Resolved

All "NEEDS CLARIFICATION" items from Technical Context have been researched and documented above. The implementation plan can now proceed to Phase 1 (Design & Contracts) with full clarity on:

1. ✅ Blur placeholder generation technique (Pillow + Gaussian blur)
2. ✅ Fullscreen API usage and mobile fallbacks
3. ✅ Progressive loading strategy (3-stage with skip logic)
4. ✅ Control visibility management (tap-to-reveal + auto-hide)
5. ✅ Build process integration (extend ThumbnailGenerator)

**Ready for Phase 1**: Data model design, API contracts, quickstart documentation.
