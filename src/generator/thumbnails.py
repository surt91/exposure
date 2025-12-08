"""Thumbnail generation service for image preprocessing."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from PIL import Image as PILImage
from PIL import ImageOps

from src.generator.constants import CACHE_VERSION, EXIF_ORIENTATION_TAG
from src.generator.metadata_filter import filter_metadata
from src.generator.model import ImageMetadata, ThumbnailConfig, ThumbnailImage
from src.generator.utils import ensure_directory, hash_bytes, validate_file_exists


class ThumbnailGenerator:
    """
    Service for generating optimized image thumbnails.

    Handles WebP and JPEG format generation, EXIF orientation correction,
    and incremental build caching.
    """

    def __init__(self, config: ThumbnailConfig, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize thumbnail generator with configuration.

        Args:
            config: Thumbnail generation configuration
            logger: Optional logger instance (creates default if None)

        Raises:
            ValueError: If config validation fails
            OSError: If output directory cannot be created
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)

        # Create output directory if it doesn't exist
        ensure_directory(self.config.output_dir)

        # Load build cache
        self.cache = self.load_cache()

    def _load_from_cache(self, source_path: Path) -> Optional[ThumbnailImage]:
        """
        Attempt to load thumbnail info from cache.

        Args:
            source_path: Path to source image file

        Returns:
            ThumbnailImage if cache valid and files exist, None otherwise
        """
        cache_entry = self.cache.entries.get(str(source_path))
        if not cache_entry:
            return None

        webp_path = Path(cache_entry.webp_path)
        jpeg_path = Path(cache_entry.jpeg_path)

        # Verify files exist (quick check without opening)
        if not (webp_path.exists() and jpeg_path.exists()):
            return None

        # Use cached dimensions and sizes if available (cache v2+)
        # Otherwise fall back to reading from files (for backward compatibility)
        if cache_entry.width > 0 and cache_entry.height > 0:
            # Fast path: use cached values
            thumb_width = cache_entry.width
            thumb_height = cache_entry.height
            webp_size = cache_entry.webp_size_bytes
            jpeg_size = cache_entry.jpeg_size_bytes
            source_size = cache_entry.source_size_bytes
        else:
            # Slow path: read from files (for old cache entries)
            webp_size = webp_path.stat().st_size
            jpeg_size = jpeg_path.stat().st_size
            source_size = source_path.stat().st_size

            try:
                with PILImage.open(webp_path) as thumb:
                    thumb_width = thumb.width
                    thumb_height = thumb.height
            except Exception:
                # If we can't open the thumbnail, invalidate cache
                self.logger.warning(
                    f"Cached thumbnail unreadable, regenerating: {source_path.name}"
                )
                return None

        # Return cached thumbnail info
        return ThumbnailImage(
            source_filename=source_path.name,
            source_path=source_path,
            webp_path=webp_path,
            jpeg_path=jpeg_path,
            width=thumb_width,
            height=thumb_height,
            webp_size_bytes=webp_size,
            jpeg_size_bytes=jpeg_size,
            source_size_bytes=source_size,
            content_hash=cache_entry.content_hash,
            generated_at=cache_entry.thumbnail_generated_at,
            metadata_stripped=cache_entry.metadata_stripped,
            metadata_strip_warning=None,  # Don't carry warnings from cache
        )

    def generate_thumbnail(
        self, source_path: Path, metadata: Optional[ImageMetadata] = None
    ) -> Optional[ThumbnailImage]:
        """
        Generate WebP and JPEG thumbnails for source image.

        Automatically detects if regeneration is needed based on build cache.
        Applies EXIF orientation correction. Preserves aspect ratio.

        Args:
            source_path: Path to source image file
            metadata: Optional pre-extracted metadata (extracted if None)

        Returns:
            ThumbnailImage with paths to generated files, or None if generation
            failed or was skipped (cache hit).

        Raises:
            FileNotFoundError: If source_path does not exist
            ValueError: If source_path is not a supported image format
            OSError: If thumbnail files cannot be written
        """
        validate_file_exists(source_path, "Source image")

        # Check cache if enabled
        if self.config.enable_cache and not self.cache.should_regenerate(source_path):
            cached_thumbnail = self._load_from_cache(source_path)
            if cached_thumbnail:
                self.logger.debug(f"Skipping {source_path.name} (cached, unchanged)")
                return cached_thumbnail

        try:
            # Extract metadata if not provided
            if metadata is None:
                metadata = self.extract_metadata(source_path)

            content_hash = generate_content_hash(source_path.read_bytes())

            with PILImage.open(source_path) as img:
                # Prepare image for thumbnailing
                img = self._prepare_image(img, metadata)

                # Generate and save thumbnails
                thumb = self._create_thumbnail(img)
                webp_path, jpeg_path, metadata_stripped, strip_warning = self._save_thumbnails(
                    thumb, source_path, content_hash
                )

                # Build result object
                thumbnail = self._build_thumbnail_result(
                    source_path,
                    webp_path,
                    jpeg_path,
                    thumb,
                    content_hash,
                    metadata,
                    metadata_stripped,
                    strip_warning,
                )

                # Update cache
                if self.config.enable_cache:
                    self.cache.update_entry(source_path, thumbnail)

                self._log_thumbnail_generation(thumbnail, metadata)
                return thumbnail

        except Exception as e:
            self.logger.warning(f"Failed to generate thumbnail for {source_path.name}: {e}")
            return None

    def _prepare_image(self, img: PILImage.Image, metadata: ImageMetadata) -> PILImage.Image:
        """
        Prepare image for thumbnail generation.

        Applies EXIF orientation and converts to RGB mode.

        Args:
            img: PIL Image to prepare
            metadata: Image metadata

        Returns:
            Prepared PIL Image
        """
        # Apply EXIF orientation
        img = apply_exif_orientation(img)

        # For animated GIFs, use first frame only
        if metadata.is_animated:
            img.seek(0)

        # Convert to RGB for JPEG compatibility
        return self._convert_to_rgb(img)

    def _convert_to_rgb(self, img: PILImage.Image) -> PILImage.Image:
        """
        Convert image to RGB mode for JPEG compatibility.

        Args:
            img: PIL Image to convert

        Returns:
            RGB PIL Image
        """
        if img.mode in ("RGBA", "LA", "P"):
            # Create white background
            rgb_img = PILImage.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            rgb_img.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
            return rgb_img
        elif img.mode not in ("RGB", "L"):
            return img.convert("RGB")
        return img

    def _create_thumbnail(self, img: PILImage.Image) -> PILImage.Image:
        """
        Create thumbnail with calculated dimensions.

        Args:
            img: Source PIL Image

        Returns:
            Thumbnail PIL Image
        """
        thumb_width, thumb_height = calculate_thumbnail_dimensions(
            img.width, img.height, self.config.max_dimension
        )
        thumb = img.copy()
        thumb.thumbnail((thumb_width, thumb_height), PILImage.Resampling.LANCZOS)
        return thumb

    def _cleanup_old_thumbnails(self, stem: str, current_hash: str) -> None:
        """
        Remove old thumbnail files for the same source image with different hashes.

        Args:
            stem: Filename stem (without extension)
            current_hash: Current content hash to preserve
        """
        # Find all thumbnails matching this stem
        old_webp_files = self.config.output_dir.glob(f"{stem}-*.webp")
        old_jpeg_files = self.config.output_dir.glob(f"{stem}-*.jpg")

        for old_file in list(old_webp_files) + list(old_jpeg_files):
            # Check if this is NOT the current hash
            if current_hash not in old_file.name:
                try:
                    old_file.unlink()
                    self.logger.debug(f"Cleaned up old thumbnail: {old_file.name}")
                except OSError as e:
                    self.logger.warning(f"Failed to remove old thumbnail {old_file.name}: {e}")

    def _save_thumbnails(
        self, thumb: PILImage.Image, source_path: Path, content_hash: str
    ) -> tuple[Path, Path, bool, Optional[str]]:
        """
        Save WebP and JPEG thumbnails to disk with metadata filtering.

        Args:
            thumb: Thumbnail PIL Image
            source_path: Path to source image
            content_hash: Content hash for filename

        Returns:
            Tuple of (webp_path, jpeg_path, metadata_stripped, strip_warning)
        """
        stem = source_path.stem
        webp_filename = f"{stem}-{content_hash}.webp"
        jpeg_filename = f"{stem}-{content_hash}.jpg"

        webp_path = self.config.output_dir / webp_filename
        jpeg_path = self.config.output_dir / jpeg_filename

        # Clean up old thumbnails with different hashes
        self._cleanup_old_thumbnails(stem, content_hash)

        # Filter metadata from source image
        cleaned_exif = filter_metadata(source_path)
        metadata_stripped = cleaned_exif is not None
        strip_warning = None

        if cleaned_exif is None:
            # Metadata filtering failed, log warning
            strip_warning = f"Metadata filtering failed for {source_path.name}"
            self.logger.warning(f"⚠ WARNING: {strip_warning}")

        # Save WebP thumbnail with cleaned EXIF
        thumb.save(
            webp_path,
            "WEBP",
            quality=self.config.webp_quality,
            method=6,  # Best compression
            exif=cleaned_exif if cleaned_exif else b"",
        )

        # Save JPEG fallback with cleaned EXIF
        thumb.save(
            jpeg_path,
            "JPEG",
            quality=self.config.jpeg_quality,
            optimize=True,
            exif=cleaned_exif if cleaned_exif else b"",
        )

        return webp_path, jpeg_path, metadata_stripped, strip_warning

    def _build_thumbnail_result(
        self,
        source_path: Path,
        webp_path: Path,
        jpeg_path: Path,
        thumb: PILImage.Image,
        content_hash: str,
        metadata: ImageMetadata,
        metadata_stripped: bool,
        strip_warning: Optional[str],
    ) -> ThumbnailImage:
        """
        Build ThumbnailImage result object.

        Args:
            source_path: Path to source image
            webp_path: Path to WebP thumbnail
            jpeg_path: Path to JPEG thumbnail
            thumb: Thumbnail PIL Image
            content_hash: Content hash
            metadata: Source image metadata
            metadata_stripped: Whether metadata was successfully stripped
            strip_warning: Error message if stripping failed

        Returns:
            ThumbnailImage object
        """
        webp_size = webp_path.stat().st_size
        jpeg_size = jpeg_path.stat().st_size

        return ThumbnailImage(
            source_filename=source_path.name,
            source_path=source_path,
            webp_path=webp_path,
            jpeg_path=jpeg_path,
            width=thumb.width,
            height=thumb.height,
            webp_size_bytes=webp_size,
            jpeg_size_bytes=jpeg_size,
            source_size_bytes=metadata.file_size_bytes,
            content_hash=content_hash,
            generated_at=datetime.now(),
            metadata_stripped=metadata_stripped,
            metadata_strip_warning=strip_warning,
        )

    def _format_size(self, bytes_count: int) -> str:
        """
        Format byte count as human-readable size string.

        Args:
            bytes_count: File size in bytes (non-negative integer)

        Returns:
            Human-readable size string with appropriate unit
        """
        if bytes_count >= 1_000_000:
            return f"{bytes_count / 1_000_000:.1f}MB"
        elif bytes_count >= 1_000:
            return f"{bytes_count / 1_000:.0f}KB"
        else:
            return f"{bytes_count}B"

    def _log_thumbnail_generation(self, thumbnail: ThumbnailImage, metadata: ImageMetadata) -> None:
        """Log thumbnail generation statistics with progress info."""
        source_size_str = self._format_size(metadata.file_size_bytes)
        thumb_size_str = self._format_size(thumbnail.webp_size_bytes)
        reduction_pct = thumbnail.size_reduction_percent

        # Log INFO-level progress message
        self.logger.info(
            f"✓ {thumbnail.source_filename} → {source_size_str} → {thumb_size_str} "
            f"({reduction_pct:.1f}% reduction)"
        )

        # Log warning if metadata stripping failed
        if thumbnail.metadata_strip_warning:
            self.logger.warning(
                f"⚠ WARNING: Metadata stripping failed for {thumbnail.source_filename}: "
                f"{thumbnail.metadata_strip_warning}"
            )

    def generate_batch(
        self,
        source_paths: list[Path],
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> tuple[list[ThumbnailImage], list[Path]]:
        """
        Generate thumbnails for multiple source images.

        Processes images sequentially with optional progress reporting.
        Continues on individual failures.

        Args:
            source_paths: List of source image paths
            progress_callback: Optional callback(current, total) for progress

        Returns:
            Tuple of (successful_thumbnails, failed_paths)
        """
        successful = []
        failed = []
        generated_count = 0
        cached_count = 0
        total = len(source_paths)

        for i, source_path in enumerate(source_paths, start=1):
            try:
                # Track initial cache state
                needs_regen = not self.config.enable_cache or self.cache.should_regenerate(
                    source_path
                )

                thumbnail = self.generate_thumbnail(source_path)
                if thumbnail:
                    successful.append(thumbnail)
                    if needs_regen:
                        generated_count += 1
                    else:
                        cached_count += 1
            except Exception as e:
                self.logger.warning(f"Failed to process {source_path.name}: {e}")
                failed.append(source_path)

            # Report progress
            if progress_callback:
                progress_callback(i, total)

        # Save cache after batch processing
        if self.config.enable_cache:
            self.save_cache()

        # Log summary
        self.logger.info(
            f"Thumbnails: {generated_count} generated, {cached_count} cached, {len(failed)} failed"
        )

        return (successful, failed)

    def load_cache(self):
        """
        Load build cache from configured cache file.

        Returns:
            BuildCache object with entries from disk, or empty cache if file
            does not exist or is invalid.
        """
        from src.generator.cache import BuildCache

        cache_file = self.config.cache_file

        if not cache_file.exists():
            self.logger.debug(f"No cache file found at {cache_file}, starting fresh")
            return BuildCache()

        try:
            cache_data = json.loads(cache_file.read_text())

            # Validate cache version
            if cache_data.get("cache_version") != CACHE_VERSION:
                self.logger.warning("Cache version mismatch, regenerating all thumbnails")
                return BuildCache()

            return BuildCache(**cache_data)
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Build cache corrupted ({e}), regenerating all thumbnails")
            return BuildCache()

    def save_cache(self) -> None:
        """
        Save current build cache to configured cache file.

        Writes cache as formatted JSON with timestamp.

        Raises:
            OSError: If cache file cannot be written
        """
        cache_file = self.config.cache_file

        # Ensure parent directory exists
        ensure_directory(cache_file.parent)

        # Update timestamp
        self.cache.last_updated = datetime.now()

        # Serialize to JSON
        cache_data = self.cache.model_dump(mode="json")

        # Write to file with formatting
        cache_file.write_text(json.dumps(cache_data, indent=2))

    def extract_metadata(self, source_path: Path) -> ImageMetadata:
        """
        Extract comprehensive metadata from image file.

        Opens image, reads dimensions, format, color mode, EXIF data, and
        animation info. Does not modify source file.

        Args:
            source_path: Path to image file

        Returns:
            ImageMetadata with all extracted fields

        Raises:
            FileNotFoundError: If source_path does not exist
            PIL.UnidentifiedImageError: If file is not a valid image
        """
        validate_file_exists(source_path, "Image file")

        with PILImage.open(source_path) as img:
            # Extract EXIF orientation if available
            exif_orientation = None
            try:
                exif = img.getexif()
                if exif:
                    exif_orientation = exif.get(EXIF_ORIENTATION_TAG)
            except Exception:
                # Ignore EXIF errors
                pass

            # Extract DPI if available
            dpi = None
            if hasattr(img, "info") and "dpi" in img.info:
                dpi = img.info["dpi"]

            # Check if animated (primarily for GIFs)
            is_animated = getattr(img, "is_animated", False)
            frame_count = getattr(img, "n_frames", 1)

            return ImageMetadata(
                filename=source_path.name,
                file_path=source_path,
                format=img.format or "UNKNOWN",
                width=img.width,
                height=img.height,
                file_size_bytes=source_path.stat().st_size,
                color_mode=img.mode,
                has_transparency="A" in img.mode or "transparency" in img.info,
                exif_orientation=exif_orientation,
                is_animated=is_animated,
                frame_count=frame_count,
                dpi=dpi,
            )


def calculate_thumbnail_dimensions(
    source_width: int, source_height: int, max_dimension: int
) -> tuple[int, int]:
    """
    Calculate thumbnail dimensions to fit within max_dimension.

    Maintains aspect ratio. If source is smaller than max_dimension,
    returns original dimensions (no upscaling).

    Args:
        source_width: Source image width in pixels
        source_height: Source image height in pixels
        max_dimension: Maximum allowed dimension (width or height)

    Returns:
        Tuple of (thumbnail_width, thumbnail_height)

    Examples:
        >>> calculate_thumbnail_dimensions(4000, 3000, 800)
        (800, 600)
        >>> calculate_thumbnail_dimensions(600, 400, 800)
        (600, 400)  # No upscaling
    """
    # No upscaling - if source is smaller, keep original dimensions
    if max(source_width, source_height) <= max_dimension:
        return (source_width, source_height)

    # Calculate scaling factor
    aspect_ratio = source_width / source_height

    if source_width >= source_height:
        # Landscape or square - width is limiting dimension
        thumb_width = max_dimension
        thumb_height = int(max_dimension / aspect_ratio)
    else:
        # Portrait - height is limiting dimension
        thumb_height = max_dimension
        thumb_width = int(max_dimension * aspect_ratio)

    return (thumb_width, thumb_height)


def generate_content_hash(image_bytes: bytes) -> str:
    """
    Generate hash from image content.

    Uses SHA-256 for reproducibility and collision resistance.

    Args:
        image_bytes: Raw image file bytes

    Returns:
        Hash string of fixed length

    Examples:
        >>> generate_content_hash(Path("photo.jpg").read_bytes())
        'a1b2c3d4'
    """
    return hash_bytes(image_bytes)


def apply_exif_orientation(image: PILImage.Image) -> PILImage.Image:
    """
    Apply EXIF orientation transformation to image.

    Handles all 8 EXIF orientation values. No-op if no EXIF data.

    Args:
        image: PIL Image object

    Returns:
        New PIL Image with orientation applied (or same image if no EXIF)
    """
    return ImageOps.exif_transpose(image) or image
