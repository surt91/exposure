# ADR 0003: Dark Mode Styling Approach

**Date**: 2025-11-01
**Status**: Accepted
**Deciders**: Development Team
**Related**: [ADR 0001 - Templating](./0001-templating.md), [ADR 0002 - Type Checking](./0002-type-checking.md)

## Context

The fotoview gallery needed a modern dark theme to reduce eye strain and enhance the viewing experience for images. The primary decision was whether to implement dark mode using:

1. Pure CSS with CSS custom properties and `@media (prefers-color-scheme: dark)`
2. JavaScript framework/library (Tailwind CSS, CSS-in-JS)
3. Manual toggle with JavaScript state management

Key constraints:
- Must maintain static-first architecture (no runtime dependencies)
- Must respect performance budgets: CSS ≤25KB, JS ≤75KB
- Must meet WCAG 2.1 AA accessibility standards
- Must preserve existing 60fps performance targets

## Decision

**We will implement dark mode using pure CSS with CSS custom properties and browser-native dark mode detection.**

### Implementation Details

- **CSS Custom Properties**: Define color palette, timing, and typography variables in `:root` selector
- **Light Mode**: Default values in `:root` (current colors)
- **Dark Mode**: Override variables in `@media (prefers-color-scheme: dark)` block
- **System Integration**: Add `<meta name="color-scheme" content="light dark">` for native OS theming
- **Reduced Motion**: Respect `prefers-reduced-motion: reduce` by setting transitions to 0ms
- **No JavaScript**: Dark mode detection is entirely CSS-based

### Color Palette Chosen

**Light Mode:**
- Background: #ffffff (white)
- Text: #1a1a1a (near-black)
- Accent: #0066cc (blue)

**Dark Mode:**
- Background: #0f0f0f (near-black)
- Text: #e8e8e8 (off-white)
- Accent: #4a9eff (lighter blue)

All colors verified to meet WCAG 2.1 AA contrast ratios (≥4.5:1 for text).

## Rationale

### Why Pure CSS?

**Performance and Budget Compliance:**
- Tailwind CSS: Even with aggressive PurgeCSS, adds ~10-15KB gzipped
  - Risk: Would consume 40-60% of 25KB CSS budget for framework alone
  - Current approach: Added only ~8KB for complete dark mode implementation
- CSS-in-JS libraries: Require 10-15KB JS runtime + generated CSS
  - Violates static-first principle (requires JS runtime)
  - Would consume significant portion of 75KB JS budget

**Architecture Alignment:**
- Static-first: No build-time or runtime JS dependencies for styling
- Progressive enhancement: Works without JavaScript
- Zero external dependencies: No CDN reliance or supply chain risks

**Browser Support:**
- `@media (prefers-color-scheme: dark)` supported since 2019 in all major browsers
- CSS custom properties supported since 2016 (98%+ coverage)
- Graceful degradation: Old browsers get light mode only

### Why Not Manual Toggle?

- Adds JavaScript complexity (state management, persistence)
- Requires UI for toggle button (design overhead)
- System preference is standard UX pattern (users expect it)
- `localStorage` persistence adds privacy/storage concerns
- Can be added later if user demand exists (backwards compatible)

## Consequences

### Positive

✅ **Budget Compliance**: CSS grew from 6.7KB → 16KB (36% under 25KB limit)
✅ **No JS Changes**: Zero impact on JS budget
✅ **Accessibility**: All contrast ratios pass WCAG 2.1 AA (verified by axe-core)
✅ **Performance**: No runtime overhead, instant switching
✅ **Maintainability**: Variables centralized, easy to adjust colors
✅ **User Experience**: Respects system preference (OS integration)
✅ **Future-Proof**: Easy to add manual toggle later if needed

### Negative

⚠️ **No Manual Toggle**: Users cannot override system preference (not requested, can add later)
⚠️ **Old Browser Support**: IE11 and very old browsers lack `prefers-color-scheme` (acceptable tradeoff - get light mode)

### Neutral

- CSS variables require fallback values for older browsers (already provided)
- Dark mode only tested in modern browsers (2019+)
- Manual testing required for each color change (automated contrast checks help)

## Validation

- ✅ All accessibility tests pass (12/12)
- ✅ All asset budget tests pass (4/4)
- ✅ Full test suite passes (78 passed, 1 skipped)
- ✅ WCAG 2.1 AA contrast ratios verified for all text
- ✅ Reduced motion preference respected
- ✅ Focus indicators visible in both modes
- ✅ CSS budget: 16KB / 25KB (64% used, 36% headroom)

## Implementation Stats

**Files Modified:**
- `src/static/css/gallery.css`: +90 lines (color palette, dark mode overrides)
- `src/static/css/fullscreen.css`: +12 lines (variable usage, transitions)
- `src/templates/index.html.tpl`: +1 line (color-scheme meta tag)

**Total Addition:**
- CSS: ~8.3KB (compressed in production)
- HTML: ~30 bytes
- JS: 0 bytes

**Development Time:** ~4 hours (specification, implementation, testing)

## Alternatives Considered

### 1. Tailwind CSS with Dark Mode
**Pros:** Popular framework, good dark mode utilities, rapid development
**Cons:** 10-15KB even with PurgeCSS, build complexity, vendor lock-in
**Verdict:** Rejected - budget risk and unnecessary abstraction

### 2. CSS-in-JS (styled-components, emotion)
**Pros:** Dynamic theming, component-scoped styles
**Cons:** Requires JS runtime, violates static-first principle, JS budget breach
**Verdict:** Rejected - constitutional violation

### 3. Separate Dark Mode CSS File
**Pros:** Clear separation of concerns
**Cons:** Extra HTTP request, duplicate CSS rules, cache complexity
**Verdict:** Rejected - CSS variables more maintainable

### 4. JavaScript Toggle with localStorage
**Pros:** User control, remembers preference
**Cons:** Adds JS complexity, requires UI design, localStorage privacy concerns
**Verdict:** Deferred - can add later if user demand emerges

## Related Decisions

- **ADR 0001 (Templating)**: Static generation approach enables CSS-only solution
- **ADR 0002 (Type Checking)**: No impact (CSS-only change)
- **Future**: If manual toggle added, will need ADR for state management approach

## References

- [CSS Custom Properties Spec](https://www.w3.org/TR/css-variables-1/)
- [MDN: prefers-color-scheme](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme)
- [WCAG 2.1 Contrast Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- Feature Specification: `specs/003-dark-mode-ui-polish/spec.md`
- Implementation Plan: `specs/003-dark-mode-ui-polish/plan.md`
