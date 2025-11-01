"""Tests for data models."""

import pytest

from generator.model import Category, GalleryConfig, Image, YamlEntry


class TestImage:
    """Tests for Image model."""

    def test_create_image(self, tmp_path):
        """Test creating a valid image."""
        img_path = tmp_path / "test.jpg"
        img_path.touch()

        img = Image(
            filename="test.jpg",
            file_path=img_path,
            category="Landscapes",
            title="Test Image",
        )

        assert img.filename == "test.jpg"
        assert img.category == "Landscapes"
        assert img.title == "Test Image"

    def test_empty_filename_raises(self, tmp_path):
        """Test that empty filename raises ValueError."""
        with pytest.raises(ValueError, match="filename cannot be empty"):
            Image(filename="", file_path=tmp_path / "test.jpg", category="Test")

    def test_empty_category_raises(self, tmp_path):
        """Test that empty category raises ValueError."""
        with pytest.raises(ValueError, match="category cannot be empty"):
            Image(filename="test.jpg", file_path=tmp_path / "test.jpg", category="")

    def test_alt_text_from_title(self, tmp_path):
        """Test alt text generation from title."""
        img = Image(
            filename="test.jpg",
            file_path=tmp_path / "test.jpg",
            category="Test",
            title="Beautiful Sunset",
        )
        assert img.alt_text == "Beautiful Sunset"

    def test_alt_text_from_filename(self, tmp_path):
        """Test alt text generation from filename when no title."""
        img = Image(
            filename="mountain_sunrise.jpg",
            file_path=tmp_path / "test.jpg",
            category="Test",
        )
        assert img.alt_text == "Mountain Sunrise"


class TestCategory:
    """Tests for Category model."""

    def test_create_category(self):
        """Test creating a valid category."""
        cat = Category(name="Landscapes", order_index=0)
        assert cat.name == "Landscapes"
        assert cat.order_index == 0
        assert len(cat.images) == 0

    def test_empty_name_raises(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            Category(name="", order_index=0)

    def test_negative_order_raises(self):
        """Test that negative order_index raises ValueError."""
        with pytest.raises(ValueError, match="order_index must be non-negative"):
            Category(name="Test", order_index=-1)

    def test_add_image(self, tmp_path):
        """Test adding image to category."""
        cat = Category(name="Landscapes", order_index=0)
        img = Image(
            filename="test.jpg",
            file_path=tmp_path / "test.jpg",
            category="Landscapes",
        )

        cat.add_image(img)
        assert len(cat.images) == 1
        assert cat.images[0] == img

    def test_add_wrong_category_raises(self, tmp_path):
        """Test that adding image with wrong category raises error."""
        cat = Category(name="Landscapes", order_index=0)
        img = Image(
            filename="test.jpg",
            file_path=tmp_path / "test.jpg",
            category="Portraits",  # Wrong category
        )

        with pytest.raises(ValueError, match="does not match"):
            cat.add_image(img)


class TestGalleryConfig:
    """Tests for GalleryConfig model."""

    def test_create_config(self, tmp_path):
        """Test creating valid configuration."""
        content_dir = tmp_path / "content"
        content_dir.mkdir()

        yaml_path = tmp_path / "gallery.yaml"
        yaml_path.write_text("categories: []")

        config = GalleryConfig(
            content_dir=content_dir,
            gallery_yaml_path=yaml_path,
            default_category="Uncategorized",
        )

        assert config.content_dir == content_dir
        assert config.gallery_yaml_path == yaml_path
        assert config.default_category == "Uncategorized"

    def test_nonexistent_content_dir_raises(self, tmp_path):
        """Test that non-existent content_dir raises error."""
        yaml_path = tmp_path / "gallery.yaml"
        yaml_path.write_text("categories: []")

        with pytest.raises(ValueError, match="content_dir does not exist"):
            GalleryConfig(
                content_dir=tmp_path / "nonexistent",
                gallery_yaml_path=yaml_path,
                default_category="Test",
            )

    def test_nonexistent_yaml_raises(self, tmp_path):
        """Test that non-existent YAML path raises error."""
        content_dir = tmp_path / "content"
        content_dir.mkdir()

        with pytest.raises(ValueError, match="gallery_yaml_path does not exist"):
            GalleryConfig(
                content_dir=content_dir,
                gallery_yaml_path=tmp_path / "nonexistent.yaml",
                default_category="Test",
            )


class TestYamlEntry:
    """Tests for YamlEntry model."""

    def test_create_entry(self):
        """Test creating valid YAML entry."""
        entry = YamlEntry(
            filename="test.jpg",
            category="Landscapes",
            title="Test",
            description="Description",
        )

        assert entry.filename == "test.jpg"
        assert entry.category == "Landscapes"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        entry = YamlEntry(
            filename="test.jpg", category="Landscapes", title="Test", description="Desc"
        )

        data = entry.to_dict()
        assert data["filename"] == "test.jpg"
        assert data["category"] == "Landscapes"
        assert data["title"] == "Test"
        assert data["description"] == "Desc"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "filename": "test.jpg",
            "category": "Landscapes",
            "title": "Test",
            "description": "Desc",
        }

        entry = YamlEntry.from_dict(data)
        assert entry.filename == "test.jpg"
        assert entry.category == "Landscapes"
