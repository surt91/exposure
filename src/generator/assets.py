"""Asset hashing and copying utilities."""

import logging
import shutil
from pathlib import Path

from .utils import hash_content, hash_file

logger = logging.getLogger(__name__)


def copy_with_hash(
    src_path: Path, dest_dir: Path, preserve_name: bool = False, strip_metadata: bool = False
) -> Path:
    """
    Copy file to destination with hash in filename, optionally stripping metadata.

    If the destination file already exists with the correct hash, skip copying
    for improved incremental build performance.

    Args:
        src_path: Source file path
        dest_dir: Destination directory
        preserve_name: If True, use original name without hash
        strip_metadata: If True, strip sensitive metadata from image files

    Returns:
        Path to the copied file with hashed name

    Raises:
        FileNotFoundError: If source file doesn't exist
    """
    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {src_path}")

    dest_dir.mkdir(parents=True, exist_ok=True)

    if preserve_name:
        dest_path = dest_dir / src_path.name
        # Check if file exists and matches source mtime
        if dest_path.exists() and dest_path.stat().st_mtime >= src_path.stat().st_mtime:
            logger.debug(f"Skipping copy of {src_path.name} (destination up to date)")
            return dest_path
    else:
        file_hash = hash_file(src_path)
        stem = src_path.stem
        ext = src_path.suffix
        hashed_name = f"{stem}.{file_hash}{ext}"
        dest_path = dest_dir / hashed_name

        # If destination with matching hash already exists, skip copy
        if dest_path.exists():
            logger.debug(f"Skipping copy of {src_path.name} (hash match: {file_hash[:8]}...)")
            return dest_path

    # For image files, strip metadata if requested
    if strip_metadata and src_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        try:
            from .metadata_filter import strip_and_save

            success = strip_and_save(src_path, dest_path)
            if not success:
                # Fallback to regular copy if stripping fails
                logger.warning(
                    f"⚠ WARNING: Metadata stripping failed for {src_path.name}, "
                    f"falling back to regular copy"
                )
                shutil.copy2(src_path, dest_path)
        except Exception as e:
            # Fallback to regular copy on any error
            logger.warning(
                f"⚠ WARNING: Metadata stripping failed for {src_path.name}: {e}, "
                f"falling back to regular copy"
            )
            shutil.copy2(src_path, dest_path)
    else:
        shutil.copy2(src_path, dest_path)

    return dest_path


def get_hashed_filename(filename: str, content: str) -> str:
    """
    Generate hashed filename for generated content.

    Args:
        filename: Original filename (e.g., "app.css")
        content: Content to hash

    Returns:
        Hashed filename (e.g., "app.a1b2c3d4.css")
    """
    content_hash = hash_content(content)
    path = Path(filename)
    stem = path.stem
    ext = path.suffix
    return f"{stem}.{content_hash}{ext}"


def _remove_old_hashed_files(base_filename: str, dest_dir: Path, keep_file: Path) -> None:
    """
    Remove old hashed versions of a file, keeping only the current one.

    Args:
        base_filename: Base filename without hash (e.g., "gallery.css")
        dest_dir: Directory containing the files
        keep_file: Path to the current file to keep

    Examples:
        If base_filename is "gallery.css" and keep_file is "gallery.abc123.css",
        this will delete files like "gallery.xyz789.css" but keep "gallery.abc123.css".
    """
    path = Path(base_filename)
    stem = path.stem
    ext = path.suffix

    # Pattern: stem.*.ext (e.g., gallery.*.css)
    pattern = f"{stem}.*{ext}"

    for file_path in dest_dir.glob(pattern):
        # Skip if it's the file we want to keep
        if file_path == keep_file:
            continue

        # Check if it matches our hash pattern (stem + 8 hex chars + extension)
        # This ensures we only delete our hashed files, not user files
        if file_path.stem.startswith(f"{stem}.") and file_path.suffix == ext:
            try:
                file_path.unlink()
                logger.debug(f"Removed old hashed file: {file_path.name}")
            except Exception as e:
                logger.warning(f"Failed to remove old file {file_path.name}: {e}")


def write_with_hash(content: str, filename: str, dest_dir: Path) -> Path:
    """
    Write content to file with hash in filename, removing old hashed versions.

    Args:
        content: Content to write
        filename: Base filename
        dest_dir: Destination directory

    Returns:
        Path to the written file
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    hashed_name = get_hashed_filename(filename, content)
    dest_path = dest_dir / hashed_name
    dest_path.write_text(content, encoding="utf-8")

    # Clean up old hashed versions
    _remove_old_hashed_files(filename, dest_dir, dest_path)

    return dest_path
