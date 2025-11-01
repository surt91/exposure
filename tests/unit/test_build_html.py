"""Tests for HTML build functionality."""

import pytest

from src.generator.build_html import generate_gallery_html, organize_by_category
from src.generator.model import Category, GalleryConfig, Image


class TestOrganizeByCategory:
    """Tests for organize_by_category function."""

    def test_organize_images_by_category(self, tmp_path):
        """Test organizing images into categories."""
        # Create test images
        img1 = Image(
            filename="img1.jpg",
            file_path=tmp_path / "img1.jpg",
            category="Landscapes",
        )
        img2 = Image(
            filename="img2.jpg",
            file_path=tmp_path / "img2.jpg",
            category="Portraits",
        )
        img3 = Image(
            filename="img3.jpg",
            file_path=tmp_path / "img3.jpg",
            category="Landscapes",
        )

        category_names = ["Landscapes", "Portraits", "Other"]
        images = [img1, img2, img3]

        categories = organize_by_category(category_names, images)

        # Should have 2 categories (Other is empty and filtered)
        assert len(categories) == 2

        # Check order is preserved
        assert categories[0].name == "Landscapes"
        assert categories[0].order_index == 0
        assert len(categories[0].images) == 2

        assert categories[1].name == "Portraits"
        assert categories[1].order_index == 1
        assert len(categories[1].images) == 1

    def test_category_ordering(self, tmp_path):
        """Test that categories maintain YAML order."""
        img1 = Image(
            filename="img1.jpg",
            file_path=tmp_path / "img1.jpg",
            category="Z Category",
        )
        img2 = Image(
            filename="img2.jpg",
            file_path=tmp_path / "img2.jpg",
            category="A Category",
        )

        # Z should come before A based on list order, not alphabetical
        category_names = ["Z Category", "A Category"]
        images = [img1, img2]

        categories = organize_by_category(category_names, images)

        assert categories[0].name == "Z Category"
        assert categories[0].order_index == 0
        assert categories[1].name == "A Category"
        assert categories[1].order_index == 1

    def test_empty_categories_filtered(self, tmp_path):
        """Test that empty categories are filtered out."""
        img1 = Image(
            filename="img1.jpg",
            file_path=tmp_path / "img1.jpg",
            category="HasImages",
        )

        category_names = ["Empty1", "HasImages", "Empty2"]
        images = [img1]

        categories = organize_by_category(category_names, images)

        assert len(categories) == 1
        assert categories[0].name == "HasImages"

    def test_unknown_category_warning(self, tmp_path, caplog):
        """Test handling of images with unknown categories."""
        img1 = Image(
            filename="img1.jpg",
            file_path=tmp_path / "img1.jpg",
            category="UnknownCategory",
        )

        category_names = ["KnownCategory"]
        images = [img1]

        organize_by_category(category_names, images)

        # Should handle gracefully and warn
        assert "Unknown category" in caplog.text
        assert "UnknownCategory" in caplog.text


class TestGenerateGalleryHTML:
    """Tests for HTML generation."""

    @pytest.fixture
    def sample_config(self, tmp_path):
        """Create a test configuration."""
        content_dir = tmp_path / "content"
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "dist"

        content_dir.mkdir()
        config_dir.mkdir()
        output_dir.mkdir()

        gallery_yaml = config_dir / "gallery.yaml"
        gallery_yaml.write_text("categories: []\nimages: []")

        return GalleryConfig(
            content_dir=content_dir,
            gallery_yaml_path=gallery_yaml,
            default_category="Uncategorized",
            output_dir=output_dir,
        )

    @pytest.fixture
    def sample_images(self, tmp_path):
        """Create sample test images."""
        img_files = []
        for i in range(3):
            img_file = tmp_path / f"test{i}.jpg"
            img_file.write_text(f"fake image {i}")
            img_files.append(img_file)
        return img_files

    def test_generate_html_structure(self, sample_config, sample_images):
        """Test that generated HTML has correct structure."""
        images = [
            Image(
                filename=f.name,
                file_path=f,
                category="Test Category",
                title=f"Image {i}",
            )
            for i, f in enumerate(sample_images)
        ]

        categories = [Category(name="Test Category", order_index=0, images=images)]

        html = generate_gallery_html(categories, sample_config)

        # Check basic structure
        assert "<!DOCTYPE html>" in html
        assert '<html lang="en">' in html
        assert '<main class="gallery">' in html
        assert '<section class="category-section">' in html
        assert "Test Category" in html

    def test_generate_html_category_sections(self, sample_config, sample_images):
        """Test category sections are generated correctly."""
        cat1_images = [
            Image(
                filename=sample_images[0].name,
                file_path=sample_images[0],
                category="Category A",
            )
        ]
        cat2_images = [
            Image(
                filename=sample_images[1].name,
                file_path=sample_images[1],
                category="Category B",
            )
        ]

        categories = [
            Category(name="Category A", order_index=0, images=cat1_images),
            Category(name="Category B", order_index=1, images=cat2_images),
        ]

        html = generate_gallery_html(categories, sample_config)

        # Categories should appear in order
        assert html.index("Category A") < html.index("Category B")
        assert html.count('<section class="category-section">') == 2

    def test_generate_html_image_attributes(self, sample_config, sample_images):
        """Test image elements have correct attributes."""
        images = [
            Image(
                filename=sample_images[0].name,
                file_path=sample_images[0],
                category="Test",
                title="Test Image",
            )
        ]

        categories = [Category(name="Test", order_index=0, images=images)]

        html = generate_gallery_html(categories, sample_config)

        # Check image attributes
        assert 'loading="lazy"' in html
        assert 'alt="Test Image"' in html
        assert 'data-category="Test"' in html
        assert f'data-filename="{sample_images[0].name}"' in html

    def test_generate_html_with_caption(self, sample_config, sample_images):
        """Test images with titles get caption overlays."""
        images = [
            Image(
                filename=sample_images[0].name,
                file_path=sample_images[0],
                category="Test",
                title="My Caption",
            )
        ]

        categories = [Category(name="Test", order_index=0, images=images)]

        html = generate_gallery_html(categories, sample_config)

        assert '<div class="image-caption">My Caption</div>' in html

    def test_generate_html_assets_created(self, sample_config, sample_images):
        """Test that CSS and JS assets are created with hashing."""
        images = [
            Image(
                filename=sample_images[0].name,
                file_path=sample_images[0],
                category="Test",
            )
        ]

        categories = [Category(name="Test", order_index=0, images=images)]

        html = generate_gallery_html(categories, sample_config)

        # Check assets directory exists
        assert sample_config.output_dir.exists()

        # Check CSS and JS files were created with hashes
        css_files = list(sample_config.output_dir.glob("gallery.*.css"))
        js_files = list(sample_config.output_dir.glob("gallery.*.js"))

        assert len(css_files) == 1
        assert len(js_files) == 1

        # Check HTML references hashed files
        assert css_files[0].name in html
        assert js_files[0].name in html

    def test_generate_html_images_copied(self, sample_config, sample_images):
        """Test that images are copied to output directory."""
        images = [
            Image(
                filename=f.name,
                file_path=f,
                category="Test",
            )
            for f in sample_images
        ]

        categories = [Category(name="Test", order_index=0, images=images)]

        generate_gallery_html(categories, sample_config)

        # Check images directory exists
        images_dir = sample_config.output_dir / "images"
        assert images_dir.exists()

        # Check images were copied with hashing
        copied_images = list(images_dir.glob("*.jpg"))
        assert len(copied_images) == len(sample_images)
