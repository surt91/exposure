"""Generate test fixture images with various aspect ratios.

This script creates minimal valid image files for testing the flexible layout algorithm.
"""

from pathlib import Path

from PIL import Image, ImageDraw


def create_test_image(path: Path, width: int, height: int, color: tuple, label: str):
    """Create a test image with dimensions and a label.

    Args:
        path: Output file path
        width: Image width in pixels
        height: Image height in pixels
        color: RGB color tuple
        label: Text to display on the image
    """
    img = Image.new("RGB", (width, height), color)
    draw = ImageDraw.Draw(img)

    # Add label text in the center
    text = f"{label}\n{width}x{height}"

    # Calculate text position (approximate center)
    text_bbox = draw.textbbox((0, 0), text)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw white text with black outline for visibility
    outline_color = (0, 0, 0) if sum(color) > 384 else (255, 255, 255)
    text_color = (255, 255, 255) if sum(color) < 384 else (0, 0, 0)

    for offset_x, offset_y in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        draw.text((x + offset_x, y + offset_y), text, fill=outline_color)

    draw.text((x, y), text, fill=text_color)

    img.save(path)
    print(f"Created {path.name}: {width}x{height} (aspect ratio: {width / height:.2f})")


def generate_test_images(
    output_dir: Path, count: int, sizes: list[tuple[int, int]] | None = None
) -> list[Path]:
    """Generate multiple test images for testing.

    Args:
        output_dir: Directory to save images
        count: Number of images to generate
        sizes: List of (width, height) tuples to cycle through. Defaults to common sizes.

    Returns:
        List of paths to generated images
    """
    if sizes is None:
        sizes = [(4000, 3000), (3000, 4000), (3000, 2000), (2000, 3000)]

    output_dir.mkdir(parents=True, exist_ok=True)
    colors = [
        (100, 150, 200),  # Blue
        (200, 100, 100),  # Red
        (100, 200, 100),  # Green
        (200, 150, 100),  # Orange
        (150, 100, 200),  # Purple
        (200, 200, 100),  # Yellow
    ]

    generated = []
    for i in range(count):
        width, height = sizes[i % len(sizes)]
        color = colors[i % len(colors)]

        filename = f"test_img_{i:04d}.jpg"
        path = output_dir / filename

        img = Image.new("RGB", (width, height), color)
        draw = ImageDraw.Draw(img)

        # Add simple label
        text = f"Image {i}"
        draw.text((10, 10), text, fill=(255, 255, 255))

        img.save(path, "JPEG", quality=85)
        generated.append(path)

    return generated


def main():
    """Generate all test fixture images."""
    fixtures_dir = Path(__file__).parent

    # Landscape images (16:9 ratio)
    create_test_image(
        fixtures_dir / "landscape_1920x1080.jpg",
        1920,
        1080,
        (100, 150, 200),  # Blue
        "Landscape 16:9",
    )

    create_test_image(
        fixtures_dir / "landscape_1600x900.jpg",
        1600,
        900,
        (150, 100, 150),  # Purple
        "Landscape 16:9",
    )

    # Portrait images (9:16 ratio)
    create_test_image(
        fixtures_dir / "portrait_1080x1920.jpg",
        1080,
        1920,
        (200, 100, 100),  # Red
        "Portrait 9:16",
    )

    create_test_image(
        fixtures_dir / "portrait_900x1600.jpg",
        900,
        1600,
        (200, 150, 100),  # Orange
        "Portrait 9:16",
    )

    # Square images (1:1 ratio)
    create_test_image(
        fixtures_dir / "square_1000x1000.jpg",
        1000,
        1000,
        (100, 200, 100),  # Green
        "Square 1:1",
    )

    create_test_image(
        fixtures_dir / "square_800x800.jpg",
        800,
        800,
        (150, 200, 100),  # Light green
        "Square 1:1",
    )

    # Panorama images (3:1 ratio)
    create_test_image(
        fixtures_dir / "panorama_3000x1000.jpg",
        3000,
        1000,
        (100, 100, 200),  # Dark blue
        "Panorama 3:1",
    )

    # Extreme panorama (4:1 ratio - at the limit)
    create_test_image(
        fixtures_dir / "panorama_4000x1000.jpg",
        4000,
        1000,
        (100, 200, 200),  # Cyan
        "Panorama 4:1",
    )

    # Vertical panorama (1:3 ratio)
    create_test_image(
        fixtures_dir / "vertical_1000x3000.jpg",
        1000,
        3000,
        (200, 100, 200),  # Magenta
        "Vertical 1:3",
    )

    # Small images for testing edge cases
    create_test_image(
        fixtures_dir / "small_100x100.jpg",
        100,
        100,
        (200, 200, 100),  # Yellow
        "Small",
    )

    # Different format
    create_test_image(
        fixtures_dir / "landscape_test.png",
        1280,
        720,
        (150, 150, 150),  # Gray
        "PNG 16:9",
    )

    print("\nAll test fixtures created successfully!")


if __name__ == "__main__":
    main()
