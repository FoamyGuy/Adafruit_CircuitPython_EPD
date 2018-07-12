import time
from adafruit_epd import mcp_sram
import digitalio

class Adafruit_EPD(object):
    """Base class for EPD displays
    """
    BLACK = 0
    WHITE = 1
    INVERSE = 2
    RED = 3
    DARK = 4
    LIGHT = 5

    def __init__(self, width, height, rst_pin, dc_pin, busy_pin, srcs_pin, cs_pin, spi):
        self.width = width
        self.height = height

         # Setup reset pin.
        self._rst = rst_pin
        self._rst.direction = digitalio.Direction.OUTPUT

         # Setup busy pin.
        self._busy = busy_pin
        self._busy.direction = digitalio.Direction.INPUT

        # Setup dc pin.
        self._dc = dc_pin
        self._dc.direction = digitalio.Direction.OUTPUT

        # Setup cs pin.
        self._cs = cs_pin
        self._cs.direction = digitalio.Direction.OUTPUT

        self.spi_device = spi

        self.sram = mcp_sram.Adafruit_MCP_SRAM(srcs_pin, spi)

    def begin(self, reset=True):
        self._cs.value = True
        self._dc.value = False

        if reset:
            self._rst.value = False
            time.sleep(.1)
            self._rst.value = True
            time.sleep(.1)

    def command(self, cmd, data=None, end=True):
        """Send command byte to display."""
        self._cs.value = True
        self._dc.value = False
        self._cs.value = False
        outbuf = bytearray(1)

        while not self.spi_device.try_lock():
            pass
        self.spi_device.write_readinto(bytearray([cmd]), outbuf)

        if data is not None:
            self.data(data)

        elif end:
            self._cs.value = True

        self.spi_device.unlock()
        return outbuf[0]

    def data(self, dat):
        """Send data to display."""
        self._dc.value = True
        self.spi_device.write(dat)
        self._cs.value = True
        self.spi_device.unlock()

    def draw_pixel(self, x, y, color):
        pass

    #framebuf methods
    def fill(self, color):
        self.fill_rect(self, 0, 0, self.width, self.height, color)

    def fill_rect(self, x, y, width, height, color):
        if width < 1 or height < 1 or (x+width) <= 0:
            return
        if (y+height) <= 0 or y >= self.height or x >= self.width:
            return
        xend = min(self.width, x+width)
        yend = min(self.height, y+height)
        x = max(x, 0)
        y = max(y, 0)
        for _x in range(xend - x):
            for _y in range(yend - y):
                self.draw_pixel(x + _x, y + _y, color)
        return

    def pixel(self, x, y, color=None):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        #TODO: figure this out when we know what framebuffer we
        # will actually use
        #if color is None:
        #    return self.get_pixel(self, x, y)

        self.draw_pixel(self, x, y, color)
        return None

    def hline(self, x, y, width, color):
        self.fill_rect(x, y, width, 1, color)

    def vline(self, x, y, height, color):
        self.fill_rect(x, y, 1, height, color)

    def rect(self, x, y, width, height, color):
        self.fill_rect(x, y, width, 1, color)
        self.fill_rect(x, y+height, width, 1, color)
        self.fill_rect(self, x, y, 1, height, color)
        self.fill_rect(self, x+width, y, 1, height, color)

    def line(self):
        raise NotImplementedError()

    def blit(self):
        raise NotImplementedError()

    def scroll(self):
        raise NotImplementedError()

    def text(self):
        raise NotImplementedError()
