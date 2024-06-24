import time
import board
import displayio
import fourwire
import adafruit_il0373
import terminalio
from adafruit_display_text import label
import adafruit_display_shapes

print("running graph_test.py...")

# Used to ensure the display is free in CircuitPython
displayio.release_displays()

# Define the pins needed for display use, create displayio connection
spi = board.SPI()
epd_cs = board.D9
epd_dc = board.D10
epd_reset = None
epd_busy = None
display_bus = fourwire.FourWire(spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000)
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

# white background (TBD if simpler way to do this)
canvas = displayio.Bitmap(display.width, display.height, 1)
background_palette = displayio.Palette(1)
background_palette[0] = 0xFFFFFF  # White
background = displayio.TileGrid(canvas, pixel_shader=background_palette, x=0, y=0)
display_group.append(background)

# dummy data for graph
data = [10,15,15,20,18,25,35,40,50,51,51]

# layout constants
axes_py0 = 100
axes_px0 = 20
marker_size = 5
px_per_sample = 10
py_total = 90
rh_max = 60
py_per_rh = py_total / rh_max

# Draw graph axes and labels
#graph = displayio.Group()
#ax1 = 
#graph.append(ax1)

axis_labels = displayio.Group(scale=2)
axis_labels.append(label.Label(x = 30, y = axes_py0 + 10, terminalio.FONT, text="Time", color=0x000000))
axis_labels.append(label.Label(x = 0, y = 10, terminalio.FONT, text="RH %", color=0x000000))
graph.append(axis_labels)

# Draw graph ticks


# # Create a text object with some content
# text = displayio.Group(scale=2, x=20, y=20)
# text_area = label.Label(terminalio.FONT, text="Hello, damp world.", color=0x000000)
# text.append(text_area)
# display_group.append(text)

# text2 = displayio.Group(scale=3, x=20, y=70)
# text2_area = label.Label(
#     terminalio.FONT,
#     text="test"",
#     color=0xFFFFFF,
#     background_color=0xFF0000
# )
# text2.append(text2_area)
# display_group.append(text2)

# Place the display group on the screen
display.root_group = display_group
display.refresh()

while True:
  pass