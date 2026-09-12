# main.py - CO2, temperature, humidity and particulate monitor on a TTGO T5 V2.3.
#
# Reads an SCD41 over I2C and an SPS30 over UART once a second, averages each
# batch, and redraws the 128x250 e-paper panel every 30 seconds. The panel is
# the reason for the averaging: a partial refresh is slow and visible, so it is
# worth showing a settled number rather than the latest sample.

import time
import framebuf
from machine import SPI, Pin, I2C, ADC

import DEPG0213BN as epaper
from sps30uart import SPS30
from sensor_pack_2.bus_service import I2cAdapter
from scd4x_sensirion import SCD4xSensirion

DISP_INTERVAL = 30
READ_INTERVAL = 1

# TTGO T5 V2.3
PIN_CS, PIN_DC, PIN_RST, PIN_BUSY = 5, 17, 16, 4
PIN_SCK, PIN_MOSI = 18, 23
PIN_BTN = 39
PIN_BAT = 35
PIN_SDA, PIN_SCL = 21, 22
PIN_TX, PIN_RX = 15, 13
UART_ID = 1

SCD41_ADDR = 0x62

WIDTH = epaper.EPD_WIDTH
HEIGHT = epaper.EPD_HEIGHT


def draw_text_2x(display, text, x, y, color=0):
    w = len(text) * 8
    h = 8
    buf = bytearray(w * h // 8)
    fb = framebuf.FrameBuffer(buf, w, h, framebuf.MONO_HMSB)
    fb.text(text, 0, 0, 1)
    for row in range(h):
        for col in range(w):
            if fb.pixel(col, row):
                display.fill_rect(x + col * 2, y + row * 2, 2, 2, color)


def draw_row(display, label, value_str, y):
    display.text(label, 2, y + 4, 0)
    x_pos = WIDTH - len(value_str) * 16 - 5
    draw_text_2x(display, value_str, x_pos, y, 0)


class Battery:
    def __init__(self, pin):
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)
        self.adc.width(ADC.WIDTH_12BIT)

    def get_status(self):
        try:
            samples = [self.adc.read() for _ in range(10)]
            raw = sum(samples) / len(samples)
            # The board halves the cell voltage into GPIO35, hence the 2. The
            # 1.1 corrects the ESP32's ADC, which reads low across this range.
            volts = (raw / 4095) * 3.3 * 2 * 1.1
            pct = int((volts - 3.2) / (4.2 - 3.2) * 100)
            return max(0, min(100, pct))
        except Exception:
            return 0


class Averager:
    def __init__(self):
        self.reset()

    def reset(self):
        self.sps, self.scd = [], []

    def add(self, d_sps, d_scd):
        if d_sps:
            self.sps.append(d_sps)
        if d_scd:
            self.scd.append(d_scd)

    def get_avg(self):
        res = {'sps_ok': False, 'scd_ok': False}
        if self.sps:
            c = len(self.sps)
            res['sps_ok'] = True
            res['PM1.0'] = sum(d['PM1.0'] for d in self.sps) / c
            res['PM2.5'] = sum(d['PM2.5'] for d in self.sps) / c
            res['PM10'] = sum(d['PM10'] for d in self.sps) / c
            res['Size'] = sum(d['Size'] for d in self.sps) / c
        if self.scd:
            c = len(self.scd)
            res['scd_ok'] = True
            res['CO2'] = sum(d['CO2'] for d in self.scd) / c
            res['T'] = sum(d['T'] for d in self.scd) / c
            res['RH'] = sum(d['RH'] for d in self.scd) / c
        return res


def main():
    print("--- tqzr AirMon ---")

    bat = Battery(PIN_BAT)
    btn = Pin(PIN_BTN, Pin.IN)

    espi = SPI(2, baudrate=4000000, sck=Pin(PIN_SCK), mosi=Pin(PIN_MOSI))
    scr = epaper.EPD(espi, Pin(PIN_CS), Pin(PIN_DC), Pin(PIN_RST), Pin(PIN_BUSY),
                     rotation=0)
    scr.fill(1)

    scd = None
    try:
        i2c = I2C(0, sda=Pin(PIN_SDA), scl=Pin(PIN_SCL), freq=100000)
        if SCD41_ADDR in i2c.scan():
            scd = SCD4xSensirion(I2cAdapter(i2c))
            try:
                scd.stop_periodic_measurement()
            except Exception:
                pass
            time.sleep(0.5)
            scd.start_measurement(start=True)
    except Exception:
        pass

    sps = SPS30(uart_id=UART_ID, tx_pin=PIN_TX, rx_pin=PIN_RX)

    draw_text_2x(scr, "tqzr", 30, 10, 0)
    draw_text_2x(scr, "AirMon", 15, 30, 0)
    scr.text("Starting...", 20, 60, 0)
    scr.update()

    avg = Averager()
    active = True
    sps_active = False

    try:
        sps.start()
        sps_active = True
    except Exception:
        pass

    last_read = 0
    last_disp = 0

    while True:
        now = time.time()

        if btn.value() == 0:
            time.sleep(0.05)
            if btn.value() == 0:
                active = not active
                scr.fill(1)
                if active:
                    scr.text("RESUMING...", 20, 100, 0)
                    try:
                        sps.start()
                        sps_active = True
                    except Exception:
                        sps_active = False
                else:
                    scr.text("PAUSED", 30, 100, 0)
                    sps.stop()
                    sps_active = False
                scr.update()
                while btn.value() == 0:
                    time.sleep(0.1)

        if active:
            if now - last_read >= READ_INTERVAL:
                v_sps = sps.read_values() if sps_active else None
                v_scd = None
                if scd:
                    try:
                        if scd.get_data_status():
                            t = scd.get_measurement_value()
                            if t:
                                v_scd = {'CO2': t.CO2, 'T': t.T, 'RH': t.RH}
                    except Exception:
                        pass

                avg.add(v_sps, v_scd)

                log_parts = []
                if v_sps:
                    log_parts.append(f"PM2.5:{v_sps['PM2.5']:.1f}")
                if v_scd:
                    log_parts.append(f"CO2:{v_scd['CO2']:.1f} T:{v_scd['T']:.1f}")
                print(" | ".join(log_parts) if log_parts else ".")

                last_read = now

            if now - last_disp >= DISP_INTERVAL:
                d = avg.get_avg()
                pct = bat.get_status()

                scr.fill(1)
                scr.fill_rect(0, 0, WIDTH, 16, 0)
                scr.text("tqzr AirMon", 20, 4, 1)

                curr_y = 22
                step_y = 30

                if d['scd_ok']:
                    draw_row(scr, "CO2,ppm", f"{int(d['CO2'])}", curr_y)
                    curr_y += step_y
                    draw_row(scr, "T, C", f"{int(d['T'])}", curr_y)
                    curr_y += step_y
                    draw_row(scr, "RH, %", f"{int(d['RH'])}", curr_y)
                    curr_y += step_y
                else:
                    scr.text("SCD41 ERR", 10, curr_y + 10, 0)
                    curr_y += step_y * 3

                scr.hline(0, curr_y - 8, WIDTH, 0)

                if d['sps_ok']:
                    draw_row(scr, "PM 1", f"{int(d['PM1.0'])}", curr_y)
                    curr_y += step_y
                    draw_row(scr, "PM 2.5", f"{int(d['PM2.5'])}", curr_y)
                    curr_y += step_y
                    draw_row(scr, "PM 10", f"{int(d['PM10'])}", curr_y)
                    curr_y += step_y

                    sz = d['Size']
                    sz_fmt = f"{sz:.0f}" if sz >= 10 else f"{sz:.1f}"
                    scr.text(f"Av.PM: {sz_fmt} um", 5, curr_y + 4, 0)
                else:
                    scr.text("SPS OFF", 35, curr_y + 20, 0)
                    scr.text("(Battery)", 30, curr_y + 35, 0)

                scr.hline(0, HEIGHT - 15, WIDTH, 0)
                scr.text(f"Bat: {pct}%", 35, HEIGHT - 10, 0)

                scr.update()

                avg.reset()
                last_disp = now

        time.sleep(0.1)


if __name__ == "__main__":
    main()
