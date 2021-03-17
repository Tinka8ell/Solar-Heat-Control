# !/usr/bin/python3
# test Ubidots.py
"""
Make sure Ubidots does what it should
"""

from unittest import TestCase, main, SkipTest, skip
from random import choice, randint

from Ubidots import Ubidots 

@skip("Only run if ok to disrupt ubidots data")
class testUbidots(TestCase):
    
    def testCreate(self):
        u = Ubidots()
        self.assertIsInstance(u, Ubidots, "Created an object")
        self.assertIsInstance(u.allKeys(), list, "Contains list of keys")
        return
        

    def testGetProperty(self):
        u = Ubidots()
        for key in u.allKeys():
            with self.subTest(key=key):
                self.assertIsNotNone(u.getProperty(key), "Getting property " + key)
        return
            
    def testGetUnknownProperty(self):
        u = Ubidots()
        with self.assertRaises(KeyError, msg="Get unknown property"):
            value = u.getProperty("Unknown")
        return

    def testGetProperties(self):
        u = Ubidots()
        keys = u.allKeys()
        count = len(keys)
        self.assertGreater(count, 0, "Must be more than one key")
        remove = choice(range(count))
        keys.pop(remove)
        values = u.getProperties(keys)
        self.assertEqual(len(keys), len(values), "All values requested returned")
        for key in keys:
            with self.subTest(key=key):
                self.assertIsNotNone(values[key], "Got property " + key)
        return 

    def testGetUnknownProperties(self):
        u = Ubidots()
        keys = u.allKeys()
        count = len(keys)
        self.assertGreater(count, 0, "Must be more than one key")
        add = choice(range(count))
        keys.insert(add, "Unknown")
        with self.assertRaises(KeyError, msg="Get unknown property"):
            values = u.getProperties(keys)
        return
 
    def testRecordIt(self):
        u = Ubidots()
        for key in u.allKeys():
            with self.subTest(key=key):
                value = randint(0, 10)
                u.recordIt(key, value)
                self.assertEqual(value, u.getProperty(key), "Got back what we set for " + key)
        return

    def testRecordUnknownIt(self):
        u = Ubidots()
        with self.assertRaises(KeyError, msg="Set unknown property"):
            value = u.recordIt("Unknown", randint(0, 10))
        return

    def testRecordAll(self):
        u = Ubidots()
        keys = u.allKeys()
        count = len(keys)
        self.assertGreater(count, 0, "Must be more than one key")
        remove = choice(range(count))
        keys.pop(remove)
        values = {}
        for key in keys:
            values[key] = randint(0, 10)
        u.recordAll(values)
        self.assertEqual(values, u.getProperties(keys), "Got back what we set")
        return
    
    def testRecordUnkownAll(self):
        u = Ubidots()
        keys = u.allKeys()
        count = len(keys)
        self.assertGreater(count, 0, "Must be more than one key")
        add = choice(range(count))
        keys.insert(add, "Unknown")
        values = {}
        for key in keys:
            values[key] = randint(0, 10)
        with self.assertRaises(KeyError, msg="Set unknown property"):
            u.recordAll(values)
        return
    
