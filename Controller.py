# !/usr/bin/python3
# Controller.py
"""
Solar Powered Pool Controller.

This is the main module for this controller.  
It runs using a dummy DataSource by detecting it is not on a Raspberry Pi
and setting the global constant REAL to False.
"""
from datetime import datetime, timedelta
from platform import machine
from time import strftime

from FileBackingStore import FileBackingStore 
from SafeInternetDownload import SafeInternetDownload
from SafeInternetOffload import SafeInternetOffload
from SafeScreen import SafeScreen
from tkinter import Tk, Frame, LabelFrame, Label, Text, Button, Scrollbar
from tkinter import LEFT, RIGHT, TOP, BOTTOM, BOTH, NONE
from tkinter import X, Y, END, VERTICAL, HORIZONTAL

from tkinter import N, E, W, S, NORMAL, DISABLED
from tkinter import IntVar, StringVar


MACHINE = machine()
# To enable debugging on non-pi environment set REAL to False.
REAL = True
if MACHINE == "AMD64":
    REAL = False # on Windows can't be real!

if REAL:
    from RealDataSource import RealDataSource as DataSource 
else:
    from DummyDataSource import DummyDataSource as DataSource

# Global constants
KEYS = ["Power", "Photo", "Pump", "Pool", "Water", "Flow", "PumpP", "Depth"]
RANGES = [(0, 1000), (0, 10), (0, 1), (0, 35),
          (0, 35), (0, 30), (0, 1000), (5, 150)]
CONTROLS = ["Period", "Threshold", "Off"]
FACTOR = 60  # 1 for seconds or 60 for minutes
DELAY_BEFORE_TESTING = timedelta(seconds=60 * 5)  # 5 minutes
MAX_LIGHT = 20  # increased from 10 to 20
TIMEOUT = 20.0
DEG_C = chr(164) + "C"


class Controller (Frame):
    'This will be the Controller class for the Solar panel package'

    # Initialisation code
    def __init__(self, master):
        # init parent
        super().__init__(master)

        # allow the screen to try and display
        self.ScreenRetry = 0

        # init data
        self.bs = FileBackingStore()
        self.ubs = None  # created and maintained as we need it

        self.controls = CONTROLS
        self.properties = {}
        self.nextPing = datetime.now()
        adjust = timedelta(
            0, self.nextPing.second, self.nextPing.microsecond)
        self.nextPing -= adjust  # remove seconds
        # set up history so we can immediately turn on the pump if light enough
        self.wasRunning = False
        self.startedPump = self.nextPing - DELAY_BEFORE_TESTING
        self.stoppedPump = self.nextPing - DELAY_BEFORE_TESTING

        self.keys = KEYS
        self.ds = {}
        for i in range(len(self.keys)):
            key = self.keys[i]
            # print("Creating ds for", key)
            ds = DataSource(key)
            if not REAL:
                # for testing have to define ranges
                # print("Setting range for", key)
                ds.setRange(RANGES[i][0], RANGES[i][1])
            self.ds[key] = ds

        self.values = {}
        self.readValues()

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

        # top is clock
        topframe = Frame(master)
        topframe.grid(column=0, row=0)
        l1 = Label(topframe, text="Time: ")
        l1.grid(column=0, row=0)
        # Label(root, font=('times', 20, 'bold'), bg='green')
        self.clockString = StringVar(master, "None")
        self.clock = Label(topframe, textvariable=self.clockString)
        self.clock.grid(column=1, row=0)
        self.currentTime = "none"
        l2 = Label(topframe, text="Next: ")
        l2.grid(column=3, row=0)
        # Label(root, font=('times', 20, 'bold'), bg='green')
        self.nextString = StringVar(master, "None")
        self.next = Label(topframe, textvariable=self.nextString)
        self.next.grid(column=4, row=0)
        self.nextTime = "none"

        # below is rest
        frame = Frame(master)
        frame.grid(column=0, row=1)

        # left is info and buttons
        leftframe = Frame(frame)
        leftframe.grid(column=0, row=0, sticky=(E, W, N, S))

        # left is info
        infoframe = LabelFrame(leftframe, text="Info")
        infoframe.grid(column=0, row=0, sticky=(E, W, N, S))
        self.info = Text(infoframe, width=30, height=10)
        self.info.grid(column=0, row=0, sticky=(E, W, N, S))
        self.info.config(state=DISABLED) # so read only!

        # bottom is stop
        stop = Button(leftframe, text="STOP",
                         bg="red", command=self.terminate)
        stop.grid(column=0, row=2)
        leftframe.grid_rowconfigure(1, weight=1) # make middle strechy

        # right is log
        logframe = LabelFrame(frame, text="Log")
        logframe.grid(column=1, row=0, sticky=(E, W, N, S))
        yscrollbar = Scrollbar(logframe, orient=VERTICAL)
        yscrollbar.grid(column=1, row=0, sticky=(N, S))
        xscrollbar = Scrollbar(logframe, orient=HORIZONTAL)
        xscrollbar.grid(column=0, row=1, sticky=(E, W))
        self.logger = Text(logframe, yscrollcommand=yscrollbar.set,
                              xscrollcommand=xscrollbar.set, 
                              width=60, height=20, wrap=NONE)
        self.logger.grid(column=0, row=0)
        self.logger.config(state=DISABLED) # so read only!
        yscrollbar.config(command=self.logger.yview)
        xscrollbar.config(command=self.logger.xview)
        logframe.grid_rowconfigure(0, weight=1) # make text strechy
        logframe.grid_columnconfigure(0, weight=1) # make text strechy

        frame.grid_columnconfigure(1, weight=1) # make right strechy
        # init values
        self.getInfo()
        self.doStuff()
        # wake us up!
        self.tick()

    def tick(self):
        # get the current local time from the PC
        updatedTime = strftime('%H:%M:%S')
        # if time string has changed, update it
        if updatedTime != self.currentTime:
            self.currentTime = updatedTime
            self.clockString.set(updatedTime)
            # add code here that needs to be kicked off start of every second
            self.ping()
        # calls itself every 200 milliseconds
        # to update the time display as needed
        # could use >200 ms, but display gets jerky
        self.after(200, self.tick)

    def ping(self):
        current = datetime.now()
        if current.timestamp() > self.nextPing.timestamp():
            # currently period is in seconds, even if set in minutes
            period = self.getPeriod()  
            while current.timestamp() > self.nextPing.timestamp():
                self.nextPing += timedelta(seconds=period)
                # print("Time adjust:", self.nextPing, self.currentTime)
            self.nextTime = self.nextPing.strftime('%H:%M:%S')
            self.nextString.set(self.nextTime)
            # print("Times:", self.nextTime, self.nextPing, self.currentTime)
            print("Ping time:", self.currentTime)
            # time to do stuff, including check our ping period
            self.getInfo()
            if period != self.getPeriod():
                # it has changed!
                self.log("Period changed from " + str(period) +
                         " to " + str(self.getPeriod()))
            self.doStuff()

    def getIntProp(self, name):
        value = self.properties.get(name, 0)
        if value == None:
            value = 0
        value = int(value)
        return value

    def getPeriod(self):
        period = self.getIntProp('Period')
        if FACTOR == 1:  # using seconds
            if period < 5:
                period = 5
            if period > 600:  # max at 10 minutes
                period = 600
        else:  # using minutes
            if period < 1:
                period = 1
            if period > 60:  # max at 1 hour
                period = 60
        return period * FACTOR

    def getOn(self):
        on = self.getIntProp('Threshold')
        if on < 0:
            on = 0
        if on > MAX_LIGHT:
            on = MAX_LIGHT
        return on

    def getOff(self):
        on = self.getOn()
        off = self.getIntProp('Off')
        if off > on:
            off = on
        if off < 0:
            off = 0
        if off > MAX_LIGHT:
            off = MAX_LIGHT
        return off

    def doStuff(self):
        # periodic things to do, like check inputs and decide things
        newValues = self.readValues()
        changeHappened = False
        for key in self.keys:
            if newValues.get(key) != self.values.get(key):
                changeHappened = True
                self.values[key] = newValues.get(key)
        # if changeHappened:
        self.decide()
        # once done record state ...
        self.recordValues()
        text = self.formatValues()
        self.showValues(text)
        self.guiShow(text)

    def readValues(self):
        # ask each its current value
        newValues = {}
        for key in self.keys:
            value = self.ds.get(key).getValue()
            newValues[key] = value
        # print("ReadValues() returned", newValues)
        return newValues

    def recordValues(self):
        # record to current data store ...
        self.bs.recordAll(self.keys, self.values)
        # now off load to UBIDOTS ...
        offload = SafeInternetOffload()
        offload.setup([self.ubs, self.keys, self.values])
        offload.start()
        offload.join(TIMEOUT)
        if offload.is_alive():
            self.ubs = None  # something went wrong, so reload next time
            self.log("Offload to UBIDOTS taking too long > " + str(TIMEOUT))
        else:
            if offload.isOk():
                self.ubs = offload.getBs()  # re-use it if ok
            else:
                self.ubs = None  # something went wrong, so reload next time
                self.log("Offload to UBIDOTS failed: " +
                         str(offload.getError()))
        # now to import the control data if we can!
        download = SafeInternetDownload()
        download.setup([self.ubs, self.bs])
        download.start()
        download.join(TIMEOUT)
        if download.is_alive():
            self.ubs = None  # something went wrong, so reload next time
            self.log("Download from UBIDOTS taking too long > " + str(TIMEOUT))
        else:
            if download.isOk():
                self.ubs = download.getBs()  # re-use it if ok
            else:
                self.ubs = None  # something went wrong, so reload next time
                self.log("Download from UBIDOTS failed: " +
                         str(download.getError()))
        self.getInfo()

    def formatPump(self):
        text = "On "
        if self.values.get("Pump") == 0:
            text = "Off"
        return text

    def formatValues(self):
        # record to screen ...
        text = ["T: " + self.currentTime + " / " + self.nextTime,
                "P: " + sig4(self.getPeriod()) + "    T: " +
                sig4(self.getOn()) + " / " + sig4(self.getOff()),
                "L: " + sig4(self.values.get("Photo")) + "    P: " +
                self.formatPump() + " / " + sig4(self.values.get("PumpP")),
                "F: " + sig4(self.values.get("Flow")) +
                "    P: " + sig4(self.values.get("Power")),
                "P: " + sig4(self.values.get("Pool")) + DEG_C 
                + "  W: " + sig4(self.values.get("Water")) + DEG_C]
        return text

    def showValues(self, text):
        print("showValues:", self.ScreenRetry)
        print(text)
        # record to screen ...
        if self.ScreenRetry > 0:
            self.ScreenRetry -= 1
        else:
            scr = SafeScreen()
            scr.setup(text)
            scr.start()
            scr.join()
            if scr.hasFailed():
                # handle what to do if does not work here
                # scr.getError() will get the exception it failed with
                error = scr.getError()
                print("scr has failed:", error)
                self.ScreenRetry = 2 # so fail more ofte than: 10

    def guiShow(self, text):
        # strip off first line as already on screen
        # and join rest with newlines
        text = chr(10).join(text[1:])
        self.info.config(state=NORMAL)
        self.info.delete("1.0", END)
        self.info.insert(END, text)
        self.info.config(state=DISABLED)

    def terminate(self):
        # put code here for "Are you sure?"
        self.master.destroy()
        if self.master.master:
            self.master.master.destroy()

    def log(self, message):
        # add to first line
        text = self.clockString.get() + ": " + message
        print(text)
        self.logger.config(state=NORMAL)
        # if removing scrolled off line: self.logger.delete("30.0", END)
        self.logger.insert("1.0", text + chr(10))
        self.logger.config(state=DISABLED)

    def getInfo(self):
        # read in the control info
        props = self.bs.getProperties()
        # print("Got props:", props, self.properties)
        self.properties = props

    def pumpRunning(self):
        # true if Flow greater than 2
        current = datetime.now()
        running = False
        if self.values["Flow"] > 2:
            running = True
        # need to detect when we last switched on or off
        if self.wasRunning != running:
            if running:
                # switched on
                self.startedPump = current
                self.log("Pump has turned on at " + str(current))
                print("Pump has turned on at " + str(current))
            else:
                # switched off
                self.stoppedPump = current
                self.log("Pump has turned off at " + str(current))
                print("Pump has turned off at " + str(current))
        self.wasRunning = running  # remember for next time
        return running

    def decide(self):
        # here be logic for changing things
        '''
        Logic:
        if pump running (flow > 2) then 
            if been on > 5 mins 
                check water temp 
                if pool > Water
                    turn off 
        if pump not running then 
            if been off > 5 mins 
                check photo 
                if > threshold 
                    turn it on 
                    record when we turned it on
        '''
        current = datetime.now()
        running = self.pumpRunning()
        if running:
            if current - self.startedPump > DELAY_BEFORE_TESTING:
                if self.values["Pool"] > self.values["Water"]:
                    # solar is too cold, so turn off
                    self.ds["Pump"].setValue(0)  # turn it off
                    self.log("Turning pump off as water now " 
                             + str(self.values["Water"]) 
                             + " is less than the pool " 
                             + str(self.values["Pool"]))
                    print("Turning pump off as water now " 
                          + str(self.values["Water"]) 
                          + " is less than the pool " 
                          + str(self.values["Pool"]))
        else:
            if current - self.stoppedPump > DELAY_BEFORE_TESTING:
                if self.values["Photo"] > self.getOn():  # above on
                    self.ds["Pump"].setValue(1)  # turn it on
                    self.log("Turning pump on as photo now " 
                             + str(self.values["Photo"]) 
                             + " and threshold is " 
                             + str(self.getOn()))
                    print("Turning pump on as photo now " 
                          + str(self.values["Photo"]) 
                          + " and threshold is " 
                          + str(self.getOn()))

    def main(root):
        # Start up code called by calling Controller.main()
        print("Welcome to the Solar Controller")
        # create window, give it a name ...
        root.title("Solar Controller")
        # root.geometry('600x400')
        controller = Controller(root)
        # return the object so caller can initiate the window loop.
        return controller


def sig4(value):
    disp = str(value)[0:4]
    disp = "    " + disp
    disp = disp[-4:]
    return disp


def main():
    # this is for testing
    root = Tk()
    Controller.main(root)
    root.mainloop()


# execute only if run as a script
if __name__ == "__main__":
    main()  # execute test code ...
