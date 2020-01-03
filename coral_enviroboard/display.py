import spidev
import Jetson.GPIO as GPIO

DISPLAYOFF = 0xAE
DISPLAYON = 0xAF
DISPLAYALLON = 0xA5
DISPLAYALLON_RESUME = 0xA4
NORMALDISPLAY = 0xA6
INVERTDISPLAY = 0xA7
SETREMAP = 0xA0
SETMULTIPLEX = 0xA8
SETCONTRAST = 0x81
CHARGEPUMP = 0x8D
COLUMNADDR = 0x21
COMSCANDEC = 0xC8
COMSCANINC = 0xC0
EXTERNALVCC = 0x1
MEMORYMODE = 0x20
PAGEADDR = 0x22
SETCOMPINS = 0xDA
SETDISPLAYCLOCKDIV = 0xD5
SETDISPLAYOFFSET = 0xD3
SETHIGHCOLUMN = 0x10
SETLOWCOLUMN = 0x00
SETPRECHARGE = 0xD9
SETSEGMENTREMAP = 0xA1
SETSTARTLINE = 0x40
SETVCOMDETECT = 0xDB
SWITCHCAPVCC = 0x2

class ssd1306(object):
    """
    Serial interface to a monochrome SSD1306 OLED display.
    On creation, an initialization sequence is pumped to the display
    to properly configure it. Further control commands can then be called to
    affect the brightness and other settings.
    :param width: The number of horizontal pixels (optional, defaults to 128).
    :type width: int
    :param height: The number of vertical pixels (optional, defaults to 64).
    :type height: int
    :param rotate: An integer value of 0 (default), 1, 2 or 3 only, where 0 is
        no rotation, 1 is rotate 90° clockwise, 2 is 180° rotation and 3
        represents 270° rotation.
    :type rotate: int
    """
    def __init__(self, width=128, height=64, rotate=0, **kwargs):
        try:
            self._spi = spidev.SpiDev()
            self._spi.open(0, 0) # /dev/spidev0.0
            self._spi.cshigh = False
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(24, GPIO.OUT)    # DC
            GPIO.setup(25, GPIO.OUT)    # RST
        except (IOError, OSError) as e:
            if e.errno == errno.ENOENT:
                raise Error('SPI device not found')
            else:  # pragma: no cover
                raise
        self._spi.max_speed_hz = 8000000
        self.capabilities(width, height, rotate)

        # Supported modes
        settings = {
            (128, 64): dict(multiplex=0x3F, displayclockdiv=0x80, compins=0x12),
            (128, 32): dict(multiplex=0x1F, displayclockdiv=0x80, compins=0x02),
            (96, 16): dict(multiplex=0x0F, displayclockdiv=0x60, compins=0x02),
            (64, 48): dict(multiplex=0x2F, displayclockdiv=0x80, compins=0x12),
            (64, 32): dict(multiplex=0x1F, displayclockdiv=0x80, compins=0x12)
        }.get((width, height))

        if settings is None:
            raise Error("Unsupported display mode: {0} x {1}".format(width, height))

        self._pages = height // 8
        self._mask = [1 << (i // width) % 8 for i in range(width * height)]
        self._offsets = [(width * (i // (width * 8))) + (i % width) for i in range(width * height)]
        self._colstart = (0x80 - self._w) // 2
        self._colend = self._colstart + self._w

        self.command(
            self.DISPLAYOFF,
            self.SETDISPLAYCLOCKDIV, settings['displayclockdiv'],
            self.SETMULTIPLEX,       settings['multiplex'],
            self.SETDISPLAYOFFSET,   0x00,
            self.SETSTARTLINE,
            self.CHARGEPUMP,         0x14,
            self.MEMORYMODE,         0x00,
            self.SETSEGMENTREMAP,
            self.COMSCANDEC,
            self.SETCOMPINS,         settings['compins'],
            self.SETPRECHARGE,       0xF1,
            self.SETVCOMDETECT,      0x40,
            self.DISPLAYALLON_RESUME,
            self.NORMALDISPLAY)

        self.contrast(0xCF)
        self.clear()
        self.show()

    def display(self, image):
        """
        Takes a 1-bit :py:mod:`PIL.Image` and dumps it to the OLED
        display.
        :param image: Image to display.
        :type image: :py:mod:`PIL.Image`
        """
        assert(image.mode == self.mode)
        assert(image.size == self.size)

        image = self.preprocess(image)

        self.command(
            # Column start/end address
            self.COLUMNADDR, self._colstart, self._colend - 1,
            # Page start/end address
            self.PAGEADDR, 0x00, self._pages - 1)

        buf = bytearray(self._w * self._pages)
        off = self._offsets
        mask = self._mask

        idx = 0
        for pix in image.getdata():
            if pix > 0:
                buf[off[idx]] |= mask[idx]
            idx += 1

        self.data(list(buf))