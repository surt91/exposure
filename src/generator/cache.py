"""Build cache models for incremental thumbnail generation."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from .constants import CACHE_VERSION

if TYPE_CHECKING:
    from .model import ThumbnailImage


class CacheEntry(BaseModel):
    """Single entry in the build cache for incremental builds."""

    source_path: str
    source_mtime: float
    webp_path: str
    jpeg_path: str
    content_hash: str
    thumbnail_generated_at: datetime
    metadata_stripped: bool = Field(
        default=True, description="Whether metadata was stripped in this build"
    )
    # Cached dimensions and sizes to avoid reopening files
    width: int = Field(default=0, description="Thumbnail width in pixels")
    height: int = Field(default=0, description="Thumbnail height in pixels")
    webp_size_bytes: int = Field(default=0, description="WebP file size in bytes")
    jpeg_size_bytes: int = Field(default=0, description="JPEG file size in bytes")
    source_size_bytes: int = Field(default=0, description="Source file size in bytes")

    model_config = {"arbitrary_types_allowed": True}


class BuildCache(BaseModel):
    """Tracks processed images and their modification times for incremental builds."""

    entries: dict[str, CacheEntry] = Field(default_factory=dict)
    cache_version: str = Field(default=CACHE_VERSION)
    last_updated: datetime = Field(default_factory=datetime.now)

    model_config = {"arbitrary_types_allowed": True}

    def should_regenerate(self, source_path: Path) -> bool:
        """Check if thumbnail needs regeneration based on mtime."""
        entry = self.entries.get(str(source_path))
        if entry is None:
            return True
        current_mtime = source_path.stat().st_mtime
        return current_mtime > entry.source_mtime

    def update_entry(self, source_path: Path, thumbnail: ThumbnailImage) -> None:
        """Update or add cache entry for processed image."""
        self.entries[str(source_path)] = CacheEntry(
            source_path=str(source_path),
            source_mtime=source_path.stat().st_mtime,
            webp_path=str(thumbnail.webp_path),
            jpeg_path=str(thumbnail.jpeg_path),
            content_hash=thumbnail.content_hash,
            thumbnail_generated_at=thumbnail.generated_at,
            metadata_stripped=thumbnail.metadata_stripped,
            width=thumbnail.width,
            height=thumbnail.height,
            webp_size_bytes=thumbnail.webp_size_bytes,
            jpeg_size_bytes=thumbnail.jpeg_size_bytes,
            source_size_bytes=thumbnail.source_size_bytes,
        )
        self.last_updated = datetime.now()
