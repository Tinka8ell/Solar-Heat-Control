# !/usr/bin/python3
# test BackingStore.py
"""
Make sure BackingStore does what it should
"""

from unittest import TestCase, main, SkipTest, skip

from BackingStore import BackingStore 

class TestBackingStore(TestCase):

    def setUp(self):
        # set up test environment
        self.bs = BackingStore()
        self.setTestProperties()
        return
    
    def setTestProperties(self):
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
        # in case we need some tear down
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
        # set up test case
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

    @skip("can't expect to read log")
    def testRecordAll(self):
        before = self.bs.dumpRecords()
        someRecords = (
            ("something", 23.456),
            ("nothing", 0),
            ("None", None),
            ("pi", 3.14159),
            )
        before.append(someRecords)
        someValues = {}
        for i in range(len(someRecords)):
            someValues[someRecords[i][0]] = someRecords[i][1]

        self.bs.recordAll(someValues)
        after = self.bs.dumpRecords()
        self.assertEqual(before, after)
        return 

    @skip("can't expect to read log")
    def testRecordIt(self):
        before = self.bs.dumpRecords()
        aRecord = ("something", 23.456)
        before.append(aRecord)
        
        self.bs.recordIt(aRecord[0], aRecord[1])
        after = self.bs.dumpRecords()
        self.assertEqual(before, after)
        return 


