# !/usr/bin/python3
"""
Looks like this was created to run the Controller class without
a GUI, but it is not clear.
"""

import os
from platform import machine
import sys

from Controller import Controller
from Controller import KEYS
import tkinter as Tk


MACHINE = machine()
# To enable debugging on non-pi environment set REAL to False.
REAL = True
if MACHINE == "AMD64":
    REAL = False # on Windows can't be real!

if REAL:
    from RealDataSource import RealDataSource as DataSource 
else:
    from DummyDataSource import DummyDataSource as DataSource
    from Controller import RANGES

def main():
    keys = KEYS
    ds = {}
    for i in range(len(keys)):
        key = keys[i]
        print("Creating ds for", key)
        dataSource = DataSource(key)
        if not REAL:
            # for testing have to define ranges
            print("Setting range for", key)
            dataSource.setRange(RANGES[i][0], RANGES[i][1])
        ds[key] = dataSource
    Controller.main(None, ds) # <==== this is old format Controller


if __name__ == "__main__":
    main()
