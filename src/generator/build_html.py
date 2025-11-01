"""Build HTML gallery from images and YAML metadata."""

import logging
import sys
from pathlib import Path

# Import model module to set the yaml file path
from . import model
from .i18n import _
from .model import Category, GalleryConfig, Image
from .scan import detect_duplicates, discover_images, filter_valid_images, get_image_dimensions
from .yaml_sync import append_stub_entries, get_entry_map, load_gallery_yaml

logger = logging.getLogger("fotoview")


def load_config(settings_path: Path) -> GalleryConfig:
    """
    Load configuration from settings.yaml and environment variables.

    Uses pydantic-settings to automatically load and merge configuration from:
    1. Environment variables (FOTOVIEW_* prefix) - highest priority
    2. .env file (if present)
    3. YAML settings file - lowest priority

    Examples:
        # Override locale via environment variable:
        FOTOVIEW_LOCALE=de python -m src.generator.build_html

        # Override log level:
        FOTOVIEW_LOG_LEVEL=DEBUG python -m src.generator.build_html

    Args:
        settings_path: Path to settings.yaml file

    Returns:
        GalleryConfig object with automatic environment variable support.

    Raises:
        FileNotFoundError: If settings file doesn't exist
        pydantic.ValidationError: If configuration is invalid with detailed field errors
    """
    if not settings_path.exists():
        raise FileNotFoundError(f"Settings file not found: {settings_path}")

    # Set the module-level YAML file path
    model._yaml_settings_file = settings_path

    # Pydantic-settings will automatically load YAML and merge with env vars
    return GalleryConfig()  # type: ignore[call-arg]


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
    logger.info(_("Scanning images in %s..."), config.content_dir)
    image_paths = discover_images(config.content_dir)
    logger.info(_("Found %d image files"), len(image_paths))

    # Filter valid images
    valid_paths = filter_valid_images(image_paths)
    if len(valid_paths) < len(image_paths):
        logger.warning(_("%d invalid images skipped"), len(image_paths) - len(valid_paths))

    # Check for duplicates
    duplicates = detect_duplicates(valid_paths)
    if duplicates:
        logger.error(_("Duplicate filenames detected:"))
        for filename, paths in duplicates.items():
            logger.error("  %s: %s", filename, ", ".join(str(p) for p in paths))
        raise ValueError(_("Cannot proceed with duplicate filenames"))

    # Load YAML
    categories, yaml_entries = load_gallery_yaml(config.gallery_yaml_path)

    # Append stubs for new images
    filenames = [p.name for p in valid_paths]
    stubs_added = append_stub_entries(config.gallery_yaml_path, filenames, config.default_category)
    if stubs_added > 0:
        logger.info(_("Added %d stub entries to YAML"), stubs_added)
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
            logger.warning(_("No YAML entry for %s, using defaults"), filename)
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


def organize_by_category(category_names: list[str], images: list[Image]) -> list[Category]:
    """
    Organize images into Category objects.

    Args:
        category_names: List of category names in display order
        images: List of Image objects

    Returns:
        List of Category objects with images assigned
    """
    # Create category objects
    categories = [Category(name=name, order_index=idx) for idx, name in enumerate(category_names)]
    category_map = {cat.name: cat for cat in categories}

    # Assign images to categories
    for image in images:
        cat = category_map.get(image.category)
        if cat is None:
            # This shouldn't happen if YAML is valid, but handle gracefully
            logger.warning(_("Unknown category '%s' for %s"), image.category, image.filename)
            continue
        cat.add_image(image)

    # Filter out empty categories
    categories = [cat for cat in categories if len(cat.images) > 0]

    return categories


def generate_gallery_html(categories: list[Category], config: GalleryConfig) -> str:
    """
    Generate HTML for the gallery from categories using Jinja2 templates.

    Args:
        categories: List of Category objects with images
        config: Gallery configuration

    Returns:
        Generated HTML string
    """
    from jinja2 import Environment, FileSystemLoader

    from .assets import copy_with_hash, write_with_hash
    from .i18n import setup_i18n

    # Setup internationalization
    translations = setup_i18n(config.locale)

    # Setup Jinja2 environment with i18n extension
    templates_dir = Path(__file__).parent.parent / "templates"
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=True,
        extensions=["jinja2.ext.i18n"],
    )
    env.install_gettext_translations(translations)  # type: ignore[attr-defined]
    template = env.get_template("index.html.j2")

    # CSS sources
    gallery_css = Path(__file__).parent.parent / "static" / "css" / "gallery.css"
    fullscreen_css = Path(__file__).parent.parent / "static" / "css" / "fullscreen.css"

    # JS sources
    gallery_js = Path(__file__).parent.parent / "static" / "js" / "gallery.js"
    a11y_js = Path(__file__).parent.parent / "static" / "js" / "a11y.js"
    fullscreen_js = Path(__file__).parent.parent / "static" / "js" / "fullscreen.js"

    # Combine CSS files
    css_content = gallery_css.read_text(encoding="utf-8")
    css_content += "\n\n/* Fullscreen Modal */\n"
    css_content += fullscreen_css.read_text(encoding="utf-8")

    # Combine JS files
    js_content = gallery_js.read_text(encoding="utf-8")
    js_content += "\n\n// Accessibility helpers\n"
    js_content += a11y_js.read_text(encoding="utf-8")
    js_content += "\n\n// Fullscreen controller\n"
    js_content += fullscreen_js.read_text(encoding="utf-8")

    # Write combined files with hashing
    css_output = write_with_hash(css_content, "gallery.css", config.output_dir)
    js_output = write_with_hash(js_content, "gallery.js", config.output_dir)

    css_href = css_output.name
    js_href = js_output.name

    # Copy images and build image data for template
    # We need to create a modified category structure with hashed image paths
    template_categories = []
    for category in categories:
        template_images = []
        for image in category.images:
            # Copy image and get hashed filename
            img_dest = copy_with_hash(image.file_path, config.output_dir / "images")
            img_href = f"images/{img_dest.name}"

            # Create image dict with hashed path for template
            template_images.append(
                {
                    "filename": image.filename,
                    "src": img_href,
                    "category": image.category,
                    "title": image.title,
                    "description": image.description,
                    "alt_text": image.alt_text,
                    "width": image.width,
                    "height": image.height,
                }
            )

        template_categories.append({"name": category.name, "images": template_images})

    # Render template with data
    html = template.render(
        gallery_title="Image Gallery",
        categories=template_categories,
        css_href=css_href,
        js_href=js_href,
    )

    return html


def build_gallery(config_path: Path = Path("config/settings.yaml")) -> None:
    """
    Main entry point for building the gallery.

    Args:
        config_path: Path to settings.yaml configuration file
    """
    logger.info("=" * 60)
    logger.info(_("Fotoview Gallery Generator"))
    logger.info("=" * 60)

    # Load configuration
    config = load_config(config_path)

    # Scan and sync
    category_names, images = scan_and_sync(config)
    logger.info(_("Loaded %d images across %d categories"), len(images), len(category_names))

    # Organize by category
    categories = organize_by_category(category_names, images)

    # Generate HTML
    logger.info(_("Generating gallery HTML..."))
    html = generate_gallery_html(categories, config)

    # Write index.html
    output_path = config.output_dir / "index.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    logger.info(_("✓ Generated %s"), output_path)
    logger.info(_("  HTML size: %d bytes"), len(html))

    logger.info(_("Categories:"))
    for cat in categories:
        logger.info("  %s: %s", cat.name, _("%d images") % len(cat.images))

    logger.info(_("✓ Gallery built successfully!"))
    logger.info(_("  Output: %s"), config.output_dir.absolute())


def main() -> None:
    """CLI entry point."""
    from . import setup_logging

    # Setup logging
    setup_logging()

    config_path = Path("config/settings.yaml")
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])

    try:
        build_gallery(config_path)
    except Exception as e:
        logger.error(_("Error: %s"), e)
        sys.exit(1)


if __name__ == "__main__":
    main()
