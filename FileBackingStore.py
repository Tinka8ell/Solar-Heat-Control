# !/usr/bin/python3
# FileBackingStore.py
"""
Backing store using file system ...

Used to log data to a backing file on the Raspberry Pi
in case (as often was) the Internet connection had failed.
"""

import datetime
import json
import os
import os.path
import time

class FileBackingStore():
    'This will be the file backing store class for the Solar panel package'

    # Initialisation code
    def __init__(self):
        self._dir = None
        self._control = None
        return

    def getDir(self):
        if not self._dir:
            path = "/temp/Solar"
            if not os.path.exists(path):
                os.makedirs(path)
            self._dir = path
        return self._dir

    def getControl(self):
        if not self._control:
            path = os.path.join(self.getDir(), "Control.json")
            if not os.path.isfile(path):
                fd = open(path, "w")
                json.dump({'Period': 60, 'Threshold': 3}, fd)
                fd.close
            self._control = path
        return self._control

    def getLog(self):
        current = datetime.datetime.now()
        today = current.date().isoformat()
        fileName = "Record-" + today + ".json"  # unique file for each day
        path = os.path.join(self.getDir(), fileName)
        if not os.path.isfile(path):
            # not exist, so create it
            fd = open(path, "w")
            fd.write('{"records": [') # start json with a dummy structure 
            # add timestamp of the file create
            data = {"timestamp": current.strftime("%d/%m/%y %H:%M:%S")}
            json.dump(data, fd)
            fd.close
        return path

    def getProperties(self):
        properties = {}
        path = self.getControl()
        with open(path) as f:
            properties = json.load(f)
        return properties

    def setProperties(self, properties):
        path = self.getControl()
        with open(path, "w") as f:
            json.dump(properties, f)
        return

    def recordIt(self, key, value):
        values = {key: value}
        self.recordAll(values)
        return

    def recordAll(self, values):
        path = self.getLog()
        current = datetime.datetime.now()
        data = {"timestamp": current.strftime("%d/%m/%y %H:%M:%S")}
        data.update(values)
        with open(path, "a") as f:
            f.write(", ") # add next record to the json list
            json.dump(data, f)
        return

    def getProperty(self, name):
        values = self.getProperties()
        return values.get(name)

    def dumpRecords(self):
        # just for testing
        path = self.getLog()
        all = ""
        with open(path) as f:
            all = f.readlines()
        all.append("]}") # complete json structure!
        str = "".join(all)
        properties = json.loads(str)
        return properties["records"]

