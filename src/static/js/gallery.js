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
   * Setup sequential lazy loading for images - top images load first
   */
  function setupLazyLoading() {
    const images = document.querySelectorAll('.image-item img');

    // Separate above-the-fold images from below-the-fold
    const viewportHeight = window.innerHeight;
    const aboveFoldImages = [];
    const belowFoldImages = [];

    images.forEach(img => {
      const rect = img.getBoundingClientRect();
      if (rect.top < viewportHeight) {
        aboveFoldImages.push(img);
      } else {
        belowFoldImages.push(img);
      }
    });

    // Load above-the-fold images immediately with high priority
    aboveFoldImages.forEach(img => {
      img.setAttribute('loading', 'eager');
      img.setAttribute('decoding', 'async');
      img.setAttribute('fetchpriority', 'high');
    });

    // Load below-the-fold images lazily as user scrolls
    belowFoldImages.forEach(img => {
      img.setAttribute('loading', 'lazy');
      img.setAttribute('decoding', 'async');
      img.setAttribute('fetchpriority', 'low');
    });

    // Optional: Use IntersectionObserver for progress tracking
    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            // Image is entering viewport - browser will start loading it
            // due to loading="lazy" attribute
          }
        });
      }, {
        // Start observing when image is 300px from viewport
        rootMargin: '300px 0px',
        threshold: 0.01
      });

      // Observe below-fold images for analytics/debugging
      belowFoldImages.forEach(img => {
        imageObserver.observe(img);
      });
    }
  }

  /**
   * Track image load states for performance and UX with blur placeholder support
   */
  function setupImageLoadTracking() {
    const images = document.querySelectorAll('.image-item img');
    let loadedCount = 0;
    const totalCount = images.length;

    images.forEach(img => {
      const container = img.closest('.image-item');
      const hasBlurPlaceholder = container && container.style.backgroundImage;

      // Skip if already loaded
      if (img.complete && img.naturalHeight !== 0) {
        img.classList.add('loaded');
        loadedCount++;
        return;
      }

      // Track load start time for intelligent skip logic
      const loadStartTime = performance.now();

      // Track load event
      img.addEventListener('load', function() {
        const loadDuration = performance.now() - loadStartTime;

        // Intelligent skip: if image loads very fast (<100ms), skip fade animation
        if (loadDuration < 100 && hasBlurPlaceholder) {
          // Image was cached/fast - immediately show without fade
          this.style.transition = 'none';
          this.classList.add('loaded');
          // Force reflow to apply transition:none before removing it
          void this.offsetHeight;
          this.style.transition = '';
        } else {
          // Normal progressive loading with fade
          this.classList.add('loaded');
        }

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
        // Keep blur placeholder on error as fallback
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
