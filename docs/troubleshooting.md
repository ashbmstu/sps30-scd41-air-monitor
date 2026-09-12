# Troubleshooting

Arranged by what you see, not by what is wrong.

## The screen never changes

E-paper holds its last image with no power at all, so a screen showing plausible
numbers proves nothing about whether the board is running. Check the timestamp
of the situation, not the display: plug in USB, open Thonny, and look for the
once-a-second console line.

If the console is silent too, the board is not running. In order of likelihood:

- **The power switch is off.** The T5's USB-serial chip is powered from USB, so
  the serial port appears on your computer regardless. A switched-off board and a
  dead board look exactly the same from the outside.
- **The USB cable is charge-only.** Many are.
- **`main.py` is in a folder.** If the board has `src/main.py` rather than
  `main.py`, nothing runs at boot.

## `SCD41 ERR` where the CO2 rows should be

The sensor did not answer at address `0x62`. Check `SDA` on `IO21`, `SCL` on
`IO22`, and that `VDD` went to **3V3** and not 5V. Then scan the bus from the
Thonny console:

```python
from machine import I2C, Pin
I2C(0, sda=Pin(21), scl=Pin(22), freq=100000).scan()
```

`[98]` is the SCD41 at `0x62`. An empty list means wiring, not the sensor.

## `SPS OFF (Battery)`

**If you are on battery, this is correct and expected.** The SPS30 needs 5 V,
which the board only has over USB. See
[hardware.md](hardware.md#the-5-v-problem).

On USB, it means the sensor is not answering. Working through it:

- **`RX` and `TX` are swapped.** The board transmits on `IO15`, which goes to the
  SPS30's **RX**; the board receives on `IO13`, from the sensor's **TX**. This is
  the most common build fault.
- **The `SEL` pin is grounded.** That selects I²C mode. Leave it unconnected.
- **`VDD` is on 3V3.** The sensor will be silent or erratic. It needs 5 V.
- **Listen for the fan.** A working SPS30 is quietly audible in a still room. No
  fan means no power, not a data problem.

## The fan runs but the PM numbers are all zero

That is what clean air looks like. Hold a lit match near the inlet and let it go
out — PM2.5 should jump within a few seconds and then decay over a minute or
two. If nothing moves, the frames are being rejected; check the console for a
`.` on every line, which means no valid data arrived at all.

## CO2 sits around 400 and never moves

Either the room is genuinely well ventilated, or a forced recalibration was run
somewhere that was not fresh air and pinned the baseline. Breathe gently towards
the box from 30 cm away: the reading should climb within a few seconds and fall
back over a minute. If it does not move at all, recalibrate outdoors — see
[measurement.md](measurement.md#calibrating-the-co2-sensor).

## CO2 readings look far too low in a stuffy room

The self-calibration baseline has drifted, which happens in a room that never
gets aired. Either open a window for an hour a week and let it correct itself, or
force a recalibration outdoors.

## Temperature reads two or three degrees high

Expected. The sensor is in a closed box with a warm processor and a fan motor.
[measurement.md](measurement.md#temperature-and-humidity) shows how to measure
and set the offset for your own build.

## The battery percentage jumps around, or sits at 100 until it dies

It is a voltage estimate with no fuel gauge behind it, and lithium cells sit near
3.7 V for most of their capacity. Expect a long plateau and then a quick fall.
Readings also sag under the load of the fan, so the figure will look lower on USB
with the SPS30 running than on the same charge at rest.

## The display is smeared or shows a shadow of the previous screen

Ghosting, and normal for e-paper after many partial updates. It clears on the
next full refresh. Persistent heavy ghosting usually means the panel is cold —
e-paper slows down markedly below about 10 °C.

## The board does not appear as a serial port

- Power switch, again.
- Charge-only cable.
- On Windows, the T5 needs a CH9102 or CH340 driver, depending on its revision.

## Related

- [hardware.md](hardware.md) — the wiring diagram and every connection
- [flashing.md](flashing.md) — getting MicroPython and the files onto the board
- [measurement.md](measurement.md) — what the numbers mean
