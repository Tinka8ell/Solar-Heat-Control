# !/usr/bin/python3
# Solar.Monitor
"""
Originally intended as a monitor only version of the software.
Not sure that this is used any more ...
"""

import datetime
import random
import sys
import time

from Controller import KEYS
import GoogleBackingStore as Bs
from datasource import DataSource
import tkinter as Tk


class Monitor (Tk.Frame):
    'This will be the Monitor class for the Solar panel package'
    # class variables here

    # Initialisation code
    def __init__(self, master):
        # init parent
        Tk.Frame.__init__(self, master)

        self.bs = Bs()

        self.properties = {}
        self.lastPing = datetime.datetime.now()

        self.keys = KEYS

#      global clock

        # Create window

        # top is clock
        topframe = Tk.Frame(master)
        topframe.pack()  # default => "side = Tk.TOP"

        frame = Tk.Frame(master)
        frame.pack(side=Tk.LEFT)

        l1 = Tk.Label(topframe, text="Time: ")
        l1.pack(side=Tk.LEFT)

        # Tk.Label(root, font=('times', 20, 'bold'), bg='green')
        self.clock = Tk.Label(topframe, text="None")
        self.clock.pack(side=Tk.LEFT)
        self.currentTime = "none"

        # below is rest
        frame = Tk.Frame(frame)
        frame.pack(side=Tk.BOTTOM, fill=Tk.Y, expand=True)

        # left is info and buttons
        leftframe = Tk.Frame(frame)
        leftframe.pack(side=Tk.LEFT, fill=Tk.Y, expand=True)

        # left is info
        infoframe = Tk.LabelFrame(leftframe, text="Info")
        infoframe.pack(side=Tk.TOP)

        self.info = Tk.Text(infoframe, width=30, height=10)
        self.info.pack(side=Tk.LEFT)

        # middle will be a graph ???
        dataframe = Tk.LabelFrame(leftframe, text="Data")
        dataframe.pack(side=Tk.TOP, fill=Tk.BOTH, expand=True)

        data = Tk.Label(dataframe, text="Data will go here")
        data.pack(side=Tk.LEFT)

        # bottom is stop
        stop = Tk.Button(leftframe, text="STOP",
                         bg="red", command=self.terminate)
        stop.pack(side=Tk.BOTTOM)

        # right is log
        logframe = Tk.LabelFrame(frame, text="Log")
        logframe.pack(side=Tk.RIGHT, fill=Tk.BOTH)

        yscrollbar = Tk.Scrollbar(logframe, orient=Tk.VERTICAL)
        yscrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)

        xscrollbar = Tk.Scrollbar(logframe, orient=Tk.HORIZONTAL)
        xscrollbar.pack(side=Tk.BOTTOM, fill=Tk.X)

        self.logger = Tk.Text(logframe, yscrollcommand=yscrollbar.set,
                              xscrollcommand=xscrollbar.set, width=40, height=20, wrap=Tk.NONE)
        self.logger.pack(side=Tk.LEFT, fill=Tk.BOTH)

        yscrollbar.config(command=self.logger.yview)
        xscrollbar.config(command=self.logger.xview)

        # init values
        self.getInfo()
        # wake us up!
        self.tick()

    def tick(self):
        # get the current local time from the PC
        updatedTime = time.strftime('%H:%M:%S')
        # if time string has changed, update it
        if updatedTime != self.currentTime:
            self.currentTime = updatedTime
            self.clock.config(text=updatedTime)
            # add code here that needs to be kicked off
            self.ping()
        # calls itself every 200 milliseconds
        # to update the time display as needed
        # could use >200 ms, but display gets jerky
        self.clock.after(200, self.tick)

    def ping(self):
        current = datetime.datetime.now()
        period = self.getPeriod()
        if self.lastPing.timestamp() + period < current.timestamp():
            self.lastPing = current
            # time to do stuff, including check our ping period
            self.doStuff()
            self.getInfo()
            if period != self.getPeriod():
                # it has changed!
                self.log("Period changed from " + str(period) +
                         " to " + str(self.getPeriod()))

    def getPeriod(self):
        # give a minimum of 5 secs
        period = int(self.properties.get('Period', 5))
        if period < 5:
            period = 5
        if period > 60:  # max at one minute
            period = 60
        return period

    def doStuff(self):
        # periodic things to do, like check inputs and decide things
        return

    def terminate(self):
        # code here for are you sure?
        self.master.destroy()
        if self.master.master:
            self.master.master.destroy()

    def log(self, message):
        self.logger.insert(
            Tk.END, self.clock["text"] + ": " + message + chr(10))

    def getInfo(self):
        # read in the control info
        current = datetime.datetime.now()
        props = self.bs.getProperties()
        readTime = datetime.datetime.now() - current
        self.log("Get info took: " + str(readTime))
        if self.properties != props:
            self.properties = props
            self.info.delete("1.0", Tk.END)
            self.info.insert(Tk.END, "Properties: " + chr(10) + str(props))

    def main(root):
        print("Monitor.Monitor.main()")
        # Start up code called by calling Monitor.main()
        Solar = "https://drive.google.com/drive/folders/0B2EaP6O9ZuIiVXhYaXN2M01PeUk"
        print("Welcome to the Solar Monitor")
        print("You can find the data in:", Solar)
        root.title("Solar Monitor")
        monitor = Monitor(root)
        monitor.pack()
        return monitor


def main():
    print("Monitor.main()")
    root = Tk.Tk()
    Monitor.main(root)
    root.mainloop()


# execute only if run as a script
if __name__ == "__main__":
    print("Solar.Monitor loaded as __main__ with args:", sys.argv)
    main()
else:
    print("Called Monitor.py with __name__ ==",
          __name__, "and args:", sys.argv)
