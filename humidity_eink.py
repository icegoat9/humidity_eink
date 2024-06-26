"""
Read relative humdity from I2C sensor, display on E Ink screen.

Additionally, display graph of RH over time, and deep sleep for long runtime on battery.
"""

import time
import board
import displayio
import fourwire
import adafruit_il0373
import terminalio
from adafruit_display_text import label
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.circle import Circle
import adafruit_ahtx0
import alarm
import rtc

# initialize real-time clock (TBD if it works on this board)
rtc_object = rtc.RTC()

# color and font constants
BLACK = 0x000000
WHITE = 0xFFFFFF
RED = 0xFF0000
FONT = terminalio.FONT

# Initialize I2C connection to humidity sensor
aht_sensor = adafruit_ahtx0.AHTx0(board.I2C())

# initialize a fixed-length RH buffer and related variables
# note: these variables may be overwritten below from Sleep Memory if we are resuming after a deep sleep
rh_data = [0] * 20
rh_data_index = 0
run_cycles = 0


def save_to_sleep_memory():
    alarm.sleep_memory[0] = run_cycles
    alarm.sleep_memory[1] = rh_data_index
    for i in range(len(rh_data)):
        alarm.sleep_memory[i + 2] = rh_data[i]


def load_from_sleep_memory():
    global rh_data
    global rh_data_index
    global run_cycles
    run_cycles = alarm.sleep_memory[0]
    rh_data_index = alarm.sleep_memory[1]
    for i in range(len(rh_data)):
        rh_data[i] = alarm.sleep_memory[i + 2]


# Initialize data depending on bootup vs. waking from deep sleep
if not alarm.wake_alarm:
    print("**********************************")
    print("first boot, initializing variables")
    run_cycles = 0
    # rh_data = [0] * 20
    rh_data_index = 0
    # DEBUG: swap in temporary dummy data
    rh_data = [10, 15, 0, 20, 21, 23, 19, 20, 21, 23, 19, 23, 19, 38, 78, 45, 55, 50, 46, 41]
    rh_data_index = 18
else:
    print("waking after deep sleep, loading variables from sleep memory")
    load_from_sleep_memory()

### Display initialization

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

# Create the display object
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

#############################
### Lay out display content

# white background
canvas = displayio.Bitmap(display.width, display.height, 1)
background_palette = displayio.Palette(1)
background_palette[0] = WHITE
background = displayio.TileGrid(canvas, pixel_shader=background_palette, x=0, y=0)
display_group.append(background)

# def append_data(n):
#    prev_data[prev_data_index] = n
#    prev_data_index += 1
#    if prev_data_index >= len(prev_data):
#        prev_data_index = 0

# chart layout constants
graph_y0 = 115
graph_x0 = 55
marker_size = 2
px_per_sample = 10
graph_width = 140
graph_height = 100
rh_max = 60
py_per_rh = graph_height / rh_max
yticks = rh_max // 10
py_tick = graph_height // yticks
px_tick = graph_width // len(rh_data)

# Draw graph axes and labels
graph = displayio.Group()

xaxis_line = Line(graph_x0, graph_y0, graph_x0 + graph_width, graph_y0, color=BLACK)
yaxis_line = Line(graph_x0, graph_y0, graph_x0, graph_y0 - graph_height, color=BLACK)
graph.append(xaxis_line)
graph.append(yaxis_line)

axis_labels = displayio.Group(scale=2, x=6, y=graph_y0 - (graph_height // 2) - 10)
axis_labels.append(label.Label(font=FONT, text="RH", color=BLACK))
axis_labels.append(label.Label(x=3, y=11, font=FONT, text="%", color=BLACK))
graph.append(axis_labels)

# Draw graph ticks
yticks_group = []
for i in range(yticks + 1):
    graph.append(Line(graph_x0 - 4, graph_y0 - i * py_tick, graph_x0 + 4, graph_y0 - i * py_tick, color=BLACK))
    if (i % 2) == 1:
        graph.append(label.Label(x=graph_x0 - 18, y=graph_y0 - i * py_tick, font=FONT, text=str(i * 10), color=BLACK))

# Set up graph object with dummy data
data_group = displayio.Group()
for i in range(len(rh_data)):
    r = marker_size
    if i == len(rh_data) - 1:
        r = marker_size * 2
    data_group.append(Circle(x0=graph_x0 + (i + 1) * px_tick, y0=graph_y0, r=r, fill=BLACK, outline=None))

graph.append(data_group)

current_rh_text = displayio.Group(scale=3, x=display.width - 70, y=graph_y0)
current_rh_text.append(
    label.Label(
        FONT,
        text="00",
        color=WHITE,
        background_color=RED,
        padding_left=3,
        padding_right=3,
        padding_top=1,
        padding_bottom=1,
    )
)
graph.append(current_rh_text)

# Place the display group on the screen
display_group.append(graph)

# special runtime # in corner
runtime_text = displayio.Group(scale=1, x=display.width - 40, y=display.height - 10)
runtime_text.append(label.Label(FONT, text=f"{run_cycles}", color=BLACK))
display_group.append(runtime_text)

## debug datetime from RTC
# runtime_text = displayio.Group(scale=1, x=display.width - 40, y=display.height - 10)
# runtime_text.append(label.Label(FONT, text=f"{run_cycles}", color=BLACK))
# display_group.append(runtime_text)

# Place the display group on the screen
display.root_group = display_group


## functions to update graph and current_rh_text with actual data


def update_rh_data():
    global rh_data
    global rh_data_index
    current_rh = aht_sensor.relative_humidity
    rh_data_index = (rh_data_index + 1) % len(rh_data)
    print(f"humidity = {current_rh}%, saving to slot {rh_data_index} in data buffer")
    rh_data[rh_data_index] = int(current_rh + 0.5)  # round


# update graph, pulling data from global rh_data buffer
def update_graph():
    for i in range(len(rh_data)):
        # start by pulling data from oldest location (i.e. one beyond current data index in circular buffer)
        i_rel = (i + rh_data_index + 1) % len(rh_data)
        val = min(rh_max, max(rh_data[i_rel], 0))
        c = BLACK
        r = marker_size
        if i == len(rh_data) - 1:
            c = RED
            r = marker_size * 2
        dy = int(val * py_per_rh)
        if val == 0:
            dy = -100  # offset zero (invalid?) data off the screen
        data_group[i].y0 = graph_y0 - dy
        data_group[i].r = r
        data_group[i].fill = c
    current_rh_text[0].text = f"{rh_data[rh_data_index]}"
    rh_y = graph_y0 - int(rh_data[rh_data_index] * py_per_rh)
    rh_y = min(100, max(20, rh_y))
    current_rh_text.y = rh_y


while True:
    # update RH and graph with current reading
    update_rh_data()
    update_graph()
    run_cycles += 1
    # actually display to E Ink screen
    display.refresh()
    ## deep sleep until next update period
    # NOTE: do not refresh this e ink display faster than 180 seconds
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 180)
    # wake and update screen hourly
    # time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 3600)
    print("entering deep sleep now, saving critical data to sleep memory...")
    save_to_sleep_memory()
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)
    print("ERROR: deep sleep failed, reached unexpected location in code...")
