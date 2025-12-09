"""Thumbnail generation service for image preprocessing."""

import base64
import json
import logging
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Callable, Optional

from PIL import Image as PILImage
from PIL import ImageOps

from src.generator.constants import CACHE_VERSION, EXIF_ORIENTATION_TAG
from src.generator.metadata_filter import filter_metadata
from src.generator.model import (
    BlurPlaceholder,
    BlurPlaceholderConfig,
    ImageMetadata,
    ThumbnailConfig,
    ThumbnailImage,
)
from src.generator.utils import ensure_directory, hash_bytes, hash_file, validate_file_exists

logger = logging.getLogger("exposure")


class ThumbnailGenerator:
    """
    Service for generating optimized image thumbnails.

    Handles WebP and JPEG format generation, EXIF orientation correction,
    blur placeholder generation, and incremental build caching.
    """

    def __init__(
        self,
        config: ThumbnailConfig,
        blur_placeholder_config: Optional[BlurPlaceholderConfig] = None,
    ) -> None:
        """
        Initialize thumbnail generator with configuration.

        Args:
            config: Thumbnail generation configuration
            blur_placeholder_config: Optional blur placeholder configuration

        Raises:
            ValueError: If config validation fails
            OSError: If output directory cannot be created
        """
        self.config = config
        self.blur_placeholder_config = blur_placeholder_config or BlurPlaceholderConfig()

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

        # Check if cache is valid (handles blur placeholder config changes)
        current_hash = hash_file(source_path)
        if not cache_entry.is_valid(current_hash, self.blur_placeholder_config.enabled):
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
                logger.warning(f"Cached thumbnail unreadable, regenerating: {source_path.name}")
                return None

        # Load blur placeholder from cache if available, otherwise regenerate
        blur_placeholder = None
        if self.blur_placeholder_config.enabled:
            if (
                cache_entry.blur_placeholder_data_url
                and cache_entry.blur_placeholder_dimensions
                and cache_entry.blur_placeholder_size_bytes is not None
            ):
                # Fast path: reconstruct from cache
                blur_placeholder = BlurPlaceholder(
                    data_url=cache_entry.blur_placeholder_data_url,
                    size_bytes=cache_entry.blur_placeholder_size_bytes,
                    dimensions=cache_entry.blur_placeholder_dimensions,
                    blur_radius=self.blur_placeholder_config.blur_radius,
                    source_hash=cache_entry.blur_placeholder_hash or "",
                    generated_at=cache_entry.blur_placeholder_generated_at or datetime.now(),
                )
            else:
                # Slow path: cache entry from old version without blur data, regenerate
                blur_placeholder = generate_blur_placeholder(
                    source_path, self.blur_placeholder_config
                )

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
            blur_placeholder=blur_placeholder,
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
                logger.debug(f"Skipping {source_path.name} (cached, unchanged)")
                return cached_thumbnail

        try:
            # Extract metadata if not provided
            if metadata is None:
                metadata = self.extract_metadata(source_path)

            content_hash = hash_bytes(source_path.read_bytes())

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
            logger.warning(f"Failed to generate thumbnail for {source_path.name}: {e}")
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
                    logger.debug(f"Cleaned up old thumbnail: {old_file.name}")
                except OSError as e:
                    logger.warning(f"Failed to remove old thumbnail {old_file.name}: {e}")

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
            logger.warning(f"⚠ WARNING: {strip_warning}")

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
        Build ThumbnailImage result object with optional blur placeholder.

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
            ThumbnailImage object with optional blur placeholder
        """
        webp_size = webp_path.stat().st_size
        jpeg_size = jpeg_path.stat().st_size

        # Generate blur placeholder if enabled
        blur_placeholder = None
        if self.blur_placeholder_config.enabled:
            blur_placeholder = generate_blur_placeholder(source_path, self.blur_placeholder_config)

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
            blur_placeholder=blur_placeholder,
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
        logger.info(
            f"✓ {thumbnail.source_filename} → {source_size_str} → {thumb_size_str} "
            f"({reduction_pct:.1f}% reduction)"
        )

        # Log warning if metadata stripping failed
        if thumbnail.metadata_strip_warning:
            logger.warning(
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
                logger.warning(f"Failed to process {source_path.name}: {e}")
                failed.append(source_path)

            # Report progress
            if progress_callback:
                progress_callback(i, total)

        # Save cache after batch processing
        if self.config.enable_cache:
            self.save_cache()

        # Log summary
        logger.info(
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
            logger.debug(f"No cache file found at {cache_file}, starting fresh")
            return BuildCache()

        try:
            cache_data = json.loads(cache_file.read_text())

            # Validate cache version
            if cache_data.get("cache_version") != CACHE_VERSION:
                logger.warning("Cache version mismatch, regenerating all thumbnails")
                return BuildCache()

            return BuildCache(**cache_data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Build cache corrupted ({e}), regenerating all thumbnails")
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


# Note: Hash functions consolidated in utils.py
# Use hash_file() for file paths and hash_bytes() for byte data


def _optimize_data_url_size(
    img: PILImage.Image, max_size_bytes: int, initial_quality: int = 50
) -> tuple[str, int]:
    """
    Optimize JPEG data URL size by iteratively reducing quality.

    Encodes image as JPEG with progressively lower quality until
    data URL size is under max_size_bytes. Stops at quality 10.

    Args:
        img: PIL Image to encode
        max_size_bytes: Maximum allowed data URL size in bytes
        initial_quality: Starting JPEG quality (1-100)

    Returns:
        Tuple of (data_url, actual_size_bytes)

    Examples:
        >>> img = PILImage.new("RGB", (20, 20))
        >>> url, size = _optimize_data_url_size(img, 1000, 50)
        >>> size <= 1000
        True
    """
    quality = initial_quality

    while quality >= 10:
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        b64_data = base64.b64encode(buffer.getvalue()).decode("ascii")
        data_url = f"data:image/jpeg;base64,{b64_data}"

        if len(data_url) <= max_size_bytes:
            return data_url, len(data_url)

        # Reduce quality by 10 and try again
        quality -= 10

    # Return smallest possible even if over budget
    return data_url, len(data_url)


def generate_blur_placeholder(
    source_path: Path, config: BlurPlaceholderConfig
) -> Optional[BlurPlaceholder]:
    """
    Generate ultra-low-resolution blur placeholder from source image.

    Process:
    1. Open source image and apply EXIF orientation
    2. Resize to target_size (e.g., 20x20px) maintaining aspect ratio
    3. Apply Gaussian blur with specified radius
    4. Encode as JPEG with specified quality
    5. Base64 encode as data URL
    6. Optimize size if exceeds max_size_bytes

    Args:
        source_path: Path to source image file
        config: Blur placeholder configuration

    Returns:
        BlurPlaceholder with data URL and metadata, or None if generation fails

    Examples:
        >>> config = BlurPlaceholderConfig()
        >>> placeholder = generate_blur_placeholder(Path("photo.jpg"), config)
        >>> placeholder.data_url.startswith("data:image/jpeg;base64,")
        True
        >>> placeholder.size_bytes < 1000
        True
    """
    try:
        with PILImage.open(source_path) as img:
            # Apply EXIF orientation first
            img = apply_exif_orientation(img)

            # Convert to RGB (required for JPEG)
            if img.mode not in ("RGB", "L"):
                if img.mode in ("RGBA", "LA", "P"):
                    # Create white background
                    rgb_img = PILImage.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    rgb_img.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
                    img = rgb_img
                else:
                    img = img.convert("RGB")

            # Resize to target size (maintaining aspect ratio)
            img.thumbnail((config.target_size, config.target_size), PILImage.Resampling.LANCZOS)

            # NOTE: No blur applied here - CSS filter: blur() is used instead
            # This results in smaller data URLs and GPU-accelerated rendering

            # Optimize data URL size
            data_url, size_bytes = _optimize_data_url_size(
                img, config.max_size_bytes, config.jpeg_quality
            )

            # Compute source hash for cache validation
            source_hash = hash_file(source_path)

            return BlurPlaceholder(
                data_url=data_url,
                size_bytes=size_bytes,
                dimensions=(img.width, img.height),
                blur_radius=config.blur_radius,
                source_hash=source_hash,
                generated_at=datetime.now(),
            )

    except Exception as e:
        logger.warning(f"Failed to generate blur placeholder for {source_path.name}: {e}")
        return None


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
