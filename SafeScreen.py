# !/usr/bin/python3
# SafeScreen.py
"""
The implementation for the mini-screen driver proved a little
dodgy and could stop the main thread.

This will enable us to do stuff on a separate thread 
and so protect the main code.
"""

import SafeOffload
import Screen


class SafeScreen(SafeOffload.SafeOffload):

    # Initialisation code
    def __init__(self):
        # init parent
        SafeOffload.SafeOffload.__init__(self)

    def init(self):
        self.scr = Screen.Screen()

    def do(self):
        self.scr.set(self.data)


def main():
    # this is for testing
    obj = SafeScreen()
    obj.setup(["My Data", "is up to", "five lines", "of text"])
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
