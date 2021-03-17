# !/usr/bin/python3
# test FileBackingStore.py
"""
Make sure FileBackingStore does what it should
"""

import os
import os.path
from unittest import TestCase, main, SkipTest, skip

from FileBackingStore import FileBackingStore 


class TestFileBackingStore(TestCase):

    def setUp(self):
        # protect existing backing files:
        self.bs = FileBackingStore()
        self.where = self.bs.getDir()
        self.log = self.bs.getLog()
        self.control = self.bs.getControl()
        self.bs = None # remove old one
        
        self.backLog = os.path.join(self.where, "back"+os.path.basename(self.log))
        if os.path.exists(self.backLog):
            os.remove(self.backLog)
        os.rename(self.log, self.backLog)
        
        self.backControl = os.path.join(self.where, "back"+os.path.basename(self.control))
        if os.path.exists(self.backControl):
            os.remove(self.backControl)
        os.rename(self.control, self.backControl)
        
        # set up test environment
        self.bs = FileBackingStore()

        # set test properties
        self.good = self.bs.getProperties()
        self.good["Period"] = 30
        self.good["Threshold"] = 3
        self.good["Off"] = 7
        self.bad = {
            "random": None,
            "missing": None,
            }
        self.bs.setProperties(self.good)
        return

    def tearDown(self):
        # restore previous backing files:
        if os.path.exists(self.backLog):
            if os.path.exists(self.log):
                os.remove(self.log)
            os.rename(self.backLog, self.log)
        
        if os.path.exists(self.backControl):
            if os.path.exists(self.control):
                os.remove(self.control)
            os.rename(self.backControl, self.control)
        return

    def testGoodGetProperty(self):
        for key in self.good.keys():
            value = self.good[key]
            with self.subTest(key=key, value=value):
                self.assertEqual(value, self.bs.getProperty(key))
        return 

    def testBadGetProperty(self):
        for key in self.bad.keys():
            value = self.bad[key]
            with self.subTest(key=key, value=value):
                self.assertEqual(value, self.bs.getProperty(key))
        return 

    def testGetProperties(self):
        self.assertEqual(self.good, self.bs.getProperties())
        return

    def testSetProperties(self):
        changed = {}
        missing = "Period"
        for key in self.good.keys():
            changed[key] = self.good[key] * 0.5
        changed.pop(missing)
        changed["new"] = 123.45
        # test it
        self.bs.setProperties(changed)
        # given expected result:
        # old behaviour: changed[missing] = self.good[missing]
        self.assertEqual(changed, self.bs.getProperties())
        return 

    def testRecordAll(self):
        before = self.bs.dumpRecords()
        someValues = {
            "something": 23.456,
            "nothing": 0,
            "None": None,
            "pi": 3.14159,
            }

        self.bs.recordAll(someValues)
        after = self.bs.dumpRecords()
        self.assertEqual(before, after[:len(before)])
        self.assertEqual(len(before) + 1, len(after))
        for key in someValues.keys():
            with self.subTest(key=key):
                self.assertEqual(someValues[key], 
                                 after[len(before)][key], 
                                 "Data for found for key: " + key)
        return 

    def testRecordIt(self):
        before = self.bs.dumpRecords()
        key = "something"
        value = 23.456
        
        self.bs.recordIt(key, value)
        after = self.bs.dumpRecords()
        self.assertEqual(before, after[:len(before)])
        self.assertEqual(len(before) + 1, len(after))
        self.assertEqual(value, 
                         after[len(before)][key], 
                         "Data for found for key: " + key)
        return 


