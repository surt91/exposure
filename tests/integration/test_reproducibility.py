"""Test build reproducibility - identical inputs produce identical outputs."""

import subprocess

import pytest


@pytest.fixture
def test_workspace(tmp_path):
    """Create a test workspace with sample images and config."""
    # Create directories
    content_dir = tmp_path / "content"
    config_dir = tmp_path / "config"
    build1_dir = tmp_path / "build1"
    build2_dir = tmp_path / "build2"

    content_dir.mkdir()
    config_dir.mkdir()

    # Create test images
    for i in range(3):
        (content_dir / f"test{i}.jpg").write_bytes(b"fake image data " + str(i).encode())

    # Create gallery.yaml
    gallery_yaml = config_dir / "gallery.yaml"
    gallery_yaml.write_text(
        """
categories:
  - TestCategory

images:
  - filename: test0.jpg
    category: TestCategory
    title: "Test Image 0"
    description: "First test"
  - filename: test1.jpg
    category: TestCategory
    title: "Test Image 1"
    description: "Second test"
  - filename: test2.jpg
    category: TestCategory
    title: ""
    description: ""
"""
    )

    # Create settings.yaml for build1
    settings1 = config_dir / "settings1.yaml"
    settings1.write_text(
        f"""
content_dir: {content_dir}
gallery_yaml_path: {gallery_yaml}
default_category: TestCategory
enable_thumbnails: false
output_dir: {build1_dir}
"""
    )

    # Create settings.yaml for build2
    settings2 = config_dir / "settings2.yaml"
    settings2.write_text(
        f"""
content_dir: {content_dir}
gallery_yaml_path: {gallery_yaml}
default_category: TestCategory
enable_thumbnails: false
output_dir: {build2_dir}
"""
    )

    return {
        "content_dir": content_dir,
        "config_dir": config_dir,
        "settings1": settings1,
        "settings2": settings2,
        "build1_dir": build1_dir,
        "build2_dir": build2_dir,
    }


class TestReproducibility:
    """Test that builds are reproducible."""

    def test_identical_builds_produce_identical_output(self, test_workspace):
        """Test that two builds with same input produce identical files."""
        # Run build 1
        result1 = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "src.generator.build_html",
                str(test_workspace["settings1"]),
            ],
            capture_output=True,
            text=True,
        )
        assert result1.returncode == 0, f"Build 1 failed: {result1.stderr}"

        # Run build 2
        result2 = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "src.generator.build_html",
                str(test_workspace["settings2"]),
            ],
            capture_output=True,
            text=True,
        )
        assert result2.returncode == 0, f"Build 2 failed: {result2.stderr}"

        # Compare outputs
        build1_dir = test_workspace["build1_dir"]
        build2_dir = test_workspace["build2_dir"]

        # Get all files from both builds
        build1_files = sorted(
            [f.relative_to(build1_dir) for f in build1_dir.rglob("*") if f.is_file()]
        )
        build2_files = sorted(
            [f.relative_to(build2_dir) for f in build2_dir.rglob("*") if f.is_file()]
        )

        # Should have same file structure
        assert build1_files == build2_files, "Build outputs have different file structures"

        # Compare file contents
        for rel_path in build1_files:
            file1 = build1_dir / rel_path
            file2 = build2_dir / rel_path

            # Read as bytes to handle binary files
            content1 = file1.read_bytes()
            content2 = file2.read_bytes()

            assert content1 == content2, (
                f"File contents differ: {rel_path}\n"
                f"Build 1 size: {len(content1)}\n"
                f"Build 2 size: {len(content2)}"
            )

    def test_hash_stability(self, test_workspace):
        """Test that hashed filenames are consistent across builds."""
        # Run first build
        subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "src.generator.build_html",
                str(test_workspace["settings1"]),
            ],
            capture_output=True,
            check=True,
        )

        build1_dir = test_workspace["build1_dir"]

        # Collect hashed filenames
        css_files1 = list(build1_dir.glob("gallery.*.css"))
        js_files1 = list(build1_dir.glob("gallery.*.js"))

        assert len(css_files1) == 1, "Should have exactly one CSS file"
        assert len(js_files1) == 1, "Should have exactly one JS file"

        css_hash1 = css_files1[0].stem.split(".")[-1]
        js_hash1 = js_files1[0].stem.split(".")[-1]

        # Run second build
        subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "src.generator.build_html",
                str(test_workspace["settings2"]),
            ],
            capture_output=True,
            check=True,
        )

        build2_dir = test_workspace["build2_dir"]

        # Collect hashed filenames
        css_files2 = list(build2_dir.glob("gallery.*.css"))
        js_files2 = list(build2_dir.glob("gallery.*.js"))

        assert len(css_files2) == 1, "Should have exactly one CSS file"
        assert len(js_files2) == 1, "Should have exactly one JS file"

        css_hash2 = css_files2[0].stem.split(".")[-1]
        js_hash2 = js_files2[0].stem.split(".")[-1]

        # Hashes should be identical
        assert css_hash1 == css_hash2, f"CSS hash mismatch: {css_hash1} != {css_hash2}"
        assert js_hash1 == js_hash2, f"JS hash mismatch: {js_hash1} != {js_hash2}"

    def test_image_hash_stability(self, test_workspace):
        """Test that image filenames with hashes are consistent."""
        # Run first build
        subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "src.generator.build_html",
                str(test_workspace["settings1"]),
            ],
            capture_output=True,
            check=True,
        )

        build1_dir = test_workspace["build1_dir"]
        images1 = sorted([f.name for f in (build1_dir / "images").glob("*")])

        # Run second build
        subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "src.generator.build_html",
                str(test_workspace["settings2"]),
            ],
            capture_output=True,
            check=True,
        )

        build2_dir = test_workspace["build2_dir"]
        images2 = sorted([f.name for f in (build2_dir / "images").glob("*")])

        # Image filenames should be identical
        assert images1 == images2, f"Image filenames differ: {images1} != {images2}"

    def test_html_references_stable(self, test_workspace):
        """Test that HTML references to hashed files are stable."""
        # Run first build
        subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "src.generator.build_html",
                str(test_workspace["settings1"]),
            ],
            capture_output=True,
            check=True,
        )

        build1_html = (test_workspace["build1_dir"] / "index.html").read_text()

        # Run second build
        subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "src.generator.build_html",
                str(test_workspace["settings2"]),
            ],
            capture_output=True,
            check=True,
        )

        build2_html = (test_workspace["build2_dir"] / "index.html").read_text()

        # HTML should be byte-for-byte identical
        assert build1_html == build2_html, "HTML content differs between builds"
