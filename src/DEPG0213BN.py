from micropython import const
from time import sleep_ms
import framebuf

# Display resolution
EPD_WIDTH = const(128)
EPD_HEIGHT = const(250)

# Some command OP-Codes
WRITE_RAM = b'\x24'
DISPLAY_UPDATE_CONTROL_1 = b'\x21'
DISPLAY_UPDATE_CONTROL_2 = b'\x22'

# Rotaion
ROTATION_0 = const(0)
ROTATION_90 = const(1)
ROTATION_180 = const(2)
ROTATION_270 = const(3)


LUT_SIZE_TTGO_DKE_PART = 153

PART_UPDATE_LUT_TTGO_DKE = bytearray([
    0x0, 0x40, 0x0, 0x0, 0x0,  0x0,  0x0,  0x0,  0x0,  0x0,  0x0, 0x0, 0x80, 0x80, 0x0, 0x0, 0x0, 0x0,  0x0, 0x0,
    0x0, 0x0,  0x0, 0x0, 0x40, 0x40, 0x0,  0x0,  0x0,  0x0,  0x0, 0x0, 0x0,  0x0,  0x0, 0x0, 0x0, 0x80, 0x0, 0x0,
    0x0, 0x0,  0x0, 0x0, 0x0,  0x0,  0x0,  0x0,  0x0,  0x0,  0x0, 0x0, 0x0,  0x0,  0x0, 0x0, 0x0, 0x0,  0x0, 0x0,
    0xF, 0x0,  0x0, 0x0, 0x0,  0x0,  0x0,  0x1,  0x0,  0x0,  0x0, 0x0, 0x0,  0x0,  0x0, 0x0, 0x0, 0x0,  0x0, 0x0,
    0x0, 0x0,  0x0, 0x0, 0x0,  0x0,  0x0,  0x0,  0x0,  0x0,  0x0, 0x0, 0x0,  0x0,  0x0, 0x0, 0x0, 0x0,  0x0, 0x0,
    0x0, 0x0,  0x0, 0x0, 0x0,  0x0,  0x0,  0x0,  0x0,  0x0,  0x0, 0x0, 0x0,  0x0,  0x0, 0x0, 0x0, 0x0,  0x0, 0x0,
    0x0, 0x0,  0x1, 0x0, 0x0,  0x0,  0x0,  0x0,  0x0,  0x1,  0x0, 0x0, 0x0,  0x0,  0x0, 0x0, 0x0, 0x0,  0x0, 0x0,
    0x0, 0x0,  0x0, 0x0, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x0, 0x0, 0x0
    ])
                                     

class EPD(framebuf.FrameBuffer):
    def __init__(self, spi, cs, dc, rst, busy, rotation=ROTATION_0):
        self.init_spi(spi, cs, dc, rst, busy)
        self.init_buffer(rotation)

    def init_buffer(self, rotation):
        self._rotation = rotation
        size = EPD_WIDTH * EPD_HEIGHT // 8
        self.buffer = bytearray(size)

        if self._rotation == ROTATION_0 or self._rotation == ROTATION_180:
            self.width = EPD_WIDTH
            self.height = EPD_HEIGHT
        else:
            self.width = EPD_HEIGHT
            self.height = EPD_WIDTH       
        
        print('width:{}, height:{}'.format(self.width, self.height))
        
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HLSB)
        self.hard_reset()

    def init_spi(self, spi, cs, dc, rst, busy):
        self.spi = spi
        self.spi.init()
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.busy = busy
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.busy.init(self.busy.IN, value=0)      
        
    def _command(self, command, data=None):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(command)
        self.cs(1)
        if data is not None:
            self._data(data)

    def _data(self, data):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)

    def _wait_until_idle(self):
        while self.busy.value() == 1:
            sleep_ms(10)

    def hard_reset(self):
        self.rst(1)
        sleep_ms(1)
        self.rst(0)
        sleep_ms(10)
        self.rst(1)

    def update_comon(self):

        self._command(b'\x12')
        self._wait_until_idle()
 
        # Set RAM entry mode 3 (x increase, y increase : normal mode)
        self._command(b'\x11', b'\x03')
        self._command(b'\x44', b'\x01\x10')
        self._command(b'\x45', b'\x00\x00\xf9\x00'
                      )

        self._command(b'\x4e', b'\x01')

        self._command(b'\x4f', b'\x00\x00')
        
    def update(self):        
        self.update_comon()
   
        self._command(WRITE_RAM, self._get_rotated_buffer())
        self._command(b'\x20')
        self._wait_until_idle()

    def update_partial(self):        
        self.update_comon()
        
#https://github.com/lewisxhe/GxEPD/blob/master/src/GxDEPG0213BN/GxDEPG0213BN.cpp
        
    
#     // set up partial update
#    this->command(0x32);
#    for (uint8_t v : PART_UPDATE_LUT_TTGO_DKE)
#      this->data(v);
        self._command(b'\x32', PART_UPDATE_LUT_TTGO_DKE)
        self._command(b'\x3F', b'\x22')
        self._command(b'\x03', b'\x17')
        self._command(b'\x04', b'\x41\x00\x32')
        self._command(b'\x2C', b'\x32')
        self._command(b'\x37', b'\x00\x00\x00\x00\x00\x40\x00\x00\x00\x00')
        self._command(b'\x3C', b'\x80')
        self._command(b'\x22', b'\xC0')
        self._command(b'\x20')
        self._wait_until_idle()
        self._command(WRITE_RAM, self._get_rotated_buffer())
        self._command(b'\x22', b'\xCF')
        self._command(b'\x20')
        self._wait_until_idle()
        self._command(b'\x24')
        sleep_ms(300)
        self._command(WRITE_RAM, self._get_rotated_buffer())
        sleep_ms(300)
        
#    @micropython.native
    def _get_rotated_buffer(self):
        # no need to rotate
        if self._rotation == ROTATION_0:
            return self.buffer
        # create buffer and rotate
        size = EPD_WIDTH * EPD_HEIGHT // 8
        fbuffer = memoryview(bytearray(size))
        frame = framebuf.FrameBuffer(
            fbuffer, EPD_WIDTH, EPD_HEIGHT, framebuf.MONO_HLSB)
        # copy buffer
        if self._rotation == ROTATION_270:
            for x in range(self.width):
                for y in range(self.height):
                    frame.pixel(y, EPD_HEIGHT-x-1, self.pixel(x, y))
        if self._rotation == ROTATION_90:
            for x in range(self.width):
                for y in range(self.height):
                    frame.pixel(EPD_WIDTH-y-1, x, self.pixel(x, y))
            frame.scroll(-6, 0)
        if self._rotation == ROTATION_180:
            for i in range(size):
                fbuffer[size-i-1] = self.buffer[i]
            frame.scroll(-6, 0)
        return fbuffer