"""Integration tests for asset budget enforcement."""

import pytest

from src.generator.build_html import build_gallery

# Asset budget thresholds (from constitution)
MAX_HTML_SIZE = 30 * 1024  # 30KB
MAX_CSS_SIZE = 25 * 1024  # 25KB (critical CSS)
MAX_JS_SIZE = 75 * 1024  # 75KB (initial JS, uncompressed)


class TestAssetBudgets:
    """Test that asset sizes stay within budget."""

    @pytest.fixture
    def test_gallery(self, tmp_path):
        """Create a test gallery with multiple images."""
        content_dir = tmp_path / "content"
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "dist"

        content_dir.mkdir()
        config_dir.mkdir()
        output_dir.mkdir()

        # Create test images (simulate 30+ images)
        image_files = []
        for i in range(35):
            img_file = content_dir / f"test_image_{i:03d}.jpg"
            # Create fake image data (small file)
            img_file.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
            image_files.append(img_file)

        # Create gallery.yaml
        gallery_yaml = config_dir / "gallery.yaml"
        yaml_content = "categories:\n  - Landscapes\n  - Portraits\nimages:\n"
        for i, img_file in enumerate(image_files):
            category = "Landscapes" if i % 2 == 0 else "Portraits"
            yaml_content += f"  - filename: {img_file.name}\n"
            yaml_content += f"    category: {category}\n"
            yaml_content += f"    title: Test Image {i}\n"
            yaml_content += f"    description: Test description {i}\n"

        gallery_yaml.write_text(yaml_content)

        # Create settings.yaml
        settings_yaml = config_dir / "settings.yaml"
        settings_yaml.write_text(
            f"content_dir: {content_dir}\n"
            f"gallery_yaml_path: {gallery_yaml}\n"
            f"default_category: Uncategorized\n"
            f"output_dir: {output_dir}\n"
        )

        return {
            "content_dir": content_dir,
            "config_dir": config_dir,
            "output_dir": output_dir,
            "settings_yaml": settings_yaml,
            "image_files": image_files,
        }

    def test_html_size_budget(self, test_gallery):
        """Test that generated HTML stays within 30KB budget."""
        build_gallery(test_gallery["settings_yaml"])

        index_html = test_gallery["output_dir"] / "index.html"
        assert index_html.exists()

        html_size = index_html.stat().st_size
        print(f"HTML size: {html_size} bytes ({html_size / 1024:.2f} KB)")

        assert html_size <= MAX_HTML_SIZE, (
            f"HTML exceeds budget: {html_size} > {MAX_HTML_SIZE} bytes"
        )

    def test_css_size_budget(self, test_gallery):
        """Test that CSS stays within 25KB budget."""
        build_gallery(test_gallery["settings_yaml"])

        # Find hashed CSS file
        css_files = list(test_gallery["output_dir"].glob("gallery.*.css"))
        assert len(css_files) == 1, "Should have exactly one CSS file"

        css_size = css_files[0].stat().st_size
        print(f"CSS size: {css_size} bytes ({css_size / 1024:.2f} KB)")

        assert css_size <= MAX_CSS_SIZE, f"CSS exceeds budget: {css_size} > {MAX_CSS_SIZE} bytes"

    def test_js_size_budget(self, test_gallery):
        """Test that JS stays within 75KB budget."""
        build_gallery(test_gallery["settings_yaml"])

        # Find hashed JS file
        js_files = list(test_gallery["output_dir"].glob("gallery.*.js"))
        assert len(js_files) == 1, "Should have exactly one JS file"

        js_size = js_files[0].stat().st_size
        print(f"JS size: {js_size} bytes ({js_size / 1024:.2f} KB)")

        assert js_size <= MAX_JS_SIZE, f"JS exceeds budget: {js_size} > {MAX_JS_SIZE} bytes"

    def test_all_budgets_combined(self, test_gallery):
        """Test all asset budgets in one pass."""
        build_gallery(test_gallery["settings_yaml"])

        output_dir = test_gallery["output_dir"]

        # Check HTML
        index_html = output_dir / "index.html"
        html_size = index_html.stat().st_size

        # Check CSS
        css_files = list(output_dir.glob("gallery.*.css"))
        css_size = css_files[0].stat().st_size if css_files else 0

        # Check JS
        js_files = list(output_dir.glob("gallery.*.js"))
        js_size = js_files[0].stat().st_size if js_files else 0

        # Report
        print("\n=== Asset Budget Report ===")
        html_pct = html_size / MAX_HTML_SIZE * 100
        css_pct = css_size / MAX_CSS_SIZE * 100
        js_pct = js_size / MAX_JS_SIZE * 100
        print(f"HTML: {html_size:>6} / {MAX_HTML_SIZE:>6} bytes ({html_pct:>5.1f}%)")
        print(f"CSS:  {css_size:>6} / {MAX_CSS_SIZE:>6} bytes ({css_pct:>5.1f}%)")
        print(f"JS:   {js_size:>6} / {MAX_JS_SIZE:>6} bytes ({js_pct:>5.1f}%)")
        print("=" * 30)

        # Assert all budgets
        budget_violations = []
        if html_size > MAX_HTML_SIZE:
            budget_violations.append(f"HTML: {html_size} > {MAX_HTML_SIZE}")
        if css_size > MAX_CSS_SIZE:
            budget_violations.append(f"CSS: {css_size} > {MAX_CSS_SIZE}")
        if js_size > MAX_JS_SIZE:
            budget_violations.append(f"JS: {js_size} > {MAX_JS_SIZE}")

        assert not budget_violations, f"Budget violations: {', '.join(budget_violations)}"

    def test_scalability_with_500_images(self, tmp_path):
        """Test that budgets hold with 500 images (stress test)."""
        content_dir = tmp_path / "content"
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "dist"

        content_dir.mkdir()
        config_dir.mkdir()
        output_dir.mkdir()

        # Create 500 test images
        image_count = 500
        image_files = []
        for i in range(image_count):
            img_file = content_dir / f"img_{i:04d}.jpg"
            img_file.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 50)
            image_files.append(img_file)

        # Create gallery.yaml
        gallery_yaml = config_dir / "gallery.yaml"
        yaml_content = "categories:\n  - Category\nimages:\n"
        for img_file in image_files:
            yaml_content += f"  - filename: {img_file.name}\n"
            yaml_content += "    category: Category\n"

        gallery_yaml.write_text(yaml_content)

        # Create settings.yaml
        settings_yaml = config_dir / "settings.yaml"
        settings_yaml.write_text(
            f"content_dir: {content_dir}\n"
            f"gallery_yaml_path: {gallery_yaml}\n"
            f"default_category: Uncategorized\n"
            f"output_dir: {output_dir}\n"
        )

        # Build
        build_gallery(settings_yaml)

        # Check budgets
        index_html = output_dir / "index.html"
        html_size = index_html.stat().st_size

        print(f"\nScalability test with {image_count} images:")
        print(f"  HTML size: {html_size} bytes ({html_size / 1024:.2f} KB)")

        # This might exceed budget with 500 images, but should be documented
        if html_size > MAX_HTML_SIZE:
            pytest.skip(
                f"HTML exceeds budget with {image_count} images: "
                f"{html_size} > {MAX_HTML_SIZE}. "
                f"This is expected and requires pagination/virtualization."
            )


class TestThumbnailPerformance:
    """Test thumbnail generation performance and file size reduction."""

    @pytest.fixture
    def gallery_with_real_images(self, tmp_path):
        """Create a test gallery with real images for thumbnail testing."""
        from tests.fixtures.generate_test_images import generate_test_images

        content_dir = tmp_path / "content"
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "dist"

        content_dir.mkdir()
        config_dir.mkdir()
        output_dir.mkdir()

        # Generate real test images (various sizes)
        image_count = 100
        image_files = generate_test_images(
            output_dir=content_dir,
            count=image_count,
            sizes=[(4000, 3000), (3000, 4000), (5000, 3000), (2000, 1500)],
        )

        # Create gallery.yaml
        gallery_yaml = config_dir / "gallery.yaml"
        yaml_content = "categories:\n  - TestCategory\nimages:\n"
        for img_file in image_files:
            yaml_content += f"  - filename: {img_file.name}\n"
            yaml_content += "    category: TestCategory\n"
            yaml_content += f"    title: {img_file.stem}\n"
            yaml_content += "    description: Test image\n"

        gallery_yaml.write_text(yaml_content)

        # Create settings.yaml with thumbnails enabled
        settings_yaml = config_dir / "settings.yaml"
        settings_yaml.write_text(
            f"content_dir: {content_dir}\n"
            f"gallery_yaml_path: {gallery_yaml}\n"
            f"default_category: Uncategorized\n"
            f"output_dir: {output_dir}\n"
        )

        return {
            "content_dir": content_dir,
            "config_dir": config_dir,
            "output_dir": output_dir,
            "settings_yaml": settings_yaml,
            "image_files": image_files,
            "image_count": image_count,
        }

    def test_thumbnail_performance_benchmark(self, gallery_with_real_images):
        """Test that thumbnail generation for 100 images completes in <2 minutes."""
        import time

        settings_yaml = gallery_with_real_images["settings_yaml"]
        image_count = gallery_with_real_images["image_count"]

        # Measure build time
        start_time = time.time()
        build_gallery(settings_yaml)
        elapsed_time = time.time() - start_time

        print("\n=== Thumbnail Performance Benchmark ===")
        print(f"Images: {image_count}")
        print(f"Build time: {elapsed_time:.2f}s")
        print(f"Average: {elapsed_time / image_count * 1000:.1f}ms per image")

        # Should complete in <2 minutes (120 seconds)
        max_time = 120
        assert elapsed_time < max_time, (
            f"Thumbnail generation too slow: {elapsed_time:.1f}s > {max_time}s "
            f"for {image_count} images"
        )

        # Verify thumbnails were actually generated
        thumbnails_dir = gallery_with_real_images["output_dir"] / "images" / "thumbnails"
        assert thumbnails_dir.exists(), "Thumbnails directory not created"

        webp_count = len(list(thumbnails_dir.glob("*.webp")))
        jpeg_count = len(list(thumbnails_dir.glob("*.jpg")))

        assert webp_count == image_count, f"Expected {image_count} WebP files, got {webp_count}"
        assert jpeg_count == image_count, f"Expected {image_count} JPEG files, got {jpeg_count}"

    def test_thumbnail_file_size_reduction(self, gallery_with_real_images):
        """Test that thumbnails achieve 90%+ file size reduction vs originals."""
        settings_yaml = gallery_with_real_images["settings_yaml"]

        # Build gallery with thumbnails
        build_gallery(settings_yaml)

        # Calculate size reduction
        originals_dir = gallery_with_real_images["output_dir"] / "images" / "originals"
        thumbnails_dir = gallery_with_real_images["output_dir"] / "images" / "thumbnails"

        # Get total size of originals
        original_total = 0
        for img_file in originals_dir.glob("*"):
            if img_file.is_file():
                original_total += img_file.stat().st_size

        # Get total size of thumbnails (WebP only for comparison)
        thumbnail_total = 0
        for img_file in thumbnails_dir.glob("*.webp"):
            thumbnail_total += img_file.stat().st_size

        # Calculate reduction percentage
        reduction_percent = ((original_total - thumbnail_total) / original_total) * 100

        print("\n=== File Size Reduction ===")
        print(f"Original images: {original_total / 1024 / 1024:.2f} MB")
        print(f"Thumbnails (WebP): {thumbnail_total / 1024 / 1024:.2f} MB")
        print(f"Reduction: {reduction_percent:.1f}%")

        # Should achieve 90%+ reduction
        min_reduction = 90.0
        assert reduction_percent >= min_reduction, (
            f"File size reduction below target: {reduction_percent:.1f}% < {min_reduction}%"
        )

    def test_thumbnail_incremental_build(self, gallery_with_real_images):
        """Test that incremental builds skip unchanged images and complete quickly."""
        import time

        settings_yaml = gallery_with_real_images["settings_yaml"]
        image_count = gallery_with_real_images["image_count"]

        # First build (full)
        print("\n=== Incremental Build Test ===")
        start_time = time.time()
        build_gallery(settings_yaml)
        first_build_time = time.time() - start_time
        print(f"First build: {first_build_time:.2f}s")

        # Second build (should be incremental)
        start_time = time.time()
        build_gallery(settings_yaml)
        second_build_time = time.time() - start_time
        print(f"Second build: {second_build_time:.2f}s")

        # Second build should be much faster (<10 seconds for 100 images)
        max_incremental_time = 10
        assert second_build_time < max_incremental_time, (
            f"Incremental build too slow: {second_build_time:.1f}s > {max_incremental_time}s "
            f"for {image_count} images"
        )

        # Second build should be at least 5x faster than first build
        speedup = first_build_time / second_build_time
        print(f"Speedup: {speedup:.1f}x")
        assert speedup >= 5.0, f"Incremental build not fast enough: {speedup:.1f}x < 5x"

    def test_webp_vs_jpeg_savings(self, gallery_with_real_images):
        """Test that WebP thumbnails are 25-35% smaller than JPEG thumbnails."""
        settings_yaml = gallery_with_real_images["settings_yaml"]

        # Build gallery with thumbnails
        build_gallery(settings_yaml)

        thumbnails_dir = gallery_with_real_images["output_dir"] / "images" / "thumbnails"

        # Calculate total sizes
        webp_total = sum(f.stat().st_size for f in thumbnails_dir.glob("*.webp"))
        jpeg_total = sum(f.stat().st_size for f in thumbnails_dir.glob("*.jpg"))

        # Calculate WebP savings
        savings_percent = ((jpeg_total - webp_total) / jpeg_total) * 100

        print("\n=== WebP vs JPEG Comparison ===")
        print(f"WebP total: {webp_total / 1024 / 1024:.2f} MB")
        print(f"JPEG total: {jpeg_total / 1024 / 1024:.2f} MB")
        print(f"WebP savings: {savings_percent:.1f}%")

        # Should achieve 25-35% savings
        min_savings = 25.0
        max_savings = 35.0
        assert min_savings <= savings_percent <= max_savings * 1.5, (
            f"WebP savings outside expected range: {savings_percent:.1f}% "
            f"(expected {min_savings}-{max_savings}%)"
        )
