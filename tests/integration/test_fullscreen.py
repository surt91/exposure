"""Integration tests for fullscreen functionality."""

from pathlib import Path

import pytest

from generator.build_html import build_gallery


class TestFullscreenIntegration:
    """Test fullscreen modal integration."""

    @pytest.fixture
    def test_gallery(self, tmp_path):
        """Create a test gallery with images."""
        content_dir = tmp_path / "content"
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "dist"

        content_dir.mkdir()
        config_dir.mkdir()

        # Create test images
        for i in range(3):
            img_file = content_dir / f"test_{i}.jpg"
            img_file.write_bytes(b"\xFF\xD8\xFF\xE0" + b"\x00" * 100)

        # Create gallery.yaml with metadata
        gallery_yaml = config_dir / "gallery.yaml"
        yaml_content = """categories:
  - TestCat
images:
  - filename: test_0.jpg
    category: TestCat
    title: "Test Image 0"
    description: "Description for image 0"
  - filename: test_1.jpg
    category: TestCat
    title: "Test Image 1"
    description: "Description for image 1"
  - filename: test_2.jpg
    category: TestCat
    title: ""
    description: ""
"""
        gallery_yaml.write_text(yaml_content)

        # Create settings.yaml
        settings_yaml = config_dir / "settings.yaml"
        settings_yaml.write_text(
            f"content_dir: {content_dir}\n"
            f"gallery_yaml_path: {gallery_yaml}\n"
            f"default_category: Uncategorized\n"
            f"enable_thumbnails: false\n"
            f"output_dir: {output_dir}\n"
        )

        return {
            "settings_yaml": settings_yaml,
            "output_dir": output_dir,
        }

    def test_fullscreen_modal_present(self, test_gallery):
        """Test that fullscreen modal HTML is present."""
        build_gallery(test_gallery["settings_yaml"])

        index_html = test_gallery["output_dir"] / "index.html"
        html_content = index_html.read_text()

        # Check modal structure
        assert 'id="fullscreen-modal"' in html_content
        assert 'role="dialog"' in html_content
        assert 'aria-modal="true"' in html_content
        assert 'class="modal-close"' in html_content
        assert 'modal-prev' in html_content
        assert 'modal-next' in html_content

    def test_fullscreen_data_attributes(self, test_gallery):
        """Test that images have correct data attributes for fullscreen."""
        build_gallery(test_gallery["settings_yaml"])

        index_html = test_gallery["output_dir"] / "index.html"
        html_content = index_html.read_text()

        # Check data attributes
        assert 'data-category="TestCat"' in html_content
        assert 'data-filename="test_0.jpg"' in html_content
        assert 'data-title="Test Image 0"' in html_content
        assert 'data-description="Description for image 0"' in html_content

    def test_fullscreen_js_included(self, test_gallery):
        """Test that fullscreen JS is included in the bundle."""
        build_gallery(test_gallery["settings_yaml"])

        # Find JS file
        js_files = list(test_gallery["output_dir"].glob("gallery.*.js"))
        assert len(js_files) == 1

        js_content = js_files[0].read_text()

        # Check for fullscreen controller
        assert "openFullscreen" in js_content
        assert "closeFullscreen" in js_content
        assert "handleKeyPress" in js_content
        assert "trapFocus" in js_content

    def test_fullscreen_css_included(self, test_gallery):
        """Test that fullscreen CSS is included in the bundle."""
        build_gallery(test_gallery["settings_yaml"])

        # Find CSS file
        css_files = list(test_gallery["output_dir"].glob("gallery.*.css"))
        assert len(css_files) == 1

        css_content = css_files[0].read_text()

        # Check for modal styles
        assert ".modal" in css_content
        assert ".modal-close" in css_content
        assert ".modal-content" in css_content
        assert ".modal-nav" in css_content

    def test_aria_attributes(self, test_gallery):
        """Test ARIA attributes for accessibility."""
        build_gallery(test_gallery["settings_yaml"])

        index_html = test_gallery["output_dir"] / "index.html"
        html_content = index_html.read_text()

        # Check ARIA attributes on modal
        assert 'aria-modal="true"' in html_content
        assert 'aria-hidden="true"' in html_content
        assert 'aria-label="Close fullscreen view"' in html_content
        assert 'aria-label="Previous image"' in html_content
        assert 'aria-label="Next image"' in html_content

    def test_keyboard_navigation_support(self, test_gallery):
        """Test that keyboard navigation is supported in JS."""
        build_gallery(test_gallery["settings_yaml"])

        js_files = list(test_gallery["output_dir"].glob("gallery.*.js"))
        js_content = js_files[0].read_text()

        # Check for keyboard event handlers
        assert "Escape" in js_content
        assert "ArrowLeft" in js_content
        assert "ArrowRight" in js_content
        assert "Tab" in js_content

    def test_focus_management(self, test_gallery):
        """Test focus management code is present."""
        build_gallery(test_gallery["settings_yaml"])

        js_files = list(test_gallery["output_dir"].glob("gallery.*.js"))
        js_content = js_files[0].read_text()

        # Check focus management
        assert "previousFocus" in js_content
        assert "focus()" in js_content
        assert "FocusManager" in js_content or "saveFocus" in js_content

    def test_metadata_display_elements(self, test_gallery):
        """Test that metadata display elements are present."""
        build_gallery(test_gallery["settings_yaml"])

        index_html = test_gallery["output_dir"] / "index.html"
        html_content = index_html.read_text()

        # Check metadata elements in modal
        assert 'id="modal-image"' in html_content
        assert 'id="modal-title"' in html_content
        assert 'id="modal-description"' in html_content
        assert 'id="modal-category"' in html_content


class TestFullscreenLatency:
    """Test fullscreen open/close performance."""

    def test_fullscreen_performance_markers(self, tmp_path):
        """Test that performance measurement code is included."""
        content_dir = tmp_path / "content"
        config_dir = tmp_path / "config"
        output_dir = tmp_path / "dist"

        content_dir.mkdir()
        config_dir.mkdir()

        # Create minimal test
        img_file = content_dir / "test.jpg"
        img_file.write_bytes(b"\xFF\xD8\xFF\xE0" + b"\x00" * 50)

        gallery_yaml = config_dir / "gallery.yaml"
        gallery_yaml.write_text("categories: [Test]\nimages:\n  - filename: test.jpg\n    category: Test\n")

        settings_yaml = config_dir / "settings.yaml"
        settings_yaml.write_text(
            f"content_dir: {content_dir}\n"
            f"gallery_yaml_path: {gallery_yaml}\n"
            f"default_category: Test\n"
            f"output_dir: {output_dir}\n"
        )

        build_gallery(settings_yaml)

        js_files = list(output_dir.glob("gallery.*.js"))
        js_content = js_files[0].read_text()

        # Check for performance monitoring
        assert "performance" in js_content
        assert "startTime" in js_content or "performance.now()" in js_content
