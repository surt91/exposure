# Feature Specification: Image Metadata Privacy and Build Progress Logging

**Feature Branch**: `010-metadata-privacy`
**Created**: 2025-11-02
**Status**: Draft
**Input**: User description: "extend the preprocessing pipeline: 1. During preprocessing we need to strip gps metadata and other sensitive metadata from the images to protect the location of the user. 2. during preprocessing we should show progress. I suppose we just log one line after each conversion which image was converted and how much the saving was in percent."

## Clarifications

### Session 2025-11-02

- Q: When metadata stripping fails for an image (corrupted file, unsupported format, etc.), should the build process continue or halt? → A: Continue with warning and flag - skip metadata removal for failed image, log clearly, continue with other images
- Q: When metadata stripping fails and the build continues with a warning, should there be a final build summary indicating which images have unstripped metadata? → A: Inline warnings only - log warning when failure occurs but no summary
- Q: When removing embedded thumbnail previews from EXIF data, should the system check if the embedded thumbnail actually contains GPS data, or remove all embedded thumbnails unconditionally? → A: Remove all embedded thumbnails - unconditionally strip all EXIF thumbnail previews regardless of GPS presence
- Q: When an image's metadata removal fails and the build continues with a warning, should the progress log for that image use a different format or indicator to distinguish it from successful processing? → A: Distinct warning format - prefix with "⚠ WARNING:" or similar indicator for failed metadata removal
- Q: Should camera model and lens information be preserved or removed from thumbnails? These fields can help with photo organization but might reveal equipment ownership. → A: Preserve camera/lens info - keep camera make, model, and lens information as they're useful for display

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Location Privacy Protection (Priority: P1)

A photographer publishes a gallery of landscape photos taken at various locations. The build process automatically removes GPS coordinates and other location metadata from all processed images, ensuring that sensitive location information cannot be extracted by visitors viewing the gallery.

**Why this priority**: Privacy protection is critical - many photographers don't realize their photos contain GPS coordinates that reveal exact shooting locations, potentially exposing private residences, unpublished locations, or security-sensitive sites.

**Independent Test**: Can be fully tested by building a gallery with GPS-tagged images, examining the generated thumbnails with metadata inspection tools, and verifying that GPS coordinates and location data have been completely removed, delivering privacy protection value immediately.

**Acceptance Scenarios**:

1. **Given** source images contain GPS coordinates in EXIF metadata, **When** thumbnails are generated during build, **Then** GPS latitude, longitude, and altitude data are completely removed from thumbnail files
2. **Given** source images contain location names or address information in IPTC metadata, **When** thumbnails are generated, **Then** location text fields are removed from thumbnail metadata
3. **Given** thumbnails are published on the web, **When** a visitor downloads a thumbnail image and inspects metadata, **Then** no GPS coordinates or location information can be extracted
4. **Given** original source images are retained with full metadata, **When** build completes, **Then** original files remain unchanged with GPS data intact for photographer's local records

---

### User Story 2 - Comprehensive Sensitive Metadata Removal (Priority: P1)

A professional photographer builds a gallery from images containing camera settings, copyright information, editing software details, and camera serial numbers. The build process removes sensitive personal metadata while preserving essential image quality information.

**Why this priority**: Beyond GPS, metadata can reveal personal information including camera serial numbers (for tracking stolen equipment), software licenses, editing workflow details, and other identifiable information that should remain private.

**Independent Test**: Can be tested by processing images with extensive EXIF/IPTC/XMP metadata, then inspecting generated thumbnails to verify that personal identifiers are removed while basic image display properties remain.

**Acceptance Scenarios**:

1. **Given** source images contain camera serial numbers in EXIF metadata, **When** thumbnails are generated, **Then** serial number fields are removed from thumbnail files
2. **Given** source images contain photographer name, copyright holder, or contact information, **When** thumbnails are generated, **Then** creator and rights holder fields are stripped from thumbnails
3. **Given** source images contain software and editing history (Photoshop, Lightroom metadata), **When** thumbnails are generated, **Then** software version, editing history, and processing metadata are removed
4. **Given** source images contain date/time stamp information, **When** thumbnails are generated, **Then** timestamps are preserved as they are not considered privacy-sensitive and may be useful for display
5. **Given** source images contain ICC color profiles, **When** thumbnails are generated, **Then** color profiles are preserved to ensure accurate color reproduction
6. **Given** source images contain orientation metadata, **When** thumbnails are generated, **Then** orientation information is preserved to ensure correct image rotation
7. **Given** source images contain camera make, model, and lens information, **When** thumbnails are generated, **Then** camera and lens metadata are preserved for display and organization purposes

---

### User Story 3 - Build Progress Visibility (Priority: P2)

A gallery owner builds a site with 200 images and wants to monitor preprocessing progress. The build process logs clear progress updates after each image is processed, showing which image was converted and the file size reduction achieved.

**Why this priority**: Progress logging helps users understand what's happening during long builds, diagnose issues with specific images, and verify that optimization is working effectively. However, the build works correctly even without detailed logging.

**Independent Test**: Can be tested by running a build with 20+ images and observing console output to verify that progress messages appear for each image with filename and size reduction percentage.

**Acceptance Scenarios**:

1. **Given** a build processes 50 images, **When** each thumbnail is generated, **Then** a log message is printed showing the image filename and percentage file size reduction
2. **Given** a thumbnail reduces file size from 5MB to 400KB, **When** log message is printed, **Then** it displays "92% smaller" or similar clear indication of compression achieved
3. **Given** build processes images sequentially, **When** viewing console output, **Then** progress messages appear in real-time as each image completes, not batched at the end
4. **Given** an image fails to process, **When** error occurs, **Then** log clearly identifies which image file caused the problem and what went wrong
5. **Given** a build processes 100 images, **When** watching progress output, **Then** user can estimate time remaining and confirm build is actively progressing

---

### User Story 4 - Selective Metadata Preservation (Priority: P3)

The build process intelligently preserves non-sensitive metadata that enhances image display quality while removing privacy-sensitive fields, ensuring thumbnails still display correctly with proper colors and orientation.

**Why this priority**: Not all metadata is sensitive - some fields like color profiles and orientation are essential for correct display. Smart selective removal provides privacy without breaking image rendering.

**Independent Test**: Can be tested by processing images with various metadata types and verifying that display-critical fields (orientation, color profile) remain while privacy-sensitive fields (GPS, serial numbers) are removed.

**Acceptance Scenarios**:

1. **Given** source image has both GPS coordinates and ICC color profile, **When** thumbnail is generated, **Then** GPS data is removed but color profile is preserved
2. **Given** source image has rotation orientation flag (e.g., portrait mode), **When** thumbnail is generated, **Then** orientation metadata is preserved to ensure correct display
3. **Given** source image has both camera serial number and image dimensions, **When** thumbnail is generated, **Then** serial number is removed but dimensions metadata can remain
4. **Given** source image has timestamp information, **When** thumbnail is generated, **Then** timestamps are preserved as they enhance display context without revealing location

---

### Edge Cases

- What happens when an image has no EXIF metadata at all? (System processes normally with no metadata to remove)
- How does the system handle malformed or non-standard metadata fields? (Graceful handling without crashing; log warning if removal fails)
- What happens if metadata stripping fails for a particular image format? (Continue build, log warning, include image with metadata intact)
- How are RAW image formats handled for metadata removal? (RAW formats not processed - only JPEG, PNG, GIF thumbnails have metadata stripped)
- What happens when an image contains XMP sidecar files with location data? (Sidecar files ignored - only embedded metadata in image files is processed)
- How does the system handle images that are already stripped of metadata? (Process normally with nothing to remove)
- What happens if removing metadata corrupts the image file structure? (Detect corruption, log error, skip metadata removal for that image, continue build)
- How are embedded thumbnail previews within EXIF data handled? (Unconditionally remove all embedded EXIF thumbnails regardless of GPS presence)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST remove GPS latitude, longitude, and altitude data from all generated thumbnail images during build process
- **FR-002**: System MUST remove location name, address, and place information from IPTC and XMP metadata in thumbnails
- **FR-003**: System MUST remove camera serial numbers from EXIF metadata in generated thumbnails
- **FR-004**: System MUST remove photographer name, copyright holder, and contact information from thumbnail metadata
- **FR-005**: System MUST remove software version, editing history, and processing metadata (Photoshop, Lightroom, etc.) from thumbnails
- **FR-006**: System MUST preserve ICC color profiles in thumbnails to maintain accurate color reproduction
- **FR-007**: System MUST preserve image orientation metadata in thumbnails to ensure correct rotation display
- **FR-008**: System MUST preserve timestamp information in thumbnails as it is not considered privacy-sensitive
- **FR-008a**: System MUST preserve camera make, model, and lens information in thumbnails as they are useful for display and organization
- **FR-009**: System MUST log a progress message to console after processing each image during build
- **FR-010**: Progress log messages MUST include the filename of the image being processed
- **FR-011**: Progress log messages MUST include the percentage file size reduction achieved for that image
- **FR-012**: Progress logging MUST output messages in real-time as each image completes processing, not batched at end
- **FR-013**: System MUST clearly log which image file caused an error if metadata removal or processing fails
- **FR-014**: System MUST leave original source images completely unchanged with all metadata intact
- **FR-015**: Metadata removal MUST not corrupt or damage image file structure or visual content
- **FR-016**: System MUST handle images with no metadata gracefully without errors
- **FR-017**: System MUST handle malformed or non-standard metadata fields without crashing the build process
- **FR-018**: Metadata removal MUST work consistently across all supported image formats (JPEG, PNG, GIF)
- **FR-019**: System MUST unconditionally remove all embedded thumbnail previews from EXIF metadata regardless of whether they contain GPS data
- **FR-020**: Progress logging MUST format file sizes and percentages in human-readable format (e.g., "5.2MB → 420KB, 92% reduction")
- **FR-021**: When metadata stripping fails for a specific image, system MUST continue processing remaining images rather than halting the entire build
- **FR-022**: System MUST log metadata stripping failures using a distinct warning format (e.g., "⚠ WARNING:" prefix) to visually distinguish from successful processing logs
- **FR-023**: Images with failed metadata stripping MUST still be included in the gallery output with thumbnail generation completed
- **FR-024**: System MUST NOT generate a summary report of metadata stripping failures at end of build - inline warnings during processing are sufficient

### Key Entities

- **SensitiveMetadata**: GPS coordinates, camera serial numbers, photographer personal information, location names, software details that must be removed from published images - includes EXIF GPS fields, IPTC creator/location fields, XMP rights holder fields, and embedded thumbnail previews with location data
- **PreservedMetadata**: Display-critical and useful metadata that must be retained in thumbnails - includes ICC color profiles for accurate color rendering, orientation flags for correct rotation, timestamp information for display context, and camera/lens information (make, model, lens) for organization and display purposes
- **ProcessingLog**: Real-time progress information output during build - includes filename being processed, original file size, thumbnail file size, percentage reduction, and success/failure status for each image

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Generated thumbnail images contain zero GPS coordinate data fields when inspected with metadata tools (exiftool, Pillow)
- **SC-002**: Generated thumbnails do not contain camera serial numbers, photographer names, or copyright holder information when inspected
- **SC-003**: Generated thumbnails display correctly with accurate colors and proper orientation matching the originals
- **SC-004**: Original source images retain 100% of their original metadata after build completes
- **SC-005**: Build process outputs at least one progress log line per image processed, appearing in real-time during execution
- **SC-006**: Progress log messages clearly show filename and file size reduction percentage in human-readable format
- **SC-007**: Users can identify which specific image caused a build failure from error log messages
- **SC-008**: Metadata removal works successfully on 100% of test images without corrupting image visual content or file structure
- **SC-009**: Images with no metadata process successfully without errors or warnings
- **SC-010**: Build time increases by no more than 10% compared to preprocessing without metadata removal

## Assumptions *(optional)*

- Pillow library provides sufficient metadata manipulation capabilities for stripping EXIF, IPTC, and XMP data
- Standard EXIF GPS tags (GPSLatitude, GPSLongitude, GPSAltitude) are the primary location privacy concern
- Timestamps (DateTimeOriginal, DateTimeDigitized) are not considered privacy-sensitive and may be useful for display sorting
- ICC color profiles and orientation flags are essential for correct image rendering and should be preserved
- Original source images are not modified - only generated thumbnails have metadata stripped
- Console logging with print statements is sufficient for progress display (no GUI progress bars needed)
- File size reduction percentage is calculated as: ((original_size - thumbnail_size) / original_size) × 100
- Metadata removal happens during thumbnail generation as part of the existing preprocessing pipeline
- XMP sidecar files, if present, are not processed - only embedded metadata in image files is handled
- Build process logs are viewed in real-time during execution, not parsed by other tools
