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


