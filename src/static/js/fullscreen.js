/**
 * Fullscreen Image Overlay Controller
 *
 * Features:
 * - Open/close fullscreen modal
 * - Keyboard navigation (Esc, Left, Right, Tab)
 * - Focus management and trapping
 * - Accessibility (ARIA attributes)
 */

(function() {
  'use strict';

  let currentImageIndex = -1;
  let currentCategory = '';
  let images = [];
  let modal = null;
  let previousFocus = null;

  /**
   * Initialize fullscreen functionality
   */
  function init() {
    modal = document.getElementById('fullscreen-modal');
    if (!modal) return;

    // Get all image items
    images = Array.from(document.querySelectorAll('.image-item'));

    // Attach click handlers to all image items
    images.forEach((item, index) => {
      item.addEventListener('click', function() {
        openFullscreen(index);
      });
    });

    // Close button
    const closeBtn = modal.querySelector('.modal-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', closeFullscreen);
    }

    // Navigation buttons
    const prevBtn = modal.querySelector('.modal-prev');
    const nextBtn = modal.querySelector('.modal-next');

    if (prevBtn) {
      prevBtn.addEventListener('click', showPreviousImage);
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', showNextImage);
    }

    // Keyboard handlers
    document.addEventListener('keydown', handleKeyPress);

    // Click outside modal to close
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        closeFullscreen();
      }
    });
  }

  /**
   * Open fullscreen view for a specific image
   */
  function openFullscreen(index) {
    if (index < 0 || index >= images.length) return;

    // Mark performance milestone
    const startTime = performance.now();

    // Store current focus
    previousFocus = document.activeElement;

    currentImageIndex = index;
    const imageItem = images[index];

    // Get image data
    const img = imageItem.querySelector('img');
    const filename = imageItem.dataset.filename || '';
    currentCategory = imageItem.dataset.category || '';

    // Get metadata from YAML (if available in data attributes)
    const title = imageItem.dataset.title || img.alt || filename;
    const description = imageItem.dataset.description || '';

    // Get original image URL (use data-original-src if available for thumbnails, fallback to img.src)
    const originalSrc = imageItem.dataset.originalSrc || img.src;

    // Update modal content
    const modalImg = modal.querySelector('#modal-image');
    const modalTitle = modal.querySelector('#modal-title');
    const modalDescription = modal.querySelector('#modal-description');
    const modalCategory = modal.querySelector('#modal-category');

    if (modalImg) {
      modalImg.src = originalSrc;
      modalImg.alt = img.alt;
    }

    if (modalTitle) {
      modalTitle.textContent = title;
    }

    if (modalDescription) {
      modalDescription.textContent = description;
      modalDescription.style.display = description ? 'block' : 'none';
    }

    if (modalCategory) {
      modalCategory.textContent = `Category: ${currentCategory}`;
    }

    // Show modal
    modal.setAttribute('aria-hidden', 'false');
    modal.style.display = 'flex';

    // Focus on close button
    const closeBtn = modal.querySelector('.modal-close');
    if (closeBtn) {
      closeBtn.focus();
    }

    // Add visible class for animations
    requestAnimationFrame(() => {
      modal.classList.add('visible');
    });

    // Check performance
    const endTime = performance.now();
    const latency = endTime - startTime;
    if (latency > 300) {
      console.warn(`Fullscreen open latency: ${latency.toFixed(2)}ms (target: <300ms)`);
    }

    // Prevent body scroll
    document.body.style.overflow = 'hidden';
  }

  /**
   * Close fullscreen view
   */
  function closeFullscreen() {
    if (!modal) return;

    // Hide modal
    modal.classList.remove('visible');

    // Wait for animation before hiding
    setTimeout(() => {
      modal.setAttribute('aria-hidden', 'true');
      modal.style.display = 'none';

      // Restore focus to original thumbnail
      if (previousFocus && currentImageIndex >= 0) {
        const originalImage = images[currentImageIndex];
        if (originalImage) {
          originalImage.focus();
        }
      } else if (previousFocus) {
        previousFocus.focus();
      }

      // Re-enable body scroll
      document.body.style.overflow = '';

      currentImageIndex = -1;
    }, 200); // Match CSS transition duration
  }

  /**
   * Show previous image in the same category
   */
  function showPreviousImage() {
    if (currentImageIndex <= 0) return;

    // Find previous image in same category
    for (let i = currentImageIndex - 1; i >= 0; i--) {
      const item = images[i];
      if (item.dataset.category === currentCategory) {
        openFullscreen(i);
        return;
      }
    }
  }

  /**
   * Show next image in the same category
   */
  function showNextImage() {
    if (currentImageIndex >= images.length - 1) return;

    // Find next image in same category
    for (let i = currentImageIndex + 1; i < images.length; i++) {
      const item = images[i];
      if (item.dataset.category === currentCategory) {
        openFullscreen(i);
        return;
      }
    }
  }

  /**
   * Handle keyboard navigation
   */
  function handleKeyPress(e) {
    // Only handle if modal is open
    if (!modal || modal.getAttribute('aria-hidden') === 'true') {
      return;
    }

    switch(e.key) {
      case 'Escape':
        e.preventDefault();
        closeFullscreen();
        break;

      case 'ArrowLeft':
        e.preventDefault();
        showPreviousImage();
        break;

      case 'ArrowRight':
        e.preventDefault();
        showNextImage();
        break;

      case 'Tab':
        // Trap focus within modal
        trapFocus(e);
        break;
    }
  }

  /**
   * Trap focus within modal for accessibility
   */
  function trapFocus(e) {
    const focusableElements = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    if (e.shiftKey) {
      // Shift + Tab (backwards)
      if (document.activeElement === firstElement) {
        e.preventDefault();
        lastElement.focus();
      }
    } else {
      // Tab (forwards)
      if (document.activeElement === lastElement) {
        e.preventDefault();
        firstElement.focus();
      }
    }
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export for testing/debugging
  window.fullscreenDebug = {
    getCurrentIndex: () => currentImageIndex,
    getImagesCount: () => images.length,
    close: closeFullscreen
  };

})();
