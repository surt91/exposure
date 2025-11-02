"""Unit tests for thumbnail generation."""

from pathlib import Path

from src.generator.model import ThumbnailConfig


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


class TestCalculateThumbnailDimensions:
    """Tests for calculate_thumbnail_dimensions helper function."""

    def test_landscape_scaling(self):
        """Test scaling landscape image (width > height)."""
        from src.generator.thumbnails import calculate_thumbnail_dimensions

        # 4000x3000 image scaled to 800px max dimension
        width, height = calculate_thumbnail_dimensions(4000, 3000, 800)

        assert width == 800
        assert height == 600
        # Verify aspect ratio preserved (within rounding error)
        assert abs((width / height) - (4000 / 3000)) < 0.01

    def test_portrait_scaling(self):
        """Test scaling portrait image (height > width)."""
        from src.generator.thumbnails import calculate_thumbnail_dimensions

        # 3000x4000 image scaled to 800px max dimension
        width, height = calculate_thumbnail_dimensions(3000, 4000, 800)

        assert width == 600
        assert height == 800
        # Verify aspect ratio preserved
        assert abs((width / height) - (3000 / 4000)) < 0.01

    def test_square_scaling(self):
        """Test scaling square image (width == height)."""
        from src.generator.thumbnails import calculate_thumbnail_dimensions

        # 2000x2000 square image
        width, height = calculate_thumbnail_dimensions(2000, 2000, 800)

        assert width == 800
        assert height == 800

    def test_no_upscaling_landscape(self):
        """Test that small images are not upscaled (landscape)."""
        from src.generator.thumbnails import calculate_thumbnail_dimensions

        # 600x400 image with max_dimension 800 - should not upscale
        width, height = calculate_thumbnail_dimensions(600, 400, 800)

        assert width == 600
        assert height == 400

    def test_no_upscaling_portrait(self):
        """Test that small images are not upscaled (portrait)."""
        from src.generator.thumbnails import calculate_thumbnail_dimensions

        # 400x600 image with max_dimension 800 - should not upscale
        width, height = calculate_thumbnail_dimensions(400, 600, 800)

        assert width == 400
        assert height == 600

    def test_exact_size_match(self):
        """Test image exactly matching max dimension."""
        from src.generator.thumbnails import calculate_thumbnail_dimensions

        # 800x600 image with max_dimension 800
        width, height = calculate_thumbnail_dimensions(800, 600, 800)

        assert width == 800
        assert height == 600

    def test_aspect_ratio_preservation(self):
        """Test various aspect ratios are preserved."""
        from src.generator.thumbnails import calculate_thumbnail_dimensions

        # 16:9 aspect ratio
        width, height = calculate_thumbnail_dimensions(1920, 1080, 800)
        assert abs((width / height) - (16 / 9)) < 0.01

        # 4:3 aspect ratio
        width, height = calculate_thumbnail_dimensions(1600, 1200, 800)
        assert abs((width / height) - (4 / 3)) < 0.01

        # 3:2 aspect ratio
        width, height = calculate_thumbnail_dimensions(3000, 2000, 800)
        assert abs((width / height) - (3 / 2)) < 0.01


class TestGenerateContentHash:
    """Tests for generate_content_hash helper function."""

    def test_hash_length(self):
        """Test that hash is exactly 8 characters."""
        from src.generator.thumbnails import generate_content_hash

        test_data = b"test image data"
        hash_result = generate_content_hash(test_data)

        assert len(hash_result) == 8

    def test_hash_is_hexadecimal(self):
        """Test that hash contains only hexadecimal characters."""
        from src.generator.thumbnails import generate_content_hash

        test_data = b"test image data"
        hash_result = generate_content_hash(test_data)

        # Should be valid hex string
        assert all(c in "0123456789abcdef" for c in hash_result)

    def test_hash_reproducibility(self):
        """Test that same input produces same hash."""
        from src.generator.thumbnails import generate_content_hash

        test_data = b"test image data"
        hash1 = generate_content_hash(test_data)
        hash2 = generate_content_hash(test_data)

        assert hash1 == hash2

    def test_hash_uniqueness(self):
        """Test that different inputs produce different hashes."""
        from src.generator.thumbnails import generate_content_hash

        data1 = b"test image data 1"
        data2 = b"test image data 2"

        hash1 = generate_content_hash(data1)
        hash2 = generate_content_hash(data2)

        assert hash1 != hash2

    def test_hash_with_empty_data(self):
        """Test hash generation with empty data."""
        from src.generator.thumbnails import generate_content_hash

        empty_data = b""
        hash_result = generate_content_hash(empty_data)

        # Should still produce valid 8-character hash
        assert len(hash_result) == 8
        assert all(c in "0123456789abcdef" for c in hash_result)

    def test_hash_with_large_data(self):
        """Test hash generation with large data."""
        from src.generator.thumbnails import generate_content_hash

        # Simulate 1MB of data
        large_data = b"x" * (1024 * 1024)
        hash_result = generate_content_hash(large_data)

        assert len(hash_result) == 8


class TestApplyExifOrientation:
    """Tests for apply_exif_orientation helper function."""

    def test_exif_orientation_no_exif(self):
        """Test that image without EXIF data is returned unchanged."""
        from PIL import Image as PILImage

        from src.generator.thumbnails import apply_exif_orientation

        # Create simple image without EXIF
        img = PILImage.new("RGB", (100, 50), color="red")

        result = apply_exif_orientation(img)

        # Should return same image or equivalent
        assert result.size == img.size
        assert result.mode == img.mode

    def test_exif_orientation_returns_image(self):
        """Test that function always returns a valid PIL Image."""
        from PIL import Image as PILImage

        from src.generator.thumbnails import apply_exif_orientation

        img = PILImage.new("RGB", (100, 50), color="blue")

        result = apply_exif_orientation(img)

        # Result should be a PIL Image
        assert isinstance(result, PILImage.Image)

    def test_exif_orientation_preserves_mode(self):
        """Test that image mode is preserved."""
        from PIL import Image as PILImage

        from src.generator.thumbnails import apply_exif_orientation

        # Test RGB mode
        img_rgb = PILImage.new("RGB", (100, 50), color="green")
        result_rgb = apply_exif_orientation(img_rgb)
        assert result_rgb.mode == "RGB"

        # Test RGBA mode
        img_rgba = PILImage.new("RGBA", (100, 50), color=(255, 0, 0, 128))
        result_rgba = apply_exif_orientation(img_rgba)
        assert result_rgba.mode == "RGBA"


class TestThumbnailGenerator:
    """Tests for ThumbnailGenerator service."""

    def test_initialization(self):
        """Test generator initialization."""
        # Tests will be added in Phase 8
        pass
