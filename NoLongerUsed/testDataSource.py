# !/usr/bin/python3
# DataSource.py
"""
test the data sources work as expected.
"""
from unittest import TestCase, main, SkipTest, skip, expectedFailure

from DataSource import DataSource 


class testDataSource (TestCase):

    # Initialisation code
    def testCreate(self):
        name = "someThing"
        value = 0
        ds = DataSource(name)
        self.assertEqual(name, ds.getName())
        self.assertEqual(value, ds.getValue())
        return

    @expectedFailure # "Base class only returns ints"
    def testGetSetValue(self):
        value = 77.7
        name = "anotherThing"
        ds = DataSource(name)
        ds.setValue(value)
        self.assertEqual(name, ds.getName())
        self.assertEqual(value, ds.getValue())
        return


