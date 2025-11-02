"""Utility functions for the gallery generator."""

import hashlib
from pathlib import Path

from .constants import CONTENT_HASH_LENGTH


def hash_file(file_path: Path) -> str:
    """
    Calculate SHA256 hash of a file.

    Args:
        file_path: Path to file to hash

    Returns:
        Hex digest of the file hash (first CONTENT_HASH_LENGTH characters)

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()[:CONTENT_HASH_LENGTH]


def hash_content(content: str) -> str:
    """
    Calculate SHA256 hash of string content.

    Args:
        content: String content to hash

    Returns:
        Hex digest of the content hash (first CONTENT_HASH_LENGTH characters)
    """
    sha256 = hashlib.sha256()
    sha256.update(content.encode("utf-8"))
    return sha256.hexdigest()[:CONTENT_HASH_LENGTH]


def hash_bytes(data: bytes) -> str:
    """
    Calculate SHA256 hash of bytes.

    Args:
        data: Binary data to hash

    Returns:
        Hex digest of the hash (first CONTENT_HASH_LENGTH characters)
    """
    sha256 = hashlib.sha256(data)
    return sha256.hexdigest()[:CONTENT_HASH_LENGTH]


def validate_directory_exists(path: Path, name: str = "Directory") -> None:
    """
    Validate that a directory exists.

    Args:
        path: Path to validate
        name: Descriptive name for error messages

    Raises:
        ValueError: If path doesn't exist or isn't a directory
    """
    if not path.exists():
        raise ValueError(f"{name} does not exist: {path}")
    if not path.is_dir():
        raise ValueError(f"{name} is not a directory: {path}")


def validate_file_exists(path: Path, name: str = "File") -> None:
    """
    Validate that a file exists.

    Args:
        path: Path to validate
        name: Descriptive name for error messages

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not path.exists():
        raise FileNotFoundError(f"{name} not found: {path}")
    if not path.is_file():
        raise ValueError(f"{name} is not a file: {path}")


def ensure_directory(path: Path, parents: bool = True) -> None:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Path to directory
        parents: Create parent directories if needed

    Raises:
        OSError: If directory cannot be created
    """
    path.mkdir(parents=parents, exist_ok=True)
