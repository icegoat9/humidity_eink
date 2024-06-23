# Test composing text objects on E Ink Featherwing
# (initialization code from Adafruit il0373 demo)

import time
import board
import displayio
import fourwire
import adafruit_il0373
import terminalio
from adafruit_display_text import label

def curtime_as_string():
  t = time.localtime()
  tstr = f"{t.tm_year}-{t.tm_mon:02}-{t.tm_mday:02} {t.tm_hour:02}:{t.tm_min:02}"
  return tstr

print('running eink_test.py...')
print(curtime_as_string())

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
text = displayio.Group(scale = 3, x=10, y=30)
text_area = label.Label(terminalio.FONT, text="Hello, sailor.")
text.append(text_area)
display_group.append(text)

text2 = displayio.Group(scale = 2, x=10, y=70)
text2_area = label.Label(terminalio.FONT, text="text line 2")
text2.append(text2_area)
display_group.append(text2)

text3 = displayio.Group(scale = 2, x=10, y=100)
text3_area = label.Label(terminalio.FONT, text=curtime_as_string())
text3.append(text3_area)
display_group.append(text3)

# Place the display group on the screen
display.root_group = display_group

while True:
    #print(f'display refresh at {curtime_as_string()}')
    display.refresh()
    time.sleep(180)   # do not refresh this e ink display faster than 180 seconds
    # update value of existing display object
    text2_area.text = "Time passes..."
    text3_area.text = curtime_as_string()
    

