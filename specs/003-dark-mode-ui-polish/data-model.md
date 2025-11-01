# Data Model: Dark Mode and UI Polish

**Feature**: 003-dark-mode-ui-polish | **Date**: 2025-11-01 | **Phase**: 1 (Design)

## Overview

This feature introduces no new data storage or runtime data structures. All entities are **compile-time configuration values** expressed as CSS custom properties and constants. The data model describes the semantic organization of these values for maintainability and testing.

---

## Entity Definitions

### Entity 1: Color Palette

**Purpose**: Define all theme colors for light and dark modes with semantic names

**Scope**: CSS custom properties in `:root` selector (global scope)

**Attributes**:

| Property Name | Type | Light Mode Value | Dark Mode Value | Constraints |
|---------------|------|------------------|-----------------|-------------|
| `--color-bg` | CSS Color | `#ffffff` | `#0f0f0f` | Background color |
| `--color-bg-elevated` | CSS Color | `#f5f5f5` | `#1a1a1a` | Cards, sections |
| `--color-text` | CSS Color | `#1a1a1a` | `#e8e8e8` | Primary text |
| `--color-text-secondary` | CSS Color | `#666666` | `#a0a0a0` | Captions, metadata |
| `--color-border` | CSS Color | `#e0e0e0` | `#2a2a2a` | Borders, dividers |
| `--color-hover` | CSS Color | `#f5f5f5` | `#252525` | Hover states |
| `--color-accent` | CSS Color | `#0066cc` | `#4a9eff` | Links, focus indicators |

**Invariants**:
- All text colors MUST achieve WCAG 2.1 AA contrast ratio (≥4.5:1) against their paired background
- `--color-bg-elevated` MUST be visually distinguishable from `--color-bg` (≥5% lightness difference)
- Focus indicator `--color-accent` MUST achieve ≥3:1 contrast against both text and background colors

**Usage**:
```css
/* Applied throughout gallery.css and fullscreen.css */
body {
  background-color: var(--color-bg);
  color: var(--color-text);
}

.image-item:hover {
  background-color: var(--color-hover);
}
```

**Testing**:
- Automated: axe-core contrast ratio verification in `tests/accessibility/test_axe_a11y.py`
- Manual: Visual inspection across browsers/OSs in Phase 2

---

### Entity 2: Animation Timing

**Purpose**: Define transition durations and easing functions for consistent motion

**Scope**: CSS custom properties in `:root` selector

**Attributes**:

| Property Name | Type | Value | Usage |
|---------------|------|-------|-------|
| `--transition-fast` | Duration | `150ms` | Hover states, focus indicators, small UI changes |
| `--transition-normal` | Duration | `250ms` | Image fade-in, modal open/close, medium UI changes |
| `--transition-slow` | Duration | `400ms` | Lazy-load shimmer, large layout shifts |
| `--easing-smooth` | Easing Function | `cubic-bezier(0.4, 0.0, 0.2, 1)` | All transitions (Material Design standard) |

**Invariants**:
- All durations MUST be 0ms when `prefers-reduced-motion: reduce` is active
- Fast < Normal < Slow (duration hierarchy maintained)
- Easing function applies to all transitions unless overridden for specific effect

**Usage**:
```css
.image-item {
  transition: transform var(--transition-fast) var(--easing-smooth),
              opacity var(--transition-normal) var(--easing-smooth);
}

@media (prefers-reduced-motion: reduce) {
  :root {
    --transition-fast: 0ms;
    --transition-normal: 0ms;
    --transition-slow: 0ms;
  }
}
```

**Testing**:
- Performance: Chrome DevTools frame rate monitoring (target 60fps)
- Accessibility: Manual testing with reduced motion system preference

---

### Entity 3: Typography Scale

**Purpose**: Define font sizes, weights, and spacing for consistent text hierarchy

**Scope**: CSS custom properties in `:root` selector (extends existing values)

**Attributes**:

| Property Name | Type | Value | Usage |
|---------------|------|-------|-------|
| `--font-size-h1` | Size | `2rem` (32px) | Gallery title |
| `--font-size-h2` | Size | `1.5rem` (24px) | Category headers |
| `--font-size-body` | Size | `1rem` (16px) | Default text |
| `--font-size-caption` | Size | `0.875rem` (14px) | Image captions, metadata |
| `--line-height-base` | Unitless | `1.65` | Body text (improved for dark mode) |
| `--line-height-heading` | Unitless | `1.3` | Headings |
| `--letter-spacing-heading` | Length | `0.01em` | Category headers (improved scanability) |

**Invariants**:
- Font sizes maintain proportional hierarchy: H1 > H2 > Body > Caption
- Line heights ≥1.5 for body text (WCAG readability guideline)
- System font stack unchanged (zero bytes, cross-platform consistency)

**Usage**:
```css
header h1 {
  font-size: var(--font-size-h1);
  line-height: var(--line-height-heading);
}

.category-section h2 {
  font-size: var(--font-size-h2);
  letter-spacing: var(--letter-spacing-heading);
}
```

**Testing**:
- Readability: Manual review at 100%-200% zoom levels
- Consistency: Visual regression testing (Phase 2, optional)

---

### Entity 4: Spacing System

**Purpose**: Define consistent margin and padding values for visual rhythm

**Scope**: CSS custom properties in `:root` selector (already exists as `--spacing-unit`)

**Attributes**:

| Property Name | Type | Value | Usage |
|---------------|------|-------|-------|
| `--spacing-unit` | Size | `1rem` (16px) | Base spacing unit (already defined) |
| `--gap` | Size | `1rem` | Grid gap (already defined) |
| `--border-radius` | Size | `0.5rem` (8px) | Image items, buttons (already defined) |

**Invariants**:
- All spacing derives from `--spacing-unit` (multiples: 0.5x, 1x, 2x, 3x)
- Consistent across light and dark modes (spacing unchanged)

**Usage**:
```css
/* Already in use, no changes needed */
.image-grid {
  gap: var(--gap);
}

.category-section {
  margin-bottom: calc(var(--spacing-unit) * 3);
}
```

**Testing**:
- Visual inspection: Ensure breathing room maintained in dark mode

---

### Entity 5: Image Shadow (Dark Mode Only)

**Purpose**: Ensure dark images remain distinguishable from dark background

**Scope**: Applied to `.image-item img` in dark mode only

**Attributes**:

| Property | Type | Value | Purpose |
|----------|------|-------|---------|
| `box-shadow` | Shadow | `0 0 0 1px rgba(255,255,255,0.05), 0 2px 8px rgba(0,0,0,0.3)` | Subtle border + depth |

**Invariants**:
- Only active in `@media (prefers-color-scheme: dark)`
- Shadow subtle enough to not distract from image content
- Border component (`1px rgba(255,255,255,0.05)`) provides separation

**Usage**:
```css
@media (prefers-color-scheme: dark) {
  .image-item img {
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.05),
                0 2px 8px rgba(0, 0, 0, 0.3);
  }
}
```

**Testing**:
- Edge case: Test with very dark images (black backgrounds, low-key photography)

---

## Entity Relationships

```
Color Palette
    ├── Used by: Body background, text colors, borders
    └── Tested by: axe-core contrast verification

Animation Timing
    ├── Used by: Image transitions, modal animations, hover effects
    └── Tested by: Frame rate monitoring, reduced motion verification

Typography Scale
    ├── Uses: Spacing System (line-height scales with --spacing-unit)
    └── Tested by: Zoom level readability checks

Spacing System
    ├── Used by: Layout grid, margins, padding
    └── Independent: No changes needed for dark mode

Image Shadow
    ├── Uses: Color Palette (shadow colors derived from palette)
    └── Tested by: Dark image edge case verification
```

---

## Data Flow

```
Build Time (generator/build_html.py):
  1. Read gallery.yaml (unchanged)
  2. Generate HTML with <meta name="color-scheme" content="light dark">
  3. Link CSS files (gallery.css, fullscreen.css with dark mode variables)
  4. Hash assets (SHA256, unchanged)

Runtime (Browser):
  1. Detect system preference via @media (prefers-color-scheme: dark)
  2. Apply dark mode CSS custom properties
  3. Render gallery with dark theme
  4. Respect prefers-reduced-motion for animations

No server-side or client-side data persistence required.
```

---

## Size Impact Analysis

| Entity | CSS Lines | Estimated Size | Cumulative |
|--------|-----------|----------------|------------|
| Color Palette (7 properties × 2 modes) | ~20 lines | ~600 bytes | 600B |
| Animation Timing (4 properties) | ~10 lines | ~300 bytes | 900B |
| Typography Scale (7 properties) | ~15 lines | ~400 bytes | 1300B |
| Spacing System (no changes) | 0 lines | 0 bytes | 1300B |
| Image Shadow (dark mode only) | ~5 lines | ~150 bytes | 1450B |
| Media queries, comments, formatting | ~15 lines | ~550 bytes | **2000B (2KB)** |

**Total Addition**: ~2KB CSS (8% of 25KB budget)

---

## Validation Rules

### Color Palette Validation
- **Contrast Check**: All text/background pairs MUST pass WCAG 2.1 AA (≥4.5:1 for normal text, ≥3:1 for large text)
- **Tool**: WebAIM Contrast Checker or axe-core automated testing
- **Enforcement**: CI gate in `.github/workflows/ci.yml` runs axe tests

### Animation Timing Validation
- **Frame Rate Check**: Animations MUST maintain ≥60fps on modern browsers
- **Tool**: Chrome DevTools Performance Monitor
- **Enforcement**: Manual testing in Phase 2, document results

### Typography Scale Validation
- **Readability Check**: Text MUST be readable at 100%-200% zoom without horizontal scrolling
- **Tool**: Manual browser testing
- **Enforcement**: Manual verification in Phase 2

---

## Migration Path

**From**: Current light-only theme with hardcoded colors  
**To**: Light/dark theme with CSS custom properties

**Steps**:
1. Extract existing color values into CSS custom properties (light mode defaults)
2. Define dark mode overrides in `@media (prefers-color-scheme: dark)` block
3. Replace hardcoded color references with `var(--color-*)` throughout CSS
4. Test contrast ratios with axe-core
5. Verify no visual regressions in light mode

**Rollback**: If dark mode fails validation, delete `@media (prefers-color-scheme: dark)` block and revert to hardcoded light mode values.

---

## References

- [CSS Custom Properties Spec (W3C)](https://www.w3.org/TR/css-variables-1/)
- [WCAG 2.1 Contrast Guidelines (Level AA)](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [MDN: prefers-color-scheme](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme)
- [Material Design Motion System](https://m3.material.io/styles/motion/overview)
