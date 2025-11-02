# Layout Algorithm API Contract

**Feature**: 007-flexible-layout
**Version**: 1.0.0
**Date**: 2025-11-02

## Overview

This contract defines the JavaScript API for the flexible layout algorithm. The algorithm is responsible for calculating optimal image positions given a set of image dimensions and container width.

---

## API Interface

### Function: `calculateLayout`

Computes optimal image positioning using the justified layout algorithm.

**Signature**:
```typescript
function calculateLayout(
  images: ImageInput[],
  options: LayoutOptions
): LayoutResult
```

---

## Input Types

### ImageInput

Array of image dimension objects.

```typescript
interface ImageInput {
  /** Original image width in pixels */
  width: number;

  /** Original image height in pixels */
  height: number;

  /** Optional identifier for the image */
  id?: string | number;

  /** Optional DOM element reference */
  element?: HTMLElement;
}
```

**Validation**:
- `width` must be > 0
- `height` must be > 0
- Array must contain at least 1 image

**Example**:
```javascript
const images = [
  { width: 1920, height: 1080 },
  { width: 800, height: 1200 },
  { width: 1600, height: 900 }
];
```

---

### LayoutOptions

Configuration parameters for the layout algorithm.

```typescript
interface LayoutOptions {
  /**
   * Container width in pixels
   * Required: true
   * Range: 320 - 3840 (mobile to 4K)
   */
  containerWidth: number;

  /**
   * Target row height in pixels
   * Default: 320
   * Range: 150 - 600
   * Description: Desired height for rows before justification
   */
  targetRowHeight?: number;

  /**
   * Maximum allowed row height in pixels
   * Default: 480
   * Range: targetRowHeight - 800
   * Description: Upper bound to prevent overly tall rows
   */
  maxRowHeight?: number;

  /**
   * Gap between images in pixels
   * Default: 8
   * Range: 0 - 32
   * Description: Horizontal and vertical spacing between images
   */
  spacing?: number;

  /**
   * Whether to force justify the last row
   * Default: false
   * Description: If true, last row stretches to full width; if false, left-aligned
   */
  forceLastRow?: boolean;

  /**
   * Minimum aspect ratio allowed (height/width)
   * Default: 0.25 (1:4 tall portrait)
   * Range: 0.1 - 1.0
   */
  minAspectRatio?: number;

  /**
   * Maximum aspect ratio allowed (width/height)
   * Default: 4.0 (4:1 wide panorama)
   * Range: 1.0 - 10.0
   */
  maxAspectRatio?: number;
}
```

**Default Values**:
```javascript
const DEFAULT_OPTIONS = {
  targetRowHeight: 320,
  maxRowHeight: 480,
  spacing: 8,
  forceLastRow: false,
  minAspectRatio: 0.25,
  maxAspectRatio: 4.0
};
```

---

## Output Type

### LayoutResult

Complete layout calculation result.

```typescript
interface LayoutResult {
  /**
   * Array of positioned image boxes
   * One per input image in same order
   */
  boxes: LayoutBox[];

  /**
   * Array of rows grouping images
   */
  rows: LayoutRowInfo[];

  /**
   * Total height of the layout in pixels
   */
  containerHeight: number;

  /**
   * Width used for calculation (from options)
   */
  containerWidth: number;

  /**
   * Performance metric: calculation time in milliseconds
   */
  calculationTime?: number;
}
```

---

### LayoutBox

Individual image position and size.

```typescript
interface LayoutBox {
  /** Horizontal position from container left in pixels */
  x: number;

  /** Vertical position from container top in pixels */
  y: number;

  /** Rendered width in pixels */
  width: number;

  /** Rendered height in pixels */
  height: number;

  /** Original aspect ratio (width / height) */
  aspectRatio: number;

  /** Row index this image belongs to (0-based) */
  rowIndex: number;

  /** Optional identifier copied from input */
  id?: string | number;

  /** Optional element reference copied from input */
  element?: HTMLElement;
}
```

**Guarantees**:
- `x >= 0`
- `y >= 0`
- `width > 0`
- `height > 0`
- `aspectRatio === width / height` (within floating point tolerance)
- Boxes do not overlap
- Boxes within same row have identical `y` and `height` values

---

### LayoutRowInfo

Metadata about a single row in the layout.

```typescript
interface LayoutRowInfo {
  /** Y position of this row in pixels */
  y: number;

  /** Height of all images in this row in pixels */
  height: number;

  /** Number of images in this row */
  imageCount: number;

  /** Indices of boxes belonging to this row */
  boxIndices: number[];

  /** Total width of all images plus spacing */
  totalWidth: number;
}
```

---

## Error Handling

### Errors

The function should throw errors for invalid input:

```typescript
class LayoutError extends Error {
  constructor(message: string, code: LayoutErrorCode) {
    super(message);
    this.name = 'LayoutError';
    this.code = code;
  }
}

enum LayoutErrorCode {
  INVALID_IMAGES = 'INVALID_IMAGES',
  INVALID_CONTAINER_WIDTH = 'INVALID_CONTAINER_WIDTH',
  INVALID_OPTIONS = 'INVALID_OPTIONS',
  CALCULATION_FAILED = 'CALCULATION_FAILED'
}
```

**Error Conditions**:

| Condition | Error Code | Message |
|-----------|------------|---------|
| Empty images array | `INVALID_IMAGES` | "Images array must contain at least one image" |
| Image width <= 0 | `INVALID_IMAGES` | "Image width must be greater than 0" |
| Image height <= 0 | `INVALID_IMAGES` | "Image height must be greater than 0" |
| Container width <= 0 | `INVALID_CONTAINER_WIDTH` | "Container width must be greater than 0" |
| Target height > max height | `INVALID_OPTIONS` | "Target row height cannot exceed max row height" |
| Calculation timeout | `CALCULATION_FAILED` | "Layout calculation exceeded time limit" |

---

## Usage Examples

### Basic Usage

```javascript
const images = [
  { width: 1920, height: 1080 },
  { width: 800, height: 1200 },
  { width: 1600, height: 900 }
];

const layout = calculateLayout(images, {
  containerWidth: 1200
});

console.log(`Layout height: ${layout.containerHeight}px`);
console.log(`Number of rows: ${layout.rows.length}`);

// Apply positions to DOM
layout.boxes.forEach((box, index) => {
  const img = document.querySelectorAll('.image-item')[index];
  img.style.transform = `translate(${box.x}px, ${box.y}px)`;
  img.style.width = `${box.width}px`;
  img.style.height = `${box.height}px`;
});
```

### Custom Options

```javascript
const layout = calculateLayout(images, {
  containerWidth: 1200,
  targetRowHeight: 250,
  maxRowHeight: 400,
  spacing: 16,
  forceLastRow: true
});
```

### With DOM References

```javascript
const images = Array.from(document.querySelectorAll('.image-item'))
  .map(el => ({
    width: parseInt(el.dataset.width),
    height: parseInt(el.dataset.height),
    element: el
  }));

const layout = calculateLayout(images, {
  containerWidth: document.querySelector('.gallery').clientWidth
});

// Apply directly using stored references
layout.boxes.forEach(box => {
  if (box.element) {
    box.element.style.transform = `translate(${box.x}px, ${box.y}px)`;
    box.element.style.width = `${box.width}px`;
    box.element.style.height = `${box.height}px`;
  }
});
```

### Responsive Resize

```javascript
let currentLayout = null;

function updateLayout() {
  const containerWidth = document.querySelector('.gallery').clientWidth;

  currentLayout = calculateLayout(images, {
    containerWidth,
    targetRowHeight: containerWidth < 640 ? 200 : 320
  });

  applyLayout(currentLayout);
}

// Initial layout
updateLayout();

// Debounced resize handler
let resizeTimeout;
window.addEventListener('resize', () => {
  clearTimeout(resizeTimeout);
  resizeTimeout = setTimeout(updateLayout, 150);
});
```

---

## Performance Guarantees

- **Time Complexity**: O(n) where n = number of images
- **Space Complexity**: O(n)
- **Calculation Time**:
  - 10 images: <1ms
  - 100 images: <5ms
  - 500 images: <20ms
  - 1000 images: <40ms
- **Browser Support**: ES6+ (Chrome 51+, Firefox 54+, Safari 10+, Edge 15+)

---

## Implementation Notes

### Justified Layout Algorithm

The algorithm operates as follows:

1. **Initialize**: Start with empty row, set current Y position to 0
2. **Row Building**: For each image:
   - Add image to current row
   - Calculate sum of aspect ratios
   - Calculate row width if all images scaled to target height
   - If row width >= container width - spacing:
     - Calculate optimal height: `(containerWidth - (n-1)*spacing) / aspectRatioSum`
     - Clamp height between min and max bounds
     - Position images in row at current Y
     - Increment Y by row height + spacing
     - Start new row
3. **Last Row**: Handle remaining images (justify or left-align based on option)
4. **Return**: Package all boxes and metadata

### Aspect Ratio Clamping

Images with extreme aspect ratios are clamped to prevent layout issues:
- Tall portraits (< minAspectRatio): Treated as minAspectRatio
- Wide panoramas (> maxAspectRatio): Treated as maxAspectRatio
- Original aspect ratio preserved in LayoutBox for reference

### Spacing Handling

- Horizontal spacing: Applied between images in a row
- Vertical spacing: Applied between rows
- Total images per row: `n` images → `n-1` gaps
- Width calculation accounts for spacing: `containerWidth - (n-1)*spacing`

---

## Testing Contract

### Unit Test Requirements

1. **Single Image**: Should return one box occupying container width
2. **Multiple Images Same Aspect**: Should create balanced rows
3. **Mixed Aspects**: Should group images sensibly
4. **Narrow Container**: Should handle mobile widths (320px)
5. **Wide Container**: Should handle desktop widths (1920px)
6. **Edge Cases**:
   - Single pixel image (1x1)
   - Extreme aspect ratios (1:10, 10:1)
   - Very tall images (10000px height)
   - Very wide images (10000px width)
7. **Error Cases**: All error conditions listed above
8. **Performance**: Should complete within time guarantees

### Property-Based Tests

1. **Non-overlapping**: No two boxes should intersect
2. **Container Bounds**: All boxes should be within container
3. **Row Consistency**: Images in same row have same height and Y position
4. **Deterministic**: Same input should produce identical output
5. **Area Preservation**: Total image area should be approximately equal (within rounding)

---

## Changelog

### Version 1.0.0 (2025-11-02)
- Initial API definition
- Justified layout algorithm specification
- Error handling contract
- Performance guarantees

---

## References

- [flickr/justified-layout](https://github.com/flickr/justified-layout) - Reference implementation
- [CSS Grid Layout](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout) - Fallback layout
- [Web Performance](https://web.dev/vitals/) - CLS and performance metrics
