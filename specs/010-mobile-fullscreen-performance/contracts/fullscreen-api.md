# Fullscreen API Contract

**Component**: `FullscreenManager` (JavaScript)
**Type**: Browser Fullscreen API Wrapper
**Version**: 1.0.0

## Purpose

Manage fullscreen mode for image overlay viewing on mobile and desktop. Abstracts browser Fullscreen API with fallback support for iOS Safari and provides consistent interface for entering/exiting fullscreen state.

---

## API Interface

```typescript
interface FullscreenManager {
  // State
  mode: FullscreenMode;
  element: HTMLElement;

  // Methods
  enterFullscreen(): Promise<void>;
  exitFullscreen(): Promise<void>;
  isFullscreen(): boolean;
  handleOrientationChange(): void;
}

enum FullscreenMode {
  NORMAL = 'normal',
  FULLSCREEN = 'fullscreen',  // Native API active
  FALLBACK = 'fallback'        // iOS Safari fallback
}
```

---

## Method Contracts

### enterFullscreen()

**Purpose**: Enter fullscreen mode for the image overlay element.

**Signature**:
```typescript
async enterFullscreen(): Promise<void>
```

**Preconditions**:
- `this.element` must be a valid DOM element
- Current `mode` must be `NORMAL`
- Element must be attached to DOM

**Behavior**:
1. Attempt to use native Fullscreen API (`element.requestFullscreen()`)
2. If API unavailable or fails, fall back to iOS Safari simulation
3. Update `mode` to `FULLSCREEN` or `FALLBACK`
4. Emit custom event: `fullscreenenter`

**Postconditions**:
- Element fills entire viewport
- Browser UI minimized/hidden (if supported)
- `mode` is `FULLSCREEN` or `FALLBACK`
- Navigation controls initialized

**Error Handling**:
- If Fullscreen API throws: catch, log warning, apply fallback
- If fallback fails: log error, remain in NORMAL mode

**Example**:
```javascript
const manager = new FullscreenManager(overlayElement);

try {
  await manager.enterFullscreen();
  console.log('Entered fullscreen mode:', manager.mode);
} catch (error) {
  console.error('Fullscreen failed:', error);
}
```

---

### exitFullscreen()

**Purpose**: Exit fullscreen mode and return to normal gallery view.

**Signature**:
```typescript
async exitFullscreen(): Promise<void>
```

**Preconditions**:
- Current `mode` must be `FULLSCREEN` or `FALLBACK`

**Behavior**:
1. If in `FULLSCREEN` mode: call `document.exitFullscreen()`
2. If in `FALLBACK` mode: remove fixed positioning, restore scroll
3. Update `mode` to `NORMAL`
4. Emit custom event: `fullscreenexit`

**Postconditions**:
- Element returns to normal flow
- Browser UI restored
- `mode` is `NORMAL`
- Scroll position restored (fallback mode only)

**Error Handling**:
- If exit fails: force fallback cleanup, log error
- Always guarantee return to NORMAL state

**Example**:
```javascript
await manager.exitFullscreen();
console.log('Exited fullscreen, mode:', manager.mode);
```

---

### isFullscreen()

**Purpose**: Check if currently in fullscreen mode (any type).

**Signature**:
```typescript
isFullscreen(): boolean
```

**Returns**:
- `true` if `mode` is `FULLSCREEN` or `FALLBACK`
- `false` if `mode` is `NORMAL`

**Example**:
```javascript
if (manager.isFullscreen()) {
  console.log('Currently in fullscreen mode');
}
```

---

### handleOrientationChange()

**Purpose**: Respond to device orientation changes while in fullscreen.

**Signature**:
```typescript
handleOrientationChange(): void
```

**Behavior**:
1. If in `FULLSCREEN` mode: no action (browser handles automatically)
2. If in `FALLBACK` mode: recalculate viewport dimensions, update styles
3. Emit custom event: `fullscreenorientationchange`

**Event Binding**:
```javascript
window.addEventListener('orientationchange', () => {
  manager.handleOrientationChange();
});

window.addEventListener('resize', () => {
  manager.handleOrientationChange();
});
```

---

## Browser API Integration

### Native Fullscreen API

**Supported Browsers**:
- Chrome 71+ (mobile), 71+ (desktop)
- Firefox 64+ (mobile), 64+ (desktop)
- Safari 16.4+ (macOS), **NOT SUPPORTED on iOS**
- Edge 79+

**API Calls**:
```javascript
// Enter fullscreen
element.requestFullscreen()
  .then(() => console.log('Fullscreen entered'))
  .catch(err => console.warn('Fullscreen failed', err));

// Exit fullscreen
document.exitFullscreen()
  .then(() => console.log('Fullscreen exited'))
  .catch(err => console.warn('Exit failed', err));

// Check fullscreen state
const isFullscreen = !!document.fullscreenElement;

// Listen for fullscreen changes
document.addEventListener('fullscreenchange', () => {
  console.log('Fullscreen state changed');
});
```

---

## iOS Safari Fallback

**Why Needed**: iOS Safari does not support Fullscreen API for non-media elements.

**Fallback Strategy**:
```javascript
function applyIOSFallback(element) {
  // Save current scroll position
  const scrollY = window.scrollY;

  // Apply fixed positioning to cover viewport
  element.style.position = 'fixed';
  element.style.top = '0';
  element.style.left = '0';
  element.style.width = '100vw';
  element.style.height = '100vh';
  element.style.zIndex = '9999';

  // Prevent body scroll
  document.body.style.overflow = 'hidden';
  document.body.style.position = 'fixed';
  document.body.style.top = `-${scrollY}px`;
  document.body.style.width = '100%';

  // Scroll to hide address bar (iOS Safari specific)
  window.scrollTo(0, 1);

  return { scrollY }; // Return for restoration
}

function exitIOSFallback(element, savedState) {
  // Remove fixed positioning
  element.style.position = '';
  element.style.top = '';
  element.style.left = '';
  element.style.width = '';
  element.style.height = '';
  element.style.zIndex = '';

  // Restore body scroll
  document.body.style.overflow = '';
  document.body.style.position = '';
  document.body.style.top = '';
  document.body.style.width = '';

  // Restore scroll position
  window.scrollTo(0, savedState.scrollY);
}
```

---

## Custom Events

### fullscreenenter

**Fired**: When entering fullscreen mode (any type)

**Event Detail**:
```javascript
{
  mode: 'fullscreen' | 'fallback',
  element: HTMLElement,
  timestamp: number
}
```

**Usage**:
```javascript
element.addEventListener('fullscreenenter', (event) => {
  console.log('Entered fullscreen:', event.detail.mode);
  // Initialize mobile control visibility
  controlManager.hideControls();
});
```

---

### fullscreenexit

**Fired**: When exiting fullscreen mode

**Event Detail**:
```javascript
{
  element: HTMLElement,
  timestamp: number
}
```

**Usage**:
```javascript
element.addEventListener('fullscreenexit', (event) => {
  console.log('Exited fullscreen');
  // Reset control visibility
  controlManager.showControls();
});
```

---

### fullscreenorientationchange

**Fired**: When device orientation changes in fullscreen

**Event Detail**:
```javascript
{
  mode: 'fullscreen' | 'fallback',
  orientation: 'portrait' | 'landscape',
  viewport: { width: number, height: number }
}
```

**Usage**:
```javascript
element.addEventListener('fullscreenorientationchange', (event) => {
  console.log('Orientation changed:', event.detail.orientation);
  // Recalculate image dimensions
  resizeImage(event.detail.viewport);
});
```

---

## Error Handling

### Fullscreen API Unavailable
```javascript
if (!document.fullscreenEnabled) {
  console.warn('Fullscreen API not supported, using fallback');
  applyIOSFallback(element);
}
```

### User Denied Permission
```javascript
element.requestFullscreen().catch((error) => {
  if (error.name === 'NotAllowedError') {
    console.warn('User denied fullscreen permission');
    // Continue with normal overlay (don't force fallback)
  }
});
```

### Fullscreen Exit During Navigation
```javascript
document.addEventListener('fullscreenchange', () => {
  if (!document.fullscreenElement && manager.mode === 'fullscreen') {
    // User pressed ESC or browser exited fullscreen
    manager.exitFullscreen(); // Clean up state
  }
});
```

---

## Testing Contract

### Manual Testing Requirements

1. **Desktop Chrome/Firefox**: Verify native fullscreen API works
2. **iPhone Safari**: Verify fallback mode applies and hides address bar
3. **Android Chrome**: Verify native fullscreen API works
4. **Orientation Changes**: Rotate device, verify layout adjusts
5. **ESC Key**: Press ESC in fullscreen, verify clean exit
6. **Back Button**: Tap back button in fullscreen (Android), verify exit

### Automated Testing

```javascript
// Unit test: Mode transitions
test('enters fullscreen mode', async () => {
  const manager = new FullscreenManager(element);
  await manager.enterFullscreen();
  expect(manager.mode).toMatch(/fullscreen|fallback/);
});

// Unit test: Exit restores state
test('exits fullscreen and restores scroll', async () => {
  window.scrollTo(0, 500);
  const manager = new FullscreenManager(element);
  await manager.enterFullscreen();
  await manager.exitFullscreen();
  expect(manager.mode).toBe('normal');
  expect(window.scrollY).toBe(500);
});

// Integration test: Event emission
test('emits fullscreenenter event', async () => {
  const listener = jest.fn();
  element.addEventListener('fullscreenenter', listener);

  const manager = new FullscreenManager(element);
  await manager.enterFullscreen();

  expect(listener).toHaveBeenCalledWith(
    expect.objectContaining({
      detail: expect.objectContaining({ mode: expect.any(String) })
    })
  );
});
```

---

## Performance Requirements

- **Enter Fullscreen**: < 100ms (perceived as instant)
- **Exit Fullscreen**: < 100ms
- **Orientation Change**: < 50ms to recalculate layout
- **Memory**: No memory leaks on repeated enter/exit cycles

---

## Browser Compatibility Matrix

| Browser           | Version | Native API | Fallback | Notes                     |
|-------------------|---------|------------|----------|---------------------------|
| Chrome Mobile     | 71+     | ✅          | N/A      | Full support              |
| Safari iOS        | 11.3+   | ❌          | ✅        | Fallback required         |
| Firefox Mobile    | 64+     | ✅          | N/A      | Full support              |
| Samsung Internet  | 10+     | ✅          | N/A      | Full support              |
| Chrome Desktop    | 71+     | ✅          | N/A      | Full support              |
| Safari macOS      | 16.4+   | ✅          | N/A      | Limited (media only <16.4)|
| Firefox Desktop   | 64+     | ✅          | N/A      | Full support              |
| Edge              | 79+     | ✅          | N/A      | Full support              |

---

## Version History

- **1.0.0** (2025-12-08): Initial API contract definition
