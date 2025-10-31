# Contract: Fullscreen Interaction

## User Action
Click (or keyboard activation using Enter/Space when focused) on an image thumbnail.

## Preconditions
- Gallery rendered
- Thumbnail has focus or receives click

## Postconditions
- Overlay element becomes visible displaying target image
- Focus moved into overlay (close button first)
- Esc key or overlay close control restores previous scroll position and focus to originating thumbnail

## Accessibility Requirements
- Overlay MUST trap focus while open
- MUST provide descriptive alt text from filename or title
- MUST be dismissible with Esc

## Keyboard Navigation
- Left/Right arrows cycle adjacent images within same category
- Tab cycles through interactive controls (close, next, previous)

## Error States
- If image fails to load, display placeholder element with alt text: "Image unavailable"

## Telemetry (Optional Future)
- Not captured initially (privacy baseline)
