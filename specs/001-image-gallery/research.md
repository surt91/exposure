# Research: Modern Image Gallery

## Overview

Collect decisions for unknowns / validations to support design and contracts.

## Decisions

### Templating Approach
- **Decision**: Use minimal Python string formatting (avoid heavy templating engines) unless complexity grows; allow future shift to Jinja2.
- **Rationale**: Keeps dependency footprint small aligning with Static-First Simplicity.
- **Alternatives Considered**: Jinja2 (more features), Mako (powerful), Pure JS build (would introduce Node stack).

### YAML Stub Strategy
- **Decision**: Append new image stubs at end with category "Uncategorized".
- **Rationale**: Preserves existing ordering and highlights new content for user curation.
- **Alternatives**: Auto-categorize by folder name (adds complexity), Insert alphabetically (could disrupt intentional ordering).

### Asset Hashing Method
- **Decision**: SHA256 file hash appended before extension (e.g., app.css → app.ab12cd.css) recorded in generated HTML.
- **Rationale**: Ensures cache busting & reproducibility trace.
- **Alternatives**: Build timestamp (not reproducible), Query string versioning (less reliable for CDN caching).

### Thumbnail Handling
- **Decision**: Defer actual thumbnail generation; rely on CSS scaling. Optional Pillow usage gated behind config flag.
- **Rationale**: Avoids premature optimization; simpler initial pipeline.
- **Alternatives**: Always generate thumbnails (adds time/deps), Pre-generate externally (requires additional tooling).

### Accessibility Testing
- **Decision**: Integrate axe CLI via GitHub Actions container step scanning generated dist/ HTML.
- **Rationale**: Automated enforcement of Principle II.
- **Alternatives**: Manual audits (less reliable), Pa11y (alternative tool, could add redundancy).

### Performance Measurement
- **Decision**: Use Lighthouse CI against deployed preview or local static server in CI.
- **Rationale**: Validates budgets with standard tooling.
- **Alternatives**: WebPageTest (slower), Custom script (reinvent metrics).

### Virtualization / Lazy Loading
- **Decision**: Use native lazy loading (loading="lazy") and defer virtualization until >500 images performance risk validated.
- **Rationale**: Minimal JS footprint; meets budgets.
- **Alternatives**: IntersectionObserver grid virtualization (premature), Infinite scroll (changes UX scope).

### Configuration File Split
- **Decision**: Keep gallery.yaml for content metadata; settings.yaml for generator operational config.
- **Rationale**: Clean separation between content and operational parameters.
- **Alternatives**: Single YAML file (risk of mixing concerns), JSON config (less user-friendly for manual edits).

### CSP Baseline
- **Decision**: `default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'; font-src 'self'; object-src 'none';`.
- **Rationale**: Restrictive default satisfying Security & Privacy Baseline.
- **Alternatives**: Allow CDNs (increase external dependency risks), Inline scripts without nonce (weaker security).

## Resolved Unknowns
No remaining NEEDS CLARIFICATION markers.

## Follow-ups
- Evaluate need for thumbnails after initial performance tests with real dataset.
- Consider introducing Jinja2 if template logic grows beyond simple loops/conditionals.
