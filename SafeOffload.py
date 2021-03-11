# !/usr/bin/python3
# SafeOffload.py

import threading

class SafeOffload(threading.Thread):
   'This will enable us to do stuff on a separate thread and so protect the main code'

   # Initialisation code
   def __init__(self):
      # init parent
      threading.Thread.__init__(self)
      self.ok = True # used to be sure we worked, so we can recycle ...
      self.object = None
      self.error = None

   def setup(self, data):
      self.data = data # what we neeed to work with

   def init(self):
      if not self.object: # not being reused
         self.object = None
      print("Initialising the objects to use")

   def run(self):
      self.ok = False
      try:
         self.init()
         self.do()
      except BaseException as e:
         self.error = e
         raise self.error
      self.ok = True

   def do(self):
      print("Doing something to the objects")
      print("Data is:", self.data)
      raise Exception("My error")

   def isOk(self):
      return self.ok

   def hasFailed(self):
      return not self.ok

   def getError(self):
      return self.error

def main():
   # this is for testing
   obj = SafeOffload()
   obj.setup("My Data")
   obj.start()
   obj.join()
   if obj.isOk():
      print("It worked")
   else:
      print("Oops it didn't work")
      print("Exception was:", obj.getError())

# execute only if run as a script
if __name__ == "__main__":
   main() # execute test code ...
