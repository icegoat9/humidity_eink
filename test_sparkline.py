# adapted from examples/display_shapes_sparkline_ticks.py in CircuitPython bundle
# original file credits are:
## SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
## SPDX-License-Identifier: MIT
## created by Kevin Matocha - Copyright 2020 (C)

import time
import board
import displayio
import fourwire
import adafruit_il0373
import terminalio
import random
from adafruit_display_text import label
from adafruit_display_shapes.sparkline import Sparkline
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.rect import Rect


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

##########################################
# Create background bitmaps and sparklines
##########################################

# Baseline size of the sparkline chart, in pixels.
chart_width = display.width - 40
chart_height = display.height - 10

font = terminalio.FONT

line_color = 0x000000

# Setup the first bitmap and sparkline

# white background (TBD if simpler way to do this)
canvas = displayio.Bitmap(display.width, display.height, 1)
background_palette = displayio.Palette(1)
background_palette[0] = 0xFFFFFF  # White
background = displayio.TileGrid(canvas, pixel_shader=background_palette, x=0, y=0)

# mySparkline1 uses a vertical y range between 0 to 10 and will contain a
# maximum of 40 items
sparkline1 = Sparkline(
    width=chart_width,
    height=chart_height,
    max_items=40,
    y_min=0,
    y_max=60,
    x=30,
    y=5,
    color=line_color,
)

# Label the y-axis range

text_xoffset = -10
text_label1a = label.Label(
    font=font, text=str(sparkline1.y_top), color=line_color
)  # yTop label
text_label1a.anchor_point = (1, 0.5)  # set the anchorpoint at right-center
text_label1a.anchored_position = (
    sparkline1.x + text_xoffset,
    sparkline1.y,
)  # set the text anchored position to the upper right of the graph

text_label1b = label.Label(
    font=font, text=str(sparkline1.y_bottom), color=line_color
)  # yTop label
text_label1b.anchor_point = (1, 0.5)  # set the anchorpoint at right-center
text_label1b.anchored_position = (
    sparkline1.x + text_xoffset,
    sparkline1.y + chart_height,
)  # set the text anchored position to the upper right of the graph

xaxis_line = Line(sparkline1.x, sparkline1.y + chart_height, sparkline1.x + chart_width, sparkline1.y + chart_height, color = line_color)
yaxis_line = Line(sparkline1.x, sparkline1.y + chart_height, sparkline1.x, sparkline1.y , color = line_color)

bounding_rectangle = Rect(
    sparkline1.x, sparkline1.y, chart_width, chart_height, outline=line_color
)


# Create a group to hold the sparkline, text, rectangle and tickmarks
# append them into the group (my_group)
#
# Note: In cases where display elements will overlap, then the order the
# elements are added to the group will set which is on top.  Latter elements
# are displayed on top of former elemtns.

my_group = displayio.Group()

my_group.append(background)
my_group.append(sparkline1)
my_group.append(text_label1a)
my_group.append(text_label1b)
my_group.append(xaxis_line)
my_group.append(yaxis_line)

total_ticks = 6

for i in range(total_ticks + 1):
    x_start = sparkline1.x - 5
    x_end = sparkline1.x
    y_both = int(round(sparkline1.y + (i * (chart_height) / (total_ticks))))
    if y_both > sparkline1.y + chart_height - 1:
        y_both = sparkline1.y + chart_height - 1
    my_group.append(Line(x_start, y_both, x_end, y_both, color=line_color))

# Set the display to show my_group that contains the sparkline and other graphics
display.root_group = my_group

# add random data
for i in range(30):
  sparkline1.add_value(random.uniform(10, 55))

while True:
  display.refresh()
  time.sleep(180)
  for i in range(10):
    sparkline1.add_value(random.uniform(10, 55))
