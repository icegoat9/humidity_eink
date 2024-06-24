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

# are we booting up or waking from deep sleep?
if not alarm.wake_alarm:
    print("first boot, initializing 'sleep memory'")
    alarm.sleep_memory[0] = 0
else:
    print("waking after deep sleep...")

# Create a text object with some content
text = displayio.Group(scale=2, x=20, y=20)
text_area = label.Label(terminalio.FONT, text="Hello, damp world.", color=0x000000)
text.append(text_area)
display_group.append(text)

def get_humidity_string():
    h = f"RH {aht_sensor.relative_humidity:.0f}%"
    print(h)  # to serial terminal, for debugging
    return h

text2 = displayio.Group(scale=3, x=20, y=70)
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

text3 = displayio.Group(scale=1, x=180, y=65)
text3_area = label.Label(
    terminalio.FONT,
    text=f"previous\nRH {alarm.sleep_memory[0]}%",
    color=0x000000,
)
text3.append(text3_area)
display_group.append(text3)

# Place the display group on the screen
display.root_group = display_group

while True:
    display.refresh()
    # deep sleep until next update...
    # do not refresh this e ink display faster than 180 seconds
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 180)
    last_RH = int(aht_sensor.relative_humidity)
    print(f"saving last RH reading {last_RH} to low-power sleep memory")
    alarm.sleep_memory[0] = last_RH
    print("entering deep sleep now...")
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)
    print("deep sleep failed, reached unexpected location in code...")
