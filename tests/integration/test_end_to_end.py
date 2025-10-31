"""End-to-end integration tests."""

from pathlib import Path

from generator.build_html import load_config, scan_and_sync


class TestEndToEnd:
    """Integration tests for full build process."""

    def test_build_with_sample_images(self, tmp_path):
        """Test complete build process with sample images."""
        # Setup directories
        content_dir = tmp_path / "content"
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "dist"

        content_dir.mkdir()
        config_dir.mkdir()

        # Create sample images
        (content_dir / "img1.jpg").write_bytes(b"fake jpg data")
        (content_dir / "img2.png").write_bytes(b"fake png data")

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
enable_thumbnails: false
output_dir: {output_dir}
"""
        )

        # Run build (currently only scan_and_sync works)
        config = load_config(settings_path)
        categories, images = scan_and_sync(config)

        # Verify results
        assert len(images) == 2
        assert len(categories) >= 1

        # Verify stubs were created
        yaml_content = yaml_path.read_text()
        assert "img1.jpg" in yaml_content
        assert "img2.png" in yaml_content

    def test_stub_generation_preserves_order(self, tmp_path):
        """Test that stub generation preserves existing category order."""
        content_dir = tmp_path / "content"
        config_dir = tmp_path / "config"

        content_dir.mkdir()
        config_dir.mkdir()

        # Create images
        (content_dir / "existing.jpg").write_bytes(b"data")
        (content_dir / "new.jpg").write_bytes(b"data")

        # Create YAML with existing image
        yaml_path = config_dir / "gallery.yaml"
        yaml_path.write_text(
            """
categories:
  - Category A
  - Category B
images:
  - filename: existing.jpg
    category: Category A
    title: Existing
    description: ""
"""
        )

        # Create settings
        settings_path = config_dir / "settings.yaml"
        settings_path.write_text(
            f"""
content_dir: {content_dir}
gallery_yaml_path: {yaml_path}
default_category: Uncategorized
enable_thumbnails: false
"""
        )

        # Run scan and sync
        config = load_config(settings_path)
        categories, images = scan_and_sync(config)

        # Verify category order preserved
        assert categories[0] == "Category A"
        assert categories[1] == "Category B"

        # Verify both images present
        assert len(images) == 2
        filenames = {img.filename for img in images}
        assert "existing.jpg" in filenames
        assert "new.jpg" in filenames
