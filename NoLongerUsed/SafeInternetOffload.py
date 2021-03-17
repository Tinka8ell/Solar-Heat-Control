# !/usr/bin/python3
# SafeInternetOffload.py
"""
As the Internet connection proved to be dodgy 
and a number of failures actually took out the main thread.

This will enable us to do stuff on a separate thread 
and so protect the main code.
"""

from time import sleep

from SafeOffload import SafeOffload
from UbidotsBackingStore import UbidotsBackingStore 


class SafeInternetOffload(SafeOffload):

    # Initialisation code
    def __init__(self):
        # init parent
        super().__init__()
        self.bs = None

    def setup(self, data):
        self.bs = data[0]
        self.keys = data[1]
        self.values = data[2]

    def init(self):
        print("Internet init called")
        if not self.bs:
            print("Initialising UBIDOTS")
            self.bs = UbidotsBackingStore()

    def do(self):
        self.bs.recordAll(self.keys, self.values)

    def getBs(self):
        bs = None
        if self.isOk():
            bs = self.bs
        return bs


def main():
    # this is for testing
    obj = SafeInternetOffload()
    bs = None
    keys = ["Power", "Photo", "Pump", "Pool", "Water", "Flow"]
    controls = ["Period", "Threshold"]
    values = {"Power": 123.45, "Photo": 3.7,
              "Pump": 1, "Water": 22.0, "Flow": 17.5}
    obj.setup([bs, keys, values])
    obj.start()
    obj.join()
    if obj.isOk():
        print("It worked")
    else:
        print("Oops it didn't work")
        print("Exception was:", obj.getError())
    print("wait 20 secs")
    sleep(20)
    values = {"Power": 0, "Photo": 1.2, "Pump": 0, "Water": 15.0, "Flow": 0}
    bs = obj.getBs()
    obj = SafeInternetOffload()
    obj.setup([bs, keys, values])
    obj.start()
    obj.join()
    if obj.isOk():
        print("It worked")
    else:
        print("Oops it didn't work")
        print("Exception was:", obj.getError())


# execute only if run as a script
if __name__ == "__main__":
    main()  # execute test code ...
