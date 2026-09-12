# Optional. Copy this file onto the board as config.py and fill it in to have
# the monitor publish to ThingSpeak. Leave it off the board and the monitor
# runs offline: the radio is never switched on. See docs/thingspeak.md.
#
# config.py is in .gitignore. Keep it that way - the write key below is a
# credential.

WIFI_SSID = ""
WIFI_PASS = ""

# The Write API Key from your channel's "API Keys" tab. The readings go to
# fixed fields: 1 is PM2.5, 2 is CO2, 3 is temperature, 4 is humidity.
THINGSPEAK_KEY = ""

# Seconds between uploads. A free ThingSpeak channel accepts one every 15, and
# the panel only refreshes every 30, so there is nothing to gain below that.
UPLOAD_INTERVAL = 60
