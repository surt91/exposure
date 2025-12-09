/**
 * Accessibility Helper Functions
 *
 * Provides reusable accessibility utilities for:
 * - Focus management
 * - ARIA attribute handling
 * - Keyboard navigation
 * - Screen reader announcements
 */

(function() {
  'use strict';

  /**
   * Standard selector for all focusable elements
   * Includes proper handling of disabled elements for accessibility
   * @constant {string}
   */
  const FOCUSABLE_ELEMENTS_SELECTOR = [
    'a[href]',
    'button:not([disabled])',
    'textarea:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    '[tabindex]:not([tabindex="-1"])'
  ].join(', ');

  /**
   * Focus trap manager for modal dialogs
   * @param {HTMLElement} container - Container to trap focus within
   */
  function createFocusTrap(container) {
    const focusableSelectors = FOCUSABLE_ELEMENTS_SELECTOR;

    return {
      activate: function() {
        const focusableElements = container.querySelectorAll(focusableSelectors);
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        container.addEventListener('keydown', function trapHandler(e) {
          if (e.key !== 'Tab') return;

          if (e.shiftKey) {
            // Backwards
            if (document.activeElement === firstElement) {
              e.preventDefault();
              lastElement.focus();
            }
          } else {
            // Forwards
            if (document.activeElement === lastElement) {
              e.preventDefault();
              firstElement.focus();
            }
          }
        });

        // Focus first element
        if (firstElement) {
          firstElement.focus();
        }
      },

      deactivate: function() {
        // Remove focus trap (handler is anonymous, so this is simplified)
        // In production, store handler reference to remove it properly
      }
    };
  }

  /**
   * Announce content to screen readers
   * @param {string} message - Message to announce
   * @param {string} priority - 'polite' or 'assertive'
   */
  function announce(message, priority = 'polite') {
    let announcer = document.getElementById('a11y-announcer');

    if (!announcer) {
      announcer = document.createElement('div');
      announcer.id = 'a11y-announcer';
      announcer.setAttribute('role', 'status');
      announcer.setAttribute('aria-live', priority);
      announcer.setAttribute('aria-atomic', 'true');
      announcer.style.position = 'absolute';
      announcer.style.left = '-10000px';
      announcer.style.width = '1px';
      announcer.style.height = '1px';
      announcer.style.overflow = 'hidden';
      document.body.appendChild(announcer);
    }

    // Update aria-live region
    announcer.setAttribute('aria-live', priority);
    announcer.textContent = message;

    // Clear after announcement
    setTimeout(() => {
      announcer.textContent = '';
    }, 1000);
  }

  /**
   * Save and restore focus for modals/overlays
   */
  class FocusManager {
    constructor() {
      this.previousFocus = null;
    }

    saveFocus() {
      this.previousFocus = document.activeElement;
    }

    restoreFocus() {
      if (this.previousFocus && this.previousFocus.focus) {
        this.previousFocus.focus();
      }
      this.previousFocus = null;
    }

    getFocusableElements(container) {
      return Array.from(container.querySelectorAll(FOCUSABLE_ELEMENTS_SELECTOR));
    }
  }

  /**
   * Add skip link for keyboard navigation
   */
  function addSkipLink() {
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'skip-link';
    skipLink.style.position = 'absolute';
    skipLink.style.top = '-40px';
    skipLink.style.left = '0';
    skipLink.style.background = '#000';
    skipLink.style.color = '#fff';
    skipLink.style.padding = '8px';
    skipLink.style.zIndex = '100';
    skipLink.style.transition = 'top 0.2s';

    skipLink.addEventListener('focus', function() {
      this.style.top = '0';
    });

    skipLink.addEventListener('blur', function() {
      this.style.top = '-40px';
    });

    document.body.insertBefore(skipLink, document.body.firstChild);
  }

  /**
   * Ensure images have alt text
   */
  function validateImageAccessibility() {
    const images = document.querySelectorAll('img');
    let missingAlt = 0;

    images.forEach(img => {
      if (!img.hasAttribute('alt')) {
        console.warn('Image missing alt attribute:', img.src);
        img.alt = ''; // Decorative image
        missingAlt++;
      }
    });

    if (missingAlt > 0) {
      console.warn(`Found ${missingAlt} images without alt attributes`);
    }

    return missingAlt === 0;
  }

  /**
   * Check color contrast (basic check)
   */
  function checkContrast() {
    // This is a simplified version
    // Production code should use a proper contrast checker
    console.log('Color contrast validation should be done with axe or similar tools');
  }

  /**
   * Initialize accessibility features
   */
  function init() {
    // Add skip link
    addSkipLink();

    // Validate images
    validateImageAccessibility();

    // Mark main content
    const main = document.querySelector('main');
    if (main && !main.id) {
      main.id = 'main-content';
    }
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export utilities
  window.a11y = {
    FOCUSABLE_ELEMENTS_SELECTOR: FOCUSABLE_ELEMENTS_SELECTOR,
    createFocusTrap: createFocusTrap,
    announce: announce,
    FocusManager: FocusManager,
    validateImageAccessibility: validateImageAccessibility
  };

})();
