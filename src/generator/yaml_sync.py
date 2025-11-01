"""YAML synchronization utilities for gallery metadata."""

from pathlib import Path

import yaml

from .model import YamlEntry


def load_gallery_yaml(yaml_path: Path) -> tuple[list[str], list[YamlEntry]]:
    """
    Load categories and images from gallery YAML file.

    Args:
        yaml_path: Path to the gallery.yaml file

    Returns:
        Tuple of (categories list, YamlEntry list)

    Raises:
        FileNotFoundError: If YAML file doesn't exist
        yaml.YAMLError: If YAML is malformed
        ValueError: If required fields are missing
    """
    if not yaml_path.exists():
        raise FileNotFoundError(f"Gallery YAML not found: {yaml_path}")

    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    if not data:
        return [], []

    categories = data.get("categories", [])
    if not isinstance(categories, list):
        raise ValueError("categories must be a list")

    # Check for duplicate categories
    if len(categories) != len(set(categories)):
        raise ValueError("Duplicate categories found")

    images_data = data.get("images", [])
    if not isinstance(images_data, list):
        raise ValueError("images must be a list")

    entries = []
    filenames_seen = set()

    for img_data in images_data:
        if not isinstance(img_data, dict):
            raise ValueError(f"Invalid image entry: {img_data}")

        filename = img_data.get("filename")
        if not filename:
            raise ValueError("Image entry missing filename")

        if filename in filenames_seen:
            raise ValueError(f"Duplicate filename in YAML: {filename}")
        filenames_seen.add(filename)

        entries.append(YamlEntry.model_validate(img_data))

    return categories, entries


def save_gallery_yaml(yaml_path: Path, categories: list[str], entries: list[YamlEntry]) -> None:
    """
    Save categories and images to gallery YAML file.

    Args:
        yaml_path: Path to the gallery.yaml file
        categories: List of category names in display order
        entries: List of YamlEntry objects

    Raises:
        ValueError: If categories contain duplicates or entries have duplicate filenames
    """
    # Validate categories
    if len(categories) != len(set(categories)):
        raise ValueError("Duplicate categories provided")

    # Validate entries
    filenames = [e.filename for e in entries]
    if len(filenames) != len(set(filenames)):
        raise ValueError("Duplicate filenames in entries")

    data = {"categories": categories, "images": [e.model_dump() for e in entries]}

    # Ensure parent directory exists
    yaml_path.parent.mkdir(parents=True, exist_ok=True)

    with open(yaml_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def append_stub_entries(yaml_path: Path, new_filenames: list[str], default_category: str) -> int:
    """
    Append stub entries for new images not in YAML.

    Preserves existing categories and image order. New stubs are added at the end
    under the default_category.

    Args:
        yaml_path: Path to the gallery.yaml file
        new_filenames: List of filenames to add as stubs
        default_category: Category to assign to new entries

    Returns:
        Number of stubs appended

    Raises:
        ValueError: If default_category is empty
    """
    if not default_category:
        raise ValueError("default_category cannot be empty")

    categories, existing_entries = load_gallery_yaml(yaml_path)

    # Ensure default category exists
    if default_category not in categories:
        categories.append(default_category)

    existing_filenames = {e.filename for e in existing_entries}
    stubs_to_add = [f for f in new_filenames if f not in existing_filenames]

    if not stubs_to_add:
        return 0

    # Create stub entries
    new_entries = [
        YamlEntry(filename=fname, category=default_category, title="", description="")
        for fname in stubs_to_add
    ]

    all_entries = existing_entries + new_entries
    save_gallery_yaml(yaml_path, categories, all_entries)

    return len(stubs_to_add)


def get_entry_map(entries: list[YamlEntry]) -> dict[str, YamlEntry]:
    """
    Create a mapping of filename to YamlEntry.

    Args:
        entries: List of YamlEntry objects

    Returns:
        Dictionary mapping filename to entry
    """
    return {entry.filename: entry for entry in entries}
