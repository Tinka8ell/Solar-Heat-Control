# !/usr/bin/python3
# FileBackingStore.py
"""
Backing store using file system ...

Used to log data to a backing file on the Raspberry Pi
in case (as often was) the Internet connection had failed.
"""

import datetime
import os.path
import time

from BackingStore import BackingStore 


class FileBackingStore(BackingStore):
    'This will be the file backing store class for the Solar panel package'

    # Initialisation code
    def __init__(self):
        super().__init__()
        self.dir = None
        self.control = None
        # print("Created file backing store")

    def getDir(self):
        if not self.dir:
            path = "/temp/Solar"
            if not os.path.exists(path):
                os.makedirs(path)
            self.dir = path
            print("Solar directory can be found at", self.dir)
        return self.dir

    def getControl(self):
        if not self.control:
            path = os.path.join(self.getDir(), "Control.csv")
            if not os.path.isfile(path):
                fd = open(path, "w")
                fd.write("'Period', 'Threshold'\n")
                fd.write("60, 3\n")
                fd.close
            self.control = path
        return self.control

    def getCsv(self, fileName, keys):
        path = os.path.join(self.getDir(), fileName)
        if not os.path.isfile(path):
            # not exist, so create it
            fd = open(path, "w")
            # now it exists, we need to head the headings ...
            heading = "'Timestamp'"
            sep = ", "
            for key in keys:
                heading += sep + "'" + key + "'"
            fd.write(heading + "\n")
            fd.close
            print("Started new file at", path)
        return path

    def getProperties(self):
        properties = {}
        path = self.getControl()
        fd = open(path)
        line = fd.readline()
        keys = line.split(",")
        line = fd.readline()
        values = line.split(",")
        i = 0
        for key in keys:
            key = key.strip().strip("'")
            value = values[i].strip()
            if value == 'None':
                value = None
            else:
                value = float(value)
            properties[key] = value
            i += 1
        print("FileBackingStore.getProperties() returned:", properties)
        return properties

    def setProperties(self, properties):
        path = self.getControl()
        fd = open(path, "w")
        line = "'Period', 'Threshold', 'Off'"
        print("FileBackingStore.setProperties writing:", line)
        fd.write(line + "\n")
        line = str(properties.get("Period")) + ", " + \
            str(properties.get("Threshold")) + ", " + \
            str(properties.get("Off"))
        print("writing:", line)
        fd.write(line + "\n")
        fd.close

    def recordIt(self, key, value):
        # this assumes that the key is always first item!
        keys = [key]
        values = {key: value}
        self.recordAll(keys, values)

    def recordAll(self, keys, values):
        # this assumes that the keys are always in the same order!
        current = datetime.datetime.now()
        today = current.date().isoformat()
        fileName = "Record-" + today + ".csv"  # unique file for each day
        csv = self.getCsv(fileName, keys)
        line = current.strftime("%d/%m/%y %H:%M:%S")  # current time stamp
        for key in keys:
            line += ", " + str(values.get(key))
        fd = open(csv, "a")
        fd.write(line + "\n")
        fd.close()

    # get a named control value
    def getProperty(self, name):
        values = self.getProperties()
        return values.get(name)


def main():
    # This is just for testing
    bs = FileBackingStore()
    print("getProperties() returned")
    print(bs.getProperties())
    print("period =", bs.getProperty("Period"))
    print("threshold =", bs.getProperty("Threshold"))
    print("off =", bs.getProperty("Off"))

    keys = ["Power", "Photo", "Pump", "Water", "Flow"]
    print("Full write")
    bs.recordAll(keys, {"Power": 123.45, "Photo": 3.7,
                        "Pump": 1, "Water": 22.0, "Flow": 17.5})
    print("Wait a bit")
    time.sleep(3)
    print("Reset write")
    bs.recordAll(keys, {"Power": 0, "Photo": 1.2,
                        "Pump": 0, "Water": 15.0, "Flow": 0})
    print("Done")


if __name__ == '__main__':
    main()
