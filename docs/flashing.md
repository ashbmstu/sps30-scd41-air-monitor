# Flashing

Getting MicroPython onto the TTGO T5 and the firmware onto its filesystem. The
MicroPython part is done once; after that, updating is copying files.

You need the T5, a USB cable that carries **data**, and a computer. Do this
before the board goes in the case — it is much easier with everything reachable.

## 1. Install Thonny

[Thonny](https://thonny.org) is a small Python editor that can install
MicroPython and copy files to a board. It runs on Windows, macOS and Linux.

## 2. Install MicroPython

1. Plug the T5 in. **Check its power switch is on** — the USB-serial chip on the
   board enumerates from USB alone, so a port appears on your computer whether or
   not the ESP32 itself is powered, and a board that is switched off looks
   identical to one that is broken.
2. In Thonny, open **Tools → Options → Interpreter**.
3. Set the interpreter to **MicroPython (ESP32)**.
4. Choose the board's port. On Windows the T5 shows up as a CH9102 or CH340
   serial device.
5. Click **Install or update MicroPython**, choose the plain **ESP32** family and
   the generic ESP32 variant, and install.

This project runs on **MicroPython 1.23.0**. Later versions should be fine.

The panel keeps whatever was last drawn on it, with no power, so the screen will
not change during any of this. That is normal.

## 3. Copy the firmware

In Thonny, open **View → Files**. The top pane is your computer, the bottom is
the board.

Copy the **contents** of this repository's `src` folder to the board's root, so
that the board ends up looking like this:

```
DEPG0213BN.py
main.py
scd4x_sensirion.py
sensor_pack_2/
    __init__.py
    base_sensor.py
    bus_service.py
    crc_mod.py
sps30uart.py
```

`sensor_pack_2` has to stay a folder — `scd4x_sensirion.py` imports from it by
name. Right-click the folder in Thonny's upper pane and choose **Upload to /**
and it will be created for you.

Do not copy the `src` folder itself. If the board ends up with `src/main.py`,
nothing will run at boot.

`config.example.py` stays on your computer. Copy it across as `config.py`, with
your own details in it, only if you want the monitor to publish readings — see
[thingspeak.md](thingspeak.md).

## 4. Run it

Press the T5's reset button, or unplug and replug. MicroPython runs `main.py`
automatically at every power-up.

You should see the splash screen, then a full reading about thirty seconds
later. In Thonny's console you also get a line every second, which is the
quickest way to tell whether both sensors are answering:

```
PM2.5:3.4 | CO2:612.0 T:22.8
```

A bare `.` on that line means neither sensor returned anything this second.

## Changing the firmware later

Edit and upload again; there is no build step. If the board is busy running
`main.py` and will not respond, click into the console and press **Ctrl+C**.

The sensors keep their own configuration in their own memory, so reflashing does
not undo a CO2 calibration.

## Related

- [hardware.md](hardware.md) — what to solder where
- [troubleshooting.md](troubleshooting.md) — when the board or a sensor stays silent
