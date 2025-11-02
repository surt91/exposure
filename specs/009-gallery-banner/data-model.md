# Data Model: Gallery Banner and Title

**Feature**: 009-gallery-banner
**Date**: 2025-11-02
**Status**: Complete

## Overview

This document defines the data entities and their relationships for the gallery banner and title feature. The feature extends existing Pydantic models with optional banner/title configuration.

---

## Entity: GalleryConfig (Extended)

**Location**: `src/generator/model.py`
**Type**: Pydantic BaseSettings model
**Purpose**: Central configuration for gallery generation, extended to include banner/title settings

### Fields

| Field Name | Type | Required | Default | Validation Rules | Description |
|-----------|------|----------|---------|------------------|-------------|
| `banner_image` | `Optional[Path]` | No | `None` | Must exist if provided; can be absolute or relative to `content_dir` | Path to banner image file |
| `gallery_title` | `Optional[str]` | No | `None` | Min length: 1 if provided; Max length: 200 | Gallery title displayed in banner or header |
| `gallery_subtitle` | `Optional[str]` | No | `None` | Max length: 300; whitespace-only treated as None | Gallery subtitle displayed below title (requires title) |

### Existing Fields (Context)

These existing fields are relevant to banner/title feature:

| Field Name | Type | Description |
|-----------|------|-------------|
| `content_dir` | `Path` | Used to resolve relative banner image paths |
| `output_dir` | `Path` | Where banner image is copied to |
| `locale` | `str` | Used for default title i18n if gallery_title not set |

### Validation Logic

```python
@field_validator("banner_image", mode="before")
@classmethod
def validate_banner_image(cls, v, info):
    """
    Validate banner image path exists if provided.

    Rules:
    - None is valid (feature disabled)
    - Absolute path must exist on filesystem
    - Relative path resolved against content_dir must exist
    - File must be readable image format (validated by Pillow later)
    """
    if v is None:
        return None

    path = Path(v) if not isinstance(v, Path) else v

    # Check absolute path
    if path.is_absolute():
        if not path.exists():
            raise ValueError(f"Banner image not found: {path}")
        if not path.is_file():
            raise ValueError(f"Banner image path is not a file: {path}")
        return path

    # Try relative to content_dir
    content_dir = info.data.get("content_dir")
    if content_dir:
        full_path = Path(content_dir) / path
        if full_path.exists() and full_path.is_file():
            return full_path

    raise ValueError(
        f"Banner image not found: {v}. "
        f"Provide absolute path or path relative to content_dir."
    )

@field_validator("gallery_title", mode="before")
@classmethod
def validate_gallery_title(cls, v):
    """
    Validate gallery title if provided.

    Rules:
    - None is valid (use default i18n title)
    - If string provided, must not be empty or whitespace-only
    - Length limit for reasonable display
    """
    if v is None:
        return None

    if isinstance(v, str):
        v = v.strip()
        if not v:
            raise ValueError("Gallery title cannot be empty or whitespace-only")
        if len(v) > 200:
            raise ValueError("Gallery title too long (max 200 characters)")

    return v

@field_validator("gallery_subtitle", mode="before")
@classmethod
def validate_gallery_subtitle(cls, v):
    """
    Validate gallery subtitle if provided.

    Rules:
    - None is valid (no subtitle)
    - If string provided, empty/whitespace-only treated as None
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

### Configuration Sources

Per pydantic-settings, configuration can come from (in priority order):

1. **Environment variables**: `EXPOSURE_BANNER_IMAGE`, `EXPOSURE_GALLERY_TITLE`
2. **.env file**: Same variable names
3. **settings.yaml**:
   ```yaml
   banner_image: "content/banner.jpg"
   gallery_title: "My Amazing Gallery"
   ```
4. **Default values**: Both default to `None` (feature disabled)

---

## Entity: BannerData (Template Context)

**Location**: Template rendering context in `build_html.py`
**Type**: Dictionary passed to Jinja2 template
**Purpose**: Provides banner/title data to HTML templates

### Structure

```python
{
    "banner_image": Optional[str],    # Relative URL: "images/banner/filename.jpg"
    "gallery_title": Optional[str],   # Title text or None
    "gallery_subtitle": Optional[str], # Subtitle text or None (requires title)
    "default_title": str,              # Fallback title from i18n
}
```

### Fields

| Field Name | Type | Source | Description |
|-----------|------|--------|-------------|
| `banner_image` | `Optional[str]` | Computed from `config.banner_image` | Relative URL to banner in output directory; `None` if not configured |
| `gallery_title` | `Optional[str]` | `config.gallery_title` | Title text; `None` if not configured |
| `gallery_subtitle` | `Optional[str]` | `config.gallery_subtitle` | Subtitle text; `None` if not configured; only displayed when title present |
| `default_title` | `str` | i18n translation | Localized default title (e.g., "Gallery" or "Galerie") |

### Derivation Logic

```python
def prepare_banner_context(config: GalleryConfig, output_dir: Path) -> dict:
    """
    Prepare banner/title data for template rendering.

    Returns:
        Dictionary with banner_image URL, gallery_title, and default_title
    """
    banner_image_url = None

    if config.banner_image:
        # Copy banner to output directory
        banner_output_dir = output_dir / "images" / "banner"
        banner_output_dir.mkdir(parents=True, exist_ok=True)

        dest_path = banner_output_dir / config.banner_image.name
        shutil.copy2(config.banner_image, dest_path)

        # Generate relative URL for template
        banner_image_url = f"images/banner/{config.banner_image.name}"

    # Get default title from i18n
    default_title = _("Gallery")  # Babel translation

    return {
        "banner_image": banner_image_url,
        "gallery_title": config.gallery_title,
        "gallery_subtitle": config.gallery_subtitle,
        "default_title": default_title,
    }
```

---

## State Transitions

The banner/title feature has simple state flow:

```
Configuration Load
    ↓
[banner_image exists?] ──No──→ banner_image = None
    ↓ Yes
Validate path exists
    ↓
[gallery_title provided?] ──No──→ gallery_title = None
    ↓ Yes
Validate title text
    ↓
Build Process
    ↓
[banner_image != None?] ──No──→ Skip banner asset copy
    ↓ Yes
Copy banner to output/images/banner/
    ↓
Generate banner_image_url
    ↓
Template Rendering
    ↓
[banner_image_url != None?] ──No──→ Render simple header
    ↓ Yes
Render banner with optional title overlay
```

### Error States

| Error Condition | When | Action |
|----------------|------|--------|
| Banner path invalid | Config load/validation | Raise `ValueError`, stop build |
| Banner file unreadable | Asset copy | Raise `IOError`, stop build |
| Title too long | Config validation | Raise `ValueError`, stop build |
| Title empty/whitespace | Config validation | Raise `ValueError`, stop build |

---

## Relationships

```
GalleryConfig
    ├── banner_image: Optional[Path]  ──relates to──→ File on filesystem
    ├── gallery_title: Optional[str]  ──used in──→ Template rendering
    └── content_dir: Path  ──used to resolve──→ banner_image (if relative)

BannerData (template context)
    ├── banner_image: Optional[str]  ──derived from──→ GalleryConfig.banner_image
    ├── gallery_title: Optional[str]  ──derived from──→ GalleryConfig.gallery_title
    └── default_title: str  ──derived from──→ i18n translations (locale setting)

Template (index.html.j2)
    ├── Receives BannerData in context
    ├── Conditionally renders banner section if banner_image present
    └── Uses gallery_title or default_title for heading
```

---

## Data Flow Diagram

```
settings.yaml
    │
    ├─→ banner_image: "banner.jpg"
    └─→ gallery_title: "My Gallery"
         │
         ↓
    GalleryConfig (Pydantic model)
         │ (validates paths, title)
         ↓
    build_html.py
         │ (copies banner asset)
         │ (generates URLs)
         ↓
    BannerData (dict)
         │
         ├─→ banner_image: "images/banner/banner.jpg"
         └─→ gallery_title: "My Gallery"
              │
              ↓
    index.html.j2 (Jinja2 template)
              │
              ↓
    dist/index.html (rendered output)
         │
         └─→ <img src="images/banner/banner.jpg">
         └─→ <h1>My Gallery</h1>
```

---

## Schema Examples

### Minimal Configuration (Feature Disabled)
```yaml
# settings.yaml - no banner/title
content_dir: "content/"
gallery_yaml_path: "config/gallery.yaml"
default_category: "Uncategorized"
# banner_image and gallery_title omitted (defaults to None)
```

### Banner Only
```yaml
# settings.yaml - banner without title
content_dir: "content/"
gallery_yaml_path: "config/gallery.yaml"
default_category: "Uncategorized"
banner_image: "banner.jpg"  # Relative to content_dir
```

### Full Configuration
```yaml
# settings.yaml - banner with title and subtitle
content_dir: "content/"
gallery_yaml_path: "config/gallery.yaml"
default_category: "Uncategorized"
banner_image: "/absolute/path/to/banner.jpg"  # Absolute path
gallery_title: "My 3D Printing Gallery"
gallery_subtitle: "Showcasing my latest creations and builds"
```

### Environment Variable Override
```bash
export EXPOSURE_BANNER_IMAGE="content/banner.jpg"
export EXPOSURE_GALLERY_TITLE="Production Gallery"
# These override settings.yaml values
```

---

## Validation Rules Summary

| Entity | Field | Validation |
|--------|-------|------------|
| GalleryConfig | banner_image | Optional; if provided must be existing file; resolved relative to content_dir if not absolute |
| GalleryConfig | gallery_title | Optional; if provided must be 1-200 chars, not whitespace-only |
| GalleryConfig | gallery_subtitle | Optional; if provided max 300 chars; whitespace-only treated as None |
| BannerData | banner_image | Optional string (URL); valid if None or matches pattern `images/banner/*.{jpg,png,gif,webp}` |
| BannerData | gallery_title | Optional string; valid if None or non-empty |
| BannerData | gallery_subtitle | Optional string; valid if None or non-empty; only displayed if gallery_title present |
| BannerData | default_title | Required string; never empty (from i18n) |

---

## Migration Path

### Existing Galleries
No migration needed. Existing `settings.yaml` files without banner/title fields continue to work:
- `banner_image = None` → no banner rendered
- `gallery_title = None` → uses `default_title` from i18n

### New Galleries
To enable banner/title, add to `settings.yaml`:
```yaml
banner_image: "path/to/banner.jpg"
gallery_title: "Gallery Name"
```

### Testing Strategy

1. **Unit Tests**: Test GalleryConfig validation with various banner_image/gallery_title inputs
2. **Integration Tests**: Test build process with banner enabled/disabled configurations
3. **Backward Compatibility Tests**: Ensure existing test galleries (without banner/title) still build successfully

---

## Performance Considerations

| Aspect | Impact | Mitigation |
|--------|--------|------------|
| Banner file size | Additional HTTP request | Document recommendation: optimize banner to <500KB |
| Build time | +1 file copy operation | Negligible (single file copy ~10ms) |
| HTML payload | +50-100 bytes | Well within 30KB budget |
| CSS payload | +2-3KB for banner styles | Within 25KB budget |
| Template rendering | +1 conditional block | Negligible (Jinja2 renders in microseconds) |

---

## Summary

The data model is intentionally minimal:
- **3 new optional fields** in existing GalleryConfig model (banner_image, gallery_title, gallery_subtitle)
- **4 derived fields** in template context dictionary (banner_image URL, gallery_title, gallery_subtitle, default_title)
- **Simple validation** via Pydantic field validators
- **Zero breaking changes** to existing configurations
- **Type-safe** with Pydantic type checking

All data flows through established patterns (pydantic-settings → build script → Jinja2 template), requiring no new architectural concepts.
