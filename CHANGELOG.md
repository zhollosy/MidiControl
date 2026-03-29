# Changelog

## [Unreleased]

### Added
- New QMCBendModWheel widget: 2-axis joystick for Bender (X) and Modulation (Y) control
  - Configurable spring-back animation (~60fps)
  - Aspect ratio options: 3:1 (wide), 2:1, 1:1 (square)
  - Labels painted relative to pad rectangle, not widget edges
- New QMCSliderGroup widget: groups sliders with optional tick marks and labels
  - Tick overlay paints between actual groove edges using transparent overlay
  - Group-level labels in a separate row so sliders pack tightly
  - Compact mode centers sliders with expanding spacers
  - Optional top/bottom title bars with line spacers
- QMCSlider now fully custom-painted (no QSlider dependency)
  - Configurable groove width, indicator color, label position
  - Show/hide label and value display independently
  - Groove extends visually beyond handle travel range
- QMCButton rewritten as hardware-style thin strip with LED slit
  - Configurable LED size (0.1-1.0), position (top/bottom), color
  - Edge light option tints border with LED color
  - Label displayed above the button body
- QMCDial redesigned with flat/edgy look (beveled outer ring, flat inner face)
  - Value arc drawn outside knob body for better visibility
- QMCGroup header now custom-painted with line spacers on both sides of text
  - Header position: top (lines at baseline) or bottom (lines at ascent)
- D-70 surface: left-of-keyboard controller panel with Volume, C1, Brightness sliders and Bender/Modulation joystick
- Removed empty MASTER section from D-70 top panel
- Widget screenshot variants for buttons, groups, and sliders

### Changed
- D-70 tone palette sliders now use QMCSliderGroup with ticks and orange indicators
- Slider groove/handle rendering moved from QSS to custom paint for pixel-precise layout
- D-70 QSS group header selector updated for custom-painted header widget

### Added (previous)
- Optional decay breakpoint between Attack and Decay (`breakpoint=False` by default)
- When enabled, splits Decay into Decay1 (Attack→Breakpoint) and Decay2 (Breakpoint→Sustain)
- Breakpoint adds a 5th time segment (127), increasing max width from 445 to 572
- New `breakpoint_time` and `breakpoint_level` properties with full drag support
- Updated README with full feature overview, property tables, and usage examples
- New ADSR and ADBSR screenshots in `doc/` folder
- Screenshot capture utility script
- New reusable widgets: QMCSlider, QMCButton (with LED toggle), QMCDial (custom-painted knob), QMCGroup (section header), QMCKeyboard (dynamic piano keyboard)
- Shared D70 color theme in `QMCWidgets/_theme.py`
- Roland D-70 Surface UI (`QMCSurfaces/QMCSurfaceD70.py`) combining all widgets
- D-70 surface includes: master volume, 6 sliders, LCD placeholder, control/tone/navigation/memory button groups, value dial, 76-key keyboard
- External QSS stylesheet (`RolandD70.qss`) for D-70 surface theming
- QMCGroup content area with D-70 style vertical gradient background
- QMCKeyboard now scales to fill available space on resize

### Fixed
- Focus rectangle now stays aligned with the actual drag point during hover
- Label no longer steals mouse events from the curve widget
- Dragging decay/attack/sustain points no longer offsets from mouse position due to coordinate space mismatch
- Point mutations now reliably update polygon data (fixed stale QPoint copy issue)
- Setters auto-sync downstream points (sustain/release) preventing pop on first drag

### Changed
- Fixed graph width model: Attack(0-127) + Decay(0-127) + Sustain(fixed 64) + Release(0-127)
- Stretching uses fixed max width (445) instead of dynamic bounding rect for stable coordinates
- All times and values clamped to 0-127 range
- Attack drag pushes decay, sustain, and release points right preserving their times
- Decay drag pushes sustain and release points right preserving release time
- Sustain drag only controls sustain level (Y)
- Release point draggable horizontally to set release time
- Label shows context-sensitive ADSR values per focused point
- Start point is not draggable (fixed at origin)

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
