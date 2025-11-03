# Feature Specification: Frontend Polish & Mobile Improvements

**Feature Branch**: `011-frontend-polish`
**Created**: November 3, 2025
**Status**: Draft
**Input**: User description: "we need to polish the frontend some more.
1. Bug: There is slight horiyontal scrolling on mobile. There should be no horiyontal scrolling. Maybe it is related to the fix for the black border around the banner.
2. Bug: There is a small black line over the banner on top left.
3. In the overlay on mobile we should be able to swipe left and right to navigate to the previous or next image.
4. In the overlay there is too much empty space. The image should be larger. A moderate amount of empty space is ok. Also the category should be displayed less prominently in the overlay.
5. When opening the overlay it can take a long time to load the original image. Show the thumbnail while the original is loading.
6. The loading indicator is too flashy. It should be a nice animation but more subtle."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Mobile Image Overlay Navigation (Priority: P1)

Mobile users viewing the photo gallery should be able to naturally swipe through images in the overlay without relying on small navigation buttons. This matches standard mobile app behavior (like native photo galleries) and makes browsing more intuitive on touch devices.

**Why this priority**: Core mobile usability improvement that directly impacts the primary user interaction (viewing and browsing images). Mobile users represent a significant portion of gallery visitors.

**Independent Test**: Can be fully tested by opening the gallery on a mobile device, tapping any image to open the overlay, and swiping left/right. User should see smooth transitions between images within the same category without touching navigation buttons.

**Acceptance Scenarios**:

1. **Given** user is viewing an image in the fullscreen overlay on a mobile device, **When** user swipes left on the image, **Then** the previous image in the same category is displayed with a smooth transition
2. **Given** user is viewing an image in the fullscreen overlay on a mobile device, **When** user swipes right on the image, **Then** the next image in the same category is displayed with a smooth transition
3. **Given** user is viewing the first image in a category, **When** user swipes left, **Then** no navigation occurs and a subtle visual feedback indicates beginning of category
4. **Given** user is viewing the last image in a category, **When** user swipes right, **Then** no navigation occurs and a subtle visual feedback indicates end of category
5. **Given** user swipes diagonally or vertically, **When** the gesture is not clearly horizontal, **Then** the swipe gesture is ignored to avoid conflicts with scrolling

---

### User Story 2 - Progressive Image Loading (Priority: P1)

Users opening the fullscreen image overlay should see content immediately (thumbnail) while the high-resolution image loads in the background. This prevents the frustrating experience of staring at a blank screen or loading spinner when viewing images, especially on slower connections.

**Why this priority**: Critical for perceived performance and user satisfaction. Long loading times without visual feedback cause users to believe the application is broken or unresponsive.

**Independent Test**: Can be fully tested by throttling network speed (e.g., Fast 3G), clicking on any thumbnail to open the overlay. User should immediately see the thumbnail image displayed while the original loads in the background, with a seamless transition once complete.

**Acceptance Scenarios**:

1. **Given** user clicks on an image thumbnail, **When** the fullscreen overlay opens, **Then** the thumbnail version of the image is displayed immediately (within 50ms)
2. **Given** the thumbnail is displayed in the overlay, **When** the original high-resolution image finishes loading, **Then** it smoothly replaces the thumbnail without jarring visual changes
3. **Given** the original image is still loading, **When** user navigates to another image, **Then** the new thumbnail is displayed immediately and the previous image load is cancelled
4. **Given** the original image fails to load, **When** the error occurs, **Then** the thumbnail remains displayed with a subtle error indicator
5. **Given** the original image is already cached, **When** the overlay opens, **Then** the high-resolution image is displayed immediately without showing the thumbnail first

---

### User Story 3 - Mobile Layout Consistency (Priority: P2)

Mobile users viewing the gallery should experience a properly contained layout without any horizontal scrolling. The entire gallery should fit within the viewport width, providing a clean and professional mobile browsing experience.

**Why this priority**: Essential for mobile usability and professional appearance. Horizontal scrolling on mobile indicates layout breakage and creates a poor user experience.

**Independent Test**: Can be fully tested by opening the gallery on various mobile devices (320px to 480px width), scrolling through the entire page, and verifying no horizontal scrollbar appears and no content extends beyond the viewport.

**Acceptance Scenarios**:

1. **Given** user opens the gallery on a mobile device (320px-480px width), **When** viewing the banner section, **Then** no horizontal scrolling is available and the banner fits perfectly within the viewport
2. **Given** user scrolls through different gallery categories on mobile, **When** viewing image grids, **Then** all content stays within viewport width without triggering horizontal scrolling
3. **Given** user views the gallery on the smallest supported mobile width (320px), **When** inspecting all page elements, **Then** no element width exceeds the viewport width
4. **Given** the gallery banner uses negative margins to achieve full-width display, **When** calculating total width, **Then** the width calculation accounts for body padding correctly

---

### User Story 4 - Optimized Overlay Layout (Priority: P2)

Users viewing images in the fullscreen overlay should see the image as large as possible while maintaining readability of metadata. The image should dominate the screen space with just enough margin for comfortable viewing, and the category label should be de-emphasized compared to the title and description.

**Why this priority**: Improves the core image viewing experience by maximizing image size, which is the primary reason users open the overlay. Better visual hierarchy reduces clutter.

**Independent Test**: Can be fully tested by opening any image in the overlay and visually inspecting that the image uses ~80-85% of the available screen space (height), metadata is readable below the image, and category information is visually secondary to the title.

**Acceptance Scenarios**:

1. **Given** user opens an image in the fullscreen overlay, **When** viewing on desktop, **Then** the image occupies up to 80% of viewport height (increased from 70vh) while maintaining aspect ratio
2. **Given** user opens an image in the fullscreen overlay, **When** viewing on mobile, **Then** the image occupies up to 75% of viewport height (increased from 60vh)
3. **Given** the overlay displays image metadata, **When** comparing visual hierarchy, **Then** the category label uses smaller font size and reduced opacity compared to title and description
4. **Given** the overlay displays multiple metadata elements, **When** arranged vertically, **Then** adequate spacing exists between image and metadata for visual separation (~1rem minimum)

---

### User Story 5 - Visual Polish & Bug Fixes (Priority: P3)

Users viewing the gallery should experience a visually clean interface without visual artifacts (black lines, borders) and with subtle, non-distracting loading animations that provide feedback without drawing excessive attention.

**Why this priority**: Addresses quality issues that affect overall polish and professionalism. While not critical to functionality, these details contribute to perceived quality and user trust.

**Independent Test**: Can be fully tested by viewing the gallery banner on desktop and mobile, looking for any black lines or artifacts near the banner (especially top-left corner), and observing the loading animation for image thumbnails to verify it's subtle and smooth.

**Acceptance Scenarios**:

1. **Given** user views the gallery banner, **When** inspecting the top-left corner area, **Then** no black lines or border artifacts are visible
2. **Given** images are loading with lazy-loading enabled, **When** observing the shimmer animation, **Then** the animation is smooth and subtle (reduced contrast compared to current implementation)
3. **Given** the fullscreen overlay displays a loading indicator, **When** the original image is loading, **Then** the indicator uses a gentle animation (such as a subtle spinner or pulse) rather than a flashy or distracting effect
4. **Given** the gallery banner extends edge-to-edge on mobile, **When** accounting for body padding, **Then** the negative margins correctly compensate without causing overflow

---

### Edge Cases

- What happens when a user with a very slow connection (2G) opens an image overlay?
  - Thumbnail should remain visible indefinitely, with a subtle indication that higher quality is loading
  - User can still navigate to other images even if current image hasn't finished loading
- How does the system handle very tall or very wide images in the optimized overlay layout?
  - Images maintain aspect ratio and fit within the maximum dimensions (80% height or 90% width, whichever is more constraining)
  - Extreme aspect ratios (e.g., panoramas) may use less vertical space but still maintain readability
- What happens when swipe gestures conflict with other touch interactions (zoom, scroll)?
  - Swipe detection should require primarily horizontal movement (>30 degree angle from horizontal)
  - Pinch-to-zoom gestures take precedence over swipe navigation
  - Vertical scrolling is not prevented by swipe detection
- How does the banner handle images with extreme aspect ratios or small dimensions?
  - Banner height is fixed (CSS custom properties: --banner-height-*), object-fit: cover handles aspect ratios
  - Very small images may appear pixelated but are constrained by object-position: center
- What happens if the thumbnail fails to load but the original succeeds?
  - System should still attempt to load the original and display it when ready
  - Brief loading indicator shown instead of missing thumbnail
- How does progressive loading work when images are already cached?
  - Browser cache detection: if original is cached, display it immediately
  - Skip the thumbnail phase if original loads within 100ms

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST eliminate horizontal scrolling on all mobile viewports (320px to 768px width)
- **FR-002**: System MUST remove any visible black lines or border artifacts near the gallery banner, particularly in the top-left corner
- **FR-003**: Mobile users MUST be able to navigate between images in the fullscreen overlay using horizontal swipe gestures (left for previous, right for next)
- **FR-004**: System MUST display thumbnail images immediately when opening the fullscreen overlay (target: <50ms)
- **FR-005**: System MUST load original high-resolution images in the background after displaying the thumbnail
- **FR-006**: System MUST smoothly transition from thumbnail to original image once the original has loaded
- **FR-007**: Fullscreen overlay MUST increase image display size to use up to 80% of viewport height on desktop (up from 70vh)
- **FR-008**: Fullscreen overlay MUST increase image display size to use up to 75% of viewport height on mobile (up from 60vh)
- **FR-009**: Category label in fullscreen overlay MUST be visually de-emphasized (smaller font size, reduced opacity) compared to title and description
- **FR-010**: System MUST replace the current shimmer loading animation with a more subtle version (reduced contrast)
- **FR-011**: Swipe gesture detection MUST require primarily horizontal movement to avoid conflicts with vertical scrolling
- **FR-012**: System MUST provide subtle visual feedback when swiping at category boundaries (first/last image)
- **FR-013**: System MUST cancel previous image loading requests when user navigates to a different image
- **FR-014**: Gallery banner MUST correctly calculate width including body padding compensation to prevent overflow

### Key Entities

- **Image Thumbnail**: Lower-resolution version of image stored/generated during build process, used for instant display in overlay and gallery grid
- **Original Image**: Full-resolution image file loaded on-demand in fullscreen overlay
- **Swipe Gesture**: Touch interaction with horizontal movement threshold used for image navigation on mobile devices
- **Loading State**: Visual indication of image loading progress (thumbnail shown, original loading, original displayed, error state)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Gallery page displays without horizontal scrolling on all tested mobile devices (320px, 375px, 414px, 480px viewport widths)
- **SC-002**: Fullscreen overlay opens with thumbnail visible within 100 milliseconds of user click/tap
- **SC-003**: Users on mobile can successfully navigate between images using swipe gestures with 90% success rate (based on gesture recognition)
- **SC-004**: Visual artifacts (black lines near banner) are eliminated and not visible on any tested viewport size
- **SC-005**: Image size in fullscreen overlay increases by at least 15% of viewport height compared to current implementation
- **SC-006**: Category label in overlay uses font size at least 20% smaller than title and opacity reduced to 0.7 or below
- **SC-007**: Loading animation perceived as "subtle" or "unobtrusive" by 80% of test users (qualitative feedback)
- **SC-008**: Perceived performance improvement: Users report fullscreen overlay feels "instant" or "fast" rather than experiencing noticeable delays
