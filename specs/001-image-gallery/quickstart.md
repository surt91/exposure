# Quickstart: Modern Image Gallery

## Prerequisites
- Python 3.11 installed
- Images placed in `content/` directory
- Initial `config/gallery.yaml` (can be minimal: categories + empty images list)

## First Run
1. Ensure `config/settings.yaml` contains paths:
   ```yaml
   content_dir: content
   gallery_yaml_path: config/gallery.yaml
   default_category: Uncategorized
   enable_thumbnails: false
   ```
2. Run generator (implementation script TBD):
   ```bash
   python -m src.generator.build_html
   ```
3. Inspect `dist/` for generated `index.html` and assets.
4. Open `dist/index.html` in a browser.

## Stub Generation
- New images without YAML entries will produce stub entries appended under `images:` in `gallery.yaml`.
- Fill in `title` and `description` manually; rerun generator.

## Development Loop
1. Add/modify images
2. Edit `gallery.yaml`
3. Run generator
4. Verify performance budgets (CI will enforce on PR)

## Testing
- Run unit tests: `pytest -q`
- Accessibility (CI): axe scan of `dist/*.html`
- Performance (CI): Lighthouse CI

## Deployment
- Upload contents of `dist/` to static host (GitHub Pages / Netlify).
- Ensure CSP headers set according to constitution.

## Troubleshooting
| Issue | Action |
|-------|--------|
| Missing images in gallery | Check filenames match YAML entries |
| Stub not created | Ensure write permissions for `gallery.yaml` |
| Performance budget fail | Audit asset sizes in `dist/` |
| Accessibility violation | Fix semantic markup / aria attributes |

