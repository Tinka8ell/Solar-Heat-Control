#!/usr/bin/env python 3
"""
I believe this code was taken from elsewhere and in practice
could stop the main thread.
Still used but now, under a threaded wrapper.
"""

from time import sleep

from PIL import ImageFont, ImageDraw, Image

from lib_oled96 import ssd1306
from smbus import SMBus


class Screen ():
    'This will be used to write to the screen'

    # Initialisation code
    def __init__(self):
        # init data
        self.font = ImageFont.truetype('FreeSans.ttf', 12)
        i2cbus = SMBus(1)    # 1 = Raspberry Pi but NOT early REV1 board
        self.oled = ssd1306(i2cbus)
        # "draw" onto this canvas, then call display() to send the canvas contents to the hardware.
        self.draw = self.oled.canvas
        self.oled.display()
        self.lines = ["", "", "", "", ""]

    def clear(self):
        # clear display and any text from before
        self.lines = ["", "", "", "", ""]
        self.oled.cls()

    def off(self):
        # switch off the screen
        self.oled.onoff(0)

    def on(self):
        # switch on the screen
        self.oled.onoff(1)

    def set(self, lines):
        # set display to the following lines
        self.lines = lines + ["", "", "", "", ""]
        self.lines = self.lines[0:5]
        self.showLines()

    def append(self, line):
        # append the line to the bottom of the display and scroll up screen
        self.lines.append(line)
        self.lines = self.lines[1:]
        self.showLines()

    def showLines(self):
        # output all 5 lines to screen
        self.oled.cls()
        for i in range(len(self.lines)):
            self.draw.text((0, i * 12), self.lines[i], font=self.font, fill=1)
        self.oled.display()


def main():
    # this is for testing
    scr = Screen()
    scr.append("Line test")
    sleep(5)
    '''
   text = "The quick brown frox jumps over the lazy dog"
   lines = text.split()
   for line in lines:
      sleep(1)
      scr.append(line)
   '''
    line = ""
    for i in range(96 + 32 + 32, 96 + 32 + 32 + 15):
        line += chr(i)
    scr.append(line)
    line = ""
    line = chr(164) + chr(164) + chr(164) + chr(170) + \
        chr(170) + chr(170) + chr(168) + chr(168) + chr(168)
    scr.append(line)
    line = "23.4" + chr(164) + "C, 23.4" + chr(170) + \
        "C, 23.4" + chr(168) + "C"
    scr.append(line)


# execute only if run as a script
if __name__ == "__main__":
    main()  # execute test code ...
