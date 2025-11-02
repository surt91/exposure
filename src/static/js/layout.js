/**
 * Flexible Image Layout
 * Calculates and applies justified layout to image gallery
 * Uses flickr/justified-layout library for calculations
 */

(function() {
  'use strict';

  /**
   * Initialize layout system
   */
  function init() {
    // Check if justified-layout library is available
    if (typeof justifiedLayout === 'undefined') {
      console.warn('justified-layout library not loaded, falling back to CSS Grid');
      return;
    }

    const galleries = document.querySelectorAll('.image-grid');

    galleries.forEach(gallery => {
      // Extract image data from DOM
      const imageData = extractImageData(gallery);

      if (imageData.length === 0) {
        console.warn('No images with dimensions found in gallery');
        return;
      }

      // Calculate initial layout
      const layout = calculateLayout(gallery, imageData);

      // Apply layout
      applyLayout(gallery, layout);

      // Setup resize handler
      setupResizeHandler(gallery, imageData);
    });
  }

  /**
   * Extract image dimensions from DOM
   * @param {HTMLElement} gallery - Gallery container element
   * @returns {Array} Array of image data objects
   */
  function extractImageData(gallery) {
    const items = gallery.querySelectorAll('.image-item');
    const data = [];

    items.forEach((item, index) => {
      const width = parseInt(item.dataset.width);
      const height = parseInt(item.dataset.height);

      if (width && height && width > 0 && height > 0) {
        data.push({
          index: index,
          width: width,
          height: height,
          aspectRatio: width / height,
          element: item
        });
      }
    });

    return data;
  }

  /**
   * Calculate layout using justified-layout library
   * @param {HTMLElement} gallery - Gallery container element
   * @param {Array} imageData - Array of image data objects
   * @returns {Object} Layout result with geometry and imageData
   */
  function calculateLayout(gallery, imageData) {
    const containerWidth = gallery.clientWidth;

    // Prepare input for justified-layout library
    const input = imageData.map(img => ({
      width: img.width,
      height: img.height
    }));

    // Calculate target row height based on viewport width
    const targetRowHeight = containerWidth < 640 ? 200 : 320;

    // Calculate layout
    const geometry = justifiedLayout(input, {
      containerWidth: containerWidth,
      targetRowHeight: targetRowHeight,
      maxRowHeight: targetRowHeight * 1.5,
      boxSpacing: 8,
      containerPadding: 0
    });

    return {
      geometry: geometry,
      imageData: imageData
    };
  }

  /**
   * Apply layout to DOM
   * @param {HTMLElement} gallery - Gallery container element
   * @param {Object} layout - Layout result from calculateLayout
   */
  function applyLayout(gallery, layout) {
    const { geometry, imageData } = layout;

    // Update gallery container
    gallery.style.position = 'relative';
    gallery.style.height = `${geometry.containerHeight}px`;
    gallery.classList.add('layout-calculated');

    // Position each image
    geometry.boxes.forEach((box, index) => {
      const item = imageData[index].element;

      item.style.position = 'absolute';
      item.style.left = `${box.left}px`;
      item.style.top = `${box.top}px`;
      item.style.width = `${box.width}px`;
      item.style.height = `${box.height}px`;
    });
  }

  /**
   * Setup responsive resize handler
   * @param {HTMLElement} gallery - Gallery container element
   * @param {Array} imageData - Array of image data objects
   */
  function setupResizeHandler(gallery, imageData) {
    let resizeTimeout;

    window.addEventListener('resize', () => {
      clearTimeout(resizeTimeout);

      resizeTimeout = setTimeout(() => {
        const layout = calculateLayout(gallery, imageData);
        applyLayout(gallery, layout);
      }, 150); // Debounce 150ms
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
