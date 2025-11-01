/**
 * Modern Image Gallery - Progressive Enhancement
 *
 * Features:
 * - Native lazy loading with fallback
 * - Image load state tracking
 * - Keyboard navigation preparation
 * - Performance monitoring
 */

(function() {
  'use strict';

  /**
   * Initialize gallery when DOM is ready
   */
  function init() {
    setupLazyLoading();
    setupImageLoadTracking();
    setupKeyboardNavigation();
  }

  /**
   * Setup lazy loading for images with fallback for older browsers
   */
  function setupLazyLoading() {
    const images = document.querySelectorAll('.image-item img');

    // Check for native lazy loading support
    if ('loading' in HTMLImageElement.prototype) {
      // Native lazy loading is supported
      images.forEach(img => {
        img.setAttribute('loading', 'lazy');
      });
    } else {
      // Fallback: Use IntersectionObserver
      if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              const img = entry.target;
              if (img.dataset.src) {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
              }
              observer.unobserve(img);
            }
          });
        }, {
          rootMargin: '50px 0px',
          threshold: 0.01
        });

        images.forEach(img => {
          // Move src to data-src for lazy loading
          if (img.src && !img.dataset.src) {
            img.dataset.src = img.src;
            img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"%3E%3C/svg%3E';
          }
          imageObserver.observe(img);
        });
      }
    }
  }

  /**
   * Track image load states for performance and UX
   */
  function setupImageLoadTracking() {
    const images = document.querySelectorAll('.image-item img');
    let loadedCount = 0;
    const totalCount = images.length;

    images.forEach(img => {
      // Skip if already loaded
      if (img.complete && img.naturalHeight !== 0) {
        img.classList.add('loaded');
        loadedCount++;
        return;
      }

      // Track load event
      img.addEventListener('load', function() {
        this.classList.add('loaded');
        loadedCount++;

        // Log when all images are loaded (for debugging/metrics)
        if (loadedCount === totalCount) {
          console.log('Gallery: All images loaded');
          markPerformanceMilestone('imagesLoaded');
        }
      }, { once: true });

      // Handle errors gracefully
      img.addEventListener('error', function() {
        this.classList.add('error');
        this.alt = 'Image failed to load';
        loadedCount++;
        console.warn('Failed to load image:', this.src);
      }, { once: true });
    });

    // Report initial load count
    if (loadedCount === totalCount) {
      markPerformanceMilestone('imagesLoaded');
    }
  }

  /**
   * Setup keyboard navigation for accessibility
   */
  function setupKeyboardNavigation() {
    const imageItems = document.querySelectorAll('.image-item');

    imageItems.forEach((item, index) => {
      // Make images keyboard focusable
      if (!item.hasAttribute('tabindex')) {
        item.setAttribute('tabindex', '0');
      }

      // Handle keyboard activation (Enter/Space)
      item.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          this.click();
        }
      });
    });
  }

  /**
   * Mark performance milestones for monitoring
   */
  function markPerformanceMilestone(name) {
    if ('performance' in window && window.performance.mark) {
      try {
        performance.mark(name);
      } catch (e) {
        // Ignore performance API errors
      }
    }
  }

  /**
   * Get performance metrics (for debugging)
   */
  function getPerformanceMetrics() {
    if (!('performance' in window)) {
      return null;
    }

    const navigation = performance.getEntriesByType('navigation')[0];
    const paint = performance.getEntriesByType('paint');

    return {
      domContentLoaded: navigation ? navigation.domContentLoadedEventEnd : null,
      loadComplete: navigation ? navigation.loadEventEnd : null,
      firstPaint: paint.find(entry => entry.name === 'first-paint')?.startTime || null,
      firstContentfulPaint: paint.find(entry => entry.name === 'first-contentful-paint')?.startTime || null
    };
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export for debugging
  window.galleryDebug = {
    getPerformanceMetrics: getPerformanceMetrics
  };

})();
