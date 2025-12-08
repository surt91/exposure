# Control Visibility Manager API Contract

**Component**: `ControlVisibilityManager` (JavaScript)
**Type**: Frontend State Management
**Version**: 1.0.0

## Purpose

Manage visibility state of navigation controls (arrows, close button) in fullscreen image overlay on mobile devices. Implements auto-hide behavior (3-second timer), tap-to-reveal interaction, and maintains keyboard accessibility.

---

## API Interface

```typescript
interface ControlVisibilityManager {
  // State
  state: ControlVisibilityState;
  hideTimer: number | null;
  isMobile: boolean;

  // Methods
  showControls(): void;
  hideControls(): void;
  resetHideTimer(): void;
  handleUserInteraction(event: Event): void;
  destroy(): void;
}

enum ControlVisibilityState {
  HIDDEN = 'hidden',
  VISIBLE = 'visible',
  PENDING = 'pending'
}
```

---

## Constructor Contract

**Signature**:
```typescript
constructor(
  controlsElement: HTMLElement,
  options?: ControlVisibilityOptions
)
```

**Parameters**:
- `controlsElement`: DOM element containing navigation controls
- `options.autoHideDelay`: Time before auto-hide (default: 3000ms)
- `options.transitionDuration`: CSS transition duration (default: 300ms)
- `options.mobileBreakpoint`: Max width for mobile mode (default: 767px)

**Example**:
```javascript
const controls = document.querySelector('.fullscreen-controls');
const manager = new ControlVisibilityManager(controls, {
  autoHideDelay: 3000,
  transitionDuration: 300,
  mobileBreakpoint: 767
});
```

---

## Method Contracts

### showControls()

**Purpose**: Display navigation controls and start auto-hide timer.

**Signature**:
```typescript
showControls(): void
```

**Preconditions**:
- `controlsElement` must exist in DOM
- Only applies on mobile viewports (< 768px)

**Behavior**:
1. Check if mobile mode active (viewport width < 768px)
2. If not mobile: return early (controls always visible on desktop)
3. Add `visible` class to controls element
4. Set `state` to `VISIBLE`
5. Start 3-second auto-hide timer
6. Emit custom event: `controlsvisible`

**Postconditions**:
- Controls have `opacity: 1` (CSS transition)
- `pointer-events: auto` enabled
- Hide timer active
- `state` is `VISIBLE`

**Example**:
```javascript
manager.showControls();
// Controls fade in over 300ms, auto-hide after 3 seconds
```

---

### hideControls()

**Purpose**: Hide navigation controls (visual only, maintain keyboard access).

**Signature**:
```typescript
hideControls(): void
```

**Preconditions**:
- Only applies on mobile viewports
- Current `state` is `VISIBLE`

**Behavior**:
1. Check if mobile mode active
2. If not mobile: return early
3. Remove `visible` class from controls element
4. Set `state` to `HIDDEN`
5. Clear any active hide timer
6. Emit custom event: `controlshidden`

**Postconditions**:
- Controls have `opacity: 0` (CSS transition)
- `pointer-events: none` (click-through)
- Controls remain focusable (`:focus-within` keeps visible)
- Hide timer cleared

**Accessibility Note**:
```css
/* Controls remain accessible via keyboard even when hidden */
.fullscreen-controls:focus-within {
  opacity: 1;
  pointer-events: auto;
}
```

**Example**:
```javascript
manager.hideControls();
// Controls fade out over 300ms
```

---

### resetHideTimer()

**Purpose**: Reset the 3-second auto-hide countdown.

**Signature**:
```typescript
resetHideTimer(): void
```

**Behavior**:
1. Clear existing timer (if any)
2. Start new 3-second timer
3. Timer callback: `hideControls()`

**Use Cases**:
- User taps on image (extends visibility)
- User clicks navigation button (extends visibility)
- User scrolls metadata area (extends visibility)

**Example**:
```javascript
// Reset timer on button click
nextButton.addEventListener('click', () => {
  manager.resetHideTimer();
  // Controls stay visible for another 3 seconds
});
```

---

### handleUserInteraction(event)

**Purpose**: Handle tap/click events to toggle or extend control visibility.

**Signature**:
```typescript
handleUserInteraction(event: Event): void
```

**Parameters**:
- `event`: Mouse or touch event from user interaction

**Behavior**:
```javascript
if (state === HIDDEN) {
  showControls();  // Reveal controls
} else if (state === VISIBLE) {
  resetHideTimer();  // Extend visibility
}
```

**Event Binding**:
```javascript
// Tap on image area reveals controls
overlay.addEventListener('click', (event) => {
  if (event.target.matches('.fullscreen-image')) {
    manager.handleUserInteraction(event);
  }
});
```

---

### destroy()

**Purpose**: Clean up timers and event listeners.

**Signature**:
```typescript
destroy(): void
```

**Behavior**:
1. Clear active hide timer
2. Remove event listeners
3. Reset state to `HIDDEN`
4. Remove `visible` class from controls

**Use Case**: Called when exiting fullscreen mode

**Example**:
```javascript
// On fullscreen exit
fullscreenManager.addEventListener('fullscreenexit', () => {
  controlManager.destroy();
});
```

---

## State Transitions

```
┌─────────┐   showControls()    ┌─────────┐
│ HIDDEN  │ ─────────────────> │ VISIBLE │
│         │ <───────────────── │         │
└─────────┘   hideControls()    └─────────┘
     │              │
     │              │ resetHideTimer()
     │              └─────────┐
     │                        │
     └────────────────────────┘
            (stays in same state)
```

**Rules**:
- `HIDDEN` → `VISIBLE`: On user tap or manual `showControls()`
- `VISIBLE` → `HIDDEN`: After 3-second timer or manual `hideControls()`
- `VISIBLE` → `VISIBLE`: Timer reset extends visibility
- Desktop mode: Always `VISIBLE` (no transitions)

---

## Custom Events

### controlsvisible

**Fired**: When controls become visible

**Event Detail**:
```javascript
{
  timestamp: number,
  triggerType: 'user' | 'manual',
  isMobile: boolean
}
```

**Usage**:
```javascript
controls.addEventListener('controlsvisible', (event) => {
  console.log('Controls shown:', event.detail);
  // Announce to screen readers
  announce('Navigation controls visible');
});
```

---

### controlshidden

**Fired**: When controls become hidden

**Event Detail**:
```javascript
{
  timestamp: number,
  reason: 'timeout' | 'manual' | 'navigation',
  isMobile: boolean
}
```

**Usage**:
```javascript
controls.addEventListener('controlshidden', (event) => {
  console.log('Controls hidden:', event.detail.reason);
});
```

---

## CSS Contract

The manager expects these CSS rules to be defined:

```css
/* Mobile only */
@media (max-width: 767px) {
  .fullscreen-controls {
    opacity: 0;
    pointer-events: none;
    transition: opacity 300ms ease-in-out;
  }

  .fullscreen-controls.visible {
    opacity: 1;
    pointer-events: auto;
  }

  /* Maintain keyboard accessibility */
  .fullscreen-controls:focus-within {
    opacity: 1;
    pointer-events: auto;
  }
}

/* Desktop: always visible */
@media (min-width: 768px) {
  .fullscreen-controls {
    opacity: 1;
    pointer-events: auto;
  }
}
```

**Required CSS Classes**:
- `.fullscreen-controls`: Container for all navigation controls
- `.visible`: Added/removed by manager to control visibility

---

## Accessibility Requirements

### Keyboard Navigation
Controls MUST remain keyboard-accessible even when visually hidden:
- Tab key can still focus controls
- `:focus-within` CSS makes controls visible when focused
- Screen reader users can navigate to controls regardless of visual state

### Screen Reader Announcements
```javascript
// Announce visibility changes
function announce(message) {
  const liveRegion = document.querySelector('[role="status"]');
  liveRegion.textContent = message;
}

// Usage in showControls()
showControls() {
  // ... show logic ...
  announce('Navigation controls visible. Use arrow keys or tap to navigate.');
}
```

### Reduced Motion Support
```css
@media (prefers-reduced-motion: reduce) {
  .fullscreen-controls {
    transition: none; /* Instant visibility changes */
  }
}
```

---

## Configuration Options

```typescript
interface ControlVisibilityOptions {
  autoHideDelay: number;       // Default: 3000ms (3 seconds)
  transitionDuration: number;  // Default: 300ms
  mobileBreakpoint: number;    // Default: 767px
  enableOnDesktop: boolean;    // Default: false (always visible on desktop)
  announceToScreenReader: boolean; // Default: true
}
```

**Usage**:
```javascript
const manager = new ControlVisibilityManager(controls, {
  autoHideDelay: 5000,  // 5 seconds instead of 3
  transitionDuration: 200,  // Faster transition
  mobileBreakpoint: 600,  // Tablets get auto-hide too
  announceToScreenReader: true
});
```

---

## Integration with Other Components

### With FullscreenManager
```javascript
// Show controls when entering fullscreen
fullscreenManager.addEventListener('fullscreenenter', () => {
  if (fullscreenManager.mode === 'fullscreen' ||
      fullscreenManager.mode === 'fallback') {
    controlManager.showControls();
  }
});

// Clean up when exiting
fullscreenManager.addEventListener('fullscreenexit', () => {
  controlManager.destroy();
});
```

### With Swipe Navigation
```javascript
// Hide controls during swipe gesture
overlay.addEventListener('touchstart', () => {
  if (controlManager.state === 'visible') {
    controlManager.hideControls();
  }
});

// Show controls after swipe completes
overlay.addEventListener('touchend', () => {
  controlManager.showControls();
});
```

### With Progressive Image Loader
```javascript
// Keep controls visible while image loads
imageLoader.addEventListener('loadstart', () => {
  controlManager.resetHideTimer();
});

// Resume auto-hide after load completes
imageLoader.addEventListener('loadend', () => {
  controlManager.resetHideTimer();
});
```

---

## Error Handling

### Missing Controls Element
```javascript
constructor(controlsElement) {
  if (!controlsElement) {
    throw new Error('ControlVisibilityManager: controlsElement is required');
  }
  if (!(controlsElement instanceof HTMLElement)) {
    throw new TypeError('ControlVisibilityManager: controlsElement must be HTMLElement');
  }
}
```

### Media Query Not Supported
```javascript
constructor() {
  if (!window.matchMedia) {
    console.warn('matchMedia not supported, assuming mobile');
    this.isMobile = true;  // Graceful degradation
  } else {
    this.isMobile = window.matchMedia('(max-width: 767px)').matches;
  }
}
```

### Timer Issues
```javascript
resetHideTimer() {
  try {
    clearTimeout(this.hideTimer);
    this.hideTimer = setTimeout(() => this.hideControls(), this.options.autoHideDelay);
  } catch (error) {
    console.error('Failed to set hide timer:', error);
    // Fallback: keep controls visible
  }
}
```

---

## Testing Contract

### Unit Tests

```javascript
describe('ControlVisibilityManager', () => {
  test('shows controls on mobile', () => {
    // Mock mobile viewport
    window.matchMedia = jest.fn(() => ({ matches: true }));

    const manager = new ControlVisibilityManager(controls);
    manager.showControls();

    expect(controls.classList.contains('visible')).toBe(true);
    expect(manager.state).toBe('visible');
  });

  test('hides controls after 3 seconds', (done) => {
    const manager = new ControlVisibilityManager(controls);
    manager.showControls();

    setTimeout(() => {
      expect(manager.state).toBe('hidden');
      done();
    }, 3100);
  });

  test('resets timer on user interaction', (done) => {
    const manager = new ControlVisibilityManager(controls);
    manager.showControls();

    // Reset timer after 2 seconds
    setTimeout(() => {
      manager.resetHideTimer();
    }, 2000);

    // Controls should still be visible at 4 seconds (2s + reset)
    setTimeout(() => {
      expect(manager.state).toBe('visible');
      done();
    }, 4000);
  });

  test('does not hide on desktop', () => {
    // Mock desktop viewport
    window.matchMedia = jest.fn(() => ({ matches: false }));

    const manager = new ControlVisibilityManager(controls);
    manager.hideControls();

    expect(manager.state).toBe('visible'); // Stays visible
  });
});
```

### Integration Tests

```javascript
test('maintains keyboard accessibility when hidden', () => {
  const manager = new ControlVisibilityManager(controls);
  manager.hideControls();

  // Controls are visually hidden
  expect(controls.style.opacity).toBe('0');

  // But still focusable
  const button = controls.querySelector('button');
  button.focus();
  expect(document.activeElement).toBe(button);

  // And become visible on focus
  expect(window.getComputedStyle(controls).opacity).toBe('1');
});
```

---

## Performance Requirements

- **State Transitions**: < 10ms (excluding CSS animation)
- **Timer Accuracy**: ±100ms (3000ms timer acceptable 2900-3100ms)
- **Memory**: No leaks on repeated show/hide cycles
- **CPU**: < 1% CPU usage during idle (timer only)

---

## Version History

- **1.0.0** (2025-12-08): Initial API contract definition
