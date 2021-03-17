# !/usr/bin/python3
# test UbidotsBackingStore.py
"""
Make sure UbidotsBackingStore does what it should
"""

import os
import os.path
from random import randint, choice
from unittest import TestCase, main, SkipTest, skip

from UbidotsBackingStore import UbidotsBackingStore 

logErrors = False
@skip("Only run if ok to disrupt ubidots data")
class TestUbidotsBackingStore(TestCase):

    def testGoodGetProperty(self):
        ubs = UbidotsBackingStore(logErrors=logErrors)
        for key in ubs._getControlKeys():
            value = randint(0, 10)
            ubs._setProperty(key, value)
            with self.subTest(key=key, value=value):
                self.assertEqual(value, 
                                 ubs.getProperty(key), 
                                 "Valid property " + key)
        return 

    def testBadGetProperty(self):
        ubs = UbidotsBackingStore(logErrors=logErrors)
        key = "unknown"
        self.assertEqual(None, 
                         ubs.getProperty(key),
                         "Invalid property " + key)
        return 

    def testGetProperties(self):
        ubs = UbidotsBackingStore(logErrors=logErrors)
        values = ubs.getProperties()
        self.assertIsNotNone(values, "Should get a dict back")
        returned = list(values.keys())
        for key in ubs._getControlKeys():
            with self.subTest(key=key):
                self.assertIn(key, 
                              returned, 
                              "Includes " + key)
                returned.remove(key)
        self.assertEqual(0, len(returned), "Nothing extra")
        return

    def testRecordIt(self):
        ubs = UbidotsBackingStore(logErrors=logErrors)
        for key in ubs._getLogKeys():
            with self.subTest(key=key):
                value = randint(0, 10)
                ubs.recordIt(key, value)
                self.assertEqual(value, 
                                 ubs.getProperty(key), 
                                 "Got back what we set for " + key)
        return

    def testRecordUnknownIt(self):
        ubs = UbidotsBackingStore(logErrors=logErrors)
        key = "Unknown"
        value = randint(0, 10)
        ubs.recordIt(key, value)
        self.assertEqual(None, 
                         ubs.getProperty(key), 
                         "Invalid property " + key)
        return

    def testRecordAll(self):
        ubs = UbidotsBackingStore(logErrors=logErrors)
        keys = ubs._getLogKeys()
        count = len(keys)
        self.assertGreater(count, 0, "Must be more than one key")
        remove = choice(range(count))
        keys.pop(remove) # just remove one
        values = {}
        for key in keys:
            values[key] = randint(0, 10)
        ubs.recordAll(values)
        for key in values.keys():
            with self.subTest(key=key):
                self.assertEqual(values[key], 
                                 ubs.getProperty(key), 
                                 "Got back what we set for " + key)
        return
    
    def testRecordUnkownAll(self):
        ubs = UbidotsBackingStore(logErrors=logErrors)
        keys = ubs._getLogKeys()
        count = len(keys)
        self.assertGreater(count, 0, "Must be more than one key")
        add = choice(range(count))
        unk = "Unknown"
        keys.insert(add, unk)
        values = {}
        for key in keys:
            values[key] = randint(0, 10)
        ubs.recordAll(values)
        self.assertIsNone(ubs.getProperty(unk), 
                          "Did not log " + key)
        return
    
