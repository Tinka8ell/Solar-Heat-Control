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
import sys
from time import strftime

from FileBackingStore import FileBackingStore
from PoolGUI import PoolGUI
from Screen import Screen
from UbidotsBackingStore import UbidotsBackingStore

MACHINE = machine()
# To enable debugging on non-pi environment set REAL to False.
REAL = True
if MACHINE == "AMD64":
    REAL = False  # on Windows can't be real!

if REAL:
    from RealDataSource import RealDataSource as DataSource
else:
    from DummyDataSource import DummyDataSource as DataSource

# Global constants
USE_UBIDOTS = False # True # set to False if not using UBIDOTS
KEYS = ["Power", "Photo", "Pump", "Pool", "Water", "Flow", "PumpP", "Depth", "SolarP"]
RANGES = [(0, 1000), (0, 10), (0, 1), (0, 35),
          (0, 35), (0, 30), (0, 1000), (5, 150), (0, 1000)]
CONTROLS = ["Period", "Threshold", "Off"]
FACTOR = 60  # 1 for seconds or 60 for minutes
DELAY_BEFORE_TESTING = timedelta(seconds=60 * 5)  # 5 minutes
MAX_LIGHT = 20  # increased from 10 to 20
TIMEOUT = 20.0
DEG_C = chr(164) + "C"


def sig4(value):
    disp = str(value)[0:4]
    disp = "    " + disp
    disp = disp[-4:]
    return disp


class Controller ():
    'This will be the Controller class for the Solar panel package'

    # Initialisation code
    def __init__(self, logger=None, callback=None):
        # init parent
        super().__init__()
        self.setLog(logger)
        self.setPeriodUpdate(callback)

        # init data
        self._fbs = FileBackingStore()
        print("Solar data directory can be found at", self._fbs.getDir())
        if USE_UBIDOTS:
            self._ubs = UbidotsBackingStore(timeout=1,
                                            control=CONTROLS,
                                            logErrors = True)
        else: # use file backing store instead ...
            self._ubs = FileBackingStore(dir=".")
        self.controls = CONTROLS
        self.properties = {}

        # set up history so we can immediately turn on the pump if light enough
        self.wasRunning = False
        current = datetime.now()
        self.startedPump = current - DELAY_BEFORE_TESTING
        self.stoppedPump = current - DELAY_BEFORE_TESTING

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

        self.readValues() # set up initial values

        # init values
        self.getInfo()
        return

    def setLog(self, logger):
        self._log = logger
        return

    def log(self, message):
        if self._log is not None:
            self._log(message)
        else:
            print(">>>", message, file=sys.stderr)
        return

    def setPeriodUpdate(self, callback):
        self._periodUpdate = callback
        return

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
                             +str(self.values["Water"])
                             +" is less than the pool "
                             +str(self.values["Pool"]))
                    # print("Turning pump off as water now "
                    #       + str(self.values["Water"])
                    #       + " is less than the pool "
                    #       + str(self.values["Pool"]))
        else:
            if current - self.stoppedPump > DELAY_BEFORE_TESTING:
                if self.values["Photo"] > self.getOn():  # above on
                    self.ds["Pump"].setValue(1)  # turn it on
                    self.log("Turning pump on as photo now "
                             +str(self.values["Photo"])
                             +" and threshold is "
                             +str(self.getOn()))
                    # print("Turning pump on as photo now "
                    #       + str(self.values["Photo"])
                    #       + " and threshold is "
                    #       + str(self.getOn()))
        return

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
        self.readValues()
        # make a decision on the current data
        self.decide()
        # once done record state ...
        self.recordValues()
        return self.formatValues()

    def readValues(self):
        # ask each its current value
        self.values = {}
        for key in self.keys:
            value = self.ds.get(key).getValue()
            self.values[key] = value
        # as SolarP is calculated from other values, get it with new values
        # calculate the power provided by solar heat based on Flow, Water and Pool temps
        # the formula is (temp out - temp in) * flow * 60 *4.2 /3600 to get kilowatts
        water = self.values.get("Water", 0)
        pool = self.values.get("Pool", 0)
        flow = self.values.get("Flow", 0)
        value = ((water - pool) * flow * 60 * 4.2 / 3600)
        self.values["SolarP"] = value
        return

    def recordValues(self):
        # record to current data store ...
        self._fbs.recordAll(self.values)
        # now off load to UBIDOTS ...
        # this could fail, but shouldn't kill us!
        self._ubs.recordAll(self.values)
        # now to import the control data if we can!
        self.getInfo()
        return

    def formatPump(self):
        text = "On "
        if self.values.get("Pump") == 0:
            text = "Off"
        return text

    def formatValues(self):
        # record to screen ...
        text = ["P: " + sig4(self.getPeriod()) + "    T: " +
                sig4(self.getOn()) + " / " + sig4(self.getOff()),
                "L: " + sig4(self.values.get("Photo")) + "    P: " +
                self.formatPump() + " / " + sig4(self.values.get("PumpP")),
                "F: " + sig4(self.values.get("Flow")) +
                "    P: " + sig4(self.values.get("Power")) +
                " / " + sig4(self.values.get("SolarP")),
                "P: " + sig4(self.values.get("Pool")) + DEG_C
                +"  W: " + sig4(self.values.get("Water")) + DEG_C]
        return text

    def getInfo(self):
        # read in the control info from ubidots
        # this could fail, but not stop us
        properties = self._ubs.getProperties()
        if properties is not None:
            # keep back up of values in case fails later
            self._fbs.setProperties(properties)
        else:
            # if failed, get from backing store
            properties = self._fbs.getProperties()
        self.properties = properties
        # notify current period
        if self._periodUpdate is not None:
            self._periodUpdate(self.getPeriod())
        return

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
                self.log("Water has started flowing at " + str(current))
                # self.log("Pump has turned on at " + str(current))
                # print("Pump has turned on at " + str(current))
            else:
                # switched off
                self.stoppedPump = current
                self.log("Water has stopped flowing at " + str(current))
                # self.log("Pump has turned off at " + str(current))
                # print("Pump has turned off at " + str(current))
        self.wasRunning = running  # remember for next time
        return running


# execute only if run as a script
if __name__ == "__main__":
    from tkinter import Tk
    root = Tk()
    root.title('Pool GUI')
    gui = PoolGUI(root)
    controller = Controller()
    controller.setLog(gui.log)
    controller.setPeriodUpdate(gui.setPeriod)
    gui.setCallback(controller.doStuff)
    root.mainloop()
