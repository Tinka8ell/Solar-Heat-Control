"""
Test we can safely execute dodgy code using the Safely object.
"""

from time import sleep
from unittest import TestCase, main, SkipTest, skip

from Safely import doSafely


class Good():

    def __init__(self, start=1, stop=10):
        self.range = range(start, stop)
        return 
    
    def doSomthing(self, *data):
        delay = data[0]
        result = 0
        for i in self.range:
            sleep(delay)
            result += i
        return result

    
class DoesException(Good):
    
    def doSomthing(self, *data):
        delay = data[0]
        raise Exception("This throws an exception")
    

def doIt(instance, *data):
    return instance.doSomething(*data)

class TestSafely(TestCase):
    
    def testOkWithObject(self):
        # print("Good: ", Good.__dict__)
        start = 1
        stop = 10
        expect = ((stop - 1) - start) * ((stop - 1) - start) / 2
        object = Good()
        # print("Good object: ", object.__dict__)
        delay = 0.1
        print("doing something on:", object)
        result = object.doSomthing(delay)
        print("did something:", result)
        print("doing something again:", object)
        result = doIt(object, delay)
        print("did something:", result)
        # this test should not take longer than delay * (stop - start)
        timeout = 2 * delay * (stop - start)
        (newObject, result) = doSafely(object, Good, (delay,), doIt, timeout)
        self.assertEqual(object, newObject, "Should start and finish with same object")
        self.assertEqual(expect, result, "Result is a sum of integers")
        return

    @skip("testing one at a time")
    def testOkWithoutObject(self):
        start = 1
        stop = 10
        expect = ((stop - 1) - start) * ((stop - 1) - start) / 2
        object = None
        delay = 0.1
        # this test should not take longer than delay * (stop - start)
        timeout = 2 * delay * (stop - start)
        (newObject, result) = doSafely(object, Good, (delay,), doIt, timeout)
        self.assertIsNotNone(newObject, "Should finish with new object")
        self.assertEqual(expect, result, "Result is a sum of integers")
        return

    @skip("testing one at a time")
    def testTimeoutWithObject(self):
        start = 1
        stop = 10
        expect = ((stop - 1) - start) * ((stop - 1) - start) / 2
        object = Good()
        delay = 0.1
        # this test should take at least delay * (stop - start)
        timeout = delay * (stop - start) - delay
        (newObject, result) = doSafely(object, Good, (delay,), doIt, timeout)
        self.assertEqual(object, newObject)
        self.assertEqual(expect, result)
        return

    @skip("testing one at a time")
    def testTimeoutWithoutObject(self):
        start = 1
        stop = 10
        expect = ((stop - 1) - start) * ((stop - 1) - start) / 2
        object = None
        delay = 0.1
        # this test should take at least delay * (stop - start)
        timeout = delay * (stop - start) - delay
        (newObject, result) = doSafely(object, Good, (delay,), doIt, timeout)
        self.assertIsNotNone(newObject)
        self.assertEqual(expect, result)
        return

    @skip("testing one at a time")
    def testExceptionWithObject(self):
        start = 1
        stop = 10
        expect = ((stop - 1) - start) * ((stop - 1) - start) / 2
        object = DoesException()
        delay = 0.1
        # this test should take at least delay * (stop - start)
        timeout = delay * (stop - start) - delay
        (newObject, result) = doSafely(object, DoesException, (delay,), doIt, timeout)
        self.assertEqual(object, newObject)
        self.assertEqual(expect, result)
        return

    @skip("testing one at a time")
    def testExceptionWithoutObject(self):
        start = 1
        stop = 10
        expect = ((stop - 1) - start) * ((stop - 1) - start) / 2
        object = None
        delay = 0.1
        # this test should take at least delay * (stop - start)
        timeout = delay * (stop - start) - delay
        (newObject, result) = doSafely(object, DoesException, (delay,), doIt, timeout)
        self.assertIsNotNone(newObject)
        self.assertEqual(expect, result)
        return

    @skip("testing one at a time")
    def testInvalidWithObject(self):
        start = 1
        stop = 10
        expect = ((stop - 1) - start) * ((stop - 1) - start) / 2
        object = Good()
        delay = 0.1
        # this test should take at least delay * (stop - start)
        timeout = delay * (stop - start) - delay
        (newObject, result) = doSafely(object, Good, None, doIt, timeout)
        self.assertEqual(object, newObject)
        self.assertEqual(expect, result)
        return

    @skip("testing one at a time")
    def testInvalidWithoutObject(self):
        start = 1
        stop = 10
        expect = ((stop - 1) - start) * ((stop - 1) - start) / 2
        object = None
        delay = 0.1
        # this test should take at least delay * (stop - start)
        timeout = delay * (stop - start) - delay
        (newObject, result) = doSafely(object, Good, None, doIt, timeout)
        self.assertIsNotNone(newObject)
        self.assertEqual(expect, result)
        return

