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
data = [10, 15, 0, 20, 21, 23, 19, 20, 21, 23, 19, 23, 19, 38, 78, 45, 55, 50, 46, 41]

# layout constants
graph_y0 = 115
graph_x0 = 55
marker_size = 5
px_per_sample = 10
graph_width = 140
graph_height = 100
rh_max = 60
py_per_rh = graph_height / rh_max
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
    graph.append(Line(graph_x0 - 4, graph_y0 - i * py_tick, graph_x0 + 4, graph_y0 - i * py_tick, color=BLACK))
    if (i % 2) == 1:
        # tick label
        graph.append(
            label.Label(x=graph_x0 - 18, y=graph_y0 - i * py_tick, font=terminalio.FONT, text=str(i * 10), color=BLACK)
        )

# Set up graph object with dummy data
data_group = displayio.Group()
for i in range(len(data)):
    r = 2
    if i == len(data) - 1:
        r = 4
    data_group.append(Circle(x0=graph_x0 + (i + 1) * px_tick, y0=graph_y0, r=r, fill=BLACK, outline=None))


def update_graph(updatedata):
    """update y values and colors of graph data"""
    for i in range(len(updatedata)):
        v = min(rh_max, max(updatedata[i], 0))
        c = BLACK
        r = 2
        if i == len(updatedata) - 1:
            c = RED
            r = 4
        dy = int(v * py_per_rh)
        if v == 0:
            dy = -100  # offset zero (invalid?) data off the screen
        data_group[i].y0 = graph_y0 - dy
        data_group[i].r = r
        data_group[i].fill = c
    data_text[0].text = f"{updatedata[-1]}"

graph.append(data_group)

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
update_graph(data)

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
    update_graph(newdata)
    display.refresh()
    quit()
