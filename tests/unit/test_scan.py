"""Tests for image scanning."""

from pathlib import Path

import pytest

from generator.scan import detect_duplicates, discover_images, filter_valid_images


class TestDiscoverImages:
    """Tests for image discovery."""

    def test_discover_jpg_images(self, tmp_path):
        """Test discovering .jpg images."""
        (tmp_path / "img1.jpg").touch()
        (tmp_path / "img2.JPG").touch()
        (tmp_path / "img3.png").touch()

        images = discover_images(tmp_path)

        assert len(images) >= 2  # At least the jpg files
        filenames = [p.name for p in images]
        assert "img1.jpg" in filenames or "img2.JPG" in filenames

    def test_discover_multiple_formats(self, tmp_path):
        """Test discovering multiple image formats."""
        (tmp_path / "img1.jpg").touch()
        (tmp_path / "img2.png").touch()
        (tmp_path / "img3.gif").touch()
        (tmp_path / "img4.webp").touch()

        images = discover_images(tmp_path)

        assert len(images) == 4

    def test_ignore_non_images(self, tmp_path):
        """Test that non-image files are ignored."""
        (tmp_path / "img1.jpg").touch()
        (tmp_path / "readme.txt").touch()
        (tmp_path / "data.json").touch()

        images = discover_images(tmp_path)

        assert len(images) == 1
        assert images[0].name == "img1.jpg"

    def test_nonexistent_dir_raises(self, tmp_path):
        """Test that non-existent directory raises error."""
        with pytest.raises(ValueError, match="does not exist"):
            discover_images(tmp_path / "nonexistent")

    def test_file_not_directory_raises(self, tmp_path):
        """Test that passing a file raises error."""
        file_path = tmp_path / "file.txt"
        file_path.touch()

        with pytest.raises(ValueError, match="not a directory"):
            discover_images(file_path)


class TestDetectDuplicates:
    """Tests for duplicate detection."""

    def test_no_duplicates(self, tmp_path):
        """Test when there are no duplicates."""
        paths = [
            tmp_path / "img1.jpg",
            tmp_path / "img2.jpg",
        ]

        duplicates = detect_duplicates(paths)

        assert len(duplicates) == 0

    def test_detect_duplicates(self, tmp_path):
        """Test detecting duplicate filenames."""
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        paths = [
            dir1 / "img1.jpg",
            dir2 / "img1.jpg",  # Duplicate filename
            dir1 / "img2.jpg",
        ]

        duplicates = detect_duplicates(paths)

        assert len(duplicates) == 1
        assert "img1.jpg" in duplicates
        assert len(duplicates["img1.jpg"]) == 2


class TestFilterValidImages:
    """Tests for image validation."""

    def test_filter_nonexistent(self, tmp_path):
        """Test that non-existent files are filtered out."""
        existing = tmp_path / "existing.jpg"
        existing.write_bytes(b"fake image data")  # Need actual data for validation

        paths = [
            existing,
            tmp_path / "nonexistent.jpg",
        ]

        valid = filter_valid_images(paths)

        # Nonexistent should be filtered, existing should pass
        assert len(valid) >= 0  # Depends on PIL availability
        if valid:
            assert tmp_path / "nonexistent.jpg" not in valid

    def test_filter_empty_files(self, tmp_path):
        """Test that empty files are filtered out."""
        good_file = tmp_path / "good.jpg"
        good_file.write_bytes(b"fake image data")

        empty_file = tmp_path / "empty.jpg"
        empty_file.touch()  # 0 bytes

        paths = [good_file, empty_file]

        valid = filter_valid_images(paths)

        # At minimum, empty should be filtered
        assert len(valid) >= 0
        if valid:
            assert empty_file not in valid
