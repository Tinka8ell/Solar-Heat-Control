#!/usr/bin/env python

"""
This is a tk implementation of the oled object 
used for the controller mini screen.

Created just for testing, it will emulate the display 
as small tkinter.TopLevel frame. 
"""

from PIL import Image, ImageDraw, ImageTk
from symbol import pass_stmt
from tkinter import N, E, W, S


class oled():

    def __init__(self, label):
        # size of the "screen" in pixels
        self.width = 128
        self.height = 64
        
        self.image = Image.new('1', (self.width, self.height))
        # this is a "draw" object for preparing display contents
        self.canvas = ImageDraw.Draw(self.image)

        # GUI components
        if label is None:
            raise KeyError("On windows and need a label")
        self.label = label
        self.cls() # blank the image and display it
        self.onoff(1)  # make visible
        return

    def display(self):
        """
        The image on the "canvas" is flushed through to the tkinter 
        canvas as the "display".
        Takes the 1-bit image and dumps it to the frame of the Toplevel.
        """
        self.picture = ImageTk.BitmapImage(image=self.image)
        self.label["image"] = self.picture
        self.label.update_idletasks() # not sure if required ...
        return 

    def cls(self):
        """
        Blank the screen using a black rectangle:
        """
        self.canvas.rectangle(
            (0, 0, self.width-1, self.height-1), outline=0, fill=0)
        self.display()
        return

    def onoff(self, onoff):
        """
        Make the label visible or not.
        """
        if onoff == 0:
            self.label.grid_forget()  # make disappear
        else:
            self.label.grid(row=0, column=0, sticky=(E, W, N, S))
        return

