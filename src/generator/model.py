"""Data models for the image gallery generator."""

from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


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

    @property
    def aspect_ratio(self) -> Optional[float]:
        """Calculate aspect ratio if dimensions available."""
        if self.width and self.height:
            return self.width / self.height
        return None


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


class YamlSettingsSource(PydanticBaseSettingsSource):
    """Custom settings source to load configuration from YAML file."""

    def __init__(self, settings_cls: type[BaseSettings], yaml_file: Path):
        super().__init__(settings_cls)
        self.yaml_file = yaml_file

    def get_field_value(self, field: Any, field_name: str) -> tuple[Any, str, bool]:
        """Not used - we override __call__ instead."""
        return None, field_name, False

    def __call__(self) -> dict[str, Any]:
        """Load and return settings from YAML file."""
        if not self.yaml_file.exists():
            return {}

        with open(self.yaml_file, "r") as f:
            data = yaml.safe_load(f)

        return data if data else {}


# Module-level variable to store YAML file path for settings customization
_yaml_settings_file: Path = Path("config/settings.yaml")


class GalleryConfig(BaseSettings):
    """Configuration for the gallery generator.

    Supports loading from YAML files and environment variables.
    Environment variables take precedence over YAML configuration.
    All environment variables should be prefixed with EXPOSURE_.

    Example:
        EXPOSURE_LOCALE=de  # Override locale setting
        EXPOSURE_LOG_LEVEL=DEBUG  # Override log level
    """

    content_dir: Path = Field(
        description="Directory containing image files to scan",
        examples=["content/", "/path/to/images"],
    )
    gallery_yaml_path: Path = Field(
        description="Path to YAML file with image metadata",
        examples=["config/gallery.yaml", "gallery.yaml"],
    )
    default_category: str = Field(
        min_length=1,
        description="Default category for images without explicit category assignment",
        examples=["Uncategorized", "General"],
    )
    enable_thumbnails: bool = Field(
        default=False, description="Whether to generate thumbnail images (not yet implemented)"
    )
    output_dir: Path = Field(
        default=Path("dist"),
        description="Output directory for generated gallery files",
        examples=["dist/", "build/", "public/"],
    )
    locale: str = Field(
        default="en",
        description="Locale for UI strings (en=English, de=German)",
        examples=["en", "de"],
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)",
        examples=["INFO", "DEBUG", "WARNING"],
    )

    model_config = SettingsConfigDict(
        env_prefix="EXPOSURE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        arbitrary_types_allowed=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Customize settings sources and their priority.

        Priority (highest to lowest):
        1. Environment variables (EXPOSURE_*)
        2. .env file
        3. YAML settings file
        4. Default values
        """
        yaml_settings = YamlSettingsSource(settings_cls, _yaml_settings_file)

        # Return sources in priority order (first = highest priority)
        return env_settings, dotenv_settings, yaml_settings, init_settings

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
