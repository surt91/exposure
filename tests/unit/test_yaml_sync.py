"""Tests for YAML synchronization."""

import pytest

from src.generator.model import YamlEntry
from src.generator.yaml_sync import (
    append_stub_entries,
    get_entry_map,
    load_gallery_yaml,
    save_gallery_yaml,
)


class TestLoadGalleryYaml:
    """Tests for loading YAML files."""

    def test_load_valid_yaml(self, tmp_path):
        """Test loading valid YAML file."""
        yaml_path = tmp_path / "gallery.yaml"
        yaml_content = """
categories:
  - Landscapes
  - Portraits

images:
  - filename: img1.jpg
    category: Landscapes
    title: Mountain
    description: Beautiful peaks
  - filename: img2.jpg
    category: Portraits
    title: Portrait
    description: ""
"""
        yaml_path.write_text(yaml_content)

        categories, entries = load_gallery_yaml(yaml_path)

        assert categories == ["Landscapes", "Portraits"]
        assert len(entries) == 2
        assert entries[0].filename == "img1.jpg"
        assert entries[0].category == "Landscapes"
        assert entries[1].filename == "img2.jpg"

    def test_load_empty_yaml(self, tmp_path):
        """Test loading empty YAML returns empty lists."""
        yaml_path = tmp_path / "gallery.yaml"
        yaml_path.write_text("")

        categories, entries = load_gallery_yaml(yaml_path)

        assert categories == []
        assert entries == []

    def test_load_nonexistent_raises(self, tmp_path):
        """Test that loading non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_gallery_yaml(tmp_path / "nonexistent.yaml")

    def test_duplicate_categories_raises(self, tmp_path):
        """Test that duplicate categories raise error."""
        yaml_path = tmp_path / "gallery.yaml"
        yaml_content = """
categories:
  - Landscapes
  - Landscapes
images: []
"""
        yaml_path.write_text(yaml_content)

        with pytest.raises(ValueError, match="Duplicate categories"):
            load_gallery_yaml(yaml_path)

    def test_duplicate_filenames_raises(self, tmp_path):
        """Test that duplicate filenames raise error."""
        yaml_path = tmp_path / "gallery.yaml"
        yaml_content = """
categories:
  - Test
images:
  - filename: test.jpg
    category: Test
  - filename: test.jpg
    category: Test
"""
        yaml_path.write_text(yaml_content)

        with pytest.raises(ValueError, match="Duplicate filename"):
            load_gallery_yaml(yaml_path)


class TestSaveGalleryYaml:
    """Tests for saving YAML files."""

    def test_save_and_reload(self, tmp_path):
        """Test saving and reloading YAML."""
        yaml_path = tmp_path / "gallery.yaml"

        categories = ["Landscapes", "Portraits"]
        entries = [
            YamlEntry(
                filename="img1.jpg", category="Landscapes", title="Mountain", description="Peaks"
            ),
            YamlEntry(
                filename="img2.jpg", category="Portraits", title="Portrait", description="Person"
            ),
        ]

        save_gallery_yaml(yaml_path, categories, entries)

        # Reload and verify
        loaded_cats, loaded_entries = load_gallery_yaml(yaml_path)

        assert loaded_cats == categories
        assert len(loaded_entries) == 2
        assert loaded_entries[0].filename == "img1.jpg"
        assert loaded_entries[1].filename == "img2.jpg"

    def test_save_duplicate_categories_raises(self, tmp_path):
        """Test that saving duplicate categories raises error."""
        yaml_path = tmp_path / "gallery.yaml"
        categories = ["Test", "Test"]

        with pytest.raises(ValueError, match="Duplicate categories"):
            save_gallery_yaml(yaml_path, categories, [])

    def test_save_duplicate_filenames_raises(self, tmp_path):
        """Test that saving duplicate filenames raises error."""
        yaml_path = tmp_path / "gallery.yaml"
        entries = [
            YamlEntry(filename="test.jpg", category="Cat1"),
            YamlEntry(filename="test.jpg", category="Cat2"),
        ]

        with pytest.raises(ValueError, match="Duplicate filenames"):
            save_gallery_yaml(yaml_path, ["Cat1", "Cat2"], entries)


class TestAppendStubEntries:
    """Tests for stub generation."""

    def test_append_new_stubs(self, tmp_path):
        """Test appending stubs for new images."""
        yaml_path = tmp_path / "gallery.yaml"
        yaml_content = """
categories:
  - Landscapes
images:
  - filename: existing.jpg
    category: Landscapes
    title: Existing
    description: ""
"""
        yaml_path.write_text(yaml_content)

        count = append_stub_entries(
            yaml_path, ["new1.jpg", "new2.jpg", "existing.jpg"], "Uncategorized"
        )

        assert count == 2  # Only new files

        # Verify YAML updated
        categories, entries = load_gallery_yaml(yaml_path)
        assert len(entries) == 3
        assert "Uncategorized" in categories

        # Check stub structure
        new_entry = next(e for e in entries if e.filename == "new1.jpg")
        assert new_entry.category == "Uncategorized"
        assert new_entry.title == ""
        assert new_entry.description == ""

    def test_no_stubs_needed(self, tmp_path):
        """Test when all images already have entries."""
        yaml_path = tmp_path / "gallery.yaml"
        yaml_content = """
categories:
  - Test
images:
  - filename: img1.jpg
    category: Test
"""
        yaml_path.write_text(yaml_content)

        count = append_stub_entries(yaml_path, ["img1.jpg"], "Uncategorized")

        assert count == 0


class TestGetEntryMap:
    """Tests for entry mapping."""

    def test_create_entry_map(self):
        """Test creating filename to entry mapping."""
        entries = [
            YamlEntry(filename="img1.jpg", category="Cat1"),
            YamlEntry(filename="img2.jpg", category="Cat2"),
        ]

        entry_map = get_entry_map(entries)

        assert len(entry_map) == 2
        assert entry_map["img1.jpg"].category == "Cat1"
        assert entry_map["img2.jpg"].category == "Cat2"
