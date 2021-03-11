# !/usr/bin/python3
# SafeInternetDownload.py

import SafeOffload
import UbidotsBackingStore as Ubs
import FileBackingStore as Fbs
import time

class SafeInternetDownload(SafeOffload.SafeOffload):
   'This will enable us to do stuff on a separate thread and so protect the main code'

   # Initialisation code
   def __init__(self):
      # init parent
      SafeOffload.SafeOffload.__init__(self)
      self.bs = None
      self.fbs = None

   def setup(self, data):
      self.bs = data[0]
      self.fbs = data[1]
      
   def init(self):
      # print("Internet init called")
      if not self.bs:
         # print("Initialising UBIDOTS")
         self.bs = Ubs.UbidotsBackingStore()

   def do(self):
      properties = self.bs.getProperties()
      # update local copy
      self.fbs.setProperties(properties)

   def getBs(self):
      bs = None
      if self.isOk():
         bs = self.bs
      return bs

def main():
   # this is for testing
   bs = None
   fbs = Fbs.FileBackingStore()
   print("Current FBS control:", fbs.getProperties())
   obj = SafeInternetDownload()
   obj.setup([bs, fbs])
   obj.start()
   obj.join()
   if obj.isOk():
      print("It worked")
   else:
      print("Oops it didn't work")
      print("Exception was:", obj.getError())
   print("Now FBS control:", fbs.getProperties())
   bs = obj.getBs()
   print("wait 20 secs")
   time.sleep(20)
   obj = SafeInternetDownload()
   obj.setup([bs, fbs])
   obj.start()
   obj.join()
   if obj.isOk():
      print("It worked")
   else:
      print("Oops it didn't work")
      print("Exception was:", obj.getError())
   print("Final FBS control:", fbs.getProperties())

# execute only if run as a script
if __name__ == "__main__":
   main() # execute test code ...
