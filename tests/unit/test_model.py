"""Tests for data models."""

import pytest
from pydantic import ValidationError

from src.generator.model import Category, GalleryConfig, Image, YamlEntry


@pytest.fixture(autouse=True)
def isolated_yaml_settings(tmp_path, monkeypatch):
    """Isolate tests from the default settings.yaml file.

    This fixture ensures that GalleryConfig doesn't load settings from
    the project's config/settings.yaml, which would interfere with tests.
    """
    import src.generator.model as model_module

    # Point to a non-existent file so tests only use explicitly provided values
    monkeypatch.setattr(model_module, "_yaml_settings_file", tmp_path / "test_settings.yaml")


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
        """Test that empty filename raises ValidationError (Pydantic)."""
        with pytest.raises(ValidationError, match="filename"):
            Image(filename="", file_path=tmp_path / "test.jpg", category="Test")

    def test_empty_category_raises(self, tmp_path):
        """Test that empty category raises ValidationError (Pydantic)."""
        with pytest.raises(ValidationError, match="category"):
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

    def test_aspect_ratio_with_dimensions(self, tmp_path):
        """Test aspect ratio calculation with dimensions."""
        img = Image(
            filename="test.jpg",
            file_path=tmp_path / "test.jpg",
            category="Test",
            width=1920,
            height=1080,
        )
        assert img.aspect_ratio is not None
        assert abs(img.aspect_ratio - 1.7777777777777777) < 0.0001

    def test_aspect_ratio_without_dimensions(self, tmp_path):
        """Test aspect ratio returns None without dimensions."""
        img = Image(
            filename="test.jpg",
            file_path=tmp_path / "test.jpg",
            category="Test",
        )
        assert img.aspect_ratio is None

    def test_aspect_ratio_with_partial_dimensions(self, tmp_path):
        """Test aspect ratio returns None with partial dimensions."""
        img = Image(
            filename="test.jpg",
            file_path=tmp_path / "test.jpg",
            category="Test",
            width=1920,
        )
        assert img.aspect_ratio is None

    def test_aspect_ratio_landscape(self, tmp_path):
        """Test aspect ratio calculation for landscape images (16:9)."""
        img = Image(
            filename="landscape.jpg",
            file_path=tmp_path / "test.jpg",
            category="Test",
            width=1920,
            height=1080,
        )
        assert img.aspect_ratio is not None
        assert abs(img.aspect_ratio - 1.7778) < 0.001

    def test_aspect_ratio_portrait(self, tmp_path):
        """Test aspect ratio calculation for portrait images (9:16)."""
        img = Image(
            filename="portrait.jpg",
            file_path=tmp_path / "test.jpg",
            category="Test",
            width=1080,
            height=1920,
        )
        assert img.aspect_ratio is not None
        assert abs(img.aspect_ratio - 0.5625) < 0.001

    def test_aspect_ratio_square(self, tmp_path):
        """Test aspect ratio calculation for square images (1:1)."""
        img = Image(
            filename="square.jpg",
            file_path=tmp_path / "test.jpg",
            category="Test",
            width=1000,
            height=1000,
        )
        assert img.aspect_ratio == 1.0

    def test_aspect_ratio_panorama(self, tmp_path):
        """Test aspect ratio calculation for panoramic images (3:1)."""
        img = Image(
            filename="panorama.jpg",
            file_path=tmp_path / "test.jpg",
            category="Test",
            width=3000,
            height=1000,
        )
        assert img.aspect_ratio == 3.0

    def test_aspect_ratio_extreme_wide(self, tmp_path):
        """Test aspect ratio calculation for extreme wide images (4:1)."""
        img = Image(
            filename="extreme_wide.jpg",
            file_path=tmp_path / "test.jpg",
            category="Test",
            width=4000,
            height=1000,
        )
        assert img.aspect_ratio == 4.0

    def test_aspect_ratio_extreme_tall(self, tmp_path):
        """Test aspect ratio calculation for extreme tall images (1:4)."""
        img = Image(
            filename="extreme_tall.jpg",
            file_path=tmp_path / "test.jpg",
            category="Test",
            width=1000,
            height=4000,
        )
        assert img.aspect_ratio == 0.25


class TestCategory:
    """Tests for Category model."""

    def test_create_category(self):
        """Test creating a valid category."""
        cat = Category(name="Landscapes", order_index=0)
        assert cat.name == "Landscapes"
        assert cat.order_index == 0
        assert len(cat.images) == 0

    def test_empty_name_raises(self):
        """Test that empty name raises ValidationError (Pydantic)."""
        with pytest.raises(ValidationError, match="name"):
            Category(name="", order_index=0)

    def test_negative_order_raises(self):
        """Test that negative order_index raises ValidationError (Pydantic)."""
        with pytest.raises(ValidationError, match="order_index"):
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
        """Test that non-existent content_dir raises ValidationError (Pydantic)."""
        yaml_path = tmp_path / "gallery.yaml"
        yaml_path.write_text("categories: []")

        with pytest.raises(ValidationError, match="content_dir does not exist"):
            GalleryConfig(
                content_dir=tmp_path / "nonexistent",
                gallery_yaml_path=yaml_path,
                default_category="Test",
            )

    def test_nonexistent_yaml_raises(self, tmp_path):
        """Test that non-existent YAML path raises ValidationError (Pydantic)."""
        content_dir = tmp_path / "content"
        content_dir.mkdir()

        with pytest.raises(ValidationError, match="gallery_yaml_path does not exist"):
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

    def test_model_dump(self):
        """Test conversion to dictionary using Pydantic model_dump()."""
        entry = YamlEntry(
            filename="test.jpg", category="Landscapes", title="Test", description="Desc"
        )

        data = entry.model_dump()
        assert data["filename"] == "test.jpg"
        assert data["category"] == "Landscapes"
        assert data["title"] == "Test"
        assert data["description"] == "Desc"

    def test_model_validate(self):
        """Test creation from dictionary using Pydantic model_validate()."""
        data = {
            "filename": "test.jpg",
            "category": "Landscapes",
            "title": "Test",
            "description": "Desc",
        }

        entry = YamlEntry.model_validate(data)
        assert entry.filename == "test.jpg"
        assert entry.category == "Landscapes"
