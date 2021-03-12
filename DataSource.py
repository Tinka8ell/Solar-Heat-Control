# !/usr/bin/python3
# DataSource.py
"""
Base class for data sources
Define main methods used by subclasses.
"""
import datetime
import math
import random
import time


class DataSource ():
    'This will be the DataSource class for the Solar panel package'
    # class variables here

    # Initialisation code
    def __init__(self, name):
        self.key = name
        self.value = 0

    def setValue(self, value):
        self.value = value

    def getName(self):
        return self.key

    def getValue(self):
        return int(self.value)


def main():
    # this is for testing
    ds = DataSource("Dummy")
    print("New datasource:", ds.getName())
    print("Current value:", ds.getValue())
    for i in range(10):
        time.sleep(5)
        print("After 5 secs value:", ds.getValue())


# execute only if run as a script
if __name__ == "__main__":
    main()  # execute test code ...
