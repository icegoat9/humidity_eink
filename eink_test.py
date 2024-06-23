# Test composing text objects on E Ink Featherwing
# (initialization code from Adafruit il0373 demo)

import time
import board
import displayio
import fourwire
import adafruit_il0373
import terminalio
from adafruit_display_text import label

print('running eink_test.py...')

# Used to ensure the display is free in CircuitPython
displayio.release_displays()

# Define the pins needed for display use
spi = board.SPI()
epd_cs = board.D9
epd_dc = board.D10
epd_reset = None
epd_busy = None

# Create the displayio connection to the display pins
display_bus = fourwire.FourWire(
    spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000
)
time.sleep(1)  # Wait a bit

# Create the display object - the third color is red (0xff0000)
display = adafruit_il0373.IL0373(
    display_bus,
    width=296,
    height=128,
    rotation=270,
    busy_pin=epd_busy,
    highlight_color=0xFF0000,
)

# Create a display group for our screen objects
display_group = displayio.Group()

# Create a text object with some content
text = displayio.Group(scale = 2, x=0, y=0)
text_area = label.Label(terminalio.FONT, text="Hello, sailor.")
text.append(text_area)
display_group.append(text)

# Place the display group on the screen
display.root_group = display_group

while True:
    display.refresh()
    time.sleep(180)   # do not refresh this e ink display faster than 180 seconds
    # update value

