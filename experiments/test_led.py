import time
import board
from digitalio import DigitalInOut, Direction, Pull

led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT

while True:
    led.value = True
    time.sleep(0.3)
    led.value = False
    time.sleep(0.3)
