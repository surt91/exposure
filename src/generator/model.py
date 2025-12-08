"""Data models for the image gallery generator."""

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

from .constants import (
    DEFAULT_CACHE_FILE,
    DEFAULT_JPEG_QUALITY,
    DEFAULT_LOCALE,
    DEFAULT_LOG_LEVEL,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_THUMBNAIL_DIR,
    DEFAULT_THUMBNAIL_MAX_DIMENSION,
    DEFAULT_WEBP_QUALITY,
    RESAMPLING_FILTERS,
)


class Image(BaseModel):
    """Represents a single image in the gallery."""

    filename: str = Field(min_length=1)
    file_path: Path
    category: str = Field(min_length=1)
    width: Optional[int] = None
    height: Optional[int] = None
    title: str = ""
    description: str = ""
    thumbnail: Optional["ThumbnailImage"] = None

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

    @property
    def image_url(self) -> str:
        """Get relative URL to original image for HTML templates."""
        return f"images/originals/{self.filename}"

    @property
    def thumbnail_url(self) -> str:
        """Get relative URL to thumbnail WebP for HTML templates."""
        if self.thumbnail:
            return f"images/thumbnails/{self.thumbnail.webp_path.name}"
        return self.image_url  # Fallback to original

    @property
    def thumbnail_fallback_url(self) -> str:
        """Get relative URL to JPEG fallback thumbnail."""
        if self.thumbnail:
            return f"images/thumbnails/{self.thumbnail.jpeg_path.name}"
        return self.image_url  # Fallback to original


class ThumbnailConfig(BaseModel):
    """
    Configuration for thumbnail generation.

    All fields have sensible defaults based on research findings.
    Configuration loaded from YAML or environment variables.
    """

    max_dimension: int = Field(
        default=DEFAULT_THUMBNAIL_MAX_DIMENSION,
        ge=100,
        le=4000,
        description="Maximum width or height for thumbnails in pixels",
    )

    webp_quality: int = Field(
        default=DEFAULT_WEBP_QUALITY,
        ge=1,
        le=100,
        description="WebP compression quality (1-100, higher = better quality)",
    )

    jpeg_quality: int = Field(
        default=DEFAULT_JPEG_QUALITY,
        ge=1,
        le=100,
        description="JPEG fallback compression quality (1-100, higher = better quality)",
    )

    output_dir: Path = Field(
        default=DEFAULT_THUMBNAIL_DIR,
        description="Directory for generated thumbnail files",
    )

    enable_cache: bool = Field(
        default=True, description="Enable incremental build caching to skip unchanged images"
    )

    cache_file: Path = Field(
        default=DEFAULT_CACHE_FILE, description="Path to build cache JSON file"
    )

    resampling_filter: str = Field(
        default="LANCZOS",
        description="PIL resampling filter for thumbnail generation",
    )

    @field_validator("resampling_filter")
    @classmethod
    def validate_resampling_filter(cls, v: str) -> str:
        """Validate resampling filter is supported."""
        if v not in RESAMPLING_FILTERS:
            raise ValueError(f"Invalid resampling filter. Must be one of: {RESAMPLING_FILTERS}")
        return v

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("output_dir", "cache_file", mode="before")
    @classmethod
    def convert_to_path(cls, v):
        """Convert string paths to Path objects."""
        return Path(v) if not isinstance(v, Path) else v


class ThumbnailImage(BaseModel):
    """Represents a generated thumbnail with both WebP and JPEG fallback formats."""

    source_filename: str = Field(min_length=1)
    source_path: Path
    webp_path: Path
    jpeg_path: Path
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    webp_size_bytes: int = Field(gt=0)
    jpeg_size_bytes: int = Field(gt=0)
    source_size_bytes: int = Field(gt=0)
    content_hash: str = Field(min_length=8, max_length=8)
    generated_at: datetime
    metadata_stripped: bool = Field(
        default=True, description="Whether sensitive metadata was successfully removed"
    )
    metadata_strip_warning: Optional[str] = Field(
        default=None, description="Error message if metadata stripping failed"
    )
    blur_placeholder: Optional["BlurPlaceholder"] = Field(
        default=None, description="Optional blur placeholder for progressive loading"
    )

    model_config = {"arbitrary_types_allowed": True}

    @property
    def size_reduction_percent(self) -> float:
        """Calculate percentage reduction in file size (WebP vs original)."""
        return ((self.source_size_bytes - self.webp_size_bytes) / self.source_size_bytes) * 100

    @property
    def webp_savings_percent(self) -> float:
        """Calculate percentage savings of WebP vs JPEG fallback."""
        return ((self.jpeg_size_bytes - self.webp_size_bytes) / self.jpeg_size_bytes) * 100

    @property
    def aspect_ratio(self) -> float:
        """Calculate thumbnail aspect ratio."""
        return self.width / self.height


class BlurPlaceholder(BaseModel):
    """Ultra-low-resolution blur placeholder for instant image preview.

    Generated during build process from source images. Encoded as base64
    data URL for inline embedding in HTML (zero network requests).
    """

    data_url: str = Field(
        ...,
        description="Base64-encoded JPEG data URL (format: 'data:image/jpeg;base64,...')",
        min_length=50,
        max_length=2000,
    )

    size_bytes: int = Field(
        ...,
        description="Size of data_url string in bytes (for budget tracking)",
        ge=0,
        le=2000,
    )

    dimensions: tuple[int, int] = Field(
        ...,
        description="Placeholder dimensions (width, height) in pixels, typically (20, 20)",
    )

    blur_radius: int = Field(
        default=10,
        description="Gaussian blur radius applied (pixels)",
        ge=5,
        le=20,
    )

    source_hash: str = Field(
        ...,
        description="SHA256 hash of source image (for cache invalidation, truncated)",
        pattern=r"^[a-f0-9]{8}$",
    )

    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of placeholder generation",
    )

    @field_validator("data_url")
    @classmethod
    def validate_data_url_format(cls, v: str) -> str:
        """Ensure data URL has correct JPEG format prefix."""
        if not v.startswith("data:image/jpeg;base64,"):
            raise ValueError("data_url must start with 'data:image/jpeg;base64,'")
        return v

    @field_validator("dimensions")
    @classmethod
    def validate_dimensions(cls, v: tuple[int, int]) -> tuple[int, int]:
        """Ensure dimensions are reasonable for blur placeholder."""
        width, height = v
        # At least one dimension must be >= 10, both must be <= 50
        # (handles extreme panoramas where one dimension might be < 10)
        if max(width, height) > 50 or min(width, height) < 5:
            raise ValueError("Dimensions must have max dimension <= 50px and min dimension >= 5px")
        return v


class BlurPlaceholderConfig(BaseModel):
    """Configuration for blur placeholder generation."""

    enabled: bool = Field(default=True, description="Enable/disable blur placeholder generation")

    target_size: int = Field(
        default=20,
        description="Target dimension (longer edge) for placeholder before blur",
        ge=10,
        le=50,
    )

    blur_radius: int = Field(
        default=10,
        description="Gaussian blur radius in pixels",
        ge=5,
        le=20,
    )

    jpeg_quality: int = Field(
        default=50,
        description="JPEG compression quality (1-100, lower = smaller file)",
        ge=1,
        le=100,
    )

    max_size_bytes: int = Field(
        default=1000,
        description="Maximum data URL size in bytes (triggers quality reduction if exceeded)",
        ge=100,
        le=2000,
    )

    @field_validator("target_size")
    @classmethod
    def validate_target_size(cls, v: int) -> int:
        """Warn if target size too large for placeholders."""
        if v > 30:
            # Log warning but allow - user may want larger placeholders
            pass
        return v


class ImageMetadata(BaseModel):
    """Extended metadata extracted from source images during thumbnail generation."""

    filename: str = Field(min_length=1)
    file_path: Path
    format: str
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    file_size_bytes: int = Field(gt=0)
    color_mode: str
    has_transparency: bool
    exif_orientation: Optional[int] = Field(default=None, ge=1, le=8)
    is_animated: bool = False
    frame_count: int = Field(default=1, ge=1)
    dpi: Optional[tuple[int, int]] = None
    blur_placeholder: Optional[BlurPlaceholder] = Field(
        default=None, description="Optional blur placeholder for progressive loading"
    )

    model_config = {"arbitrary_types_allowed": True}


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
    thumbnail_config: ThumbnailConfig = Field(
        default_factory=ThumbnailConfig, description="Thumbnail generation configuration"
    )
    blur_placeholder_config: BlurPlaceholderConfig = Field(
        default_factory=BlurPlaceholderConfig,
        description="Blur placeholder generation configuration for progressive loading",
    )
    output_dir: Path = Field(
        default=DEFAULT_OUTPUT_DIR,
        description="Output directory for generated gallery files",
        examples=["dist/", "build/", "public/"],
    )
    locale: str = Field(
        default=DEFAULT_LOCALE,
        description="Locale for UI strings (en=English, de=German)",
        examples=["en", "de"],
    )
    log_level: str = Field(
        default=DEFAULT_LOG_LEVEL,
        description="Logging level (DEBUG, INFO, WARNING, ERROR)",
        examples=["INFO", "DEBUG", "WARNING"],
    )
    banner_image: Optional[Path] = Field(
        default=None,
        description=(
            "Path to banner image displayed at top of gallery (relative to content_dir or absolute)"
        ),
        examples=["banner.jpg", "/path/to/banner.jpg"],
    )
    gallery_title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Gallery title displayed prominently in banner or header",
        examples=["My 3D Printing Gallery", "Nature Photography"],
    )
    gallery_subtitle: Optional[str] = Field(
        default=None,
        description="Gallery subtitle displayed below title (requires gallery_title)",
        examples=["Showcasing my latest creations", "A journey through landscapes"],
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

    @field_validator("banner_image", mode="before")
    @classmethod
    def validate_banner_image(cls, v, info):
        """Validate banner image path exists if provided."""
        if v is None:
            return None

        path = Path(v) if not isinstance(v, Path) else v

        # Check absolute path
        if path.is_absolute():
            if not path.exists():
                raise ValueError(f"Banner image not found: {path}")
            if not path.is_file():
                raise ValueError(f"Banner image path is not a file: {path}")
            return path

        # Try relative to content_dir
        content_dir = info.data.get("content_dir")
        if content_dir:
            full_path = Path(content_dir) / path
            if full_path.exists() and full_path.is_file():
                return full_path

        raise ValueError(
            f"Banner image not found: {v}. Provide absolute path or path relative to content_dir."
        )

    @field_validator("gallery_title", mode="before")
    @classmethod
    def validate_gallery_title(cls, v):
        """Validate gallery title if provided."""
        if v is None:
            return None

        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("Gallery title cannot be empty or whitespace-only")
            if len(v) > 200:
                raise ValueError("Gallery title must be 200 characters or less")

        return v

    @field_validator("gallery_subtitle", mode="before")
    @classmethod
    def validate_gallery_subtitle(cls, v):
        """Validate gallery subtitle if provided."""
        if v is None:
            return None

        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None  # Treat empty as None
            if len(v) > 300:
                raise ValueError("Gallery subtitle must be 300 characters or less")

        return v

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
