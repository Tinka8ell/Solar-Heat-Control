#!/usr/bin/env python 3
"""
I believe this code was taken from elsewhere and in practice
could stop the main thread.
Still used but now, under a threaded wrapper.
"""

from platform import machine
from time import sleep

from PIL import ImageFont, ImageDraw, Image


MACHINE = machine()
if MACHINE == "AMD64":
    from lib_oledtk import oled
else:
    from lib_oled96 import ssd1306
    from smbus import SMBus


BLANK_LINES = ["", "", "", "", ""]


class Screen ():
    'This will be used to write to the screen'

    # Initialisation code
    def __init__(self, label=None):
        # init data
        if MACHINE == "AMD64":
            self.oled = oled(label=label) # on Windows simulate
        else:
            i2cbus = SMBus(1)    # 1 = Raspberry Pi but NOT early REV1 board
            self.oled = ssd1306(i2cbus)
        # "draw" onto this canvas, then call display() to send the canvas contents to the hardware.
        self.font = ImageFont.truetype('FreeSans.ttf', 12)
        self.draw = self.oled.canvas
        self.oled.display()
        self.lines = BLANK_LINES
        return
        

    def clear(self):
        # clear display and any text from before
        self.lines = BLANK_LINES
        self.oled.cls()
        return 

    def off(self):
        # switch off the screen
        self.oled.onoff(0)
        return

    def on(self):
        # switch on the screen
        self.oled.onoff(1)
        return

    def set(self, lines):
        # set display to the first 5 of the following lines
        self.lines = lines + BLANK_LINES
        self.lines = self.lines[0:5]
        self.showLines()
        return

    def append(self, line):
        # append the line to the bottom of the display and scroll up screen
        self.lines.append(line)
        self.lines = self.lines[1:]
        self.showLines()
        return

    def showLines(self):
        # output all 5 lines to screen
        self.oled.cls()
        for i in range(len(self.lines)):
            self.draw.text((0, i * 12), self.lines[i], font=self.font, fill=1)
            # print("---->", self.lines[i])
        self.oled.display()
        return


