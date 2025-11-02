# ADR 0010: Banner Cropping Approach

**Status**: Accepted
**Date**: 2025-11-02
**Context**: Feature 009-gallery-banner

## Context

The gallery banner feature displays a full-width image at the top of the page. Banner images have varying aspect ratios, but the display area needs consistent height across different viewports. We needed to decide between client-side (CSS) or server-side (build-time) image cropping to handle this.

## Decision

Use **CSS `object-fit: cover`** with viewport-relative heights (`vh` units) for banner image cropping.

The banner is styled with:
```css
.banner-image {
  width: 100%;
  height: var(--banner-height-desktop, 40vh);
  object-fit: cover;
  object-position: center center;
}
```

With responsive breakpoints:
- Desktop (>1024px): 40vh
- Tablet (768-1024px): 30vh
- Mobile (<768px): 25vh

## Rationale

### Advantages of CSS Cropping

1. **Simplicity**: No additional image processing pipeline needed. Browser-native CSS handles cropping automatically.

2. **Flexibility**: Gallery owners can adjust banner height via CSS custom properties without regenerating images.

3. **Performance**: Original banner image is served directly (optimized by user). CSS cropping is instantaneous with no build-time overhead.

4. **Responsive Design**: Different viewports can use different aspect ratios with media queries without requiring multiple image versions.

5. **Zero Build Complexity**: No need to track banner processing state, invalidate caches, or handle failed transformations.

### Alternatives Considered

#### Server-side Pre-cropping
- **Rejected** because it requires additional build-time processing
- Reduces flexibility (fixed aspect ratio per build)
- Complicates incremental builds
- Gallery owners must regenerate to try different cropping

#### Multiple Image Versions with Art Direction
- **Rejected** as over-engineering
- Increases build complexity and storage requirements
- CSS `object-fit` is widely supported (97%+ browsers)
- Simple solution provides better UX

#### Art Direction with `<picture>` Element
- **Rejected** because it's unnecessary complexity for this use case
- Single image with CSS cropping is sufficient for most banner scenarios
- Banner images are typically landscape-oriented with center-weighted composition
- Users can manually prepare images for specific layouts if needed

## Consequences

### Positive

- Clean implementation with no build-time image processing
- Easy customization through CSS custom properties
- Responsive out of the box
- No additional dependencies or tooling
- Backward compatible (CSS `object-fit` has excellent browser support)

### Negative

- Gallery owners have less control over which part of the image is displayed
- Tall portrait images may have important content cropped out
- No automatic art direction for different viewport sizes

### Mitigation

- Document recommended banner aspect ratios (16:9, 21:9 for optimal display)
- Provide `object-position` override via CSS custom properties for fine-tuning
- Banner images should be composed with center-weighted important content
- Gallery owners can prepare images specifically for banner use if needed

## Implementation

The CSS cropping is implemented in:
- `src/static/css/gallery.css` - Banner image styles
- `src/templates/index.html.j2` - Banner HTML structure

CSS custom properties allow easy customization:
```css
:root {
  --banner-height-desktop: 40vh;
  --banner-height-tablet: 30vh;
  --banner-height-mobile: 25vh;
}
```

Gallery owners can override these in their own stylesheets if needed.

## References

- [MDN: object-fit](https://developer.mozilla.org/en-US/docs/Web/CSS/object-fit)
- [CSS Tricks: Aspect Ratio Boxes](https://css-tricks.com/aspect-ratio-boxes/)
- Research: `specs/009-gallery-banner/research.md` (Q1: Banner Image Cropping Strategy)
