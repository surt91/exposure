"""
Image metadata filtering module for privacy protection.

This module provides functionality to strip sensitive metadata (GPS coordinates,
camera serial numbers, personal information, software details) from images while
preserving display-critical metadata (orientation, color profiles, timestamps).

Uses piexif library for robust EXIF manipulation.
"""

import logging
from pathlib import Path
from typing import Optional

import piexif
from PIL import Image

logger = logging.getLogger(__name__)


# EXIF tags to REMOVE (privacy-sensitive)
# Using piexif named constants instead of magic numbers

# Sensitive tags in Exif IFD
SENSITIVE_EXIF_TAGS: set[int] = {
    piexif.ExifIFD.BodySerialNumber,  # 0xA431 - Camera serial number
    piexif.ExifIFD.LensSerialNumber,  # 0xA435 - Lens serial number
    piexif.ExifIFD.ImageUniqueID,  # 0xA420 - Unique image ID
}

# Sensitive tags in 0th IFD (main image)
SENSITIVE_0TH_TAGS: set[int] = {
    piexif.ImageIFD.Artist,  # 0x013B - Creator name
    piexif.ImageIFD.Copyright,  # 0x8298 - Copyright holder
    piexif.ImageIFD.Software,  # 0x0131 - Software used
    piexif.ImageIFD.HostComputer,  # 0x013C - Computer used
    piexif.ImageIFD.XPAuthor,  # 0x9C9D - Windows XP author field
    piexif.ImageIFD.XPComment,  # 0x9C9C - Windows XP comment
    # Embedded thumbnail removal
    piexif.ImageIFD.JPEGInterchangeFormat,  # 0x0201 - Thumbnail offset
    piexif.ImageIFD.JPEGInterchangeFormatLength,  # 0x0202 - Thumbnail length
}

# Safe tags to PRESERVE in 0th IFD (display-critical)
SAFE_0TH_TAGS: set[int] = {
    piexif.ImageIFD.Orientation,  # 0x0112 - Image orientation
    piexif.ImageIFD.Make,  # 0x010F - Camera manufacturer
    piexif.ImageIFD.Model,  # 0x0110 - Camera model
    piexif.ImageIFD.DateTime,  # 0x0132 - File modification timestamp
    piexif.ImageIFD.XResolution,  # 0x011A - Horizontal resolution
    piexif.ImageIFD.YResolution,  # 0x011B - Vertical resolution
    piexif.ImageIFD.ResolutionUnit,  # 0x0128 - Resolution unit
}

# Safe tags to PRESERVE in Exif IFD
SAFE_EXIF_TAGS: set[int] = {
    piexif.ExifIFD.DateTimeOriginal,  # 0x9003 - Original capture time
    piexif.ExifIFD.DateTimeDigitized,  # 0x9004 - Digitization time
    piexif.ExifIFD.LensModel,  # 0xA434 - Lens model name
    piexif.ExifIFD.LensMake,  # 0xA433 - Lens manufacturer
    piexif.ExifIFD.FNumber,  # 0x829D - F-number (aperture)
    piexif.ExifIFD.ExposureTime,  # 0x829A - Exposure time
    piexif.ExifIFD.ISOSpeedRatings,  # 0x8827 - ISO sensitivity
    piexif.ExifIFD.FocalLength,  # 0x920A - Focal length
    piexif.ExifIFD.ColorSpace,  # 0xA001 - Color space
}


def filter_metadata(source_path: Path) -> Optional[bytes]:
    """
    Filter sensitive metadata from source image, return cleaned EXIF bytes.

    Removes GPS IFD entirely, filters sensitive tags from Exif/0th IFDs,
    preserves display-critical tags.

    Args:
        source_path: Path to source image file

    Returns:
        Cleaned EXIF data as bytes, or None if filtering failed

    Raises:
        Does not raise exceptions - all errors are caught and logged
    """
    try:
        # Load EXIF data
        exif_dict = piexif.load(str(source_path))

        # Remove GPS IFD entirely (all location data)
        exif_dict.pop("GPS", None)

        # Filter sensitive tags
        exif_dict = _remove_sensitive_tags(exif_dict)

        # Remove embedded thumbnail
        exif_dict["thumbnail"] = None

        # Dump cleaned EXIF back to bytes
        return piexif.dump(exif_dict)

    except piexif.InvalidImageDataError as e:
        logger.warning(f"⚠ WARNING: EXIF data corrupted in {source_path.name}: {e}")
        return None
    except Exception as e:
        logger.warning(f"⚠ WARNING: Metadata filtering failed for {source_path.name}: {e}")
        return None


def _remove_sensitive_tags(exif_dict: dict) -> dict:
    """
    Remove sensitive tags from EXIF dict, preserve safe tags.

    Args:
        exif_dict: EXIF dictionary from piexif.load()

    Returns:
        Filtered EXIF dictionary
    """
    # Filter Exif IFD (main EXIF data)
    if "Exif" in exif_dict:
        filtered_exif = {}
        for tag, value in exif_dict["Exif"].items():
            if tag in SAFE_EXIF_TAGS:
                filtered_exif[tag] = value
            # Tags not in SAFE_EXIF_TAGS are implicitly removed
        exif_dict["Exif"] = filtered_exif

    # Filter 0th IFD (main image data)
    if "0th" in exif_dict:
        filtered_0th = {}
        for tag, value in exif_dict["0th"].items():
            if tag in SAFE_0TH_TAGS:
                filtered_0th[tag] = value
            # Tags not in SAFE_0TH_TAGS are implicitly removed
        exif_dict["0th"] = filtered_0th

    return exif_dict


def strip_and_save(src_path: Path, dest_path: Path) -> bool:
    """
    Strip metadata from image and save to destination.

    Opens source image, filters metadata, saves to destination with cleaned EXIF.

    Args:
        src_path: Source image file path
        dest_path: Destination file path

    Returns:
        True if successful, False if failed

    Raises:
        Does not raise exceptions - all errors are caught and logged
    """
    try:
        # Filter metadata
        cleaned_exif = filter_metadata(src_path)

        # Open image
        img = Image.open(src_path)

        # Save with cleaned EXIF
        if cleaned_exif is not None:
            img.save(dest_path, exif=cleaned_exif)
        else:
            # Save without EXIF if filtering failed
            img.save(dest_path)

        return True

    except Exception as e:
        logger.warning(f"⚠ WARNING: Failed to strip and save {src_path.name}: {e}")
        return False
