# Quickstart: Dark Mode and UI Polish

**Feature**: 003-dark-mode-ui-polish | **Date**: 2025-11-01 | **Phase**: 1 (Design)

## Overview

This guide explains how to work with the dark mode implementation in fotoview. The dark theme uses CSS custom properties and browser-native dark mode detection (`@media (prefers-color-scheme: dark)`).

---

## For End Users

### Enabling Dark Mode

Dark mode **automatically activates** based on your system preferences:

- **macOS**: System Settings → Appearance → Dark
- **Windows 11**: Settings → Personalization → Colors → Choose your mode → Dark
- **iOS/iPadOS**: Settings → Display & Brightness → Dark
- **Android**: Settings → Display → Dark theme
- **Linux (GNOME)**: Settings → Appearance → Dark

No manual toggle needed - the gallery respects your OS preference.

### Browser Support

Dark mode works in:
- Chrome/Edge 76+ (2019+)
- Firefox 67+ (2019+)
- Safari 12.1+ (2019+)

Older browsers fall back to light mode automatically.

---

## For Developers

### Quick Setup

1. **Clone and install dependencies**:
   ```bash
   git clone <repo-url>
   cd fotoview
   uv sync --dev
   ```

2. **Run local preview**:
   ```bash
   cd src
   uv run python -m generator.build_html ../config/gallery.yaml ../output
   cd ../output
   python -m http.server 8000
   ```
   Open http://localhost:8000 in your browser

3. **Toggle system dark mode** to test both themes

---

### CSS Architecture

#### File Structure
```
src/static/css/
├── gallery.css       # Main styles + dark mode variables
└── fullscreen.css    # Modal styles + dark mode overrides
```

#### Variable Definitions

**Light Mode** (default in `:root`):
```css
:root {
  --color-bg: #ffffff;
  --color-text: #1a1a1a;
  --color-accent: #0066cc;
  /* ...7 color variables total */
  
  --transition-fast: 150ms;
  --easing-smooth: cubic-bezier(0.4, 0.0, 0.2, 1);
  /* ...4 timing variables total */
  
  --font-size-h1: 2rem;
  --line-height-base: 1.65;
  /* ...7 typography variables total */
}
```

**Dark Mode Override**:
```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0f0f0f;
    --color-text: #e8e8e8;
    --color-accent: #4a9eff;
    /* ...override only color variables */
  }
  
  /* Dark-specific styles */
  .image-item img {
    box-shadow: 0 0 0 1px rgba(255,255,255,0.05), 0 2px 8px rgba(0,0,0,0.3);
  }
}
```

#### Usage Pattern
```css
/* Use variables throughout CSS */
body {
  background-color: var(--color-bg);
  color: var(--color-text);
  transition: background-color var(--transition-normal) var(--easing-smooth);
}

.category-section h2 {
  color: var(--color-text);
  border-bottom: 2px solid var(--color-border);
}
```

---

### Testing Dark Mode

#### Manual Testing

1. **Visual Inspection**:
   ```bash
   # Toggle system dark mode and refresh browser
   # Verify all sections use dark theme
   ```

2. **Contrast Check**:
   - Open browser DevTools → Elements → Computed
   - Select text element
   - Check `color` and `background-color` values
   - Use [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/) to verify ≥4.5:1 ratio

3. **Animation Performance**:
   ```bash
   # Chrome DevTools → Performance → Record
   # Hover over images, open fullscreen modal
   # Check frame rate ≥60fps
   ```

4. **Reduced Motion**:
   - **macOS**: System Settings → Accessibility → Display → Reduce motion
   - **Windows**: Settings → Accessibility → Visual effects → Animation effects → Off
   - Verify transitions are disabled (instant state changes)

#### Automated Testing

```bash
# Run full test suite
uv run pytest

# Test accessibility (includes contrast checks)
uv run pytest tests/accessibility/test_axe_a11y.py -v

# Test asset budgets (verify CSS ≤25KB)
uv run pytest tests/integration/test_asset_budgets.py -v
```

**Expected Results**:
- axe-core: Zero critical violations
- CSS size: ≤25KB (currently ~8KB after dark mode)
- All tests pass

---

### Development Workflow

#### Adding New Colors

1. **Define in light mode** (`:root`):
   ```css
   :root {
     --color-new-element: #ff6600;
   }
   ```

2. **Override in dark mode**:
   ```css
   @media (prefers-color-scheme: dark) {
     :root {
       --color-new-element: #ffaa66;
     }
   }
   ```

3. **Verify contrast**:
   - Text on background: ≥4.5:1
   - UI components (borders, icons): ≥3:1

4. **Update contract**:
   - Document in `specs/003-dark-mode-ui-polish/contracts/css-variables.md`

#### Modifying Existing Colors

1. **Find variable** in `gallery.css` or `fullscreen.css`:
   ```css
   :root {
     --color-accent: #0066cc;  /* Original */
   }
   ```

2. **Adjust values**:
   ```css
   :root {
     --color-accent: #0073e6;  /* Updated */
   }
   
   @media (prefers-color-scheme: dark) {
     :root {
       --color-accent: #5eb0ff;  /* Updated dark mode */
     }
   }
   ```

3. **Test contrast** and run tests:
   ```bash
   uv run pytest tests/accessibility/test_axe_a11y.py
   ```

---

### Troubleshooting

#### Problem: Dark mode not activating

**Check**:
1. System dark mode enabled?
2. Browser supports `prefers-color-scheme` (check caniuse.com)
3. CSS file loaded correctly (DevTools → Network → gallery.css)

**Debug**:
```javascript
// Run in browser console
matchMedia('(prefers-color-scheme: dark)').matches  // Should return true
```

#### Problem: Poor contrast in dark mode

**Solution**:
1. Open DevTools → Elements → Select text element
2. Check computed color values
3. Use [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
4. Adjust `--color-*` variables in `@media (prefers-color-scheme: dark)` block
5. Re-run `uv run pytest tests/accessibility/test_axe_a11y.py`

#### Problem: Animations too slow or jarring

**Solution**:
1. Adjust timing variables in `:root`:
   ```css
   :root {
     --transition-fast: 100ms;   /* Faster (was 150ms) */
     --transition-normal: 200ms; /* Faster (was 250ms) */
   }
   ```
2. Test in Chrome DevTools → Performance (60fps target)

#### Problem: Dark images blend with background

**Solution**:
Already handled via subtle shadow in dark mode:
```css
@media (prefers-color-scheme: dark) {
  .image-item img {
    box-shadow: 0 0 0 1px rgba(255,255,255,0.05), 0 2px 8px rgba(0,0,0,0.3);
  }
}
```

If still problematic, increase border opacity:
```css
box-shadow: 0 0 0 1px rgba(255,255,255,0.1), /* Increased from 0.05 */
            0 2px 8px rgba(0,0,0,0.3);
```

---

### Performance Checklist

- [ ] CSS file size ≤25KB (`uv run pytest tests/integration/test_asset_budgets.py`)
- [ ] Animations maintain 60fps (Chrome DevTools Performance Monitor)
- [ ] Lighthouse Performance score ≥90 (3G throttled)
- [ ] Lighthouse Accessibility score ≥90
- [ ] No layout shift when switching themes (test by toggling system dark mode)

---

### Code Style

#### DO:
```css
/* Use CSS variables for all theme-dependent values */
.element {
  color: var(--color-text);
  background: var(--color-bg);
}

/* Group related properties */
:root {
  /* Colors */
  --color-bg: #fff;
  --color-text: #1a1a1a;
  
  /* Timing */
  --transition-fast: 150ms;
}

/* Add comments for non-obvious values */
--easing-smooth: cubic-bezier(0.4, 0.0, 0.2, 1);  /* Material Design standard */
```

#### DON'T:
```css
/* Don't hardcode colors */
.element {
  color: #e8e8e8;  /* ❌ Use var(--color-text) */
}

/* Don't duplicate values */
.element1 { transition: 250ms; }
.element2 { transition: 250ms; }  /* ❌ Use var(--transition-normal) */

/* Don't create unnecessary variables */
--very-specific-button-bg: #fff;  /* ❌ Use --color-bg */
```

---

### CI Integration

Dark mode checks run automatically on every commit:

```yaml
# .github/workflows/ci.yml
- name: Accessibility Tests
  run: uv run pytest tests/accessibility/test_axe_a11y.py
  # Verifies WCAG 2.1 AA contrast ratios

- name: Asset Budget Tests
  run: uv run pytest tests/integration/test_asset_budgets.py
  # Ensures CSS ≤25KB
```

**Merge Blockers**:
- axe-core critical violations > 0
- CSS file size > 25KB
- Any test failure

---

### Browser DevTools Tips

#### Chrome/Edge
1. **Force dark mode**: DevTools → Rendering → Emulate CSS media feature `prefers-color-scheme: dark`
2. **Check contrast**: DevTools → Elements → Accessibility → Contrast ratio
3. **Performance**: DevTools → Performance → Record → Check frame rate

#### Firefox
1. **Force dark mode**: DevTools → Inspector → `@media` sidebar → Toggle dark mode
2. **Check contrast**: DevTools → Accessibility → Check for Issues → Color contrast

#### Safari
1. **Force dark mode**: Develop → Experimental Features → Dark Mode CSS Override
2. **Check contrast**: Web Inspector → Elements → Computed → Color values

---

### Resources

- [CSS Variables Documentation](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [WCAG 2.1 Contrast Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Material Design Motion Guidelines](https://m3.material.io/styles/motion/overview)
- [Can I Use: prefers-color-scheme](https://caniuse.com/prefers-color-scheme)

---

## Next Steps

After implementing dark mode:

1. Run full test suite: `uv run pytest`
2. Visual review in Chrome, Firefox, Safari (both light and dark)
3. Test on mobile devices (iOS Safari, Android Chrome)
4. Document any color adjustments in CHANGELOG.md
5. Create ADR 0003 documenting styling approach decision

For implementation tasks, see `specs/003-dark-mode-ui-polish/tasks.md` (created in Phase 2 via `/speckit.tasks` command).
