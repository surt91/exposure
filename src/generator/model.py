"""Data models for the image gallery generator."""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class Image(BaseModel):
    """Represents a single image in the gallery."""

    filename: str = Field(min_length=1)
    file_path: Path
    category: str = Field(min_length=1)
    width: Optional[int] = None
    height: Optional[int] = None
    title: str = ""
    description: str = ""

    model_config = {"arbitrary_types_allowed": True}

    @property
    def alt_text(self) -> str:
        """Generate appropriate alt text for the image."""
        if self.title:
            return self.title
        # Fallback to filename without extension
        return Path(self.filename).stem.replace("_", " ").replace("-", " ").title()


class Category(BaseModel):
    """Represents a category grouping images."""

    name: str = Field(min_length=1)
    order_index: int = Field(ge=0)
    images: list[Image] = Field(default_factory=list)

    def add_image(self, image: Image) -> None:
        """Add an image to this category."""
        if image.category != self.name:
            raise ValueError(f"Image category '{image.category}' does not match '{self.name}'")
        self.images.append(image)


class GalleryConfig(BaseModel):
    """Configuration for the gallery generator."""

    content_dir: Path
    gallery_yaml_path: Path
    default_category: str = Field(min_length=1)
    enable_thumbnails: bool = False
    output_dir: Path = Path("dist")
    locale: str = "en"
    log_level: str = "INFO"

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("content_dir", "gallery_yaml_path", "output_dir", mode="before")
    @classmethod
    def convert_to_path(cls, v):
        """Convert string paths to Path objects."""
        return Path(v) if not isinstance(v, Path) else v

    @model_validator(mode="after")
    def validate_paths(self):
        """Validate that required paths exist."""
        if not self.content_dir.exists():
            raise ValueError(f"content_dir does not exist: {self.content_dir}")
        if not self.gallery_yaml_path.exists():
            raise ValueError(f"gallery_yaml_path does not exist: {self.gallery_yaml_path}")
        return self


class YamlEntry(BaseModel):
    """Represents a single entry in the gallery YAML file."""

    filename: str = Field(min_length=1)
    category: str = Field(min_length=1)
    title: str = ""
    description: str = ""
