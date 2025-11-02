"""Constants used throughout the gallery generator."""

from pathlib import Path

# Image file extensions
IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".gif", ".webp"})

# Cache version for build cache compatibility
CACHE_VERSION = "1.0"

# Default configuration values
DEFAULT_THUMBNAIL_MAX_DIMENSION = 800
DEFAULT_WEBP_QUALITY = 85
DEFAULT_JPEG_QUALITY = 90
DEFAULT_LOCALE = "en"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_OUTPUT_DIR = Path("dist")
DEFAULT_THUMBNAIL_DIR = Path("build/images/thumbnails")
DEFAULT_CACHE_FILE = Path("build/.build-cache.json")

# EXIF orientation tag
EXIF_ORIENTATION_TAG = 274

# Thumbnail hash length
CONTENT_HASH_LENGTH = 8

# PIL resampling filters
RESAMPLING_FILTERS = frozenset({"LANCZOS", "BICUBIC", "BILINEAR", "NEAREST"})
