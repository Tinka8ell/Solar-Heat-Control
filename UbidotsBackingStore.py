# !/usr/bin/python3
# UbidotsBackingStore.py
"""
Safe version of the UbidotsBackingStore that can cope with unexpected errors 
and access that takes too long.
Final backing store used by the Solar project.
Backing store using ubidots so it can be monitored and controlled
remotely and also generate nice graphs and stuff.
"""

from datetime import datetime
from sys import stderr
from threading import Thread

from Ubidots import Ubidots


class UbidotsBackingStore():

    # Initialisation code
    def __init__(self, 
                 timeout=1, 
                 control=["Period", "Threshold", "Off"],
                 logErrors = False):
        super().__init__()
        self._ubidots =  None # place holder for access to ubidots
        self._timeout = timeout
        self._createTimeout = self._timeout * 10
        self._controlKeys = control
        self._logErrors = logErrors
        return
    
    def _logError(self, method):
        if self._logErrors:
            print(datetime.now().isoformat(' '),
                  "UbidotsBackingStore: ", 
                  method, " - ", 
                  self._exc, file=stderr)
        return
    
    def _getUbidots(self):
        # ensure we have a Ubidots object
        self.ok = False
        try:
            self._ubidots = Ubidots() # logging=self._logErrors)
            self.ok = True
        except Exception as exc:
            self._exc = exc
        return 

    def getUbidots(self):
        # ensure we have a Ubidots object
        if self._ubidots is None:
            self.thread = Thread(target=self._getUbidots)
            self._exc = "Timeout creating ubidots object"
            self.thread.start()
            self.thread.join(self._createTimeout) 
            if not self.ok: # if there was a problem
                self._ubidots = None # throw away old object
                self._logError("getUbidots")
        return self._ubidots 

    # get a named control value
    def _getProperty(self, name):
        self.ok = False
        try:
            self._value = self.getUbidots().getProperty(name)
            self.ok = True
        except Exception as exc:
            self._exc = exc
        return
    
    # get a named control value
    def getProperty(self, name):
        self._value = None
        if self.getUbidots() is not None:
            self.thread = Thread(target=self._getProperty, args=(name,))
            self._exc = "Timeout getting property " + name
            self.thread.start()
            self.thread.join(self._timeout)
            if not self.ok: # if there was a problem
                self._ubidots = None # throw away old object
                self._value = None
                self._logError("getProperty")
        return self._value

    # get all named control values
    def _getProperties(self):
        self.ok = False
        try:
            self._values = self.getUbidots().getProperties(self._controlKeys)
            self.ok = True
        except Exception as exc:
            self._exc = exc
        return 

    # get all named control values
    def getProperties(self):
        self._values = None
        if self.getUbidots() is not None:
            self.thread = Thread(target=self._getProperties)
            self._exc = "Timeout getting all properties"
            self.thread.start()
            self.thread.join(self._timeout * len(self._controlKeys))
            if not self.ok: # if there was a problem
                self._ubidots = None # throw away old object
                self._values = None
                self._logError("getProperties")
        return self._values

    # record all the values using the given keys
    def _recordAll(self, values):
        self.ok = False
        try:
            self.getUbidots().recordAll(values)
            self.ok = True
        except Exception as exc:
            self._exc = exc
        return

    # record all the values using the given keys
    def recordAll(self, values):
        if self.getUbidots() is not None:
            self.thread = Thread(target=self._recordAll, args=(values,))
            self._exc = "Timeout recording all values"
            self.thread.start()
            self.thread.join(self._timeout * len(values))
            if not self.ok: # if there was a problem
                self._ubidots = None # throw away old object
                self._logError("recordAll")
        return 

    # record a value using the given key
    def _recordIt(self, key, value):
        self.ok = False
        try:
            self.getUbidots().recordIt(key, value)
            self.ok = True
        except Exception as exc:
            self._exc = exc
        return

    # record a value using the given key
    def recordIt(self, key, value):
        if self.getUbidots() is not None:
            self.thread = Thread(target=self._recordIt, args=(key, value))
            self._exc = "Timeout recording value for " + key
            self.thread.start()
            self.thread.join(self._timeout)
            if not self.ok: # if there was a problem
                self._ubidots = None # throw away old object
                self._logError("recordIt")
        return 

    # set a property - only for testing!
    def _setProperty(self, key, value):
        self.recordIt(key, value)
        return 

    # get list of control keys - only for testing!
    def _getControlKeys(self):
        return list(self._controlKeys)

    # get list of log keys - only for testing!
    def _getLogKeys(self):
        u = self.getUbidots()
        logKeys = []
        if u is not None:
            logKeys = u.allKeys()
        for key in self._getControlKeys():
            if key in logKeys:
                logKeys.remove(key)
        return logKeys

