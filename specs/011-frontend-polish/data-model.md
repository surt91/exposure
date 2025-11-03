# Data Model: Frontend Polish & Mobile Improvements

**Feature**: 011-frontend-polish
**Date**: November 3, 2025
**Status**: Complete

## Overview

This feature is primarily a frontend enhancement with minimal data model changes. The core entities are client-side state management structures and DOM data attributes. No backend data models or database schemas are modified.

---

## Entity 1: TouchGestureState

**Purpose**: Track touch interaction state for swipe gesture detection on mobile devices

**Scope**: Client-side JavaScript state (not persisted)

**Structure**:
```javascript
{
  touchStartX: number,      // Initial X coordinate when touch begins (screen pixels)
  touchStartY: number,      // Initial Y coordinate when touch begins (screen pixels)
  touchEndX: number,        // Final X coordinate when touch ends (screen pixels)
  touchEndY: number,        // Final Y coordinate when touch ends (screen pixels)
  touchStartTime: number,   // Timestamp when touch begins (milliseconds, performance.now())
  touchEndTime: number      // Timestamp when touch ends (milliseconds, performance.now())
}
```

**Lifecycle**:
1. **Created**: On `touchstart` event (user touches screen in overlay)
2. **Updated**: On `touchend` event (user lifts finger)
3. **Validated**: Calculates angle and distance to determine if gesture is valid horizontal swipe
4. **Destroyed**: After gesture processing completes (no persistence)

**Validation Rules**:
- `touchStartX`, `touchStartY`, `touchEndX`, `touchEndY`: Must be positive numbers (screen coordinates)
- Swipe distance: `|touchEndX - touchStartX|` must be ≥50 pixels (minimum swipe threshold)
- Swipe angle: Must be within 30° of horizontal axis (`angle < 30° || angle > 150°`)
- Swipe duration: Should be <500ms for responsive feel (not enforced, but used for analytics)

**Relationships**:
- One-to-one with current overlay modal session
- Resets on each new `touchstart` event

**State Transitions**:
```
IDLE → TOUCH_STARTED → TOUCH_ENDED → VALIDATED → ACTION_DISPATCHED → IDLE
                     ↓
                  CANCELLED (if user navigates or modal closes)
```

---

## Entity 2: ImageLoadingState

**Purpose**: Track progressive image loading state for thumbnail-to-original transition

**Scope**: Client-side JavaScript state (per image in overlay)

**Structure**:
```javascript
{
  imageIndex: number,           // Index in images array
  thumbnailSrc: string,         // URL of thumbnail (e.g., "/images/thumb_image001.jpg")
  originalSrc: string,          // URL of original (e.g., "/images/image001.jpg")
  loadingStatus: LoadingStatus, // Enum: 'idle' | 'loading' | 'loaded' | 'error'
  imageLoader: Image | null,    // Browser Image() object for preloading (nullable)
  loadStartTime: number,        // Timestamp when original load began (milliseconds)
  loadEndTime: number | null    // Timestamp when original load completed (milliseconds, nullable)
}
```

**LoadingStatus Enum**:
- `idle`: No load initiated yet
- `loading`: Original image is being fetched in background
- `loaded`: Original image successfully loaded and displayed
- `error`: Original image failed to load, thumbnail remains visible

**Lifecycle**:
1. **Created**: When user opens overlay (`openFullscreen()`)
2. **Thumbnail displayed**: Immediately (<50ms)
3. **Loading initiated**: `imageLoader = new Image()`, status set to `loading`
4. **Loaded**: `imageLoader.onload` fires, status set to `loaded`, thumbnail replaced with original
5. **Destroyed**: When user closes overlay or navigates to different image (cancel previous load)

**Validation Rules**:
- `thumbnailSrc`, `originalSrc`: Must be valid URLs (relative or absolute)
- `imageIndex`: Must be valid index within images array (0 ≤ index < images.length)
- `imageLoader`: Can be null (cancelled load) or Image object
- `loadStartTime`: Must be positive number (timestamp)
- `loadEndTime`: Can be null (still loading) or positive number ≥ `loadStartTime`

**Relationships**:
- One-to-one with current overlay modal session
- References global `images` array for image metadata
- Can be replaced/cancelled when user navigates to different image

**State Transitions**:
```
IDLE → LOADING (thumbnail displayed, original fetching)
     ↓
     LOADED (original displayed, smooth transition)
     ↓
     CANCELLED (user navigated to different image)

OR

IDLE → LOADING
     ↓
     ERROR (original failed, thumbnail remains)
```

**Cancellation Logic**:
- When `openFullscreen()` called with new index:
  - Set `currentImageLoader = null` (previous load cancelled)
  - Start new load sequence for new image
  - Previous `Image.onload` handler checks if `this === currentImageLoader` before applying

---

## Entity 3: ModalState

**Purpose**: Track fullscreen overlay state and current image context

**Scope**: Client-side JavaScript global state

**Structure**:
```javascript
{
  isOpen: boolean,             // Whether modal is currently visible
  currentImageIndex: number,   // Index in FLAT allImages array (-1 if closed)
  previousFocus: Element | null, // Element to restore focus to when modal closes
  allImages: Array<ImageItem>  // FLAT array of ALL images across ALL categories
}
```

**ImageItem Structure** (stored in allImages flat array):
```javascript
{
  element: HTMLElement,        // DOM reference to .image-item div
  category: string,            // From data-category attribute
  categoryName: string,        // Display name of category (for overlay label)
  thumbnailSrc: string,        // From data-thumbnail-src attribute
  originalSrc: string,         // From data-original-src attribute
  title: string,               // From data-title attribute
  description: string,         // From data-description attribute
  filename: string,            // From data-filename attribute
  globalIndex: number          // Index in flat allImages array (for navigation)
}
```

**Lifecycle**:
1. **Initialized**: On page load (`init()` function)
2. **allImages array populated**: Flatten all categories into single array, each item gets globalIndex
3. **Modal opened**: `isOpen = true`, `currentImageIndex` set, `previousFocus` stored
4. **Modal closed**: `isOpen = false`, `currentImageIndex = -1`, focus restored

**Validation Rules**:
- `currentImageIndex`: Must be -1 (closed) or valid index (0 ≤ index < allImages.length)
- `previousFocus`: Can be null (no previous focus) or valid DOM element
- `allImages`: Flat array length must match total number of `.image-item` elements across ALL categories

**Cross-Category Navigation**:
- Navigation uses modulo arithmetic: `(currentIndex + 1) % allImages.length` for next
- Wrapping behavior: Last image of gallery → First image of gallery (and vice versa)
- Category label updates automatically when crossing boundaries (tracked via image.categoryName)

**Relationships**:
- One global instance per page
- References DOM elements (`.image-item`, `#fullscreen-modal`)
- Used by both touch gesture handler and keyboard navigation handler

**State Transitions**:
```
CLOSED (isOpen=false, currentImageIndex=-1)
  ↓
OPENING (thumbnail loading)
  ↓
OPEN (isOpen=true, currentImageIndex set)
  ↓
NAVIGATING (new image loading, index updated)
  ↓
CLOSING (animation playing)
  ↓
CLOSED (focus restored)
```

---

## Entity 4: CSSLayoutState

**Purpose**: CSS custom properties and computed values for responsive layout

**Scope**: CSS variables and browser-computed styles

**Structure**:
```css
:root {
  /* Banner dimensions */
  --banner-height-desktop: 40vh;
  --banner-height-tablet: 30vh;
  --banner-height-mobile: 25vh;

  /* Spacing (existing) */
  --spacing-unit: 1rem;
  --gap: 1rem;

  /* Animation timing */
  --transition-fast: 150ms;
  --transition-normal: 250ms;
  --transition-slow: 400ms;
  --easing-smooth: cubic-bezier(0.4, 0.0, 0.2, 1);
}
```

**Computed Values** (JavaScript queries these via getComputedStyle):
- `body.offsetWidth`: Total body width including padding
- `window.innerWidth`: Viewport width (used for 100vw calculations)
- `.modal-content img` computed max-height: 80vh (desktop) or 75vh (mobile)

**Lifecycle**:
- **Defined**: On page load (CSS parsing)
- **Applied**: Continuously by browser layout engine
- **Queried**: On demand by JavaScript (rare, only for debugging/analytics)

**Validation Rules**:
- All dimension values must be positive
- Viewport units (vh, vw) must be supported by browser
- Spacing unit must be consistent (1rem = 16px default)

**Relationships**:
- Used by `.gallery-banner` for responsive height
- Used by `.modal-content img` for overlay image sizing
- Used by animation transitions for consistent timing

---

## Entity 5: DOM Data Attributes

**Purpose**: Store image metadata in HTML for JavaScript access

**Scope**: Server-side generated (Jinja2 template), client-side read (JavaScript)

**Template Structure** (gallery.html):
```jinja2
<div class="image-item"
     data-category="{{ image.category }}"
     data-thumbnail-src="{{ image.thumbnail_url }}"
     data-original-src="{{ image.url }}"
     data-title="{{ image.title | e }}"
     data-description="{{ image.description | e }}"
     data-filename="{{ image.filename }}">
  <img src="{{ image.thumbnail_url }}"
       alt="{{ image.title | e }}"
       loading="lazy">
</div>
```

**Attributes**:
- `data-category`: Category name (e.g., "Dragons", "Dinosaurs")
- `data-thumbnail-src`: Relative URL to thumbnail (e.g., "/images/thumb_dragon001.jpg")
- `data-original-src`: Relative URL to original image (e.g., "/images/dragon001.jpg")
- `data-title`: Image title for display in overlay
- `data-description`: Optional description for display in overlay
- `data-filename`: Original filename for debugging/analytics

**Lifecycle**:
1. **Generated**: During build process (Python → Jinja2 → HTML)
2. **Rendered**: Static HTML delivered to browser
3. **Parsed**: JavaScript reads via `element.dataset.*` API
4. **Cached**: Values stored in `images` array for fast access

**Validation Rules** (enforced during build):
- `data-category`: Required, must match YAML category key
- `data-thumbnail-src`: Required, must be valid path
- `data-original-src`: Required, must be valid path
- `data-title`: Required, non-empty string
- `data-description`: Optional, can be empty string
- `data-filename`: Required, must match source file

**Relationships**:
- Generated from YAML configuration (`gallery.yaml`)
- Read by `fullscreen.js` and `gallery.js`
- Used to populate `ImageItem` objects in `images` array

---

## Data Flow Diagram

```
Build Time (Python):
gallery.yaml → build_html.py → Jinja2 → gallery.html (with data attributes)

Runtime (Browser):
1. Page Load:
   gallery.html → DOM → fullscreen.js init() → Parse data attributes → images array

2. User Interaction (Open Overlay):
   Click/Tap → openFullscreen(index) → Create ImageLoadingState
                                     → Display thumbnail immediately
                                     → Start Image() preload
                                     → Wait for load
                                     → Swap to original

3. User Interaction (Swipe):
   touchstart → Create TouchGestureState
             → touchend → Validate gesture
                       → Calculate angle/distance
                       → If valid: showNextImage() / showPreviousImage()
                                 → openFullscreen(newIndex)
```

---

## Persistence

**None**. All data is transient (client-side state) or static (HTML data attributes generated at build time).

**No localStorage, sessionStorage, cookies, or backend API calls**. Fully static architecture maintained.

---

## Validation Summary

| Entity | Server-Side Validation | Client-Side Validation |
|--------|----------------------|----------------------|
| TouchGestureState | N/A | Angle threshold, distance threshold |
| ImageLoadingState | N/A | Index bounds, URL format |
| ModalState | N/A | Index bounds, category consistency |
| CSSLayoutState | N/A | Browser CSS validation |
| DOM Data Attributes | Build-time (YAML schema) | Runtime (non-null checks) |

---

## Performance Considerations

- **ImageLoadingState**: Single `Image()` object per session (not per image), reused via nulling
- **TouchGestureState**: Minimal memory (<100 bytes), created/destroyed per gesture
- **ModalState**: Single global object, references DOM elements (no duplication)
- **images array**: Populated once on init, reused for all interactions (~5KB for 100 images)

---

## Accessibility Considerations

- **DOM Data Attributes**: All text content (title, description) must be HTML-escaped (handled by Jinja2 `| e` filter)
- **ImageLoadingState**: `alt` text applied to both thumbnail and original (no duplicate screen reader announcements)
- **ModalState**: Focus management (previousFocus) ensures keyboard users return to correct context

---

## Summary

This feature introduces minimal data model complexity. Primary entities are client-side JavaScript state objects (`TouchGestureState`, `ImageLoadingState`, `ModalState`) and CSS custom properties. No backend changes, no persistence layer, no external APIs. Data flow is entirely local: build-time generation → static HTML → runtime JavaScript state management.
