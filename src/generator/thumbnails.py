"""Thumbnail generation service for image preprocessing."""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from PIL import Image as PILImage
from PIL import ImageOps

from src.generator.constants import CACHE_VERSION, CONTENT_HASH_LENGTH, EXIF_ORIENTATION_TAG
from src.generator.model import ImageMetadata, ThumbnailConfig, ThumbnailImage
from src.generator.utils import ensure_directory, validate_file_exists


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

        # Verify files exist
        if not (webp_path.exists() and jpeg_path.exists()):
            return None

        # Get file sizes
        webp_size = webp_path.stat().st_size
        jpeg_size = jpeg_path.stat().st_size

        # Extract dimensions from WebP file
        try:
            with PILImage.open(webp_path) as thumb:
                thumb_width = thumb.width
                thumb_height = thumb.height
        except Exception:
            # If we can't open the thumbnail, invalidate cache
            self.logger.warning(f"Cached thumbnail unreadable, regenerating: {source_path.name}")
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
            source_size_bytes=source_path.stat().st_size,
            content_hash=cache_entry.content_hash,
            generated_at=cache_entry.thumbnail_generated_at,
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
            # If cache entry missing or files don't exist, fall through to regeneration

        try:
            # Extract metadata if not provided
            if metadata is None:
                metadata = self.extract_metadata(source_path)

            # Generate content hash for filename
            content_hash = generate_content_hash(source_path.read_bytes())

            # Open and process image
            with PILImage.open(source_path) as img:
                # Apply EXIF orientation
                img = apply_exif_orientation(img)

                # For animated GIFs, use first frame only
                if metadata.is_animated:
                    img.seek(0)

                # Convert RGBA to RGB for JPEG compatibility
                if img.mode in ("RGBA", "LA", "P"):
                    # Create white background
                    rgb_img = PILImage.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    rgb_img.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
                    img = rgb_img
                elif img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")

                # Calculate thumbnail dimensions
                thumb_width, thumb_height = calculate_thumbnail_dimensions(
                    img.width, img.height, self.config.max_dimension
                )

                # Create thumbnail
                thumb = img.copy()
                thumb.thumbnail((thumb_width, thumb_height), PILImage.Resampling.LANCZOS)

                # Generate output filenames
                stem = source_path.stem
                webp_filename = f"{stem}-{content_hash}.webp"
                jpeg_filename = f"{stem}-{content_hash}.jpg"

                webp_path = self.config.output_dir / webp_filename
                jpeg_path = self.config.output_dir / jpeg_filename

                # Save WebP thumbnail
                thumb.save(
                    webp_path,
                    "WEBP",
                    quality=self.config.webp_quality,
                    method=6,  # Best compression
                )

                # Save JPEG fallback
                thumb.save(jpeg_path, "JPEG", quality=self.config.jpeg_quality, optimize=True)

                # Get file sizes
                webp_size = webp_path.stat().st_size
                jpeg_size = jpeg_path.stat().st_size

                # Create ThumbnailImage
                thumbnail = ThumbnailImage(
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
                )

                # Update cache
                if self.config.enable_cache:
                    self.cache.update_entry(source_path, thumbnail)

                self.logger.debug(
                    f"Generated thumbnail for {source_path.name}: "
                    f"{metadata.file_size_bytes // 1024}KB → "
                    f"{webp_size // 1024}KB WebP, "
                    f"{jpeg_size // 1024}KB JPEG "
                    f"({thumbnail.size_reduction_percent:.1f}% reduction)"
                )

                return thumbnail

        except Exception as e:
            self.logger.warning(f"Failed to generate thumbnail for {source_path.name}: {e}")
            return None

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
        from src.generator.model import BuildCache

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
        First CONTENT_HASH_LENGTH characters of SHA-256 hex digest

    Examples:
        >>> generate_content_hash(Path("photo.jpg").read_bytes())
        'a1b2c3d4'
    """
    hash_obj = hashlib.sha256(image_bytes)
    return hash_obj.hexdigest()[:CONTENT_HASH_LENGTH]


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
