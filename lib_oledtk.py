#!/usr/bin/env python

"""
This is a tk implementation of the oled object 
used for the controller mini screen.

Created just for testing, it will emulate the display 
as small tkinter.TopLevel frame. 
"""

from PIL import Image, ImageDraw, ImageTk
from symbol import pass_stmt
from tkinter import Tk, Toplevel, Canvas


class oled():

    def __init__(self, master=None):
        self.width = 128
        self.height = 64
        # not sure if required: self.pages = int(self.height / 8)
        self.image = Image.new('1', (self.width, self.height))
        # this is a "draw" object for preparing display contents
        self.canvas = ImageDraw.Draw(self.image)
        if master is None:
            master = Tk()
        self.master = master
        self.window = Toplevel(master)
        self.window.geometry(f"{self.width}x{self.height}")
        self.place = Canvas(self.window, height=self.height, width=self.width)
        self.place.grid(column=0, row=0)
        # self.place.create_bitmap(self.image, x=0, y=0)

    def display(self):
        """
        The image on the "canvas" is flushed through to the tkinter.Toplevel
        frame as the "display".
        Takes the 1-bit image and dumps it to the frame of the Toplevel.
        """
        print("oled: display")
        self.picture = ImageTk.BitmapImage(image=self.image)
        self.place.create_image(
                (self.width / 2 + 1, 
                 self.height / 2 + 1), 
                image=self.picture)
        self.window.update_idletasks()
        return 

    def cls(self):
        """
        Blank the screen using a black rectangle:
        """
        print("oled: cls")
        self.canvas.rectangle(
            (0, 0, self.width-1, self.height-1), outline=0, fill=0)
        self.display()

    def onoff(self, onoff):
        """
        Make the Toplevel visible or not.
        """
        print("oled: onoff", onoff)
        if onoff == 0:
            self.window.withdraw()
        else:
            self.window.deiconify()
        return

