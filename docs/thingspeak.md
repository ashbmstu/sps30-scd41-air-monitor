# Publishing readings

The monitor can post its readings to a **ThingSpeak** channel, which gives you a
chart of the last day or the last month instead of only the last thirty
seconds. It is free for this sort of use and it needs no server of your own.

**This is off unless you turn it on.** Without a `config.py` on the board the
firmware never imports the networking modules and never switches the radio on.
Nothing is sent, and there is nothing to configure.

## Turning it on

1. **Make an account** at [thingspeak.com](https://thingspeak.com/) and create a
   new channel. *Channels* → *My Channels* → *New Channel*.

2. **Name four fields**, in this order. The firmware writes to them by number,
   so the order matters and the names are only for your own benefit:

   | Field | Reading |
   |---|---|
   | 1 | PM2.5, µg/m³ |
   | 2 | CO2, ppm |
   | 3 | Temperature, °C |
   | 4 | Humidity, %RH |

3. **Copy the Write API Key** from the channel's *API Keys* tab. It is the one
   marked *Write*, not *Read*.

4. **Fill in your own copy of the config.** Take `src/config.example.py`, save
   it as `config.py`, and put your details in:

   ```python
   WIFI_SSID = "your network"
   WIFI_PASS = "your password"

   THINGSPEAK_KEY = "the write key you just copied"

   UPLOAD_INTERVAL = 60
   ```

5. **Upload `config.py` to the board** the same way as the rest — Thonny, right
   click, *Upload to /* — and reset.

A small square appears in the bottom right of the panel, beside the battery
percentage. **Filled means the last upload landed; hollow means it did not.**
The console says the same thing in words:

```
uploaded: field1=4.2&field2=689.0&field3=22.4&field4=41.8
```

## Turning it off again

Delete `config.py` from the board and reset, or blank out `THINGSPEAK_KEY`. The
firmware only publishes when both the network name and the key are set.

## Things worth knowing

- **What gets sent is what is on the panel** — the average over the last thirty
  seconds, not an instantaneous sample. The upload happens just before the
  refresh, using the same numbers.
- **Missing readings are left out, not sent as zero.** On battery the SPS30 is
  unpowered, so no PM2.5 value is sent at all for that period. A zero would
  draw as perfectly clean air, which is a worse lie than a gap in the line.
- **Nothing is queued.** If the Wi-Fi drops, that period's reading is lost and
  the next one is tried as normal. The monitor keeps measuring and keeps
  displaying regardless; the upload is the part that is allowed to fail.
- **One reading a minute by default.** A free channel accepts one update every
  15 seconds, and the panel only refreshes every 30, so there is nothing to
  gain from going faster.
- **2.4 GHz only.** The ESP32 cannot see a 5 GHz network.

## Keep the key to yourself

`config.py` holds your Wi-Fi password and a key that lets anyone write to your
channel. Two habits worth keeping:

- **It is in `.gitignore` for a reason.** If you fork this repository, do not
  commit your `config.py`. Git remembers a file even after you delete it.
- **The key travels in clear text.** ThingSpeak's simple API is plain HTTP, and
  the key sits in the URL, so anyone on the same network can read it. It is a
  write-only key to one channel, which limits the damage, but do not reuse it
  anywhere else and regenerate it from the *API Keys* tab if you ever paste it
  somewhere public.

## Related

- [flashing.md](flashing.md) — copying files onto the board
- [measurement.md](measurement.md) — what the numbers you are charting mean
