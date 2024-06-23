import time
import board
import displayio
import fourwire
import adafruit_il0373
import terminalio
from adafruit_display_text import label
import adafruit_ahtx0
import alarm

print("running humidity_eink.py...")

# Used to ensure the display is free in CircuitPython
displayio.release_displays()

# Initialize I2C connection to humidity sensor
aht_sensor = adafruit_ahtx0.AHTx0(board.I2C())

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

# Create a text object with some content
text = displayio.Group(scale=2, x=20, y=30)
text_area = label.Label(terminalio.FONT, text="Hello, damp world.", color=0x000000)
text.append(text_area)
display_group.append(text)


def get_humidity_string():
    h = f"RH {aht_sensor.relative_humidity:.0f}%"
    print(h)  # to serial terminal, for debugging
    return h


text2 = displayio.Group(scale=3, x=20, y=80)
text2_area = label.Label(
    terminalio.FONT,
    text=get_humidity_string(),
    color=0xFFFFFF,
    background_color=0xFF0000,
    padding_left=3,
    padding_right=3,
    padding_top=2,
    padding_bottom=2,
)
text2.append(text2_area)
display_group.append(text2)

# Place the display group on the screen
display.root_group = display_group

# test of sleeping, to integrate...
if not alarm.wake_alarm:
    print("********************\n* first boot, initializing 'sleep memory'")
    alarm.sleep_memory[0] = 0
else:
    print("* waking after deep sleep...")
time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 5)
print(f"* sleep/wake cycles (from sleep memory): {alarm.sleep_memory[0]}")
alarm.sleep_memory[0] += 1
print("* entering deep sleep now...")
alarm.exit_and_deep_sleep_until_alarms(time_alarm)
print("deep sleep failed")

while True:
    display.refresh()
    # do not refresh this e ink display faster than 180 seconds
    for i in range(18):
        time.sleep(10)
        get_humidity_string()  # to display to serial port for debugging
    # update value of existing display object
    text2_area.text = get_humidity_string()
