# Measurement

What each number is, how it is produced, and how far to trust it.

## Averaging

Both sensors are polled every second and their results pushed into a buffer.
Every thirty seconds the firmware takes the mean of everything in the buffer,
draws it, and empties the buffer.

That is a deliberate trade. An e-paper refresh takes on the order of a second
and flickers the whole panel while it happens, so it is worth spending on a
settled figure. The cost is that the display is up to thirty seconds behind the
room, and a brief spike can be averaged away. If you want to watch something
happen in real time, watch the serial console instead, which prints every
reading as it arrives.

## Carbon dioxide

The SCD41 is a true NDIR sensor: it measures how much infrared light carbon
dioxide absorbs across a small optical cavity. It is not one of the cheap
"eCO2" parts that infer a number from a VOC sensor and a guess.

Indoors, CO2 is mostly a proxy for **how much of the air you are breathing has
already been breathed**. That is why it tracks ventilation and occupancy so
closely, and why it is a better guide to opening a window than temperature is.

### Calibrating the CO2 sensor

An NDIR sensor drifts, and the SCD41 corrects for this with **automatic
self-calibration**. ASC watches the lowest reading it has seen over the past
week and assumes that low point was fresh outdoor air at about 400 ppm.

The firmware never changes this setting, so your sensor is at whatever its
factory default is — for the SCD4x family, ASC **enabled**.

That assumption fails in a room that is never aired. If the box lives somewhere
that never drops to outdoor levels, the baseline drifts upwards and every reading
comes out low. There are two ways to fix it:

**Air the room.** Give the sensor at least an hour of genuinely fresh air a week
and ASC looks after itself.

**Force a recalibration.** Take the box outside on its battery — this is what the
cell is for — and leave it running in shade, away from your own breath, for at
least five minutes. Then, over USB in the Thonny console:

```python
from machine import I2C, Pin
from sensor_pack_2.bus_service import I2cAdapter
from scd4x_sensirion import SCD4xSensirion

i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)
scd = SCD4xSensirion(I2cAdapter(i2c))

scd.start_measurement(start=False)      # forced recalibration needs idle mode
print(scd.force_recalibration(400))     # 400 ppm, roughly outdoor air
scd.save_config()
```

`force_recalibration` returns the correction it applied, in ppm. A number in the
tens is ordinary; a number in the hundreds means the sensor had drifted a long
way, or that it was not actually in fresh air.

`save_config()` writes the result into the sensor's own memory, so it survives a
reflash and a power cut.

Outdoor air is close to 400 ppm but not exactly: it is nearer 420 ppm globally
and higher again in a city street. Calibrating next to a road will bias every
indoor reading downwards by the difference.

### Altitude and pressure

CO2 absorption depends on air density, so the SCD41 wants to know where it is.
The default is **0 metres above sea level**, and the firmware does not change it.
If you live somewhere appreciably higher, set it once:

```python
scd.start_measurement(start=False)
scd.set_altitude(160)     # metres above sea level
scd.save_config()
```

Both of these must be done in idle mode, and both need `save_config()` to
persist.

## Temperature and humidity

These come from the same SCD41 package, and they are a bonus rather than the
point of it. **They read high**, because the sensor sits inside a closed printed
box beside a warm ESP32 and a fan motor.

The SCD4x compensates with a fixed offset, set to **4 °C** from the factory. That
is a generic figure, not a measurement of this enclosure. To tune it, let the box
run in its case until the temperature stops climbing, compare it with a
thermometer in the same room, and apply the difference:

```python
scd.start_measurement(start=False)
new = scd.get_temperature_offset() + (reading_shown - actual_room_temperature)
scd.set_temperature_offset(new)
scd.save_config()
```

Getting this right also improves humidity, which is derived from temperature.
It does not affect CO2 accuracy at all.

## Particulates

The SPS30 draws air past a laser with a small fan and sizes particles by how
they scatter light. The firmware asks for measurements in float mode and reads
back ten values, of which it uses five:

| Shown | What it is |
|---|---|
| `PM 1` | Mass of particles up to 1 µm, in µg/m³ |
| `PM 2.5` | Mass up to 2.5 µm — the number health guidance is written around |
| `PM 10` | Mass up to 10 µm |
| `Av.PM` | Typical particle size in µm, useful for guessing what a spike was |

The mass figures are cumulative, so PM10 is always at least PM2.5, which is
always at least PM1. If they ever come out the other way round, the frame was
corrupt.

The typical-size figure is the interesting one indoors. Cooking and candles
produce a lot of very small particles and a reading well under 1 µm; sweeping,
dust and pollen sit much higher. A spike with a small typical size came from
combustion, and one with a large typical size came from something being
disturbed.

**The SPS30 is uncalibrated in absolute terms.** It is consistent with itself,
which makes it good at before-and-after comparisons and at watching a spike
decay, and it is not a reference instrument. Sensirion also recommend running
its fan-cleaning cycle periodically; this firmware does not, so if the box lives
somewhere dusty, expect readings to drift down over months.

## Battery percentage

The cell voltage reaches GPIO35 through a divider on the board. The firmware
averages ten ADC samples, scales them, and maps 3.2 V to 0 % and 4.2 V to 100 %:

```python
volts = (raw / 4095) * 3.3 * 2 * 1.1
pct = (volts - 3.2) / (4.2 - 3.2) * 100
```

The `2` undoes the divider. The `1.1` corrects the ESP32's ADC, which reads low
across this range and is not especially linear even after correction.

Treat this as three states — full, middling, nearly flat — and not as a
percentage. A lithium cell holds about 3.7 V across most of its useful capacity,
so the middle of the scale passes very slowly and the bottom arrives quickly.

## Related

- [hardware.md](hardware.md) — why particulates stop on battery
- [troubleshooting.md](troubleshooting.md) — readings that look wrong
