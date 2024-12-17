# Test drawing what was initially conceived as a box-and-whisker plot for each day's data,
#  though in prototyping evolved to a simpler plot with just a line to show min/max values
#  for the day and a circle to mark the mean, so this test program is slightly misnamed.

import time
import board
import displayio
import fourwire
import adafruit_il0373
import terminalio
from adafruit_display_text import label
import adafruit_display_shapes
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.circle import Circle

print("running test_box_graph.py")

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

# color constants
BLACK = 0x000000
WHITE = 0xFFFFFF
RED = 0xFF0000

# Create the display object - the third color is red (0xff0000)
display = adafruit_il0373.IL0373(
    display_bus,
    width=296,
    height=128,
    rotation=270,
    busy_pin=epd_busy,
    highlight_color=RED,
)

# Create a display group for our screen objects
display_group = displayio.Group()

# white background (TBD if simpler way to do this)
canvas = displayio.Bitmap(display.width, display.height, 1)
background_palette = displayio.Palette(1)
background_palette[0] = WHITE  # White
background = displayio.TileGrid(canvas, pixel_shader=background_palette, x=0, y=0)
display_group.append(background)

# dummy data for graph
data = [5, 7, 13, 23, 16, 10, 19, 20, 13, 18, 17, 6, 20, 15, 22, 20, 21, 23, 19, 20, 21, 23, 19, 23, 19, 38, 78, 45, 55, 50, 46, 41]
data_per_box = 12  # how many data points per box (often meaning, per day)

# graph layout constants
graph_y0 = 115
graph_x0 = 54
marker_size = 2
highlight_marker_size = 4
px_per_sample = 10
graph_width = 140
graph_height = 100
rh_max = 60
py_per_rh = graph_height / rh_max
tick_halfwidth = 3
yticks = rh_max // 10
py_tick = graph_height // yticks
px_tick = graph_width // len(data)

# Draw graph axes and labels
graph = displayio.Group()

xaxis_line = Line(graph_x0, graph_y0, graph_x0 + graph_width, graph_y0, color=BLACK)
yaxis_line = Line(graph_x0, graph_y0, graph_x0, graph_y0 - graph_height, color=BLACK)
graph.append(xaxis_line)
graph.append(yaxis_line)

axis_labels = displayio.Group(scale=2, x=6, y=graph_y0 - (graph_height // 2) - 10)
# axis_labels.append(label.Label(x=30, y=graph_y0 + 10, font=terminalio.FONT, text="Time", color=BLACK))
axis_labels.append(label.Label(font=terminalio.FONT, text="RH", color=BLACK))
axis_labels.append(label.Label(x=3, y=11, font=terminalio.FONT, text="%", color=BLACK))
graph.append(axis_labels)

# Draw graph ticks
yticks_group = []
for i in range(yticks + 1):
    graph.append(Line(graph_x0 - tick_halfwidth, graph_y0 - i * py_tick, graph_x0 + tick_halfwidth, graph_y0 - i * py_tick, color=BLACK))
    if (i % 2) == 1:
        # tick label
        graph.append(
            label.Label(x=graph_x0 - 18, y=graph_y0 - i * py_tick, font=terminalio.FONT, text=str(i * 10), color=BLACK)
        )

def mean(list):
    return sum(list) / len(list)

data_group = displayio.Group()
graph.append(data_group)
data_group_index = graph.index(data_group)

def scale_and_clip(rh):
    """Convert RH data into pixel Y position, with some clipping safety checks."""
    d = min(rh_max, max(rh, 0))
    dy = int(d * py_per_rh)
    if dy == 0:
        dy = -100  # offset zero (invalid?) data off the screen
    return dy

def overwrite_graph(updatedata):
    """create graph data object, and replace existing display.io Group"""
    data_group = displayio.Group()
    num_boxes = (len(updatedata) - 1) // data_per_box + 1
    for b in range(num_boxes):
        # extract subset of data for this box
        boxdata = updatedata[data_per_box * b: data_per_box * (b+1)]
        # calculate (clipped-to-visible) versions of grouped data parameters
        dmin_y = scale_and_clip(min(boxdata))
        dmax_y = scale_and_clip(max(boxdata))
        davg_y = scale_and_clip(mean(boxdata))
        x = graph_x0 + 5 + (b + 1) * px_tick
        data_group.append(Line(x0 = x, y0 = graph_y0 - dmin_y, x1 = x, y1 = graph_y0  - dmax_y, color=BLACK))
        data_group.append(Circle(x, graph_y0 - davg_y, r = marker_size, fill=BLACK, outline=None))
    # add most recent data
    drecent_y = scale_and_clip(updatedata[-1])
    data_group.append(Circle(x, graph_y0 - drecent_y, r = highlight_marker_size, fill=RED, outline=None))
    # replace past data
    graph.pop(data_group_index)
    graph.insert(data_group_index, data_group)
    data_text[0].text = f"{updatedata[-1]}"

data_text = displayio.Group(scale=3, x=display.width - 67, y=graph_y0 - int(data[-1] * py_per_rh))
data_text.append(
    label.Label(
        terminalio.FONT,
        text="00",
        color=WHITE,
        background_color=RED,
        padding_left=3,
        padding_right=3,
        padding_top=1,
        padding_bottom=1,
    )
)
graph.append(data_text)

# update graph and data_text with actual data (well, dummy data)
overwrite_graph(data)

# Place the display group on the screen
display_group.append(graph)

# special runtime # in corner
data_text = displayio.Group(scale=1, x=display.width - 40, y=display.height - 10)
data_text.append(label.Label(terminalio.FONT, text="27", color=BLACK))
display_group.append(data_text)

display.root_group = display_group
display.refresh()

while True:
    # dummy data for graph
    time.sleep(180)
    newdata = [20, 21, 23, 19, 20, 21, 23, 19, 23, 19, 38, 78, 45, 55, 50, 46, 41, 35, 27, 17]
    overwrite_graph(newdata)
    display.refresh()
    quit()
