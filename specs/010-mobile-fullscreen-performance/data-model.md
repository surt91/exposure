# Data Model: Mobile Full-Screen Experience & Advanced Performance

**Feature**: 010-mobile-fullscreen-performance
**Date**: December 8, 2025
**Status**: Complete

## Overview

This document defines the data structures, state machines, and validation rules for mobile full-screen viewing with blur placeholder progressive loading.

---

## 1. Python Data Models (Build-Time)

### 1.1 BlurPlaceholder

Ultra-low-resolution blur preview data embedded in HTML.

```python
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, field_validator

class BlurPlaceholder(BaseModel):
    """Ultra-low-resolution blur placeholder for instant image preview.

    Generated during build process from source images. Encoded as base64
    data URL for inline embedding in HTML (zero network requests).
    """

    data_url: str = Field(
        ...,
        description="Base64-encoded JPEG data URL (format: 'data:image/jpeg;base64,...')",
        min_length=50,  # Minimum valid data URL length
        max_length=2000  # Maximum 2KB per placeholder
    )

    size_bytes: int = Field(
        ...,
        description="Size of data_url string in bytes (for budget tracking)",
        ge=0,
        le=2000
    )

    dimensions: tuple[int, int] = Field(
        ...,
        description="Placeholder dimensions (width, height) in pixels, typically (20, 20)",
    )

    blur_radius: int = Field(
        default=10,
        description="Gaussian blur radius applied (pixels)",
        ge=5,
        le=20
    )

    source_hash: str = Field(
        ...,
        description="SHA256 hash of source image (for cache invalidation)",
        pattern=r'^[a-f0-9]{64}$'
    )

    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of placeholder generation"
    )

    @field_validator('data_url')
    @classmethod
    def validate_data_url_format(cls, v: str) -> str:
        """Ensure data URL has correct JPEG format prefix."""
        if not v.startswith('data:image/jpeg;base64,'):
            raise ValueError("data_url must start with 'data:image/jpeg;base64,'")
        return v

    @field_validator('dimensions')
    @classmethod
    def validate_dimensions(cls, v: tuple[int, int]) -> tuple[int, int]:
        """Ensure dimensions are reasonable for blur placeholder."""
        width, height = v
        if width < 10 or width > 50 or height < 10 or height > 50:
            raise ValueError("Dimensions must be between 10-50 pixels")
        return v


class BlurPlaceholderConfig(BaseModel):
    """Configuration for blur placeholder generation."""

    enabled: bool = Field(
        default=True,
        description="Enable/disable blur placeholder generation"
    )

    target_size: int = Field(
        default=20,
        description="Target dimension (longer edge) for placeholder before blur",
        ge=10,
        le=50
    )

    blur_radius: int = Field(
        default=10,
        description="Gaussian blur radius in pixels",
        ge=5,
        le=20
    )

    jpeg_quality: int = Field(
        default=50,
        description="JPEG compression quality (lower = smaller file)",
        ge=10,
        le=80
    )

    max_size_bytes: int = Field(
        default=1500,
        description="Maximum allowed size per placeholder (bytes)",
        ge=500,
        le=2000
    )
```

### 1.2 ImageMetadata (Extended)

Extend existing `ImageMetadata` model to include blur placeholder.

```python
class ImageMetadata(BaseModel):
    """Complete metadata for a gallery image (EXTENDED)."""

    # ... existing fields (path, title, description, thumbnail, etc.) ...

    blur_placeholder: BlurPlaceholder | None = Field(
        default=None,
        description="Optional blur placeholder for progressive loading"
    )

    # Validation: blur_placeholder should always exist if config.enabled
    @field_validator('blur_placeholder')
    @classmethod
    def validate_blur_placeholder(cls, v, info):
        """Warn if blur placeholder missing when enabled in config."""
        if v is None:
            # Log warning but don't fail (graceful degradation)
            import logging
            logging.warning(f"Blur placeholder missing for image")
        return v
```

### 1.3 BuildCacheEntry (Extended)

Extend build cache to track blur placeholders for incremental builds.

```python
class BuildCacheEntry(BaseModel):
    """Cache entry for a single image (EXTENDED)."""

    # ... existing fields (source_path, source_hash, thumbnail_info, etc.) ...

    blur_placeholder: BlurPlaceholder | None = Field(
        default=None,
        description="Cached blur placeholder data"
    )

    cache_version: str = Field(
        default="2.0.0",  # Bump version for blur placeholder addition
        description="Cache format version"
    )

    def is_valid(self, current_source_hash: str) -> bool:
        """Check if cache entry is still valid."""
        if self.source_hash != current_source_hash:
            return False
        if self.blur_placeholder and self.blur_placeholder.source_hash != current_source_hash:
            return False
        return True
```

---

## 2. JavaScript Data Models (Runtime)

### 2.1 ControlVisibilityState

State machine for navigation control visibility on mobile.

```typescript
enum ControlVisibilityState {
  HIDDEN = 'hidden',      // Controls not visible (default on mobile)
  VISIBLE = 'visible',    // Controls visible (after tap)
  PENDING = 'pending'     // Transition in progress
}

interface ControlVisibilityManager {
  state: ControlVisibilityState;
  hideTimer: number | null;
  isMobile: boolean;

  // Actions
  showControls(): void;
  hideControls(): void;
  resetHideTimer(): void;
  handleUserInteraction(event: Event): void;
}

// Implementation
class ControlVisibilityManager {
  constructor() {
    this.state = ControlVisibilityState.HIDDEN;
    this.hideTimer = null;
    this.isMobile = window.matchMedia('(max-width: 767px)').matches;
  }

  showControls() {
    if (!this.isMobile) return; // Desktop always visible

    this.state = ControlVisibilityState.VISIBLE;
    document.querySelector('.fullscreen-controls')?.classList.add('visible');
    this.resetHideTimer();
  }

  hideControls() {
    if (!this.isMobile) return;

    this.state = ControlVisibilityState.HIDDEN;
    document.querySelector('.fullscreen-controls')?.classList.remove('visible');
    clearTimeout(this.hideTimer);
  }

  resetHideTimer() {
    clearTimeout(this.hideTimer);
    this.hideTimer = setTimeout(() => this.hideControls(), 3000);
  }

  handleUserInteraction(event) {
    if (this.state === ControlVisibilityState.HIDDEN) {
      this.showControls();
    } else {
      this.resetHideTimer();
    }
  }
}
```

### 2.2 ProgressiveLoadState

State machine for progressive image loading.

```typescript
enum LoadStage {
  BLUR = 'blur',           // Blur placeholder visible (instant)
  THUMBNAIL = 'thumbnail', // Thumbnail loaded (fast)
  ORIGINAL = 'original',   // Original high-res loaded (full quality)
  ERROR = 'error'          // Loading failed
}

interface ProgressiveImageLoader {
  currentStage: LoadStage;
  element: HTMLImageElement;
  blurDataUrl: string;
  thumbnailSrc: string;
  originalSrc: string;

  // Actions
  loadBlur(): void;
  loadThumbnail(): Promise<void>;
  loadOriginal(): Promise<void>;
  handleError(stage: LoadStage, error: Error): void;
}

// State transitions
// BLUR → THUMBNAIL → ORIGINAL (normal flow)
// BLUR → ORIGINAL (skip thumbnail if cached)
// * → ERROR (on any failure)

class ProgressiveImageLoader {
  constructor(element, blurDataUrl, thumbnailSrc, originalSrc) {
    this.currentStage = LoadStage.BLUR;
    this.element = element;
    this.blurDataUrl = blurDataUrl;
    this.thumbnailSrc = thumbnailSrc;
    this.originalSrc = originalSrc;
  }

  async load() {
    // Stage 1: Blur (instant, no network request)
    this.loadBlur();

    try {
      // Stage 2: Thumbnail (or skip if original cached)
      const originalCached = await this.checkIfCached(this.originalSrc);

      if (originalCached) {
        // Skip thumbnail, load original directly
        await this.loadOriginal();
      } else {
        // Load thumbnail first
        await this.loadThumbnail();
        // Then load original in background
        await this.loadOriginal();
      }
    } catch (error) {
      this.handleError(this.currentStage, error);
    }
  }

  loadBlur() {
    const container = this.element.closest('.image-container');
    container.style.backgroundImage = `url("${this.blurDataUrl}")`;
    this.currentStage = LoadStage.BLUR;
  }

  async loadThumbnail() {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        this.element.src = this.thumbnailSrc;
        this.element.classList.add('loaded');
        this.currentStage = LoadStage.THUMBNAIL;
        resolve();
      };
      img.onerror = reject;
      img.src = this.thumbnailSrc;
    });
  }

  async loadOriginal() {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        this.element.src = this.originalSrc;
        this.currentStage = LoadStage.ORIGINAL;
        resolve();
      };
      img.onerror = reject;
      img.src = this.originalSrc;
    });
  }

  async checkIfCached(src) {
    const startTime = performance.now();
    const img = new Image();

    return new Promise((resolve) => {
      img.onload = () => {
        const loadTime = performance.now() - startTime;
        resolve(loadTime < 100); // < 100ms = likely cached
      };
      img.onerror = () => resolve(false);
      img.src = src;
    });
  }

  handleError(stage, error) {
    console.error(`Progressive load failed at stage ${stage}:`, error);
    this.currentStage = LoadStage.ERROR;
    // Fallback: show whatever loaded successfully
    // (blur placeholder remains visible if thumbnail/original failed)
  }
}
```

### 2.3 FullscreenState

State machine for fullscreen mode management.

```typescript
enum FullscreenMode {
  NORMAL = 'normal',           // Regular gallery view
  FULLSCREEN = 'fullscreen',   // Native fullscreen API active
  FALLBACK = 'fallback',       // iOS Safari fallback mode
  EXITING = 'exiting'          // Transition out of fullscreen
}

interface FullscreenManager {
  mode: FullscreenMode;
  element: HTMLElement;
  previousScrollPosition: number;

  // Actions
  enterFullscreen(): Promise<void>;
  exitFullscreen(): Promise<void>;
  applyFallback(): void;
  handleOrientationChange(): void;
}

// State transitions
// NORMAL → FULLSCREEN (API supported)
// NORMAL → FALLBACK (iOS Safari)
// FULLSCREEN → NORMAL (exit via API)
// FALLBACK → NORMAL (exit manually)

class FullscreenManager {
  constructor(element) {
    this.mode = FullscreenMode.NORMAL;
    this.element = element;
    this.previousScrollPosition = 0;
  }

  async enterFullscreen() {
    try {
      if (this.element.requestFullscreen) {
        await this.element.requestFullscreen();
        this.mode = FullscreenMode.FULLSCREEN;
      } else {
        this.applyFallback();
      }
    } catch (error) {
      console.warn('Fullscreen API failed, using fallback:', error);
      this.applyFallback();
    }
  }

  async exitFullscreen() {
    this.mode = FullscreenMode.EXITING;

    if (document.fullscreenElement) {
      await document.exitFullscreen();
    } else {
      // Exit fallback mode
      this.element.style.position = '';
      this.element.style.zIndex = '';
      document.body.style.overflow = '';
      window.scrollTo(0, this.previousScrollPosition);
    }

    this.mode = FullscreenMode.NORMAL;
  }

  applyFallback() {
    this.mode = FullscreenMode.FALLBACK;
    this.previousScrollPosition = window.scrollY;

    // Fixed positioning fallback
    this.element.style.position = 'fixed';
    this.element.style.top = '0';
    this.element.style.left = '0';
    this.element.style.width = '100vw';
    this.element.style.height = '100vh';
    this.element.style.zIndex = '9999';

    // Hide address bar on iOS
    window.scrollTo(0, 1);
    document.body.style.overflow = 'hidden';
  }

  handleOrientationChange() {
    // Recalculate dimensions in fallback mode
    if (this.mode === FullscreenMode.FALLBACK) {
      this.element.style.width = '100vw';
      this.element.style.height = '100vh';
    }
    // Native fullscreen API handles orientation automatically
  }
}
```

---

## 3. Relationships & Dependencies

### Data Flow Diagram

```
[Build Process]
    │
    ├─> Source Image (JPG/PNG)
    │       │
    │       ├─> ThumbnailGenerator.generate_thumbnails()
    │       │       └─> Thumbnail (WebP/JPEG)
    │       │
    │       └─> ThumbnailGenerator.generate_blur_placeholder()
    │               └─> BlurPlaceholder (data URL)
    │
    └─> ImageMetadata (with blur_placeholder field)
            │
            └─> Jinja2 Template (index.html.j2)
                    │
                    └─> Generated HTML (blur data URLs embedded inline)
                            │
                            └─> [Browser Runtime]
                                    │
                                    ├─> ProgressiveImageLoader
                                    │       └─> Load stages: BLUR → THUMBNAIL → ORIGINAL
                                    │
                                    ├─> FullscreenManager
                                    │       └─> Modes: NORMAL → FULLSCREEN/FALLBACK
                                    │
                                    └─> ControlVisibilityManager
                                            └─> States: HIDDEN ↔ VISIBLE
```

### Validation Rules

**Build-Time Validation**:
1. Blur placeholder data URL must be < 2KB
2. Blur placeholder must be valid base64-encoded JPEG
3. Source hash must match between thumbnail and blur placeholder
4. Total HTML size increase from blur placeholders must be tracked (warn if > 100KB)

**Runtime Validation**:
1. Blur data URL must exist before initializing ProgressiveImageLoader
2. Fullscreen mode can only enter from NORMAL state
3. Control visibility state changes only apply to mobile viewports (<768px)
4. Load stage transitions must follow: BLUR → THUMBNAIL → ORIGINAL (or BLUR → ORIGINAL)

---

## 4. Performance Constraints

### Build-Time Constraints
- Blur placeholder generation: < 100ms per image
- Total build time increase: < 20% (for 500 images: +10 seconds acceptable)
- Cache hit rate: > 95% on incremental builds

### Runtime Constraints
- Blur placeholder visibility: < 50ms from page load
- Fullscreen mode transition: < 100ms (perceived instant)
- Control visibility animation: 300ms (CSS transition)
- Progressive load stages: blur (instant) → thumbnail (< 500ms on 3G) → original (< 3s on 3G)

### Memory Constraints
- Preload cache: max 10 images (prevent memory leaks)
- Data URL storage: ~80KB total for 100 images (inline in HTML)

---

## 5. Error Handling

### Build-Time Error Handling
```python
def generate_blur_placeholder_safe(source_path: Path) -> BlurPlaceholder | None:
    """Generate blur placeholder with graceful error handling."""
    try:
        return generate_blur_placeholder(source_path)
    except Exception as e:
        logger.warning(f"Failed to generate blur placeholder for {source_path}: {e}")
        return None  # Graceful degradation: continue without blur placeholder
```

### Runtime Error Handling
```javascript
// Progressive loading error: fall back to showing blur placeholder only
loader.addEventListener('error', () => {
  console.warn('Image failed to load, showing blur placeholder only');
  // Blur placeholder already visible, no action needed
});

// Fullscreen API error: fall back to fixed positioning
try {
  await element.requestFullscreen();
} catch (error) {
  applyFullscreenFallback(); // iOS Safari fallback
}

// Control visibility error: default to always-visible
if (!isMobileSupported()) {
  controls.classList.add('always-visible');
}
```

---

## Summary

This data model defines:
- **3 Python models**: `BlurPlaceholder`, `BlurPlaceholderConfig`, extended `ImageMetadata`
- **3 JavaScript state machines**: `ControlVisibilityManager`, `ProgressiveImageLoader`, `FullscreenManager`
- **Validation rules**: Size limits, format validation, state transition constraints
- **Performance constraints**: Timing thresholds for all operations
- **Error handling**: Graceful degradation strategies

All models support the core requirements: instant blur placeholders, mobile full-screen mode, and progressive image loading with smooth transitions.
