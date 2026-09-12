# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-12

First public release. The box has been running on a desk since January 2026;
this is the point at which somebody else could build one.

### Added

- **Seven readings on a 128 × 250 e-paper panel** — CO2, temperature and
  humidity from an SCD41, PM1, PM2.5, PM10 and typical particle size from an
  SPS30, plus a battery percentage. Values are drawn at double size so the box
  is readable across a room.
- **A UART driver for the SPS30** (`src/sps30uart.py`), implementing Sensirion's
  SHDLC framing: byte stuffing, checksum, and the ten-float measurement frame.
  The UART interface is used in preference to I²C because it returns every
  measurement value in one frame and leaves the I²C bus to the CO2 sensor.
- **Averaging between refreshes.** Both sensors are polled once a second and the
  mean is drawn every thirty. An e-paper refresh is slow and flickers the whole
  panel, so it is worth spending on a settled number rather than on whatever the
  sensor said at that instant.
- **A pause button.** The board's own button stops and restarts the SPS30's fan,
  which is the only moving part and most of the power budget.
- **Graceful degradation when the particulate sensor has no power.** The SPS30
  needs 5 V, which the board only has over USB, so on battery the PM rows are
  replaced with `SPS OFF (Battery)` and the CO2 side carries on. This is what
  makes the cell useful: it lets the box go outside to give the CO2 sensor a
  look at fresh air.
- **Documentation for the whole build**: [flashing](docs/flashing.md),
  [hardware](docs/hardware.md) with a wiring diagram,
  [measurement](docs/measurement.md) including the CO2 calibration procedure,
  and symptom-first [troubleshooting](docs/troubleshooting.md).
- **A CI check that the pin numbers agree** across `src/main.py`,
  `docs/hardware.md` and the wiring diagram. Two of the four cross over between
  the board and the sensor, and that pairing is asserted rather than inferred,
  so a documentation edit that quietly un-crosses them fails the build.

### Changed

- **The firmware is offline.** It opens no sockets and never enables the radio.
  Everything the box knows is on its front panel and on the serial console.
- Exception handlers catch `Exception` rather than using a bare `except:`, so
  Ctrl+C interrupts a board stuck in the sensor loop instead of being swallowed
  by it.
- Panel dimensions come from the display driver rather than being repeated as
  literals in the drawing code.
