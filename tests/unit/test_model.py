"""Tests for data models."""

from datetime import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.generator.cache import BuildCache, CacheEntry
from src.generator.model import (
    Category,
    GalleryConfig,
    Image,
    ThumbnailConfig,
    ThumbnailImage,
    YamlEntry,
)


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

    def test_banner_image_none(self, tmp_path):
        """Test that banner_image can be None."""
        content_dir = tmp_path / "content"
        content_dir.mkdir()

        yaml_path = tmp_path / "gallery.yaml"
        yaml_path.write_text("categories: []")

        config = GalleryConfig(
            content_dir=content_dir,
            gallery_yaml_path=yaml_path,
            default_category="Test",
            banner_image=None,
        )
        assert config.banner_image is None

    def test_banner_image_absolute_path(self, tmp_path):
        """Test banner_image with absolute path."""
        content_dir = tmp_path / "content"
        content_dir.mkdir()

        yaml_path = tmp_path / "gallery.yaml"
        yaml_path.write_text("categories: []")

        banner_file = tmp_path / "banner.jpg"
        banner_file.touch()

        config = GalleryConfig(
            content_dir=content_dir,
            gallery_yaml_path=yaml_path,
            default_category="Test",
            banner_image=banner_file,
        )
        assert config.banner_image == banner_file

    def test_banner_image_relative_path(self, tmp_path):
        """Test banner_image with path relative to content_dir."""
        content_dir = tmp_path / "content"
        content_dir.mkdir()

        yaml_path = tmp_path / "gallery.yaml"
        yaml_path.write_text("categories: []")

        banner_file = content_dir / "banner.jpg"
        banner_file.touch()

        config = GalleryConfig(
            content_dir=content_dir,
            gallery_yaml_path=yaml_path,
            default_category="Test",
            banner_image=Path("banner.jpg"),
        )
        assert config.banner_image == banner_file

    def test_banner_image_not_found(self, tmp_path):
        """Test validation error when banner image doesn't exist."""
        content_dir = tmp_path / "content"
        content_dir.mkdir()

        yaml_path = tmp_path / "gallery.yaml"
        yaml_path.write_text("categories: []")

        with pytest.raises(ValidationError, match="Banner image not found"):
            GalleryConfig(
                content_dir=content_dir,
                gallery_yaml_path=yaml_path,
                default_category="Test",
                banner_image=Path("nonexistent.jpg"),
            )

    def test_gallery_title_valid(self, tmp_path):
        """Test gallery_title with valid string."""
        content_dir = tmp_path / "content"
        content_dir.mkdir()

        yaml_path = tmp_path / "gallery.yaml"
        yaml_path.write_text("categories: []")

        config = GalleryConfig(
            content_dir=content_dir,
            gallery_yaml_path=yaml_path,
            default_category="Test",
            gallery_title="My Gallery",
        )
        assert config.gallery_title == "My Gallery"

    def test_gallery_title_none(self, tmp_path):
        """Test that gallery_title can be None."""
        content_dir = tmp_path / "content"
        content_dir.mkdir()

        yaml_path = tmp_path / "gallery.yaml"
        yaml_path.write_text("categories: []")

        config = GalleryConfig(
            content_dir=content_dir,
            gallery_yaml_path=yaml_path,
            default_category="Test",
            gallery_title=None,
        )
        assert config.gallery_title is None

    def test_gallery_title_empty(self, tmp_path):
        """Test validation error for empty gallery_title."""
        content_dir = tmp_path / "content"
        content_dir.mkdir()

        yaml_path = tmp_path / "gallery.yaml"
        yaml_path.write_text("categories: []")

        with pytest.raises(ValidationError, match="cannot be empty"):
            GalleryConfig(
                content_dir=content_dir,
                gallery_yaml_path=yaml_path,
                default_category="Test",
                gallery_title="   ",
            )

    def test_gallery_title_too_long(self, tmp_path):
        """Test validation error for too long gallery_title."""
        content_dir = tmp_path / "content"
        content_dir.mkdir()

        yaml_path = tmp_path / "gallery.yaml"
        yaml_path.write_text("categories: []")

        with pytest.raises(ValidationError, match="200 characters"):
            GalleryConfig(
                content_dir=content_dir,
                gallery_yaml_path=yaml_path,
                default_category="Test",
                gallery_title="x" * 201,
            )

    def test_gallery_subtitle_valid(self, tmp_path):
        """Test gallery_subtitle with valid string."""
        content_dir = tmp_path / "content"
        content_dir.mkdir()

        yaml_path = tmp_path / "gallery.yaml"
        yaml_path.write_text("categories: []")

        config = GalleryConfig(
            content_dir=content_dir,
            gallery_yaml_path=yaml_path,
            default_category="Test",
            gallery_subtitle="My subtitle",
        )
        assert config.gallery_subtitle == "My subtitle"

    def test_gallery_subtitle_none(self, tmp_path):
        """Test that gallery_subtitle can be None."""
        content_dir = tmp_path / "content"
        content_dir.mkdir()

        yaml_path = tmp_path / "gallery.yaml"
        yaml_path.write_text("categories: []")

        config = GalleryConfig(
            content_dir=content_dir,
            gallery_yaml_path=yaml_path,
            default_category="Test",
            gallery_subtitle=None,
        )
        assert config.gallery_subtitle is None

    def test_gallery_subtitle_empty_becomes_none(self, tmp_path):
        """Test that empty/whitespace subtitle becomes None."""
        content_dir = tmp_path / "content"
        content_dir.mkdir()

        yaml_path = tmp_path / "gallery.yaml"
        yaml_path.write_text("categories: []")

        config = GalleryConfig(
            content_dir=content_dir,
            gallery_yaml_path=yaml_path,
            default_category="Test",
            gallery_subtitle="   ",
        )
        assert config.gallery_subtitle is None

    def test_gallery_subtitle_too_long(self, tmp_path):
        """Test validation error for too long gallery_subtitle."""
        content_dir = tmp_path / "content"
        content_dir.mkdir()

        yaml_path = tmp_path / "gallery.yaml"
        yaml_path.write_text("categories: []")

        with pytest.raises(ValidationError, match="300 characters"):
            GalleryConfig(
                content_dir=content_dir,
                gallery_yaml_path=yaml_path,
                default_category="Test",
                gallery_subtitle="x" * 301,
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


class TestThumbnailConfig:
    """Tests for ThumbnailConfig model validation."""

    def test_default_configuration(self):
        """Verify default configuration values."""
        config = ThumbnailConfig()

        assert config.max_dimension == 800
        assert config.webp_quality == 85
        assert config.jpeg_quality == 90
        assert config.output_dir == Path("build/images/thumbnails")
        assert config.enable_cache is True
        assert config.resampling_filter == "LANCZOS"

    def test_custom_configuration(self):
        """Test creating configuration with custom values."""
        config = ThumbnailConfig(
            max_dimension=1200,
            webp_quality=80,
            jpeg_quality=85,
            output_dir=Path("custom/thumbnails"),
            enable_cache=False,
            resampling_filter="BICUBIC",
        )

        assert config.max_dimension == 1200
        assert config.webp_quality == 80
        assert config.jpeg_quality == 85
        assert config.output_dir == Path("custom/thumbnails")
        assert config.enable_cache is False
        assert config.resampling_filter == "BICUBIC"

    def test_max_dimension_too_small_raises(self):
        """Test that max_dimension below 100 raises ValidationError."""
        with pytest.raises(ValidationError, match="max_dimension"):
            ThumbnailConfig(max_dimension=50)

    def test_max_dimension_too_large_raises(self):
        """Test that max_dimension above 4000 raises ValidationError."""
        with pytest.raises(ValidationError, match="max_dimension"):
            ThumbnailConfig(max_dimension=5000)

    def test_webp_quality_too_low_raises(self):
        """Test that webp_quality below 1 raises ValidationError."""
        with pytest.raises(ValidationError, match="webp_quality"):
            ThumbnailConfig(webp_quality=0)

    def test_webp_quality_too_high_raises(self):
        """Test that webp_quality above 100 raises ValidationError."""
        with pytest.raises(ValidationError, match="webp_quality"):
            ThumbnailConfig(webp_quality=150)

    def test_jpeg_quality_validation(self):
        """Test JPEG quality validation range."""
        # Valid quality values
        config = ThumbnailConfig(jpeg_quality=1)
        assert config.jpeg_quality == 1

        config = ThumbnailConfig(jpeg_quality=100)
        assert config.jpeg_quality == 100

        # Invalid values
        with pytest.raises(ValidationError, match="jpeg_quality"):
            ThumbnailConfig(jpeg_quality=0)

        with pytest.raises(ValidationError, match="jpeg_quality"):
            ThumbnailConfig(jpeg_quality=101)

    def test_resampling_filter_validation(self):
        """Test resampling filter validation."""
        # Valid filters
        for filter_name in ["LANCZOS", "BICUBIC", "BILINEAR", "NEAREST"]:
            config = ThumbnailConfig(resampling_filter=filter_name)
            assert config.resampling_filter == filter_name

        # Invalid filter
        with pytest.raises(ValidationError, match="resampling_filter"):
            ThumbnailConfig(resampling_filter="INVALID")

    def test_path_conversion(self):
        """Test automatic conversion of strings to Path objects."""
        config = ThumbnailConfig(output_dir="build/thumbnails", cache_file="build/cache.json")

        assert isinstance(config.output_dir, Path)
        assert isinstance(config.cache_file, Path)


class TestThumbnailImage:
    """Tests for ThumbnailImage model."""

    def test_create_thumbnail_image(self, tmp_path):
        """Test creating valid ThumbnailImage."""
        source = tmp_path / "source.jpg"
        webp = tmp_path / "thumb.webp"
        jpeg = tmp_path / "thumb.jpg"

        thumbnail = ThumbnailImage(
            source_filename="source.jpg",
            source_path=source,
            webp_path=webp,
            jpeg_path=jpeg,
            width=800,
            height=600,
            webp_size_bytes=45_000,
            jpeg_size_bytes=65_000,
            source_size_bytes=2_500_000,
            content_hash="a1b2c3d4",
            generated_at=datetime.now(),
        )

        assert thumbnail.source_filename == "source.jpg"
        assert thumbnail.width == 800
        assert thumbnail.height == 600

    def test_size_reduction_percent(self, tmp_path):
        """Test size reduction percentage calculation."""
        source = tmp_path / "source.jpg"
        webp = tmp_path / "thumb.webp"
        jpeg = tmp_path / "thumb.jpg"

        thumbnail = ThumbnailImage(
            source_filename="source.jpg",
            source_path=source,
            webp_path=webp,
            jpeg_path=jpeg,
            width=800,
            height=600,
            webp_size_bytes=50_000,  # 50KB
            jpeg_size_bytes=70_000,  # 70KB
            source_size_bytes=2_500_000,  # 2.5MB
            content_hash="a1b2c3d4",
            generated_at=datetime.now(),
        )

        # Should be 98% reduction (2.5MB -> 50KB)
        assert abs(thumbnail.size_reduction_percent - 98.0) < 0.1

    def test_webp_savings_percent(self, tmp_path):
        """Test WebP savings vs JPEG percentage calculation."""
        source = tmp_path / "source.jpg"
        webp = tmp_path / "thumb.webp"
        jpeg = tmp_path / "thumb.jpg"

        thumbnail = ThumbnailImage(
            source_filename="source.jpg",
            source_path=source,
            webp_path=webp,
            jpeg_path=jpeg,
            width=800,
            height=600,
            webp_size_bytes=45_000,  # 45KB
            jpeg_size_bytes=65_000,  # 65KB
            source_size_bytes=2_500_000,
            content_hash="a1b2c3d4",
            generated_at=datetime.now(),
        )

        # Should be ~30.8% savings (65KB - 45KB) / 65KB
        assert abs(thumbnail.webp_savings_percent - 30.769) < 0.1

    def test_aspect_ratio(self, tmp_path):
        """Test aspect ratio calculation."""
        source = tmp_path / "source.jpg"
        webp = tmp_path / "thumb.webp"
        jpeg = tmp_path / "thumb.jpg"

        thumbnail = ThumbnailImage(
            source_filename="source.jpg",
            source_path=source,
            webp_path=webp,
            jpeg_path=jpeg,
            width=800,
            height=600,
            webp_size_bytes=45_000,
            jpeg_size_bytes=65_000,
            source_size_bytes=2_500_000,
            content_hash="a1b2c3d4",
            generated_at=datetime.now(),
        )

        # 800/600 = 1.333...
        assert abs(thumbnail.aspect_ratio - (4 / 3)) < 0.001

    def test_validation_errors(self, tmp_path):
        """Test validation errors for invalid values."""
        source = tmp_path / "source.jpg"
        webp = tmp_path / "thumb.webp"
        jpeg = tmp_path / "thumb.jpg"

        # Zero width
        with pytest.raises(ValidationError, match="width"):
            ThumbnailImage(
                source_filename="source.jpg",
                source_path=source,
                webp_path=webp,
                jpeg_path=jpeg,
                width=0,
                height=600,
                webp_size_bytes=45_000,
                jpeg_size_bytes=65_000,
                source_size_bytes=2_500_000,
                content_hash="a1b2c3d4",
                generated_at=datetime.now(),
            )

        # Invalid hash length
        with pytest.raises(ValidationError, match="content_hash"):
            ThumbnailImage(
                source_filename="source.jpg",
                source_path=source,
                webp_path=webp,
                jpeg_path=jpeg,
                width=800,
                height=600,
                webp_size_bytes=45_000,
                jpeg_size_bytes=65_000,
                source_size_bytes=2_500_000,
                content_hash="abc",  # Too short
                generated_at=datetime.now(),
            )


class TestBuildCache:
    """Tests for BuildCache model."""

    def test_create_empty_cache(self):
        """Test creating empty build cache."""
        cache = BuildCache()

        assert len(cache.entries) == 0
        assert cache.cache_version == "2.0"  # Updated for metadata stripping feature
        assert isinstance(cache.last_updated, datetime)

    def test_should_regenerate_missing_entry(self, tmp_path):
        """Test that should_regenerate returns True for missing entries."""
        cache = BuildCache()
        source = tmp_path / "image.jpg"
        source.touch()

        assert cache.should_regenerate(source) is True

    def test_should_regenerate_modified_file(self, tmp_path):
        """Test that should_regenerate returns True for modified files."""
        cache = BuildCache()
        source = tmp_path / "image.jpg"
        source.write_text("original content")

        # Add cache entry with old mtime
        old_mtime = source.stat().st_mtime - 100
        cache.entries[str(source)] = CacheEntry(
            source_path=str(source),
            source_mtime=old_mtime,
            webp_path="thumb.webp",
            jpeg_path="thumb.jpg",
            content_hash="abc123",
            thumbnail_generated_at=datetime.now(),
        )

        # File has been modified (current mtime > cached mtime)
        assert cache.should_regenerate(source) is True

    def test_should_regenerate_unchanged_file(self, tmp_path):
        """Test that should_regenerate returns False for unchanged files."""
        cache = BuildCache()
        source = tmp_path / "image.jpg"
        source.write_text("content")

        # Add cache entry with current mtime
        current_mtime = source.stat().st_mtime
        cache.entries[str(source)] = CacheEntry(
            source_path=str(source),
            source_mtime=current_mtime,
            webp_path="thumb.webp",
            jpeg_path="thumb.jpg",
            content_hash="abc123",
            thumbnail_generated_at=datetime.now(),
        )

        # File unchanged
        assert cache.should_regenerate(source) is False

    def test_update_entry(self, tmp_path):
        """Test updating cache entry with new thumbnail."""
        cache = BuildCache()
        source = tmp_path / "image.jpg"
        source.write_text("content")

        webp = tmp_path / "thumb.webp"
        jpeg = tmp_path / "thumb.jpg"

        thumbnail = ThumbnailImage(
            source_filename="image.jpg",
            source_path=source,
            webp_path=webp,
            jpeg_path=jpeg,
            width=800,
            height=600,
            webp_size_bytes=45_000,
            jpeg_size_bytes=65_000,
            source_size_bytes=100_000,
            content_hash="a1b2c3d4",
            generated_at=datetime.now(),
        )

        cache.update_entry(source, thumbnail)

        # Entry should be added
        assert str(source) in cache.entries
        entry = cache.entries[str(source)]
        assert entry.content_hash == "a1b2c3d4"
        assert entry.source_path == str(source)

    def test_cache_versioning(self):
        """Test cache version field."""
        cache = BuildCache(cache_version="1.0")
        assert cache.cache_version == "1.0"

        # Version can be set to different value
        cache2 = BuildCache(cache_version="2.0")
        assert cache2.cache_version == "2.0"
