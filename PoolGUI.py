# !/usr/bin/python3
# PoolGui.py
"""
GUI view from the Solar Powered Pool Controller.

This handles all the GUI display so we can view what's going on under VNC.
"""
from datetime import datetime, timedelta
from platform import machine
from time import strftime
from tkinter import Frame, LabelFrame, Label, Text, Button, Scrollbar
from tkinter import IntVar, StringVar
from tkinter import LEFT, RIGHT, TOP, BOTTOM, BOTH, NONE
from tkinter import N, E, W, S, NORMAL, DISABLED
from tkinter import Tk, Toplevel
from tkinter import X, Y, END, VERTICAL, HORIZONTAL
from tkinter import Toplevel

from FileBackingStore import FileBackingStore
from Screen import Screen
from UbidotsBackingStore import UbidotsBackingStore


# Global constants
MACHINE = machine()
# To enable debugging on non-pi environment set REAL to False.
REAL = True
if MACHINE == "AMD64":
    REAL = False  # on Windows can't be real!


class PoolGUI(Frame):
    'This will be the GUI class for the Solar panel package'

    # Initialisation code
    def __init__(self, master, callback=None):
        '''
        Parameters:
            master is the main GUI window to use, usually Tk.
            callback is what to call each period.
        '''
        # init parent
        super().__init__(master)
        self.setCallback(callback)
        self._lastTime = None
        self.text = ["Nothing happening", "No callback"]

        # create "screen" object
        if REAL:
            self._screen = Screen()
        else:
            toplevel = Toplevel(master)
            toplevel.title('Pseudo Screen')
            frame = Frame(toplevel)
            frame.grid(row=0, column=0, sticky=(E, W, N, S))
            label = Label(frame)
            label.grid(row=0, column=0, sticky=(E, W, N, S))
            self._screen = Screen(label)

        # init data
        self._nextPing = datetime.now()
        adjust = timedelta(
            0, self._nextPing.second, self._nextPing.microsecond)
        self._nextPing -= adjust  # current time less seconds

        # init view
        # Create window
        """
        We are looking at:
        +===================================+
        |   Time: hh:mm:ss Next: hh:mm:ss   |
        +-Info-----------+-Log--------------+
        |                |                 ^|
        |                |                 ||
        |                |                 ||
        |                |                 ||
        +----------------+                 ||
        |                |                 ||
        |                |                 ||
        |     <STOP>     |<===============>v|
        +----------------+------------------+
        """

        # top is _clock
        topframe = Frame(master)
        topframe.grid(column=0, row=0)
        master.grid_rowconfigure(0, weight=0)  # make topframe fixed
        master.grid_rowconfigure(1, weight=1)  # make rest able to stretch
        l1 = Label(topframe, text="Time: ")
        l1.grid(column=0, row=0)
        # Label(root, font=('times', 20, 'bold'), bg='green')
        self._clockString = StringVar(master, "None")
        self._clock = Label(topframe, textvariable=self._clockString)
        self._clock.grid(column=1, row=0)
        self._currentTime = "none"
        l2 = Label(topframe, text="Next: ")
        l2.grid(column=3, row=0)
        # Label(root, font=('times', 20, 'bold'), bg='green')
        self._nextString = StringVar(master, "None")
        self._next = Label(topframe, textvariable=self._nextString)
        self._next.grid(column=4, row=0)
        self._nextTime = "none"

        # below is rest
        frame = Frame(master)
        frame.grid(column=0, row=1, sticky=(E, W, N, S))
        master.grid_columnconfigure(0, weight=1)  # make whole able to stretch

        # left is _info and buttons
        leftframe = Frame(frame)
        leftframe.grid(column=0, row=0, sticky=(E, W, N, S))
        frame.grid_columnconfigure(0, weight=0)  # make left fixed width
        frame.grid_rowconfigure(0, weight=1)  # make left stretch down

        # left is _info
        infoframe = LabelFrame(leftframe, text="Info")
        infoframe.grid(column=0, row=0, sticky=(E, W, N, S))
        leftframe.grid_rowconfigure(0, weight=1)  # make info stretch down
        self._info = Text(infoframe, width=30, height=10)
        self._info.grid(column=0, row=0, sticky=(E, W, N, S))
        self._info.config(state=DISABLED)  # so read only!

        # bottom is stop
        stop = Button(leftframe, text="STOP",
                         bg="red", command=self.terminate)
        stop.grid(column=0, row=2)
        leftframe.grid_rowconfigure(2, weight=0)  # make button fixed

        # right is log
        logframe = LabelFrame(frame, text="Log")
        logframe.grid(column=1, row=0, sticky=(E, W, N, S))
        frame.grid_columnconfigure(1, weight=1)  # make right (log) frame able to stretch
        frame.grid_rowconfigure(0, weight=1)  # make and stretch down

        yscrollbar = Scrollbar(logframe, orient=VERTICAL)
        yscrollbar.grid(column=1, row=0, sticky=(N, S))
        xscrollbar = Scrollbar(logframe, orient=HORIZONTAL)
        xscrollbar.grid(column=0, row=1, sticky=(E, W))
        self._logger = Text(logframe, yscrollcommand=yscrollbar.set,
                              xscrollcommand=xscrollbar.set,
                              width=60, height=20, wrap=NONE)
        self._logger.grid(column=0, row=0, sticky=(E, W, N, S))
        logframe.grid_rowconfigure(0, weight=1)  # make logger able to stretch
        logframe.grid_columnconfigure(0, weight=1)  # make logger able to stretch
        self._logger.config(state=DISABLED)  # so read only!
        yscrollbar.config(command=self._logger.yview)
        xscrollbar.config(command=self._logger.xview)

        # set default period ...
        self._period = 30  # seconds

        # wake us up!
        self._tick()
        return

    def setCallback(self, callback):
        '''
        Allow owner to set a callback after initialisation
        '''
        self._callback = callback
        return

    def setPeriod(self, period):
        '''
        Set period.
        Called by controller to change the period
        between calls to callback
        '''
        self._period = period
        return

    def terminate(self):
        # put code here for "Are you sure?"
        self.master.destroy()
        if self.master.master:
            self.master.master.destroy()
        return

    def log(self, message):
        # add to first line
        text = self._clockString.get() + ": " + message
        self._logger.config(state=NORMAL)
        # if removing scrolled off line: self._logger.delete("30.0", END)
        self._logger.insert("1.0", text + chr(10))
        self._logger.config(state=DISABLED)

        # also log to stdout
        print(text)
        return

    def _tick(self):
        # get the current local time from the computer
        updatedTime = strftime('%H:%M:%S')
        # if time string has changed, update it
        if updatedTime != self._currentTime:
            self._currentTime = updatedTime
            self._clockString.set(updatedTime)
            # add code here that needs to be kicked off start of every second
            self._ping()
        # calls itself every 200 milliseconds
        # to update the time display as needed
        # could use >200 ms, but display gets jerky
        self.after(200, self._tick)
        return

    def _ping(self):
        current = datetime.now()
        if current.timestamp() > self._nextPing.timestamp():
            # currently period is in seconds, even if set in minutes
            while current.timestamp() > self._nextPing.timestamp():
                self._nextPing += timedelta(seconds=self._period)
                # print("Time adjust:", self._nextPing, self._currentTime)
            self._nextTime = self._nextPing.strftime('%H:%M:%S')
            self._nextString.set(self._nextTime)
            # print("Times:", self._nextTime, self._nextPing, self._currentTime)
            # print("Ping time:", self._currentTime)
            # time to do stuff, including check our _ping period
            self.update_idletasks()  # update display before we do stuff
            self._doStuff()
            self._guiShow()
        self._showValues()
        return

    def _doStuff(self):
        # periodic things to do, like check inputs and decide things
        if self._callback is not None:
            self.text = self._callback()
        return

    def _showValues(self):
        # record to screen ...
        if self._screen is not None:
            thisTime = "T: " + self._currentTime + " / " + self._nextTime
            if thisTime != self._lastTime:
                self._lastTime = thisTime
                text = [thisTime] + self.text
                self._screen.set(text)
        return

    def _guiShow(self):
        # strip off first line as already on screen
        # and join rest with newlines
        text = "\n".join(self.text)
        self._info.config(state=NORMAL)
        self._info.delete("1.0", END)
        self._info.insert(END, text)
        self._info.config(state=DISABLED)
        return


# execute only if run as a script - for testing
if __name__ == "__main__":
    root = Tk()
    PoolGUI(root)  # start without a call back
    root.mainloop()
