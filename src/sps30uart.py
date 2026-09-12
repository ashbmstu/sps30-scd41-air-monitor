# sps30uart.py - MicroPython driver for the Sensirion SPS30 over its UART
# (SHDLC) interface, rather than I2C.
#
# The SPS30 speaks the same commands on both buses, but only the UART variant
# returns all ten measurement floats in one frame, and it leaves the ESP32's
# I2C bus free for the CO2 sensor.

import time
import struct
from machine import UART, Pin


class SPS30:
    def __init__(self, uart_id=1, tx_pin=15, rx_pin=13, baudrate=115200):
        self.uart = UART(uart_id, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin))
        self.init_connection()

    def init_connection(self):
        while self.uart.any():
            self.uart.read()

    def _calc_checksum(self, data):
        return (~(sum(data) & 0xFF)) & 0xFF

    def _stuff_byte(self, data):
        output = bytearray()
        for b in data:
            if b in (0x7E, 0x7D, 0x11, 0x13):
                output.append(0x7D)
                output.append(b ^ 0x20)
            else:
                output.append(b)
        return output

    def _unstuff_byte(self, data):
        output = bytearray()
        escaped = False
        for b in data:
            if escaped:
                output.append(b ^ 0x20)
                escaped = False
            elif b == 0x7D:
                escaped = True
            else:
                output.append(b)
        return output

    def _send_cmd(self, cmd, data=None):
        if data is None:
            data = []
        frame = [0x00, cmd, len(data)] + list(data)
        frame.append(self._calc_checksum(frame))
        self.uart.write(b'\x7e' + self._stuff_byte(frame) + b'\x7e')

    def _read_response(self):
        start_time = time.ticks_ms()
        while self.uart.any() < 1:
            if time.ticks_diff(time.ticks_ms(), start_time) > 1000:
                return None
            time.sleep_ms(10)

        # A frame arrives faster than it can be assembled byte by byte, so let
        # the rest of it land before reading.
        time.sleep_ms(50)
        raw = self.uart.read()
        if not raw:
            return None

        start_idx = raw.find(b'\x7e')
        end_idx = raw.rfind(b'\x7e')
        if start_idx == -1 or end_idx == -1 or start_idx == end_idx:
            return None

        payload = self._unstuff_byte(raw[start_idx + 1:end_idx])
        if len(payload) < 4:
            return None
        if self._calc_checksum(payload[:-1]) != payload[-1]:
            return None

        return payload[4:]

    def start(self):
        """Start measuring, in big-endian float output format."""
        self._send_cmd(0x00, [0x01, 0x03])
        time.sleep(0.1)
        while self.uart.any():
            self.uart.read()

    def stop(self):
        """Stop measuring and shut the fan down."""
        self._send_cmd(0x01)

    def read_values(self):
        """Return a dict of mass concentrations and typical size, or None."""
        self._send_cmd(0x03)
        data = self._read_response()

        if data and len(data) >= 40:
            try:
                v = struct.unpack('>ffffffffff', data)
            except Exception:
                return None
            return {
                "PM1.0": v[0], "PM2.5": v[1], "PM4.0": v[2], "PM10": v[3],
                "Size": v[9],
            }
        return None
