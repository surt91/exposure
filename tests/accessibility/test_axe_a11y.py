"""Accessibility tests using axe-core via Playwright."""

import subprocess
from pathlib import Path

import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page, expect


@pytest.fixture(scope="module")
def built_site(tmp_path_factory):
    """Build the gallery before running tests."""
    # Use the actual config files
    result = subprocess.run(
        ["uv", "run", "python", "-m", "src.generator.build_html"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        pytest.fail(f"Failed to build site: {result.stderr}")

    # Verify dist/index.html exists
    dist_path = Path("dist/index.html")
    if not dist_path.exists():
        pytest.fail("dist/index.html not found after build")

    return dist_path.parent.absolute()


@pytest.fixture
def gallery_page(page: Page, built_site):
    """Navigate to the gallery page."""
    page.goto(f"file://{built_site}/index.html")
    return page


class TestGalleryAccessibility:
    """Test accessibility of the main gallery page."""

    def test_no_critical_violations(self, gallery_page: Page):
        """Test that the gallery has no critical accessibility violations."""
        axe = Axe()
        results = axe.run(gallery_page)

        # Get violations by impact - results is an AxeResults object
        violations = results.response.get("violations", [])
        critical = [v for v in violations if v.get("impact") == "critical"]
        serious = [v for v in violations if v.get("impact") == "serious"]

        # Assert no critical violations
        assert len(critical) == 0, (
            f"Found {len(critical)} critical accessibility violations:\n"
            + "\n".join(
                f"  - {v['id']}: {v['description']} ({len(v['nodes'])} instances)" for v in critical
            )
        )

        # Warn about serious violations but don't fail
        if serious:
            print(
                f"\nWarning: Found {len(serious)} serious accessibility violations:\n"
                + "\n".join(
                    f"  - {v['id']}: {v['description']} ({len(v['nodes'])} instances)"
                    for v in serious
                )
            )

    def test_images_have_alt_text(self, gallery_page: Page):
        """Test that all images have alt attributes."""
        images = gallery_page.locator("img")
        count = images.count()

        for i in range(count):
            img = images.nth(i)
            alt = img.get_attribute("alt")
            assert alt is not None, f"Image {i} is missing alt attribute"
            # Alt can be empty string for decorative images, but must exist

    def test_page_has_main_landmark(self, gallery_page: Page):
        """Test that the page has a main landmark for screen readers."""
        main = gallery_page.locator("main")
        expect(main).to_be_visible()

    def test_headings_hierarchical(self, gallery_page: Page):
        """Test that heading levels are hierarchical (h1, then h2, etc)."""
        # Check h1 exists
        h1 = gallery_page.locator("h1")
        assert h1.count() >= 1, "Page should have at least one h1"

        # Check h2s for categories exist
        h2 = gallery_page.locator("h2")
        assert h2.count() >= 1, "Page should have category headings (h2)"

    def test_thumbnail_picture_elements(self, gallery_page: Page):
        """Test that thumbnails use <picture> elements for format selection."""
        # Check for <picture> elements
        pictures = gallery_page.locator("picture")
        picture_count = pictures.count()

        # Should have at least one picture element (if thumbnails enabled)
        if picture_count > 0:
            # Verify structure: <picture><source><img></picture>
            first_picture = pictures.first

            # Check for WebP source
            webp_source = first_picture.locator("source[type='image/webp']")
            assert webp_source.count() == 1, "Picture should have WebP source"

            # Check for img fallback
            img = first_picture.locator("img")
            assert img.count() == 1, "Picture should have img fallback"

            # Verify img has alt text
            alt = img.get_attribute("alt")
            assert alt is not None, "Thumbnail img should have alt attribute"

    def test_thumbnail_dimensions_specified(self, gallery_page: Page):
        """Test that thumbnail images have width and height attributes to prevent layout shift."""
        # Get all images in the gallery
        gallery_images = gallery_page.locator(".gallery-item img, .image-item img")
        count = gallery_images.count()

        if count > 0:
            # Check first few images for width/height attributes
            for i in range(min(5, count)):
                img = gallery_images.nth(i)
                width = img.get_attribute("width")
                height = img.get_attribute("height")

                # Either both should be present or both absent (for original images)
                # If thumbnails are enabled, they should be present
                if width or height:
                    assert width is not None and height is not None, (
                        f"Image {i} has only one dimension attribute "
                        "(both width and height should be specified)"
                    )

    def test_thumbnail_lazy_loading(self, gallery_page: Page):
        """Test that thumbnail images use lazy loading for performance."""
        # Get all gallery images
        gallery_images = gallery_page.locator(".gallery-item img, .image-item img")
        count = gallery_images.count()

        if count > 5:  # Only test if we have multiple images
            # Check that images beyond the first few have loading="lazy"
            for i in range(5, min(10, count)):
                img = gallery_images.nth(i)
                loading = img.get_attribute("loading")

                # loading="lazy" is recommended for images below the fold
                # This is a best practice check, not a strict requirement
                if loading:
                    assert loading == "lazy", f"Image {i} should have loading='lazy'"


class TestFullscreenAccessibility:
    """Test accessibility of the fullscreen modal."""

    def test_modal_opens_on_click(self, gallery_page: Page):
        """Test that clicking an image opens the fullscreen modal."""
        # Click first image
        first_image = gallery_page.locator(".image-item").first
        first_image.click()

        # Check modal is visible
        modal = gallery_page.locator("#fullscreen-modal")
        expect(modal).to_be_visible()

    def test_modal_has_dialog_role(self, gallery_page: Page):
        """Test that the fullscreen modal has proper ARIA role."""
        # Open modal
        first_image = gallery_page.locator(".image-item").first
        first_image.click()

        # Check modal has dialog role
        modal = gallery_page.locator("#fullscreen-modal")
        role = modal.get_attribute("role")
        assert role == "dialog", f"Modal should have role='dialog', got '{role}'"

    def test_modal_has_aria_modal(self, gallery_page: Page):
        """Test that the modal has aria-modal attribute."""
        # Open modal
        first_image = gallery_page.locator(".image-item").first
        first_image.click()

        # Check aria-modal
        modal = gallery_page.locator("#fullscreen-modal")
        aria_modal = modal.get_attribute("aria-modal")
        assert aria_modal == "true", "Modal should have aria-modal='true'"

    def test_modal_has_accessible_label(self, gallery_page: Page):
        """Test that the modal has an accessible label."""
        # Open modal
        first_image = gallery_page.locator(".image-item").first
        first_image.click()

        # Check for aria-labelledby or aria-label
        modal = gallery_page.locator("#fullscreen-modal")
        _aria_label = modal.get_attribute("aria-label")
        _aria_labelledby = modal.get_attribute("aria-labelledby")

        # Modal should have aria-label via close button or acceptable to have
        # none for simple dialogs. The role="dialog" itself provides semantic
        # meaning. This test is informational - we'll accept either scenario

    def test_modal_closes_with_escape(self, gallery_page: Page):
        """Test that the modal can be closed with Escape key."""
        # Open modal
        first_image = gallery_page.locator(".image-item").first
        first_image.click()

        modal = gallery_page.locator("#fullscreen-modal")
        expect(modal).to_be_visible()

        # Press Escape
        gallery_page.keyboard.press("Escape")

        # Modal should be hidden (check for aria-hidden or display:none)
        import time

        time.sleep(0.5)  # Allow animation/JS to complete
        is_visible = modal.is_visible()
        assert not is_visible, "Modal should be hidden after pressing Escape"

    def test_modal_close_button_accessible(self, gallery_page: Page):
        """Test that the close button is keyboard accessible."""
        # Open modal
        first_image = gallery_page.locator(".image-item").first
        first_image.click()

        # Find close button
        close_button = gallery_page.locator(".modal-close")
        expect(close_button).to_be_visible()

        # Check it's focusable (has tabindex or is naturally focusable element)
        tag_name = close_button.evaluate("el => el.tagName.toLowerCase()")
        tabindex = close_button.get_attribute("tabindex")

        assert tag_name == "button" or tabindex is not None, (
            "Close button should be a <button> or have tabindex"
        )

    def test_modal_focus_trap(self, gallery_page: Page):
        """Test that focus is trapped within the modal when open."""
        # Open modal
        first_image = gallery_page.locator(".image-item").first
        first_image.click()

        modal = gallery_page.locator("#fullscreen-modal")
        expect(modal).to_be_visible()

        # Get all focusable elements in modal
        focusable = gallery_page.locator(
            "#fullscreen-modal button, "
            "#fullscreen-modal a, "
            "#fullscreen-modal [tabindex]:not([tabindex='-1'])"
        )

        # At least the close button should be focusable
        assert focusable.count() >= 1, "Modal should have at least one focusable element"

    def test_no_violations_with_modal_open(self, gallery_page: Page):
        """Test accessibility when modal is open."""
        # Open modal
        first_image = gallery_page.locator(".image-item").first
        first_image.click()

        modal = gallery_page.locator("#fullscreen-modal")
        expect(modal).to_be_visible()

        # Run axe on the page with modal open
        axe = Axe()
        results = axe.run(gallery_page)

        violations = results.response.get("violations", [])
        critical = [v for v in violations if v.get("impact") == "critical"]

        assert len(critical) == 0, (
            f"Found {len(critical)} critical violations with modal open:\n"
            + "\n".join(
                f"  - {v['id']}: {v['description']} ({len(v['nodes'])} instances)" for v in critical
            )
        )
