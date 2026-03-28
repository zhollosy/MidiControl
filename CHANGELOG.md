# Changelog

## [Unreleased]

### Fixed
- Focus rectangle now stays aligned with the actual drag point during hover
- Label no longer steals mouse events from the curve widget
- Dragging decay/attack/sustain points no longer offsets from mouse position due to coordinate space mismatch
- Point mutations now reliably update polygon data (fixed stale QPoint copy issue)

### Changed
- Attack drag: normal drag clamped to decay point, Ctrl+drag preserves decay time and shifts decay along
- Sustain drag now controls sustain level (Y) and release time (X distance to end)
- Removed sustain_time property (not a real synth parameter)
- Start and end points are no longer draggable (fixed positions)
- End point always pinned to bottom-right corner

## 2026-03-28

### Updated
- Refreshed project README for clarity and setup instructions
- Adapted ADSR widget to PyQt6 API and styling
- Migrated main application entry point to PyQt6
- Added PyQt6 to project dependencies
- Refined gitignore for development files

## 2023-04-13

### Changed
- Misc updates

## 2021-01-12

### Updated
- Updated gitignore
- Fixed relative image path in docs

## 2020-11-02

### Changed
- Simplify refactor work-in-progress

## 2020-11-01

### Changed
- Simplify refactor work-in-progress

## 2020-10-28

### Added
- Optimized range finder for polygon points
- New in-range finder for polygon
- QCurveData mapped to content area

## 2020-10-25

### Added
- QCurveData connected to widget

## 2020-10-18

### Added
- QCurveData added (not yet connected)

## 2020-10-17

### Updated
- Documentation and ADSR sample image

## 2020-10-15

### Added
- Mouse over curve point capture
- Mouse click detection on curve points

## 2020-10-14

### Added
- Label widget for ADSR display

## 2020-10-13

### Updated
- ADSR v0.1 with target size fitting

## 2020-10-11

### Changed
- General updates

## 2020-10-10

### Added
- First WIP version of ADSR curve widget

## 2020-10-04

### Added
- Initial commit
