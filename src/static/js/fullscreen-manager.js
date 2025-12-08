/**
 * Fullscreen Manager
 *
 * Manages true full-screen mode for mobile devices with browser UI hidden.
 * Supports native Fullscreen API with iOS Safari fallback.
 *
 * Features:
 * - Native Fullscreen API with vendor prefixes
 * - iOS Safari fallback (fixed positioning + viewport units)
 * - Orientation change handling
 * - State tracking
 */

class FullscreenManager {
  constructor(element) {
    this.element = element;
    this.mode = 'normal'; // 'normal', 'fullscreen', 'fallback', 'exiting'
    this.previousScrollPosition = 0;
    this.orientationChangeHandler = null;

    // Bind methods to preserve context
    this.handleOrientationChange = this.handleOrientationChange.bind(this);
    this.handleFullscreenChange = this.handleFullscreenChange.bind(this);
  }

  /**
   * Check if Fullscreen API is supported
   */
  isFullscreenSupported() {
    return !!(
      this.element.requestFullscreen ||
      this.element.webkitRequestFullscreen ||
      this.element.msRequestFullscreen ||
      this.element.mozRequestFullScreen
    );
  }

  /**
   * Check if currently in fullscreen mode
   */
  isFullscreen() {
    return this.mode === 'fullscreen' || this.mode === 'fallback';
  }

  /**
   * Enter fullscreen mode (native API or fallback)
   */
  async enterFullscreen() {
    if (this.isFullscreen()) {
      return; // Already in fullscreen
    }

    // Try native Fullscreen API first
    if (this.isFullscreenSupported()) {
      try {
        if (this.element.requestFullscreen) {
          await this.element.requestFullscreen();
        } else if (this.element.webkitRequestFullscreen) {
          await this.element.webkitRequestFullscreen();
        } else if (this.element.msRequestFullscreen) {
          await this.element.msRequestFullscreen();
        } else if (this.element.mozRequestFullScreen) {
          await this.element.mozRequestFullScreen();
        }
        this.mode = 'fullscreen';

        // Listen for fullscreen change events
        document.addEventListener('fullscreenchange', this.handleFullscreenChange);
        document.addEventListener('webkitfullscreenchange', this.handleFullscreenChange);
        document.addEventListener('msfullscreenchange', this.handleFullscreenChange);
        document.addEventListener('mozfullscreenchange', this.handleFullscreenChange);

        // Listen for orientation changes
        window.addEventListener('orientationchange', this.handleOrientationChange);
        window.addEventListener('resize', this.handleOrientationChange);

        return;
      } catch (error) {
        console.warn('Fullscreen API failed, using fallback:', error);
        // Fall through to fallback mode
      }
    }

    // Fallback mode (iOS Safari, older browsers)
    this.applyFallback();
  }

  /**
   * Exit fullscreen mode
   */
  async exitFullscreen() {
    if (!this.isFullscreen()) {
      return; // Not in fullscreen
    }

    this.mode = 'exiting';

    // Remove event listeners
    document.removeEventListener('fullscreenchange', this.handleFullscreenChange);
    document.removeEventListener('webkitfullscreenchange', this.handleFullscreenChange);
    document.removeEventListener('msfullscreenchange', this.handleFullscreenChange);
    document.removeEventListener('mozfullscreenchange', this.handleFullscreenChange);
    window.removeEventListener('orientationchange', this.handleOrientationChange);
    window.removeEventListener('resize', this.handleOrientationChange);

    // Exit native fullscreen if active
    if (document.fullscreenElement || document.webkitFullscreenElement ||
        document.msFullscreenElement || document.mozFullScreenElement) {
      try {
        if (document.exitFullscreen) {
          await document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
          await document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
          await document.msExitFullscreen();
        } else if (document.mozCancelFullScreen) {
          await document.mozCancelFullScreen();
        }
      } catch (error) {
        console.warn('Error exiting fullscreen:', error);
      }
    }

    // Exit fallback mode
    this.removeFallback();

    this.mode = 'normal';
  }

  /**
   * Apply iOS Safari fallback mode (fixed positioning)
   */
  applyFallback() {
    this.mode = 'fallback';
    this.previousScrollPosition = window.scrollY;

    // Fixed positioning to simulate fullscreen
    this.element.classList.add('fullscreen-fallback');
    this.element.style.position = 'fixed';
    this.element.style.top = '0';
    this.element.style.left = '0';
    this.element.style.width = '100vw';
    this.element.style.height = '100vh';
    this.element.style.zIndex = '9999';

    // Prevent body scroll
    document.body.style.overflow = 'hidden';
    document.body.style.position = 'fixed';
    document.body.style.width = '100%';
    document.body.style.top = `-${this.previousScrollPosition}px`;

    // Hide Safari address bar by scrolling
    setTimeout(() => {
      window.scrollTo(0, 1);
    }, 100);

    // Listen for orientation changes
    window.addEventListener('orientationchange', this.handleOrientationChange);
    window.addEventListener('resize', this.handleOrientationChange);
  }

  /**
   * Remove fallback mode styles
   */
  removeFallback() {
    this.element.classList.remove('fullscreen-fallback');
    this.element.style.position = '';
    this.element.style.top = '';
    this.element.style.left = '';
    this.element.style.width = '';
    this.element.style.height = '';
    this.element.style.zIndex = '';

    // Restore body scroll
    document.body.style.overflow = '';
    document.body.style.position = '';
    document.body.style.width = '';
    document.body.style.top = '';

    // Restore scroll position
    window.scrollTo(0, this.previousScrollPosition);
  }

  /**
   * Handle orientation changes in fullscreen/fallback mode
   */
  handleOrientationChange() {
    if (this.mode === 'fallback') {
      // Recalculate dimensions for fallback mode
      this.element.style.width = '100vw';
      this.element.style.height = '100vh';

      // Re-hide Safari address bar
      setTimeout(() => {
        window.scrollTo(0, 1);
      }, 100);
    }
    // Native fullscreen API handles orientation automatically
  }

  /**
   * Handle fullscreen change events (for native API)
   */
  handleFullscreenChange() {
    const isInFullscreen = !!(
      document.fullscreenElement ||
      document.webkitFullscreenElement ||
      document.msFullscreenElement ||
      document.mozFullScreenElement
    );

    if (!isInFullscreen && this.mode === 'fullscreen') {
      // User exited fullscreen (e.g., via ESC key)
      this.mode = 'normal';

      // Remove event listeners
      document.removeEventListener('fullscreenchange', this.handleFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', this.handleFullscreenChange);
      document.removeEventListener('msfullscreenchange', this.handleFullscreenChange);
      document.removeEventListener('mozfullscreenchange', this.handleFullscreenChange);
      window.removeEventListener('orientationchange', this.handleOrientationChange);
      window.removeEventListener('resize', this.handleOrientationChange);
    }
  }

  /**
   * Cleanup and remove all event listeners
   */
  destroy() {
    if (this.isFullscreen()) {
      this.exitFullscreen();
    }

    document.removeEventListener('fullscreenchange', this.handleFullscreenChange);
    document.removeEventListener('webkitfullscreenchange', this.handleFullscreenChange);
    document.removeEventListener('msfullscreenchange', this.handleFullscreenChange);
    document.removeEventListener('mozfullscreenchange', this.handleFullscreenChange);
    window.removeEventListener('orientationchange', this.handleOrientationChange);
    window.removeEventListener('resize', this.handleOrientationChange);
  }
}

// Make FullscreenManager globally available for other modules
if (typeof window !== 'undefined') {
  window.FullscreenManager = FullscreenManager;
}

// Export for use in Node.js/CommonJS (if needed for testing)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FullscreenManager;
}
