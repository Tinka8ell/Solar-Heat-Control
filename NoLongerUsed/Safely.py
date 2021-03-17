"""
An object which can do something to an object on a separate thread.

Safely is created with and optional object, 
a method to create a replacement object, 
a method to be done on that object and
the data for method to be done.

It has an wrapper method: doSafely which takes the above and
a timeout to execute "safely" the "action" method and return
the object used for re-use, if completed safely and any returned data.
"""
from threading import Thread


def doSafely(original, replace, dataIn, action, timeout):
    dodgy = Safely(original, replace, dataIn, action)
    dodgy.start()
    dodgy.join(timeout)
    return (dodgy.getObject(), dodgy.getOutput())


class Safely(Thread):
    
    def __init__(self, original, replace, dataIn, action):
        super().__init__()
        self._object = original
        self._replace = replace
        self._dataIn = dataIn
        self._action = action
        self._ok = True
        self._output = None
        return
    
    def run(self):
        if self._object is None:
            print("Getting new object as did not have one")
            self._object = self._replace() # create a new one
        if self._object is not None:
            print("Using object to do something")
            try:
                print("self._object =", self._object)
                print("self._dataIn =", self._dataIn)
                self._output = self._action(self._object, self._dataIn)
                print("self._output =", self._output)
            except Exception as exc:
                print("Failing as exception:", exc)
                self._ok = False
                self._output = exc # return the exception if there was one
                self._object = None # do not return the object if there was 
        else:
            print("Failing as no object")
            self._ok = False
        return 
    
    def getObject(self):
        return self._object
    
    def getOutput(self):
        return self._output
    
    def isOk(self):
        return self._ok

