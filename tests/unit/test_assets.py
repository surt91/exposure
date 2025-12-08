"""Unit tests for asset hashing and copying."""

from pathlib import Path

from src.generator.assets import write_with_hash


def test_write_with_hash_creates_hashed_file(tmp_path: Path) -> None:
    """Test that write_with_hash creates a file with hash in the name."""
    content = "body { color: red; }"
    result = write_with_hash(content, "style.css", tmp_path)

    assert result.exists()
    assert result.name.startswith("style.")
    assert result.name.endswith(".css")
    assert result.name != "style.css"  # Should have hash
    assert result.read_text() == content


def test_write_with_hash_removes_old_files(tmp_path: Path) -> None:
    """Test that write_with_hash removes old hashed versions."""
    # Create first version
    content_v1 = "body { color: red; }"
    file_v1 = write_with_hash(content_v1, "style.css", tmp_path)
    assert file_v1.exists()

    # Create second version with different content
    content_v2 = "body { color: blue; }"
    file_v2 = write_with_hash(content_v2, "style.css", tmp_path)
    assert file_v2.exists()

    # Old file should be deleted
    assert not file_v1.exists()
    # New file should exist
    assert file_v2.exists()
    # Should only have one CSS file
    css_files = list(tmp_path.glob("style.*.css"))
    assert len(css_files) == 1
    assert css_files[0] == file_v2


def test_write_with_hash_preserves_current_file(tmp_path: Path) -> None:
    """Test that write_with_hash doesn't delete the file being written."""
    content = "body { color: red; }"

    # Write twice with same content
    file_v1 = write_with_hash(content, "style.css", tmp_path)
    file_v2 = write_with_hash(content, "style.css", tmp_path)

    # Both should point to same file since content is identical
    assert file_v1 == file_v2
    assert file_v1.exists()
    # Should only have one file
    css_files = list(tmp_path.glob("style.*.css"))
    assert len(css_files) == 1


def test_write_with_hash_different_base_names(tmp_path: Path) -> None:
    """Test that write_with_hash only removes files with matching base name."""
    # Create CSS file
    css_content = "body { color: red; }"
    css_file = write_with_hash(css_content, "style.css", tmp_path)

    # Create JS file
    js_content = "console.log('test');"
    js_file = write_with_hash(js_content, "app.js", tmp_path)

    # Both should exist
    assert css_file.exists()
    assert js_file.exists()

    # Update CSS
    css_content_v2 = "body { color: blue; }"
    css_file_v2 = write_with_hash(css_content_v2, "style.css", tmp_path)

    # Old CSS should be gone, new CSS should exist
    assert not css_file.exists()
    assert css_file_v2.exists()
    # JS file should still exist
    assert js_file.exists()


def test_write_with_hash_handles_multiple_extensions(tmp_path: Path) -> None:
    """Test that cleanup works for different file extensions."""
    # Create CSS files
    css_content_v1 = "body { color: red; }"
    css_file_v1 = write_with_hash(css_content_v1, "gallery.css", tmp_path)

    css_content_v2 = "body { color: blue; }"
    css_file_v2 = write_with_hash(css_content_v2, "gallery.css", tmp_path)

    # Create JS files
    js_content_v1 = "console.log('v1');"
    js_file_v1 = write_with_hash(js_content_v1, "gallery.js", tmp_path)

    js_content_v2 = "console.log('v2');"
    js_file_v2 = write_with_hash(js_content_v2, "gallery.js", tmp_path)

    # Only new versions should exist
    assert not css_file_v1.exists()
    assert css_file_v2.exists()
    assert not js_file_v1.exists()
    assert js_file_v2.exists()

    # Should have exactly one CSS and one JS
    css_files = list(tmp_path.glob("gallery.*.css"))
    js_files = list(tmp_path.glob("gallery.*.js"))
    assert len(css_files) == 1
    assert len(js_files) == 1
