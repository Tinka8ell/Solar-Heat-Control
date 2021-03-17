# !/usr/bin/python3
# DataSource.py
"""
Dummy data source used to provide inputs when testing 
without the backing of hardware. 
"""

import datetime
import math
import random
import time

from DataSource import DataSource


class DummyDataSource (DataSource):
    'This will be the DataSource class for the Solar panel package'
    # class variables here

    # Initialisation code
    def __init__(self, name):
        super().__init__(name)
        self.max = 10
        self.min = 0

    def setRange(self, minimum, maximum):
        self.max = maximum
        self.min = minimum
        # print("Setting", self.getName(), 
        #       "max to", maximum, "and min to", minimum)
        self.setValue((maximum + minimum) / 2)

    def setValue(self, value):
        self.value = value
#         if self.getName() == "Pump":
#             print("DummyDataSource.setValue for Pump to", 
#                   self.value, int(self.value))
        # print("Setting", self.getName(), "to", self.value)
        # these of for the dummy data generator
        self.dummy = datetime.datetime.now()
        self.offset = random.randint(0, 360)  # randomise start of cycle
        self.period = random.randint(18, 54)  # length of cycle 30 - 90 mins

    def getName(self):
        return self.key

    def getValue(self):
#         if self.getName() == "Pump":
#             print("DummyDataSource.getValue for Pump =", 
#                   self.value, int(self.value))
        if self.getName() != "Pump":
            # add a dummy cycle value for testing
            diff = datetime.datetime.now() - self.dummy   # time since created
            diff = diff.total_seconds()                   # in seconds
            # and the randomisers
            diff = self.offset + (diff * self.period / 360)
            # rotate approx every 6 minutes
            diff = math.radians(diff)
            diff = (self.max - self.min) * math.sin(diff)  # to +/- 1
            self.value = (self.max + self.min + diff) / 2  # into range
        return int(self.value)                        # keep it as an integer


def main():
    # this is for testing
    ds = DummyDataSource("Dummy")
    print("New datasource:", ds.getName())
    print("Current value:", ds.getValue())
    for i in range(10):
        time.sleep(5)
        print("After 5 secs value:", ds.getValue())


# execute only if run as a script
if __name__ == "__main__":
    main()  # execute test code ...
