"""Utility functions for the gallery generator."""

from pathlib import Path


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
