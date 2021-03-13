# !/usr/bin/python3
# SafeScreen.py
"""
The implementation for the mini-screen driver proved a little
dodgy and could stop the main thread.

This will enable us to do stuff on a separate thread 
and so protect the main code.
"""

from SafeOffload import SafeOffload
from Screen import Screen


class SafeScreen(SafeOffload):

    def init(self):
        print("SafeScreen: init")
        self.scr = Screen()

    def do(self):
        print("SafeScreen: do")
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
