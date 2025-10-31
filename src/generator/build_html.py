"""Build HTML gallery from images and YAML metadata."""

import sys
from pathlib import Path

import yaml

from .model import Category, GalleryConfig, Image
from .scan import detect_duplicates, discover_images, filter_valid_images, get_image_dimensions
from .yaml_sync import append_stub_entries, get_entry_map, load_gallery_yaml


def load_config(settings_path: Path) -> GalleryConfig:
    """
    Load configuration from settings.yaml.

    Args:
        settings_path: Path to settings.yaml file

    Returns:
        GalleryConfig object

    Raises:
        FileNotFoundError: If settings file doesn't exist
        ValueError: If configuration is invalid
    """
    if not settings_path.exists():
        raise FileNotFoundError(f"Settings file not found: {settings_path}")

    with open(settings_path, "r") as f:
        settings = yaml.safe_load(f)

    return GalleryConfig(
        content_dir=Path(settings["content_dir"]),
        gallery_yaml_path=Path(settings["gallery_yaml_path"]),
        default_category=settings["default_category"],
        enable_thumbnails=settings.get("enable_thumbnails", False),
        output_dir=Path(settings.get("output_dir", "dist")),
    )


def scan_and_sync(config: GalleryConfig) -> tuple[list[str], list[Image]]:
    """
    Scan images and synchronize with YAML metadata.

    This function:
    1. Discovers images in content directory
    2. Validates images and checks for duplicates
    3. Loads YAML metadata
    4. Creates stub entries for new images
    5. Merges image data with metadata

    Args:
        config: Gallery configuration

    Returns:
        Tuple of (category names in order, list of Image objects)

    Raises:
        ValueError: If duplicate filenames found or other validation errors
    """
    # Discover images
    print(f"Scanning images in {config.content_dir}...")
    image_paths = discover_images(config.content_dir)
    print(f"Found {len(image_paths)} image files")

    # Filter valid images
    valid_paths = filter_valid_images(image_paths)
    if len(valid_paths) < len(image_paths):
        print(f"Warning: {len(image_paths) - len(valid_paths)} invalid images skipped")

    # Check for duplicates
    duplicates = detect_duplicates(valid_paths)
    if duplicates:
        print("Error: Duplicate filenames detected:")
        for filename, paths in duplicates.items():
            print(f"  {filename}: {', '.join(str(p) for p in paths)}")
        raise ValueError("Cannot proceed with duplicate filenames")

    # Load YAML
    categories, yaml_entries = load_gallery_yaml(config.gallery_yaml_path)

    # Append stubs for new images
    filenames = [p.name for p in valid_paths]
    stubs_added = append_stub_entries(
        config.gallery_yaml_path, filenames, config.default_category
    )
    if stubs_added > 0:
        print(f"Added {stubs_added} stub entries to YAML")
        # Reload after stub addition
        categories, yaml_entries = load_gallery_yaml(config.gallery_yaml_path)

    # Create Image objects by merging paths with YAML metadata
    entry_map = get_entry_map(yaml_entries)
    images = []

    for path in valid_paths:
        filename = path.name
        entry = entry_map.get(filename)

        if entry is None:
            # This shouldn't happen after stub generation, but handle gracefully
            print(f"Warning: No YAML entry for {filename}, using defaults")
            entry_category = config.default_category
            entry_title = ""
            entry_description = ""
        else:
            entry_category = entry.category
            entry_title = entry.title
            entry_description = entry.description

        # Get dimensions if enabled
        width, height = None, None
        if config.enable_thumbnails:
            dims = get_image_dimensions(path)
            if dims:
                width, height = dims

        image = Image(
            filename=filename,
            file_path=path,
            category=entry_category,
            width=width,
            height=height,
            title=entry_title,
            description=entry_description,
        )
        images.append(image)

    return categories, images


def organize_by_category(
    category_names: list[str], images: list[Image]
) -> list[Category]:
    """
    Organize images into Category objects.

    Args:
        category_names: List of category names in display order
        images: List of Image objects

    Returns:
        List of Category objects with images assigned
    """
    # Create category objects
    categories = [
        Category(name=name, order_index=idx) for idx, name in enumerate(category_names)
    ]
    category_map = {cat.name: cat for cat in categories}

    # Assign images to categories
    for image in images:
        cat = category_map.get(image.category)
        if cat is None:
            # This shouldn't happen if YAML is valid, but handle gracefully
            print(f"Warning: Unknown category '{image.category}' for {image.filename}")
            continue
        cat.add_image(image)

    # Filter out empty categories
    categories = [cat for cat in categories if len(cat.images) > 0]

    return categories


def build_gallery(config_path: Path = Path("config/settings.yaml")) -> None:
    """
    Main entry point for building the gallery.

    Args:
        config_path: Path to settings.yaml configuration file
    """
    print("=" * 60)
    print("Fotoview Gallery Generator")
    print("=" * 60)

    # Load configuration
    config = load_config(config_path)

    # Scan and sync
    category_names, images = scan_and_sync(config)
    print(f"Loaded {len(images)} images across {len(category_names)} categories")

    # Organize by category
    categories = organize_by_category(category_names, images)

    # TODO: Generate HTML (Phase 3)
    # TODO: Generate CSS (Phase 3)
    # TODO: Generate JS (Phase 3)
    # TODO: Copy images to dist with hashing (Phase 3)

    print("\nCategories:")
    for cat in categories:
        print(f"  {cat.name}: {len(cat.images)} images")

    print("\n✓ Scan and sync complete")
    print("  (HTML generation coming in Phase 3)")


def main() -> None:
    """CLI entry point."""
    config_path = Path("config/settings.yaml")
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])

    try:
        build_gallery(config_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
