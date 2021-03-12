# !/usr/bin/python3
# BackingStore.py
"""
Base class for backing stores
Define main methods used by subclasses.
"""

class BackingStore():
    'This will be the base backing store class for the Solar panel package'

    # Initialisation code
    def __init__(self):
        self.testData = {"period": 60}

    # get a named control value
    def getProperty(self, name):
        # for now only support period => 1 minute
        return self.testData.get("period", 60)

    # get all named control values
    def getProperties(self):
        return self.testData

    # record all the values using the given keys
    def recordAll(self, keys, values):
        # this assumes that the keys are always in the same order!
        for key in keys:
            self.recordIt(key, values.get(key, "none"))

    # record a value using the given key
    def recordIt(self, key, value):
        print("Key:", key, "=", value)


def main():
    # This is just for testing
    bs = BackingStore()
    print("getProperties() returned")
    print(bs.getProperties())
    print("period =", bs.getProperty("period"))
    keys = ["One", "Two", "Three"]
    bs.recordAll(keys, {"One": 1, "Two": 2, "Three": 3})
    bs.recordAll(keys, {"Two": 5, "Three": 6})
    bs.recordAll(keys, {"This": 6, "That": 5, "The Other": 4, "One": 9})
    bs.recordIt("Four", 9)


if __name__ == '__main__':
    main()
