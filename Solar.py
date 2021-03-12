# !/usr/bin/python3
"""
Looks like this was created to run the Controller class without
a GUI, but it is not clear.
"""

import sys
import os
import tkinter as Tk
from Controller import Controller
from Controller import KEYS
import RealDataSource as Ds


def main():
    keys = KEYS
    ds = {}
    for i in range(len(keys)):
        key = keys[i]
        print("Creating ds for", key)
        dataSource = Rds.RealDataSource(key)
        ds[key] = dataSource
    Controller.main(None, ds)


if __name__ == "__main__":
    main()
