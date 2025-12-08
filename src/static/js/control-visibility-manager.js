/**
 * Control Visibility Manager
 *
 * Manages navigation control visibility on mobile full-screen mode.
 * Controls auto-hide after 3 seconds of inactivity, show on tap.
 *
 * Features:
 * - State machine (HIDDEN/VISIBLE/PENDING)
 * - 3-second auto-hide timer
 * - Mobile detection (< 768px)
 * - Keyboard accessibility (controls visible on focus)
 * - Reset timer on user interaction
 */

class ControlVisibilityManager {
  constructor(controlsElement, options = {}) {
    this.controlsElement = controlsElement;
    this.state = 'hidden'; // 'hidden', 'visible', 'pending'
    this.hideTimer = null;
    this.hideDelay = options.hideDelay || 3000; // Default 3 seconds
    this.mobileBreakpoint = options.mobileBreakpoint || 768; // Default 768px
    this.isMobile = this._checkIsMobile();

    // Bind methods to preserve context
    this.showControls = this.showControls.bind(this);
    this.hideControls = this.hideControls.bind(this);
    this.resetHideTimer = this.resetHideTimer.bind(this);
    this.handleUserInteraction = this.handleUserInteraction.bind(this);
    this.handleResize = this.handleResize.bind(this);
    this.handleFocusWithin = this.handleFocusWithin.bind(this);

    // Add event listeners
    this._attachEventListeners();
  }

  /**
   * Check if viewport is mobile size
   */
  _checkIsMobile() {
    return window.matchMedia(`(max-width: ${this.mobileBreakpoint - 1}px)`).matches;
  }

  /**
   * Attach event listeners for mobile detection and focus management
   */
  _attachEventListeners() {
    // Listen for viewport resize to update mobile state
    window.addEventListener('resize', this.handleResize);

    // Listen for focus within controls (keyboard accessibility)
    if (this.controlsElement) {
      this.controlsElement.addEventListener('focusin', this.handleFocusWithin);
    }
  }

  /**
   * Handle viewport resize
   */
  handleResize() {
    const wasMobile = this.isMobile;
    this.isMobile = this._checkIsMobile();

    // If transitioning from mobile to desktop, ensure controls are visible
    if (wasMobile && !this.isMobile) {
      this.showControls();
      clearTimeout(this.hideTimer);
    }

    // If transitioning from desktop to mobile, hide controls
    if (!wasMobile && this.isMobile) {
      this.hideControls();
    }
  }

  /**
   * Handle focus within controls (keyboard accessibility)
   */
  handleFocusWithin() {
    if (this.isMobile && this.state === 'hidden') {
      this.showControls();
    }
    this.resetHideTimer();
  }

  /**
   * Show navigation controls
   */
  showControls() {
    if (!this.isMobile) {
      // Desktop always shows controls
      if (this.controlsElement) {
        this.controlsElement.classList.add('visible');
      }
      this.state = 'visible';
      return;
    }

    // Mobile: show controls with fade-in animation
    if (this.state === 'visible') {
      // Already visible, just reset timer
      this.resetHideTimer();
      return;
    }

    this.state = 'pending';

    if (this.controlsElement) {
      this.controlsElement.classList.add('visible');
    }

    // Use requestAnimationFrame to ensure transition plays
    requestAnimationFrame(() => {
      this.state = 'visible';
    });

    // Start auto-hide timer
    this.resetHideTimer();
  }

  /**
   * Hide navigation controls
   */
  hideControls() {
    if (!this.isMobile) {
      // Desktop always shows controls
      return;
    }

    if (this.state === 'hidden') {
      // Already hidden
      return;
    }

    this.state = 'pending';

    // Clear any pending hide timer
    clearTimeout(this.hideTimer);
    this.hideTimer = null;

    if (this.controlsElement) {
      this.controlsElement.classList.remove('visible');
    }

    // Wait for transition to complete
    setTimeout(() => {
      if (this.state === 'pending') {
        this.state = 'hidden';
      }
    }, 300); // Match CSS transition duration
  }

  /**
   * Reset auto-hide timer (3 seconds)
   */
  resetHideTimer() {
    if (!this.isMobile) {
      // Desktop doesn't auto-hide
      return;
    }

    // Clear existing timer
    clearTimeout(this.hideTimer);

    // Start new timer
    this.hideTimer = setTimeout(() => {
      this.hideControls();
    }, this.hideDelay);
  }

  /**
   * Handle user interaction (tap, click)
   * Toggles visibility if hidden, resets timer if visible
   */
  handleUserInteraction(event) {
    if (!this.isMobile) {
      // Desktop doesn't need interaction handling
      return;
    }

    // Prevent event from bubbling to avoid conflicts
    if (event) {
      event.stopPropagation();
    }

    if (this.state === 'hidden') {
      // Show controls
      this.showControls();
    } else if (this.state === 'visible') {
      // Reset timer to keep controls visible longer
      this.resetHideTimer();
    }
  }

  /**
   * Immediately hide controls (for swipe navigation)
   */
  immediateHide() {
    if (!this.isMobile) {
      return;
    }

    clearTimeout(this.hideTimer);
    this.hideTimer = null;

    if (this.controlsElement) {
      this.controlsElement.classList.remove('visible');
    }

    this.state = 'hidden';
  }

  /**
   * Check if controls are currently visible
   */
  isVisible() {
    return this.state === 'visible' || this.state === 'pending';
  }

  /**
   * Force controls to be visible (e.g., when modal opens)
   */
  forceShow() {
    if (this.isMobile) {
      this.showControls();
    }
  }

  /**
   * Force controls to be hidden
   */
  forceHide() {
    if (this.isMobile) {
      this.hideControls();
    }
  }

  /**
   * Cleanup and remove all event listeners
   */
  destroy() {
    clearTimeout(this.hideTimer);
    this.hideTimer = null;

    window.removeEventListener('resize', this.handleResize);

    if (this.controlsElement) {
      this.controlsElement.removeEventListener('focusin', this.handleFocusWithin);
      this.controlsElement.classList.remove('visible');
    }
  }
}

// Make ControlVisibilityManager globally available
if (typeof window !== 'undefined') {
  window.ControlVisibilityManager = ControlVisibilityManager;
}

// Export for use in Node.js/CommonJS (if needed for testing)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ControlVisibilityManager;
}
