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
data = [10, 15, 15, 20, 18, 27, 45, 55, 50, 46, 43]

# layout constants
graph_py0 = 120
graph_px0 = 60
marker_size = 5
px_per_sample = 10
graph_width = 160
graph_height = 110
rh_max = 60
py_per_rh = graph_height / rh_max
font = terminalio.FONT
yticks = rh_max // 10
py_tick = graph_height // yticks
px_tick = graph_width // len(data)

# Draw graph axes and labels
graph = displayio.Group()

xaxis_line = Line(graph_px0, graph_py0, graph_px0 + graph_width, graph_py0, color=0x000000)
yaxis_line = Line(graph_px0, graph_py0, graph_px0, graph_py0 - graph_height, color=0x000000)
graph.append(xaxis_line)
graph.append(yaxis_line)

axis_labels = displayio.Group(scale=2, x=10, y=graph_py0 - (graph_height // 2) - 10)
# axis_labels.append(label.Label(x=30, y=graph_py0 + 10, font=font, text="Time", color=0x000000))
axis_labels.append(label.Label(font=font, text="RH", color=0x000000))
axis_labels.append(label.Label(x=4, y=11, font=font, text="%", color=0x000000))
graph.append(axis_labels)

# Draw graph ticks
yticks_group = []
for i in range(yticks + 1):
    graph.append(Line(graph_px0 - 4, graph_py0 - i * py_tick, graph_px0 + 4, graph_py0 - i * py_tick, color=0x000000))
    if (i % 2) == 1:
        # tick label
        graph.append(
            label.Label(x=graph_px0 - 18, y=graph_py0 - i * py_tick, font=font, text=str(i * 10), color=0x000000)
        )

# Draw data
data_group = displayio.Group()
for i in range(len(data)):
    v = data[i]
    c = 0x000000
    r = 3
    if i == len(data) - 1:
        c = 0xFF0000
        r = 5
    data_group.append(
        Circle(x0=graph_px0 + (i + 1) * px_tick, y0=graph_py0 - int(v * py_per_rh), r=r, fill=c, outline=None)
    )

graph.append(data_group)

data_text = displayio.Group(scale=3, x=display.width - 55, y=graph_py0 - int(data[-1] * py_per_rh))
data_text.append(
    label.Label(
        terminalio.FONT,
        text=f"{data[-1]}",
        color=0xFFFFFF,
        background_color=0xFF0000,
        padding_left=3,
        padding_right=3,
        padding_top=1,
        padding_bottom=1,
    )
)
graph.append(data_text)

# Place the display group on the screen
display_group.append(graph)
display.root_group = display_group
display.refresh()

while True:
    pass
