"""End-to-end integration tests."""

from src.generator.build_html import build_gallery, load_config, scan_and_sync


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

    def test_complete_gallery_build(self, tmp_path):
        """Test complete gallery build including HTML generation."""
        content_dir = tmp_path / "content"
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "dist"

        content_dir.mkdir()
        config_dir.mkdir()

        # Create 30+ images for scrollable content test
        for i in range(35):
            img_file = content_dir / f"image_{i:03d}.jpg"
            img_file.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        # Create YAML
        yaml_path = config_dir / "gallery.yaml"
        yaml_content = "categories:\n  - Landscapes\n  - Portraits\nimages:\n"
        for i in range(35):
            category = "Landscapes" if i < 20 else "Portraits"
            yaml_content += f"  - filename: image_{i:03d}.jpg\n"
            yaml_content += f"    category: {category}\n"
            yaml_content += f"    title: Image {i}\n"

        yaml_path.write_text(yaml_content)

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

        # Build gallery
        build_gallery(settings_path)

        # Verify outputs exist
        assert (output_dir / "index.html").exists()
        assert len(list(output_dir.glob("gallery.*.css"))) == 1
        assert len(list(output_dir.glob("gallery.*.js"))) == 1
        assert (output_dir / "images").exists()

        # Verify HTML structure
        html_content = (output_dir / "index.html").read_text()

        # Check for categories in order
        assert "Landscapes" in html_content
        assert "Portraits" in html_content
        assert html_content.index("Landscapes") < html_content.index("Portraits")

        # Check for multiple images (scrollable content)
        assert html_content.count('class="image-item"') == 35

        # Check for lazy loading
        assert 'loading="lazy"' in html_content

        # Check for semantic structure
        assert '<main class="gallery">' in html_content
        assert '<section class="category-section">' in html_content
        assert '<div class="image-grid">' in html_content

        # Verify images were copied
        copied_images = list((output_dir / "images").glob("*.jpg"))
        assert len(copied_images) == 35
