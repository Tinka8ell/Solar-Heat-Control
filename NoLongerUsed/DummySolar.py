# !/usr/bin/python3
# Test things
"""
Dummy copy of Solar.py intended for testing.
Not sure it is used any more.
"""

import os
import sys

from Controller import Controller
from Controller import KEYS
from Controller import RANGES
import DummyDataSource as Ds
import tkinter as Tk


def main():
    keys = KEYS
    ds = {}
    for i in range(len(keys)):
        key = keys[i]
        print("Creating ds for", key)
        ds = Ds.DummyDataSource(key)
        print("Setting range for", key)
        ds.setRange(RANGES[i][0], RANGES[i][1])
        ds[key] = ds
    Controller.main(None, ds)


if __name__ == "__main__":
    main()
