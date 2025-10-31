# Data Model: Modern Image Gallery

## Entities

### Image
| Field | Type | Rules | Notes |
|-------|------|-------|-------|
| filename | string | MUST be unique within content folder | Derived from file system |
| file_path | string | MUST resolve to existing file (or placeholder state) | Absolute or relative path |
| category | string | MUST reference existing Category or "Uncategorized" | Fallback applied on stub generation |
| width | int | OPTIONAL | Collected if Pillow enabled |
| height | int | OPTIONAL | Collected if Pillow enabled |
| title | string | OPTIONAL | From YAML if provided |
| description | string | OPTIONAL | From YAML if provided |

### Category
| Field | Type | Rules | Notes |
|-------|------|-------|-------|
| name | string | MUST be unique | Order defined externally |
| order_index | int | MUST reflect sequence in YAML | Determines render order |
| images | list[Image] | Derived | Populated after scan |

### GalleryConfig
| Field | Type | Rules | Notes |
|-------|------|-------|-------|
| content_dir | string | MUST exist & be readable | Source of image files |
| gallery_yaml_path | string | MUST be writable for stub append | Location of metadata |
| default_category | string | MUST exist as implicit Category | Default = "Uncategorized" |
| enable_thumbnails | bool | OPTIONAL | Controls Pillow usage |

### YamlEntry
| Field | Type | Rules | Notes |
|-------|------|-------|-------|
| filename | string | MUST match image filename | Primary key |
| category | string | MUST map to Category | If missing → stub with default |
| title | string | OPTIONAL | User-added |
| description | string | OPTIONAL | User-added |

## Relationships
- Category 1..* Image (Image references Category by name)
- GalleryConfig independent; used across pipeline
- YamlEntry maps 1:1 to Image once created

## State Transitions
1. Discovery: Image files scanned → temporary Image objects (category unknown)
2. YAML Merge: For each Image → if entry exists enrich metadata else create stub entry
3. Ordering: Categories sequenced based on YAML list → assign order_index
4. Output: Final ordered categories used to generate HTML sections

## Validation Workflow
- On scan: enforce unique filenames; duplicates discarded with warning.
- On YAML parse: validate categories list uniqueness.
- During stub append: guarantee no existing entry overwritten.

## Derived Data
- Category.images populated after assignment pass.
- Asset hash calculated externally and not stored in YAML (build artifact only).
