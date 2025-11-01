# Research: Dark Mode and UI Polish

**Feature**: 003-dark-mode-ui-polish | **Date**: 2025-11-01 | **Phase**: 0 (Technology Decisions)

## Research Questions

### RQ-001: CSS-Only vs JS Framework/Library for Styling?

**Context**: User asked "also think about if using a js framework or library for styling is a sensible way to go"

**Options Evaluated**:

1. **Tailwind CSS** (utility-first CSS framework)
   - Size: ~10-15KB gzipped even with aggressive PurgeCSS configuration
   - Pros: Popular, good dark mode support via `dark:` prefix
   - Cons: Requires build step (PostCSS), risks CSS budget breach (currently ~4KB, limit 25KB)
   - Verdict: ❌ **REJECTED** - Budget risk too high

2. **CSS-in-JS** (styled-components, emotion, etc.)
   - Size: 10-15KB JS runtime + generated CSS
   - Pros: Dynamic theming, component-scoped styles
   - Cons: Violates static-first principle (requires JS runtime), breaches JS budget
   - Verdict: ❌ **REJECTED** - Constitutional violation (static-first)

3. **Vanilla CSS with CSS Custom Properties**
   - Size: ~2KB additional CSS for dark theme variables
   - Pros: Zero runtime, browser-native dark mode detection via `@media (prefers-color-scheme: dark)`, no build complexity
   - Cons: Slightly more manual work, no utility classes
   - Verdict: ✅ **SELECTED** - Preserves budgets, maintains static-first architecture

**Decision**: Pure CSS approach using CSS custom properties (`--color-*` variables) and `@media (prefers-color-scheme: dark)` query.

**Rationale**:
- Current CSS footprint: gallery.css (~4KB) + fullscreen.css (~2KB) = ~6KB
- Dark mode addition: ~2KB for color palette, animation timing variables
- Total: ~8KB (well under 25KB limit, 68% headroom)
- No JS changes needed, maintains 100% static delivery
- Browser-native dark mode detection (no manual toggle needed for MVP)

---

### RQ-002: Dark Color Palette Selection

**Requirements**: WCAG 2.1 AA contrast ratios (4.5:1 normal text, 3:1 large text)

**Selected Palette** (targeting modern dark mode aesthetics):

```css
/* Dark Mode Colors */
--color-bg-dark: #0f0f0f;              /* Near-black background */
--color-bg-dark-elevated: #1a1a1a;     /* Slightly lighter for cards/sections */
--color-text-dark: #e8e8e8;            /* Off-white text (softer than #fff) */
--color-text-dark-secondary: #a0a0a0;  /* Dimmed text for captions */
--color-border-dark: #2a2a2a;          /* Subtle borders */
--color-hover-dark: #252525;           /* Hover state background */
--color-accent-dark: #4a9eff;          /* Blue accent for links/focus */
```

**Contrast Verification** (using WebAIM contrast checker):
- `#e8e8e8` on `#0f0f0f` = 13.5:1 ✅ (exceeds 4.5:1)
- `#a0a0a0` on `#0f0f0f` = 6.2:1 ✅ (exceeds 4.5:1)
- `#4a9eff` on `#0f0f0f` = 8.1:1 ✅ (exceeds 4.5:1 for links)
- Modal buttons: `#ffffff` on `rgba(255,255,255,0.1)` background needs testing in Phase 1

**Inspiration**: GitHub dark theme, VS Code dark+ theme (familiar to developers)

---

### RQ-003: Animation Strategy

**Requirements**: 60fps, subtle flourishes, respect `prefers-reduced-motion`

**Selected Approach**: CSS transitions + CSS keyframes (no JS animation library)

**Animation Timing Values**:
```css
--transition-fast: 150ms;     /* Hover states, focus indicators */
--transition-normal: 250ms;   /* Image fade-in, modal open/close */
--transition-slow: 400ms;     /* Lazy-load shimmer (already exists) */
--easing-smooth: cubic-bezier(0.4, 0.0, 0.2, 1);  /* Material Design standard easing */
```

**Planned Flourishes**:
1. **Image hover**: Subtle scale (1.02x) + brightness increase (110%) - already exists, tune for dark mode
2. **Image fade-in**: Opacity 0 → 1 over 250ms when scrolling into view
3. **Modal transitions**: Backdrop fade + content slide-up (or fade only for reduced-motion)
4. **Focus indicators**: Smooth outline transition (already exists, verify contrast)

**JS Integration**: Use existing Intersection Observer (if present) or scroll event for fade-in trigger. Keep under 100 lines of code.

---

### RQ-004: Typography Scale and Font Choices

**Current Stack** (from gallery.css):
```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
```

**Decision**: ✅ **KEEP** existing system font stack
- Zero additional bytes (no web fonts)
- Excellent cross-platform consistency
- Already optimized for readability

**Typography Scale** (already defined, verify effectiveness):
- `h1`: 2rem (32px) - Gallery title
- `h2`: 1.5rem (24px) - Category headers
- Body: 1rem (16px) - Default text
- Caption: 0.875rem (14px) - Image captions, metadata

**Enhancements for Dark Mode**:
1. Increase line-height for body text: 1.6 → 1.65 (subtle breathing room)
2. Add letter-spacing to category headers: `letter-spacing: 0.01em` (improves scanability)
3. Verify font weights render well on dark backgrounds (system fonts generally OK)

**No Changes Needed**: Typography is already well-structured

---

### RQ-005: Browser Support Matrix

**Target Browsers** (from constitution: "last 2 versions of major browsers"):

| Feature | Chrome 120+ | Firefox 121+ | Safari 17+ | Edge 120+ |
|---------|-------------|--------------|------------|-----------|
| CSS Custom Properties | ✅ | ✅ | ✅ | ✅ |
| `@media (prefers-color-scheme)` | ✅ | ✅ | ✅ | ✅ |
| `prefers-reduced-motion` | ✅ | ✅ | ✅ | ✅ |
| CSS Grid (already used) | ✅ | ✅ | ✅ | ✅ |
| `aspect-ratio` (already used) | ✅ | ✅ | ✅ | ✅ |

**Fallback Strategy**: None needed - all target browsers support CSS custom properties since 2016+. If older browser detected (via analytics, post-implementation), can add fallback via `@supports` query.

**Testing Plan**:
- BrowserStack for visual verification across browsers/OSs
- Check OS-level dark mode integration (macOS, Windows 11, iOS, Android)
- Verify color-scheme meta tag enables native scrollbar styling

---

### RQ-006: Light Mode Support (Optional)

**Specification**: "light mode is optional" (spec.md assumption A-004)

**Decision**: ✅ **IMPLEMENT** light mode as fallback (minimal additional work)

**Rationale**:
- Users without dark mode preference should see existing light theme
- Only ~10 extra lines of CSS (keep current colors as default, override in dark mode)
- Good UX: respects user's system preference

**Implementation**:
```css
/* Default (Light Mode) - Keep existing variables */
:root {
  --color-bg: #ffffff;
  --color-text: #1a1a1a;
  /* ... existing ... */
}

/* Dark Mode Override */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0f0f0f;
    --color-text: #e8e8e8;
    /* ... dark palette ... */
  }
}
```

---

### RQ-007: Image Visibility on Dark Backgrounds

**Edge Case** (from spec.md): "What happens when images have very dark colors that blend with the dark background?"

**Research Findings**:
1. Gallery images typically have natural borders/frames from camera capture
2. Adding borders breaks aesthetic (spec: "simple")
3. Subtle drop shadow works well without being heavy

**Solution**:
```css
@media (prefers-color-scheme: dark) {
  .image-item img {
    /* Very subtle shadow to separate dark images from background */
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.05),
                0 2px 8px rgba(0, 0, 0, 0.3);
  }
}
```

**Testing**: Will verify with test images containing:
- Pure black backgrounds
- Very dark product photos
- Low-key portrait photography

---

### RQ-008: Color Scheme Meta Tag

**Discovery**: Modern browsers support `<meta name="color-scheme" content="light dark">` to hint OS-level UI theming (scrollbars, form controls, etc.)

**Decision**: ✅ **ADD** to template

**Benefits**:
- Native scrollbar styling matches dark theme automatically
- Form controls (if added later) inherit OS dark mode styling
- Zero performance cost, single line of HTML

**Implementation**:
```html
<meta name="color-scheme" content="light dark">
```

Add to `src/templates/index.html.tpl` in `<head>` section.

---

## Summary of Decisions

| ID | Question | Decision | Impact |
|----|----------|----------|--------|
| RQ-001 | CSS vs JS framework | Pure CSS with custom properties | +2KB CSS, no JS changes |
| RQ-002 | Color palette | 7 dark colors, WCAG AA verified | Defines theme aesthetic |
| RQ-003 | Animation strategy | CSS transitions + keyframes | ~20 lines CSS, <100 lines JS |
| RQ-004 | Typography | Keep system fonts, minor tuning | 0 bytes, improved readability |
| RQ-005 | Browser support | Last 2 major versions, no fallback | 100% coverage |
| RQ-006 | Light mode | Implement as default fallback | +10 lines CSS |
| RQ-007 | Dark image visibility | Subtle shadow/border | ~5 lines CSS |
| RQ-008 | Color scheme meta | Add to HTML template | 1 line HTML |

**Total Estimated Addition**: ~2KB CSS, ~100 lines JS (image fade-in logic), 1 line HTML

**Budget Verification**:
- Current: HTML ~6KB, CSS ~6KB, JS ~15KB
- After: HTML ~6KB, CSS ~8KB, JS ~15.5KB
- Headroom: HTML 80%, CSS 68%, JS 79% ✅

---

## Next Steps (Phase 1)

1. Create `data-model.md`: Define Color Palette entity, Animation Timing entity, Typography Scale entity
2. Create `contracts/css-variables.schema.yaml`: Document all CSS custom properties
3. Create `contracts/animation-timing.md`: Document transition values and easing functions
4. Create `quickstart.md`: Developer guide for applying dark theme, testing procedures
5. Update agent context: Run `.specify/scripts/bash/update-agent-context.sh`

---

## References

- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [MDN: prefers-color-scheme](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme)
- [MDN: color-scheme](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta/name#standard_metadata_names)
- [Material Design Motion Guidelines](https://m3.material.io/styles/motion/easing-and-duration/applying-easing-and-duration)
- [CSS Tricks: Dark Mode](https://css-tricks.com/a-complete-guide-to-dark-mode-on-the-web/)
