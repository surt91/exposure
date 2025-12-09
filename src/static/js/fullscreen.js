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
  let allImages = []; // Flat array of all images across categories with globalIndex
  let modal = null;
  let controlVisibilityManager = null; // ControlVisibilityManager for mobile auto-hide
  let previousFocus = null;
  let currentImageLoader = null; // Track current Image() preloader for cancellation
  let preloadCache = new Map(); // Cache for preloaded images: key=src, value=Image()
  let navigationDirection = null; // Track navigation direction: 'next' or 'prev'

  // Touch gesture state
  let touchStartX = 0;
  let touchStartY = 0;
  let touchEndX = 0;
  let touchEndY = 0;
  let touchStartTime = 0;
  let touchEndTime = 0;

  /**
   * Handle touch start event
   */
  function handleTouchStart(event) {
    touchStartX = event.changedTouches[0].screenX;
    touchStartY = event.changedTouches[0].screenY;
    touchStartTime = performance.now();
  }

  /**
   * Handle touch end event
   */
  function handleTouchEnd(event) {
    touchEndX = event.changedTouches[0].screenX;
    touchEndY = event.changedTouches[0].screenY;
    touchEndTime = performance.now();
    handleSwipeGesture();
  }

  /**
   * Process swipe gesture and navigate if valid
   */
  function handleSwipeGesture() {
    const deltaX = touchEndX - touchStartX;
    const deltaY = touchEndY - touchStartY;
    const distance = Math.abs(deltaX);
    const angle = Math.abs(Math.atan2(deltaY, deltaX) * 180 / Math.PI);

    // Validate: must be primarily horizontal (within 30° of horizontal axis)
    // and meet minimum distance threshold (50px)
    if ((angle < 30 || angle > 150) && distance > 50) {
      // Hide controls immediately on swipe navigation
      if (controlVisibilityManager) {
        controlVisibilityManager.immediateHide();
      }

      if (deltaX > 0) {
        showPreviousImage(); // Swipe right
      } else {
        showNextImage(); // Swipe left
      }
    }
  }

  /**
   * Preload adjacent images (next and previous) for instant navigation
   * Preloads both thumbnails and originals since gallery uses lazy loading
   * (thumbnails may not be loaded if images are outside viewport)
   */
  function preloadAdjacentImages(currentIndex) {
    if (allImages.length === 0) return;

    // Calculate indices for next and previous images (with wraparound)
    const nextIndex = (currentIndex + 1) % allImages.length;
    const prevIndex = (currentIndex - 1 + allImages.length) % allImages.length;

    const nextImage = allImages[nextIndex];
    const prevImage = allImages[prevIndex];

    // Preload next image (both thumbnail and original for instant + smooth loading)
    if (nextImage) {
      // Thumbnail for instant display during navigation
      if (nextImage.thumbnailSrc && !preloadCache.has(nextImage.thumbnailSrc)) {
        const thumbImg = new Image();
        thumbImg.src = nextImage.thumbnailSrc;
        preloadCache.set(nextImage.thumbnailSrc, thumbImg);
      }

      // Original for high-res display
      if (nextImage.originalSrc && !preloadCache.has(nextImage.originalSrc)) {
        const origImg = new Image();
        origImg.src = nextImage.originalSrc;
        preloadCache.set(nextImage.originalSrc, origImg);
      }
    }

    // Preload previous image (both thumbnail and original for instant + smooth loading)
    if (prevImage) {
      // Thumbnail for instant display during navigation
      if (prevImage.thumbnailSrc && !preloadCache.has(prevImage.thumbnailSrc)) {
        const thumbImg = new Image();
        thumbImg.src = prevImage.thumbnailSrc;
        preloadCache.set(prevImage.thumbnailSrc, thumbImg);
      }

      // Original for high-res display
      if (prevImage.originalSrc && !preloadCache.has(prevImage.originalSrc)) {
        const origImg = new Image();
        origImg.src = prevImage.originalSrc;
        preloadCache.set(prevImage.originalSrc, origImg);
      }
    }

    // Clean up old cache entries (keep current + 2 neighbors, both formats)
    // Increased limit to accommodate thumbnails + originals
    if (preloadCache.size > 15) {
      const currentImage = allImages[currentIndex];
      const keepSrcs = new Set([
        currentImage.thumbnailSrc,
        currentImage.originalSrc,
        nextImage?.thumbnailSrc,
        nextImage?.originalSrc,
        prevImage?.thumbnailSrc,
        prevImage?.originalSrc
      ].filter(Boolean)); // Remove null/undefined values

      for (const [src, img] of preloadCache.entries()) {
        if (!keepSrcs.has(src)) {
          preloadCache.delete(src);
        }
      }
    }
  }

  /**
   * Initialize fullscreen functionality
   */
  function init() {
    modal = document.getElementById('fullscreen-modal');
    if (!modal) return;

    // Initialize control visibility manager for mobile auto-hide
    const controlsElement = modal.querySelector('.fullscreen-controls');
    if (typeof ControlVisibilityManager !== 'undefined' && controlsElement) {
      controlVisibilityManager = new ControlVisibilityManager(controlsElement);
    }

    // Get all image items
    images = Array.from(document.querySelectorAll('.image-item'));

    // Create flat allImages array with globalIndex and parsed metadata
    allImages = images.map((item, globalIndex) => {
      const img = item.querySelector('img');
      return {
        element: item,
        category: item.dataset.category || '',
        categoryName: item.dataset.category || '',
        thumbnailSrc: item.dataset.thumbnailSrc || img.src,
        originalSrc: item.dataset.originalSrc || img.src,
        blurPlaceholder: item.dataset.blurPlaceholder || '',
        title: item.dataset.title || img.alt || item.dataset.filename || '',
        description: item.dataset.description || '',
        filename: item.dataset.filename || '',
        width: parseInt(item.dataset.width) || null,
        height: parseInt(item.dataset.height) || null,
        globalIndex: globalIndex
      };
    });

    // Attach click handlers to all image items
    images.forEach((item, index) => {
      item.addEventListener('click', function() {
        openFullscreen(index);
      });
    });

    // Close button
    const closeBtn = modal.querySelector('.modal-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function(e) {
        // Reset control visibility timer on button click
        if (controlVisibilityManager) {
          controlVisibilityManager.resetHideTimer();
        }
        closeFullscreen();
      });
    }

    // Navigation buttons
    const prevBtn = modal.querySelector('.modal-prev');
    const nextBtn = modal.querySelector('.modal-next');

    if (prevBtn) {
      prevBtn.addEventListener('click', function(e) {
        // Reset control visibility timer on button click
        if (controlVisibilityManager) {
          controlVisibilityManager.resetHideTimer();
        }
        showPreviousImage();
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', function(e) {
        // Reset control visibility timer on button click
        if (controlVisibilityManager) {
          controlVisibilityManager.resetHideTimer();
        }
        showNextImage();
      });
    }

    // Tap on image area to toggle control visibility (mobile)
    const modalContent = modal.querySelector('.modal-content');
    const modalImageContainer = modal.querySelector('.modal-image-container');
    const modalImage = modal.querySelector('#modal-image');

    if (controlVisibilityManager) {
      // Handle tap/click on various elements to show controls
      const handleTapToShowControls = function(e) {
        // Only toggle if tapping on the image area, not controls or metadata
        if (e.target.classList.contains('modal-content') ||
            e.target.classList.contains('modal-image-container') ||
            e.target.id === 'modal-image') {
          controlVisibilityManager.handleUserInteraction(e);
        }
      };

      // Use both touch and click events for better mobile support
      if (modalContent) {
        modalContent.addEventListener('click', handleTapToShowControls);
        modalContent.addEventListener('touchend', handleTapToShowControls, { passive: true });
      }
      if (modalImageContainer) {
        modalImageContainer.addEventListener('click', handleTapToShowControls);
        modalImageContainer.addEventListener('touchend', handleTapToShowControls, { passive: true });
      }
      if (modalImage) {
        modalImage.addEventListener('click', handleTapToShowControls);
        modalImage.addEventListener('touchend', handleTapToShowControls, { passive: true });
      }
    }

    // Keyboard handlers
    document.addEventListener('keydown', handleKeyPress);

    // Click outside modal to close
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        closeFullscreen();
      }
    });

    // Touch event listeners for swipe gestures
    modal.addEventListener('touchstart', handleTouchStart, { passive: true });
    modal.addEventListener('touchend', handleTouchEnd, { passive: true });
  }

  /**
   * Open fullscreen view for a specific image
   */
  function openFullscreen(index) {
    if (index < 0 || index >= allImages.length) return;

    // Mark performance milestone
    const startTime = performance.now();

    // Store current focus
    previousFocus = document.activeElement;

    currentImageIndex = index;
    const imageItem = allImages[index];

    // Update current category for consistency
    currentCategory = imageItem.category;

    // Get thumbnail and original image URLs
    const thumbnailSrc = imageItem.thumbnailSrc;
    const originalSrc = imageItem.originalSrc;
    const blurPlaceholder = imageItem.blurPlaceholder;

    // Update modal content
    const modalImg = modal.querySelector('#modal-image');
    const modalImageContainer = modal.querySelector('.modal-image-container');
    const modalTitle = modal.querySelector('#modal-title');
    const modalDescription = modal.querySelector('#modal-description');
    const modalCategory = modal.querySelector('#modal-category');

    // Cancel previous image load
    if (currentImageLoader) {
      currentImageLoader = null;
    }

    if (modalImg) {
      // Apply swipe animation if navigating between images
      if (navigationDirection && modalImageContainer) {
        // Remove previous animation classes
        modalImageContainer.classList.remove('swipe-out-left', 'swipe-out-right', 'swipe-in-left', 'swipe-in-right');

        // Apply exit animation for current image
        if (navigationDirection === 'next') {
          modalImageContainer.classList.add('swipe-out-left');
        } else if (navigationDirection === 'prev') {
          modalImageContainer.classList.add('swipe-out-right');
        }

        // Wait for exit animation to complete before loading new image
        setTimeout(() => {
          loadImage();
        }, 300); // Match animation duration
      } else {
        // No animation for initial open
        loadImage();
      }
    }

    function loadImage() {
      // Hide the image immediately to prevent showing previous image
      modalImg.style.opacity = '0';

      // Set blur placeholder as background if available
      if (modalImageContainer && blurPlaceholder) {
        modalImageContainer.style.backgroundImage = `url('${blurPlaceholder}')`;
        modalImageContainer.style.backgroundSize = 'cover';
        modalImageContainer.style.backgroundPosition = 'center';
      } else {
        // Clear background if no placeholder
        if (modalImageContainer) {
          modalImageContainer.style.backgroundImage = '';
        }
      }

      // Calculate display dimensions to prevent size jumps
      // Both thumbnail and original will be constrained to these dimensions
      if (imageItem.width && imageItem.height) {
        const maxWidth = Math.min(window.innerWidth * 0.9, imageItem.width);
        const maxHeight = Math.min(window.innerHeight * 0.8, imageItem.height);
        const aspectRatio = imageItem.width / imageItem.height;

        let displayWidth, displayHeight;

        // Fit within constraints while maintaining aspect ratio
        if (imageItem.width / maxWidth > imageItem.height / maxHeight) {
          // Width is the limiting factor
          displayWidth = maxWidth;
          displayHeight = maxWidth / aspectRatio;
        } else {
          // Height is the limiting factor
          displayHeight = maxHeight;
          displayWidth = maxHeight * aspectRatio;
        }

        // Set container dimensions to exactly match the image display size
        // This ensures the blur placeholder background is fully covered by the image
        if (modalImageContainer) {
          modalImageContainer.style.width = `${displayWidth}px`;
          modalImageContainer.style.height = `${displayHeight}px`;
          // Adjust background to fill the exact container size (stretch to fit)
          modalImageContainer.style.backgroundSize = '100% 100%';
        }

        // Set explicit image dimensions to prevent size jumps
        // Use object-fit: cover to ensure image completely fills the container
        // This crops to fill rather than stretching, maintaining aspect ratio
        modalImg.style.width = `${displayWidth}px`;
        modalImg.style.height = `${displayHeight}px`;
        modalImg.style.objectFit = 'cover';
      } else {
        // Fallback: clear explicit dimensions if metadata unavailable
        if (modalImageContainer) {
          modalImageContainer.style.width = '';
          modalImageContainer.style.height = '';
          modalImageContainer.style.backgroundSize = 'cover';
        }
        modalImg.style.width = '';
        modalImg.style.height = '';
        modalImg.style.objectFit = 'contain';
      }

      // Check if original image is already preloaded
      const preloadedOriginal = preloadCache.get(originalSrc);
      const isOriginalReady = preloadedOriginal && preloadedOriginal.complete;

      if (isOriginalReady) {
        // Original is ready - show it immediately
        modalImg.src = originalSrc;
        modalImg.alt = imageItem.title;
        modalImg.classList.add('loaded');

        // Wait for the image to be rendered at correct size before showing
        requestAnimationFrame(() => {
          modalImg.style.opacity = '1';
        });
      } else {
        // Original not ready - show thumbnail first
        modalImg.src = thumbnailSrc;
        modalImg.alt = imageItem.title;
        modalImg.classList.remove('loaded');

        // Show thumbnail after it's loaded
        const thumbnailLoader = new Image();
        thumbnailLoader.onload = function() {
          // Thumbnail is loaded, fade it in
          requestAnimationFrame(() => {
            modalImg.style.opacity = '1';
          });
        };
        thumbnailLoader.src = thumbnailSrc;

        // Load original in background
        currentImageLoader = new Image();
        const loaderId = currentImageLoader;
        currentImageLoader.onload = function() {
          // Only update if this is still the current image
          if (currentImageLoader === loaderId) {
            modalImg.src = originalSrc;
            modalImg.classList.add('loaded');
          }
        };
        currentImageLoader.onerror = function() {
          console.warn(`Failed to load original image: ${originalSrc}`);
        };
        currentImageLoader.src = originalSrc;
        // Add to cache
        preloadCache.set(originalSrc, currentImageLoader);
      }

      // Apply entrance animation if navigating between images
      if (navigationDirection && modalImageContainer) {
        // Remove exit animations
        modalImageContainer.classList.remove('swipe-out-left', 'swipe-out-right');

        // Apply entrance animation
        if (navigationDirection === 'next') {
          modalImageContainer.classList.add('swipe-in-right');
        } else if (navigationDirection === 'prev') {
          modalImageContainer.classList.add('swipe-in-left');
        }

        // Remove animation classes after animation completes
        setTimeout(() => {
          if (modalImageContainer) {
            modalImageContainer.classList.remove('swipe-in-left', 'swipe-in-right');
          }
        }, 300); // Match animation duration
      }

      // Reset navigation direction
      navigationDirection = null;
    }

    // Preload adjacent images for instant navigation
    preloadAdjacentImages(index);

    if (modalTitle) {
      modalTitle.textContent = imageItem.title;
    }

    if (modalDescription) {
      modalDescription.textContent = imageItem.description;
      modalDescription.style.display = imageItem.description ? 'block' : 'none';
    }

    if (modalCategory) {
      // Get translated category label from modal data attribute
      const categoryLabel = modal.dataset.i18nCategory || 'Category:';
      modalCategory.textContent = `${categoryLabel} ${imageItem.categoryName}`;
    }

    // Show modal
    modal.setAttribute('aria-hidden', 'false');
    modal.style.display = 'flex';

    // Show controls initially on mobile with auto-hide timer
    if (controlVisibilityManager) {
      controlVisibilityManager.forceShow();
    }

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
   * Show previous image (crosses category boundaries, wraps around)
   */
  function showPreviousImage() {
    if (currentImageIndex < 0 || allImages.length === 0) return;
    navigationDirection = 'prev';
    currentImageIndex = (currentImageIndex - 1 + allImages.length) % allImages.length;
    openFullscreen(currentImageIndex);
  }

  /**
   * Show next image (crosses category boundaries, wraps around)
   */
  function showNextImage() {
    if (currentImageIndex < 0 || allImages.length === 0) return;
    navigationDirection = 'next';
    currentImageIndex = (currentImageIndex + 1) % allImages.length;
    openFullscreen(currentImageIndex);
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
