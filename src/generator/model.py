"""Data models for the image gallery generator."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Image:
    """Represents a single image in the gallery."""

    filename: str
    file_path: Path
    category: str
    width: Optional[int] = None
    height: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None

    def __post_init__(self):
        """Validate image data."""
        if not self.filename:
            raise ValueError("filename cannot be empty")
        if not self.category:
            raise ValueError("category cannot be empty")

    @property
    def alt_text(self) -> str:
        """Generate appropriate alt text for the image."""
        if self.title:
            return self.title
        # Fallback to filename without extension
        return Path(self.filename).stem.replace("_", " ").replace("-", " ").title()


@dataclass
class Category:
    """Represents a category grouping images."""

    name: str
    order_index: int
    images: list[Image] = field(default_factory=list)

    def __post_init__(self):
        """Validate category data."""
        if not self.name:
            raise ValueError("name cannot be empty")
        if self.order_index < 0:
            raise ValueError("order_index must be non-negative")

    def add_image(self, image: Image) -> None:
        """Add an image to this category."""
        if image.category != self.name:
            raise ValueError(f"Image category '{image.category}' does not match '{self.name}'")
        self.images.append(image)


@dataclass
class GalleryConfig:
    """Configuration for the gallery generator."""

    content_dir: Path
    gallery_yaml_path: Path
    default_category: str
    enable_thumbnails: bool = False
    output_dir: Path = Path("dist")

    def __post_init__(self):
        """Validate configuration."""
        self.content_dir = Path(self.content_dir)
        self.gallery_yaml_path = Path(self.gallery_yaml_path)
        self.output_dir = Path(self.output_dir)

        if not self.content_dir.exists():
            raise ValueError(f"content_dir does not exist: {self.content_dir}")
        if not self.gallery_yaml_path.exists():
            raise ValueError(f"gallery_yaml_path does not exist: {self.gallery_yaml_path}")
        if not self.default_category:
            raise ValueError("default_category cannot be empty")


@dataclass
class YamlEntry:
    """Represents a single entry in the gallery YAML file."""

    filename: str
    category: str
    title: str = ""
    description: str = ""

    def __post_init__(self):
        """Validate YAML entry."""
        if not self.filename:
            raise ValueError("filename cannot be empty")
        if not self.category:
            raise ValueError("category cannot be empty")

    def to_dict(self) -> dict:
        """Convert to dictionary for YAML serialization."""
        return {
            "filename": self.filename,
            "category": self.category,
            "title": self.title,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "YamlEntry":
        """Create from dictionary loaded from YAML."""
        return cls(
            filename=data["filename"],
            category=data["category"],
            title=data.get("title", ""),
            description=data.get("description", ""),
        )
