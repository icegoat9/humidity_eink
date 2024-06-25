import time
import board
import displayio
import fourwire
import adafruit_il0373
import terminalio
from adafruit_display_text import label
import adafruit_ahtx0
import alarm
import rtc

print("running humidity_eink.py...")

rtc_object = rtc.RTC()

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
    alarm.sleep_memory[0] = 0   # number of sleep/wake cycles since boot
    alarm.sleep_memory[1] = 0   # last RH value
#    prev_data = [0] * 20 
#    prev_data_index = 0
else:
    print("waking after deep sleep...")

#def append_data(n):
#    prev_data[prev_data_index] = n
#    prev_data_index += 1
#    if prev_data_index >= len(prev_data):
#        prev_data_index = 0

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

text3 = displayio.Group(scale=2, x=170, y=70)
text3_area = label.Label(
    terminalio.FONT,
    text=f"(prev {alarm.sleep_memory[1]}%)",
    color=0x000000,
)
text3.append(text3_area)
display_group.append(text3)

text4 = displayio.Group(scale=1, x=20, y=115)
tm = time.localtime()
tmstr = f"{tm.tm_year}-{tm.tm_mon:02}-{tm.tm_mday:02} {tm.tm_hour:02}:{tm.tm_min:02}"
text4_area = label.Label(
    terminalio.FONT,
    text=f"runtime: {alarm.sleep_memory[0]} hours",
    color=0x000000,
)
text4.append(text4_area)
display_group.append(text4)


# Place the display group on the screen
display.root_group = display_group

while True:
    display.refresh()
    # deep sleep until next update...
    # do not refresh this e ink display faster than 180 seconds
    #time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 180)
    # wake and update screen hourly?
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 3600)
    last_RH = int(aht_sensor.relative_humidity)
    print(f"saving last RH reading {last_RH} to low-power sleep memory")
    alarm.sleep_memory[0] += 1
    alarm.sleep_memory[1] = last_RH
    print("entering deep sleep now...")
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)
    print("deep sleep failed, reached unexpected location in code...")
