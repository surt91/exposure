"""Asset hashing and copying utilities."""

import hashlib
import shutil
from pathlib import Path


def hash_file(file_path: Path) -> str:
    """
    Calculate SHA256 hash of a file.

    Args:
        file_path: Path to file to hash

    Returns:
        Hex digest of the file hash (first 8 characters for brevity)

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()[:8]


def hash_content(content: str) -> str:
    """
    Calculate SHA256 hash of string content.

    Args:
        content: String content to hash

    Returns:
        Hex digest of the content hash (first 8 characters)
    """
    sha256 = hashlib.sha256()
    sha256.update(content.encode("utf-8"))
    return sha256.hexdigest()[:8]


def copy_with_hash(src_path: Path, dest_dir: Path, preserve_name: bool = False) -> Path:
    """
    Copy file to destination with hash in filename.

    Args:
        src_path: Source file path
        dest_dir: Destination directory
        preserve_name: If True, use original name without hash

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
    else:
        file_hash = hash_file(src_path)
        stem = src_path.stem
        ext = src_path.suffix
        hashed_name = f"{stem}.{file_hash}{ext}"
        dest_path = dest_dir / hashed_name

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


def write_with_hash(content: str, filename: str, dest_dir: Path) -> Path:
    """
    Write content to file with hash in filename.

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
    return dest_path
