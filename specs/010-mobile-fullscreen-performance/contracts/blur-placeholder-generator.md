# Blur Placeholder Generator API Contract

**Component**: `ThumbnailGenerator.generate_blur_placeholder()`  
**Type**: Build-time Python API  
**Version**: 1.0.0

## Purpose

Generate ultra-low-resolution blur placeholders from source images during the build process. Placeholders are base64-encoded data URLs embedded directly in HTML for instant display without network requests.

---

## API Signature

```python
def generate_blur_placeholder(
    source_path: Path,
    config: BlurPlaceholderConfig
) -> BlurPlaceholder:
    """
    Generate blur placeholder from source image.
    
    Args:
        source_path: Path to source image file (JPEG, PNG, WebP)
        config: Blur placeholder generation configuration
        
    Returns:
        BlurPlaceholder object with data URL and metadata
        
    Raises:
        FileNotFoundError: If source_path does not exist
        ValueError: If image cannot be decoded or is invalid
        RuntimeError: If placeholder generation fails
    """
```

---

## Input Contract

### source_path: Path
- **Type**: `pathlib.Path`
- **Required**: Yes
- **Constraints**:
  - Must exist and be readable
  - Must be valid image file (JPEG, PNG, WebP, GIF)
  - File size: Any (will be downscaled)
  - Minimum dimensions: 10x10 pixels
  - Maximum dimensions: No limit (will be downscaled)

### config: BlurPlaceholderConfig
- **Type**: `BlurPlaceholderConfig` (Pydantic model)
- **Required**: Yes
- **Fields**:
  ```python
  class BlurPlaceholderConfig(BaseModel):
      enabled: bool = True
      target_size: int = 20          # 10-50 pixels
      blur_radius: int = 10          # 5-20 pixels
      jpeg_quality: int = 50         # 10-80
      max_size_bytes: int = 1500     # 500-2000 bytes
  ```

---

## Output Contract

### Returns: BlurPlaceholder

```python
class BlurPlaceholder(BaseModel):
    data_url: str              # "data:image/jpeg;base64,/9j/4AAQ..."
    size_bytes: int            # Length of data_url string
    dimensions: tuple[int, int]  # (width, height) after resize
    blur_radius: int           # Applied blur radius
    source_hash: str           # SHA256 hash of source image
    generated_at: datetime     # Timestamp of generation
```

**Guarantees**:
- `data_url` always starts with `"data:image/jpeg;base64,"`
- `size_bytes` ≤ `config.max_size_bytes` (will reduce quality if needed)
- `dimensions` both values between 10-50 pixels
- `source_hash` is 64-character hex string (SHA256)

---

## Processing Steps

The function performs these operations:

1. **Open Source Image**
   ```python
   img = PILImage.open(source_path)
   img = ImageOps.exif_transpose(img)  # Fix EXIF orientation
   ```

2. **Downscale to Target Size**
   ```python
   img.thumbnail((config.target_size, config.target_size), PILImage.Resampling.LANCZOS)
   # Maintains aspect ratio, longest edge = target_size
   ```

3. **Apply Gaussian Blur**
   ```python
   img = img.filter(ImageFilter.GaussianBlur(radius=config.blur_radius))
   ```

4. **Convert to JPEG & Compress**
   ```python
   buffer = BytesIO()
   img.save(buffer, format='JPEG', quality=config.jpeg_quality, optimize=True)
   ```

5. **Base64 Encode**
   ```python
   b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
   data_url = f"data:image/jpeg;base64,{b64}"
   ```

6. **Validate Size Budget**
   ```python
   if len(data_url) > config.max_size_bytes:
       # Retry with lower quality until within budget
       ...
   ```

---

## Error Handling

### FileNotFoundError
- **Trigger**: `source_path` does not exist or is not accessible
- **Response**: Raise immediately with clear error message
- **Example**: `FileNotFoundError: Source image not found: /path/to/missing.jpg`

### ValueError
- **Trigger**: Image file is corrupt, unsupported format, or < 10x10 pixels
- **Response**: Raise with format/validation error details
- **Example**: `ValueError: Image dimensions 5x5 below minimum 10x10`

### RuntimeError
- **Trigger**: Unexpected processing failure (rare: disk full, memory exhausted)
- **Response**: Raise with technical details for debugging
- **Example**: `RuntimeError: Failed to apply Gaussian blur: [details]`

### Size Budget Exceeded
- **Trigger**: Generated data URL > `config.max_size_bytes` even at minimum quality
- **Response**: Log warning and return placeholder at maximum allowed size
- **Fallback**: Reduce quality iteratively until within budget or reach quality=10 minimum

---

## Performance Contract

### Timing Guarantees
- **Single Image**: < 100ms per image (on typical hardware)
- **Batch Processing**: Linear scaling with parallelization support
- **Cache Hit**: < 5ms (read from cache, skip generation)

### Memory Footprint
- **Peak Memory**: < 50MB per worker thread
- **Temporary Storage**: No disk writes (in-memory processing)

### Build Cache Integration
```python
# Cache key format
cache_key = f"blur_{hash_file(source_path)}_{config.target_size}_{config.blur_radius}"

# Cache value format
cache_value = {
    "data_url": "data:image/jpeg;base64,...",
    "size_bytes": 823,
    "dimensions": [20, 15],
    "blur_radius": 10,
    "source_hash": "sha256:abc123...",
    "generated_at": "2025-12-08T10:30:00"
}
```

---

## Usage Example

```python
from pathlib import Path
from src.generator.model import BlurPlaceholderConfig
from src.generator.thumbnails import ThumbnailGenerator

# Configure blur placeholder generation
config = BlurPlaceholderConfig(
    enabled=True,
    target_size=20,
    blur_radius=10,
    jpeg_quality=50,
    max_size_bytes=1500
)

# Generate blur placeholder
generator = ThumbnailGenerator(config=config)
source_path = Path("content/photo001.jpg")

try:
    placeholder = generator.generate_blur_placeholder(source_path, config)
    
    print(f"Generated blur placeholder:")
    print(f"  Size: {placeholder.size_bytes} bytes")
    print(f"  Dimensions: {placeholder.dimensions}")
    print(f"  Data URL: {placeholder.data_url[:50]}...")
    
    # Use in HTML template
    html = f'<div style="background-image: url(\'{placeholder.data_url}\')"></div>'
    
except FileNotFoundError as e:
    print(f"Error: Source image not found - {e}")
except ValueError as e:
    print(f"Error: Invalid image - {e}")
```

---

## Testing Contract

### Unit Test Requirements

1. **Happy Path**: Generate placeholder from valid JPEG, PNG, WebP
2. **Size Validation**: Verify output ≤ max_size_bytes
3. **Format Validation**: Verify data URL has correct prefix
4. **Dimension Validation**: Verify dimensions within 10-50px range
5. **Blur Application**: Verify blur radius applied (check image properties)
6. **Cache Integration**: Verify cache hit returns identical result
7. **EXIF Orientation**: Verify rotated images handled correctly

### Error Test Requirements

1. **Missing File**: Verify FileNotFoundError raised
2. **Invalid Format**: Verify ValueError for corrupt images
3. **Tiny Images**: Verify ValueError for < 10x10 images
4. **Budget Exceeded**: Verify quality reduction fallback

### Performance Test Requirements

1. **Generation Speed**: < 100ms per image on standard hardware
2. **Memory Usage**: < 50MB peak per worker
3. **Cache Performance**: < 5ms for cache hits

---

## Integration Points

### Caller: `build_html.py`
```python
# Called during image scanning/processing
for image_path in scan_images(content_dir):
    metadata = ImageMetadata(path=image_path, ...)
    metadata.blur_placeholder = generator.generate_blur_placeholder(
        image_path, blur_config
    )
    images.append(metadata)
```

### Consumer: `index.html.j2` (Jinja2 Template)
```jinja2
{% for image in category.images %}
  <div class="image-container"
       style="background-image: url('{{ image.blur_placeholder.data_url }}')">
    <img data-thumbnail="{{ image.thumbnail.webp_path }}"
         data-original="{{ image.original_path }}"
         alt="{{ image.title }}" />
  </div>
{% endfor %}
```

---

## Version History

- **1.0.0** (2025-12-08): Initial API contract definition
