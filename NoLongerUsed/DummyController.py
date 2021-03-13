# !/usr/bin/python3
# Controller.py
"""
Was a dummy version of Controller.py for testing.
Don't think it is currently used.
Probably out of date.
"""

import sys
import datetime
import time
import random
import FileBackingStore as Fbs
import SafeInternetDownload as SafeInternetDownload
import SafeInternetOffload as SafeInternetOffload
import SafeScreen as SafeScreen
import tkinter as Tk
KEYS = ["Power", "Photo", "Pump", "Pool", "Water", "Flow"]
RANGES = [(0, 1000), (0, 10), (0, 1), (0, 35), (0, 35), (0, 30)]
CONTROLS = ["Period", "Threshold"]
FACTOR = 1  # for seconds or 60 for minutes
DEG_C = chr(164) + "C"
REAL = False


if REAL:
    import RealDataSource as Rds
else:
    import DataSource as Ds


# Global constant
'''
For now we use these named data stores:
   Power = John's power meter - variable5 = api.get_variable('58ccef12762542259a52564a')
   Photo = John's photoresistor value - variable = api.get_variable('58cab87676254236fd1da01c')
   Pump  = John's switch pump on / off - variable3 = api.get_variable("58cac36f76254236fd1e14c3")
   Water = John's water temperature reading = variable = api.get_variable('58cb232676254236faacf06c')
   Pool  = John's water temperature reading = variable = api.get_variable('58cb232676254236faacf06c')
   Flow  = John's water flow rate meter = variable = api.get_variable('58cf0bee762542735c52735b')
and this control:
   Threshold = John's threshold value - variable2 = api.get_variable("58cac4ad76254236fbe2541d")
will add period once worked out how!
'''


class Controller (Tk.Frame):
    'This will be the Controller class for the Solar panel package'
    # class variables here

    # Initialisation code
    def __init__(self, master):
        # init parent
        Tk.Frame.__init__(self, master)

        # allow the screen to try and display
        self.ScreenRetry = 0

        # init data
        self.bs = Fbs.FileBackingStore()
        self.ubs = None  # created and maintained as we need it

        self.controls = CONTROLS
        self.properties = {}
        self.nextPing = datetime.datetime.now()

        self.keys = KEYS
        self.ds = {}
        for i in range(len(self.keys)):
            key = self.keys[i]
            print("Creating ds for", key)
            if REAL:
                ds = Rds.RealDataSource(key)
            else:
                ds = Ds.DataSource(key)
            print("Setting range for", key)
            ds.setRange(RANGES[i][0], RANGES[i][1])
            self.ds[key] = ds

        self.values = {}
        self.readValues()

        # init view
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
        l2 = Tk.Label(topframe, text="Next: ")
        l2.pack(side=Tk.LEFT)
        # Tk.Label(root, font=('times', 20, 'bold'), bg='green')
        self.next = Tk.Label(topframe, text="None")
        self.next.pack(side=Tk.LEFT)
        self.nextTime = "none"

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
        self.doStuff()
        # wake us up!
        self.tick()

    def tick(self):
        # get the current local time from the PC
        updatedTime = time.strftime('%H:%M:%S')
        # if time string has changed, update it
        if updatedTime != self.currentTime:
            self.currentTime = updatedTime
            self.clock.config(text=updatedTime)
            # add code here that needs to be kicked off start of every second
            self.ping()
        # calls itself every 200 milliseconds
        # to update the time display as needed
        # could use >200 ms, but display gets jerky
        self.clock.after(200, self.tick)

    def ping(self):
        current = datetime.datetime.now()
        period = self.getPeriod()  # currently period is in seconds, even if set in minutes
        if current.timestamp() > self.nextPing.timestamp():
            self.nextPing += datetime.timedelta(seconds=period)
            self.nextTime = self.nextPing.strftime('%H:%M:%S')
            self.next.config(text=self.nextTime)
            # time to do stuff, including check our ping period
            self.getInfo()
            if period != self.getPeriod():
                # it has changed!
                self.log("Period changed from " + str(period) +
                         " to " + str(self.getPeriod()))
            self.doStuff()

    def getPeriod(self):
        period = int(self.properties.get('Period', 0))
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

    def doStuff(self):
        # periodic things to do, like check inputs and decide things
        newValues = self.readValues()
        changeHappened = False
        for key in self.keys:
            if newValues.get(key) != self.values.get(key):
                changeHappened = True
                self.values[key] = newValues.get(key)
        if changeHappened:
            # here be logic for changing things
            # for now keep it simple ...
            was = self.values["Pump"]
            if self.values["Photo"] > self.properties["Threshold"]:
                self.ds["Pump"].setValue(1)  # turn it on
            else:
                self.ds["Pump"].setValue(0)  # turn it off
            if was != self.values["Pump"]:
                if self.values["Photo"] == 0:
                    self.log("Turning pump on as photo now " +
                             self.values["Photo"])
                else:
                    self.log("Turning pump off as photo is " +
                             self.values["Photo"])
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
        return newValues

    def recordValues(self):
        # record to current data store ...
        self.bs.recordAll(self.keys, self.values)
        # now off load to UBIDOTS ...
        offload = SafeInternetOffload.SafeInternetOffload()
        offload.setup([self.ubs, self.keys, self.values])
        offload.start()
        offload.join()
        if offload.isOk():
            self.ubs = offload.getBs()  # re-use it if ok
        else:
            self.ubs = None  # something went wrong, so reload next time
            self.log("Offload to UBIDOTS failed: " + str(offload.getError()))
        # now to import the control data if we can!
        download = SafeInternetDownload.SafeInternetDownload()
        download.setup([self.ubs, self.bs])
        download.start()
        download.join()
        if download.isOk():
            self.ubs = download.getBs()  # re-use it if ok
        else:
            self.ubs = None  # something went wrong, so reload next time
            self.log("Download from UBIDOTS failed: " +
                     str(download.getError()))

    def formatValues(self):
        # record to screen ...
        '''
  KEYS = ["Power", "Photo", "Pump", "Pool", "Water", "Flow"]
  Time  hh:mm:ss Next  hh:mm:ss
  Period  999    Threshold 99
  Light = 99     Pump  = on/off
  Pool  = 99.9dC Water = 99.9dC
  Flow  = 999.9  Power = 999.9
        '''
        text = ["Time" + chr(9) + self.currentTime + chr(9) + "Next" + chr(9) + self.nextTime,
                "Period:" + chr(9) + str(self.getPeriod()) + chr(9) +
                "Threshold" + chr(9) + str(self.properties["Threshold"]),
                "Light:" + chr(9) + str(self.values.get("Photo")) +
                chr(9) + "Pump:" + chr(9) + str(self.values.get("Pump")),
                "Pool:" + chr(9) + str(self.values.get("Pool")) + DEG_C + chr(9) +
                "Water:" + chr(9) + str(self.values.get("Water")) + DEG_C,
                "Flow:" + chr(9) + str(self.values.get("Flow")) + chr(9) + "Power:" + chr(9) + str(self.values.get("Power"))]
        return text

    def showValues(self, text):
        # record to screen ...
        if self.ScreenRetry > 0:
            self.ScreenRetry -= 1
        else:
            scr = SafeScreen.SafeScreen()
            scr.setup(text)
            scr.start()
            scr.join()
            if scr.hasFailed():
                # handle what to do if does not work here
                # scr.getError() will get the exception it failed with
                error = scr.getError()
                self.ScreenRetry = 10

    def guiShow(self, text):
        # strip off first line as already on screen
        # and join rest with newlines
        text = chr(10).join(text[1:])
        self.info.delete("1.0", Tk.END)
        self.info.insert(Tk.END, text)

    def terminate(self):
        # put code here for "Are you sure?"
        self.master.destroy()
        if self.master.master:
            self.master.master.destroy()

    def log(self, message):
        self.logger.insert(
            Tk.END, self.clock["text"] + ": " + message + chr(10))

    def getInfo(self):
        # read in the control info
        props = self.bs.getProperties()
        if self.properties != props:
            self.properties = props

    def main(root):
        # Start up code called by calling Controller.main()
        print("Welcome to the Solar Controller")
        # Google backing store info
        Solar = "https://drive.google.com/drive/folders/0B2EaP6O9ZuIiVXhYaXN2M01PeUk"
        print("You can find the data in:", Solar)
        # create window, give it a name ...
        root.title("Solar Controller")
        controller = Controller(root)
        controller.pack()
        # return the object so caller can initiate the window loop.
        return controller


def main():
    # this is for testing
    root = Tk.Tk()
    Controller.main(root)
    root.mainloop()


# execute only if run as a script
if __name__ == "__main__":
    main()  # execute test code ...
