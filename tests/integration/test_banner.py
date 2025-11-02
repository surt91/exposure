"""Integration tests for banner and title feature."""

import pytest

from src.generator.build_html import build_gallery, load_config


class TestBannerIntegration:
    """Integration tests for banner image and title display."""

    def test_build_with_banner_and_title(self, tmp_path):
        """Test full build with banner and title configured."""
        # Setup directories
        content_dir = tmp_path / "content"
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "dist"

        content_dir.mkdir()
        config_dir.mkdir()

        # Create sample image
        (content_dir / "img1.jpg").write_bytes(b"fake jpg data")

        # Create banner image
        banner = content_dir / "banner.jpg"
        banner.write_bytes(b"fake banner data")

        # Create YAML
        yaml_path = config_dir / "gallery.yaml"
        yaml_path.write_text(
            """
categories:
  - Test Category
images: []
"""
        )

        # Create settings with banner and title
        settings_path = config_dir / "settings.yaml"
        settings_path.write_text(
            f"""
content_dir: {content_dir}
gallery_yaml_path: {yaml_path}
default_category: Uncategorized
output_dir: {output_dir}
banner_image: banner.jpg
gallery_title: Test Gallery
"""
        )

        # Run build
        build_gallery(settings_path)

        # Verify banner copied to output
        banner_output = output_dir / "images" / "banner" / "banner.jpg"
        assert banner_output.exists(), "Banner image should be copied to output directory"

        # Verify HTML contains banner elements
        html_path = output_dir / "index.html"
        assert html_path.exists(), "HTML file should be generated"

        html_content = html_path.read_text()
        assert "images/banner/banner.jpg" in html_content, "Banner image URL should be in HTML"
        assert "Test Gallery" in html_content, "Gallery title should be in HTML"
        assert 'class="gallery-banner"' in html_content, "Banner section should be in HTML"
        assert 'class="banner-title"' in html_content, "Title overlay should be in HTML"

    def test_build_without_banner(self, tmp_path):
        """Test build without banner configured (backward compatibility)."""
        # Setup directories
        content_dir = tmp_path / "content"
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "dist"

        content_dir.mkdir()
        config_dir.mkdir()

        # Create sample image
        (content_dir / "img1.jpg").write_bytes(b"fake jpg data")

        # Create YAML
        yaml_path = config_dir / "gallery.yaml"
        yaml_path.write_text(
            """
categories:
  - Test Category
images: []
"""
        )

        # Create settings WITHOUT banner
        settings_path = config_dir / "settings.yaml"
        settings_path.write_text(
            f"""
content_dir: {content_dir}
gallery_yaml_path: {yaml_path}
default_category: Uncategorized
output_dir: {output_dir}
"""
        )

        # Run build
        build_gallery(settings_path)

        # Verify no banner directory created
        banner_dir = output_dir / "images" / "banner"
        assert not banner_dir.exists(), (
            "Banner directory should not exist without banner configured"
        )

        # Verify HTML uses simple header
        html_path = output_dir / "index.html"
        html_content = html_path.read_text()
        assert "gallery-banner" not in html_content, "Banner section should not be in HTML"
        assert "<h1>" in html_content, "Simple header h1 should be present"

    def test_build_with_title_only(self, tmp_path):
        """Test build with custom title but no banner."""
        # Setup directories
        content_dir = tmp_path / "content"
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "dist"

        content_dir.mkdir()
        config_dir.mkdir()

        # Create sample image
        (content_dir / "img1.jpg").write_bytes(b"fake jpg data")

        # Create YAML
        yaml_path = config_dir / "gallery.yaml"
        yaml_path.write_text(
            """
categories:
  - Test Category
images: []
"""
        )

        # Create settings with title only
        settings_path = config_dir / "settings.yaml"
        settings_path.write_text(
            f"""
content_dir: {content_dir}
gallery_yaml_path: {yaml_path}
default_category: Uncategorized
output_dir: {output_dir}
gallery_title: My Custom Gallery
"""
        )

        # Run build
        build_gallery(settings_path)

        # Verify HTML contains custom title in simple header
        html_path = output_dir / "index.html"
        html_content = html_path.read_text()
        assert "My Custom Gallery" in html_content, "Custom title should be in HTML"
        assert "gallery-banner" not in html_content, "No banner section without banner image"

    def test_banner_asset_copying(self, tmp_path):
        """Test that banner image is correctly copied to output directory."""
        # Setup directories
        content_dir = tmp_path / "content"
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "dist"

        content_dir.mkdir()
        config_dir.mkdir()

        # Create sample image
        (content_dir / "img1.jpg").write_bytes(b"fake jpg data")

        # Create banner with specific content
        banner = content_dir / "my-banner.jpg"
        banner_content = b"unique banner content 12345"
        banner.write_bytes(banner_content)

        # Create YAML
        yaml_path = config_dir / "gallery.yaml"
        yaml_path.write_text(
            """
categories:
  - Test Category
images: []
"""
        )

        # Create settings
        settings_path = config_dir / "settings.yaml"
        settings_path.write_text(
            f"""
content_dir: {content_dir}
gallery_yaml_path: {yaml_path}
default_category: Uncategorized
output_dir: {output_dir}
banner_image: my-banner.jpg
gallery_title: Test
"""
        )

        # Run build
        build_gallery(settings_path)

        # Verify banner copied with correct content
        banner_output = output_dir / "images" / "banner" / "my-banner.jpg"
        assert banner_output.exists()
        assert banner_output.read_bytes() == banner_content, "Banner content should match source"

    def test_banner_with_absolute_path(self, tmp_path):
        """Test banner with absolute path instead of relative."""
        # Setup directories
        content_dir = tmp_path / "content"
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "dist"
        banner_dir = tmp_path / "banners"

        content_dir.mkdir()
        config_dir.mkdir()
        banner_dir.mkdir()

        # Create sample image
        (content_dir / "img1.jpg").write_bytes(b"fake jpg data")

        # Create banner in different location
        banner = banner_dir / "external-banner.jpg"
        banner.write_bytes(b"external banner content")

        # Create YAML
        yaml_path = config_dir / "gallery.yaml"
        yaml_path.write_text(
            """
categories:
  - Test Category
images: []
"""
        )

        # Create settings with absolute banner path
        settings_path = config_dir / "settings.yaml"
        settings_path.write_text(
            f"""
content_dir: {content_dir}
gallery_yaml_path: {yaml_path}
default_category: Uncategorized
output_dir: {output_dir}
banner_image: {banner}
gallery_title: Test
"""
        )

        # Run build
        build_gallery(settings_path)

        # Verify banner copied
        banner_output = output_dir / "images" / "banner" / "external-banner.jpg"
        assert banner_output.exists()


class TestBannerValidation:
    """Tests for banner validation and error handling."""

    def test_invalid_banner_path_raises_error(self, tmp_path):
        """Test that invalid banner path raises validation error."""
        # Setup directories
        content_dir = tmp_path / "content"
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "dist"

        content_dir.mkdir()
        config_dir.mkdir()

        # Create YAML
        yaml_path = config_dir / "gallery.yaml"
        yaml_path.write_text(
            """
categories:
  - Test Category
images: []
"""
        )

        # Create settings with non-existent banner
        settings_path = config_dir / "settings.yaml"
        settings_path.write_text(
            f"""
content_dir: {content_dir}
gallery_yaml_path: {yaml_path}
default_category: Uncategorized
output_dir: {output_dir}
banner_image: nonexistent-banner.jpg
"""
        )

        # Should raise validation error
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="Banner image not found"):
            load_config(settings_path)

    def test_empty_title_raises_error(self, tmp_path):
        """Test that empty gallery title raises validation error."""
        # Setup directories
        content_dir = tmp_path / "content"
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "dist"

        content_dir.mkdir()
        config_dir.mkdir()

        # Create YAML
        yaml_path = config_dir / "gallery.yaml"
        yaml_path.write_text(
            """
categories:
  - Test Category
images: []
"""
        )

        # Create settings with empty title
        settings_path = config_dir / "settings.yaml"
        settings_path.write_text(
            f"""
content_dir: {content_dir}
gallery_yaml_path: {yaml_path}
default_category: Uncategorized
output_dir: {output_dir}
gallery_title: "   "
"""
        )

        # Should raise validation error
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="cannot be empty"):
            load_config(settings_path)
