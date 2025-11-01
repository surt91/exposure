# CSS Variables Contract

**Feature**: 003-dark-mode-ui-polish | **Date**: 2025-11-01 | **Type**: Interface Contract

## Overview

This document defines the contract for CSS custom properties used in the dark mode implementation. All properties are defined in the `:root` selector and available globally. Changes to these properties MUST maintain backward compatibility or trigger a MINOR version bump.

---

## Color Palette Variables

### `--color-bg`
- **Type**: CSS Color (hex, rgb, hsl, or color name)
- **Purpose**: Primary background color for body/page
- **Light Mode**: `#ffffff` (white)
- **Dark Mode**: `#0f0f0f` (near-black)
- **Contrast Requirements**: MUST provide ≥4.5:1 contrast with `--color-text`
- **Used By**: `body`, `.gallery`, `.modal`

### `--color-bg-elevated`
- **Type**: CSS Color
- **Purpose**: Background for elevated surfaces (cards, sections)
- **Light Mode**: `#f5f5f5` (light gray)
- **Dark Mode**: `#1a1a1a` (dark gray)
- **Contrast Requirements**: MUST be distinguishable from `--color-bg` (≥5% lightness difference)
- **Used By**: `.category-section`, `.image-item` (loading state)

### `--color-text`
- **Type**: CSS Color
- **Purpose**: Primary text color
- **Light Mode**: `#1a1a1a` (near-black)
- **Dark Mode**: `#e8e8e8` (off-white)
- **Contrast Requirements**: ≥4.5:1 against `--color-bg` (WCAG 2.1 AA)
- **Used By**: `body`, `h1`, `h2`, `p`

### `--color-text-secondary`
- **Type**: CSS Color
- **Purpose**: Secondary text (captions, metadata, less prominent text)
- **Light Mode**: `#666666` (medium gray)
- **Dark Mode**: `#a0a0a0` (light gray)
- **Contrast Requirements**: ≥4.5:1 against `--color-bg` (WCAG 2.1 AA)
- **Used By**: `.image-caption`, `.modal-category`, `.modal-metadata p`

### `--color-border`
- **Type**: CSS Color
- **Purpose**: Borders, dividers, subtle separation lines
- **Light Mode**: `#e0e0e0` (light gray)
- **Dark Mode**: `#2a2a2a` (dark gray)
- **Contrast Requirements**: Visually distinguishable from backgrounds
- **Used By**: `header` (border-bottom), `.category-section h2` (border-bottom)

### `--color-hover`
- **Type**: CSS Color
- **Purpose**: Background color for hover states
- **Light Mode**: `#f5f5f5` (light gray)
- **Dark Mode**: `#252525` (dark gray)
- **Contrast Requirements**: Subtle but noticeable difference from `--color-bg`
- **Used By**: `.image-item:hover`, button hover states

### `--color-accent`
- **Type**: CSS Color
- **Purpose**: Accent color for links, focus indicators, interactive elements
- **Light Mode**: `#0066cc` (blue)
- **Dark Mode**: `#4a9eff` (lighter blue for dark backgrounds)
- **Contrast Requirements**: ≥3:1 against both `--color-bg` and `--color-text` (WCAG 2.1 AA for UI components)
- **Used By**: `.image-item:focus-within` (outline), links, `.modal-close:focus`

---

## Animation Timing Variables

### `--transition-fast`
- **Type**: CSS Duration (`<time>`)
- **Purpose**: Fast transitions for small UI changes
- **Value**: `150ms`
- **Reduced Motion**: `0ms` (when `prefers-reduced-motion: reduce`)
- **Used By**: Hover effects, focus indicators, button state changes

### `--transition-normal`
- **Type**: CSS Duration
- **Purpose**: Standard transitions for medium UI changes
- **Value**: `250ms`
- **Reduced Motion**: `0ms`
- **Used By**: Image fade-in, modal open/close, `.image-item` transform

### `--transition-slow`
- **Type**: CSS Duration
- **Purpose**: Slow transitions for large changes or loading states
- **Value**: `400ms`
- **Reduced Motion**: `0ms`
- **Used By**: Lazy-load shimmer animation (existing)

### `--easing-smooth`
- **Type**: CSS Easing Function (`<easing-function>`)
- **Purpose**: Standard easing for all transitions
- **Value**: `cubic-bezier(0.4, 0.0, 0.2, 1)` (Material Design standard)
- **Used By**: All transition declarations unless overridden

---

## Typography Variables

### `--font-size-h1`
- **Type**: CSS Length (`<length>`)
- **Purpose**: Font size for main page title
- **Value**: `2rem` (32px at default browser settings)
- **Used By**: `header h1`

### `--font-size-h2`
- **Type**: CSS Length
- **Purpose**: Font size for category headers
- **Value**: `1.5rem` (24px)
- **Used By**: `.category-section h2`

### `--font-size-body`
- **Type**: CSS Length
- **Purpose**: Default body text size
- **Value**: `1rem` (16px)
- **Used By**: `body`, `p`, default text

### `--font-size-caption`
- **Type**: CSS Length
- **Purpose**: Small text for captions and metadata
- **Value**: `0.875rem` (14px)
- **Used By**: `.image-caption`, `.modal-category`

### `--line-height-base`
- **Type**: Unitless number (`<number>`)
- **Purpose**: Line height for body text
- **Value**: `1.65`
- **Used By**: `body`, paragraphs, default text

### `--line-height-heading`
- **Type**: Unitless number
- **Purpose**: Line height for headings
- **Value**: `1.3`
- **Used By**: `h1`, `h2`, headings

### `--letter-spacing-heading`
- **Type**: CSS Length
- **Purpose**: Letter spacing for improved heading scanability
- **Value**: `0.01em`
- **Used By**: `.category-section h2`

---

## Spacing Variables (Existing - No Changes)

### `--spacing-unit`
- **Type**: CSS Length
- **Purpose**: Base spacing unit for margins and padding
- **Value**: `1rem` (16px)
- **Used By**: Margins, padding throughout layout

### `--gap`
- **Type**: CSS Length
- **Purpose**: Grid gap for image grid
- **Value**: `1rem`
- **Used By**: `.image-grid` (grid-gap)

### `--border-radius`
- **Type**: CSS Length
- **Purpose**: Border radius for rounded corners
- **Value**: `0.5rem` (8px)
- **Used By**: `.image-item`, buttons, modal elements

---

## Usage Example

```css
/* Define variables in :root (light mode defaults) */
:root {
  /* Colors */
  --color-bg: #ffffff;
  --color-text: #1a1a1a;
  --color-accent: #0066cc;
  
  /* Timing */
  --transition-fast: 150ms;
  --easing-smooth: cubic-bezier(0.4, 0.0, 0.2, 1);
  
  /* Typography */
  --font-size-h1: 2rem;
  --line-height-base: 1.65;
}

/* Override for dark mode */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0f0f0f;
    --color-text: #e8e8e8;
    --color-accent: #4a9eff;
  }
}

/* Apply variables */
body {
  background-color: var(--color-bg);
  color: var(--color-text);
  line-height: var(--line-height-base);
  transition: background-color var(--transition-normal) var(--easing-smooth),
              color var(--transition-normal) var(--easing-smooth);
}

a {
  color: var(--color-accent);
  transition: color var(--transition-fast) var(--easing-smooth);
}

/* Reduced motion override */
@media (prefers-reduced-motion: reduce) {
  :root {
    --transition-fast: 0ms;
    --transition-normal: 0ms;
    --transition-slow: 0ms;
  }
}
```

---

## Validation Rules

### Type Safety
- Color variables MUST be valid CSS color values (hex, rgb, hsl, named colors)
- Duration variables MUST use time units (`ms` or `s`)
- Length variables MUST use length units (`px`, `rem`, `em`, `%`)
- Unitless variables (line-height) MUST be numbers without units

### Contrast Requirements
- All color pairs (text on background) MUST pass WCAG 2.1 AA contrast checks:
  - Normal text (≥16px): 4.5:1 minimum
  - Large text (≥18px bold or ≥24px): 3:1 minimum
  - UI components (focus indicators): 3:1 minimum

### Performance Requirements
- Transition durations SHOULD be ≤400ms for perceived instant feedback
- Animations MUST maintain ≥60fps (test with Chrome DevTools Performance Monitor)

---

## Backward Compatibility

### Adding New Variables
- ✅ Safe: Add new variables without removing old ones
- ✅ Safe: Add new variables with default fallbacks using `var(--new-var, fallback)`

### Changing Variable Values
- ⚠️ Breaking: Change color values significantly (may affect user themes)
- ⚠️ Breaking: Change timing values dramatically (may affect animations)
- ✅ Safe: Minor tweaks to improve contrast or readability

### Removing Variables
- ❌ Breaking: Remove existing variables (breaks dependent CSS)
- ✅ Safe: Deprecate and provide fallback for 1+ versions before removal

---

## Testing Contract

### Automated Tests
- `tests/accessibility/test_axe_a11y.py`: Verify all contrast ratios pass WCAG 2.1 AA
- `tests/integration/test_asset_budgets.py`: Verify CSS file size ≤25KB after dark mode

### Manual Tests
- Visual inspection in Chrome, Firefox, Safari (light and dark modes)
- Keyboard navigation test (focus indicators visible with `--color-accent`)
- Reduced motion test (transitions disabled when system preference set)

---

## Versioning

**Current Version**: 1.0.0 (initial dark mode implementation)

**Change Log**:
- 1.0.0 (2025-11-01): Initial CSS variables contract for dark mode

**Future Versions**:
- Patch (1.0.x): Minor color tweaks, bug fixes
- Minor (1.x.0): New variables added, non-breaking enhancements
- Major (x.0.0): Breaking changes (removed variables, incompatible color schemes)

---

## References

- [CSS Custom Properties Spec (W3C)](https://www.w3.org/TR/css-variables-1/)
- [WCAG 2.1 Contrast Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [MDN: Using CSS custom properties](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
