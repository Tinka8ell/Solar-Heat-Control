# !/usr/bin/python3
#MultipleBackingStores.py
# Backing store using alternatives ...

import BackingStore as Bs
import FileBackingStore as Fbs
import GoogleBackingStore as Gbs
import UbidotsBackingStore as Ubs

import time, datetime

class MultipleBackingStores(Bs.BackingStore):
   'This will be the backing store class for the Solar panel package, using all the available options'

   # Initialisation code
   def __init__(self):
      Bs.BackingStore.__init__(self)
      # Create an BackingStore of each type:
      fileBs = Fbs.FileBackingStore()
      googleBs = Gbs.GoogleBackingStore()
      ubidotsBs = Ubs.UbidotsBackingStore()
      self.order = ["Ubidots", # primary
                    "Google",  # backup
                    "File"]    # last resort
      self.backingStores = {"Ubidots": ubidotsBs, # primary
                            "Google": googleBs,   # backup
                            "File": fileBs        # last resort
                            }
      print("Created mutilple backing stores")

   # get a named control value
   def getProperty(self, name):
      value = None
      # use each in turn till get one
      for key in self.order:
         if value is None: # not got a value yet
            bs = self.backingStores.get(key)
            if not (bs is None): # if have a bs to use
               value = bs.getProperty(name) # get it's value
               if not (value is None): # got a value
                  print("Read control value from:", key)
      return value

   # get all named control values
   def getProperties(self):
      values = {}
      # use each in turn till get one
      for key in self.order:
         if len(values) == 0: # not got any values yet
            bs = self.backingStores.get(key)
            if not (bs is None): # if have a bs to use
               values = bs.getProperties() # get the values
               if len(values) > 0: # got some values
                  print("Read control values from:", key)
      return values

   # record all the values using the given keys
   def recordAll(self, keys, values):
      # this assumes that the keys are always in the same order!
      # record to all bs's
      for key in self.order:
         bs = self.backingStores.get(key)
         if not (bs is None): # if have a bs to use
            # time each to give comparison for debugging
            current = datetime.datetime.now()
            bs.recordAll(keys, values)
            # compare time and report it
            saveTime = datetime.datetime.now() - current
            print("Time to record using " + key + ": " + str(saveTime))

   # record a value using the given key
   def recordIt(self, key, value):
      if value is None:
         print("Error: value not set for", key)
      else:
         # record to all bs's
         for key in self.order:
            bs = self.backingStores.get(key)
            if not (bs is None): # if have a bs to use
               bs.recordIt(key, value)
#      print("Key:", key, "=", value)

def main():
    # This is just for testing
   bs = MultipleBackingStores()
   print("getProperties() returned")
   print(bs.getProperties())
   print("period =", bs.getProperty("Period"))
   print("threshold =", bs.getProperty("Threshold"))
   
   keys = ["Power", "Photo", "Pump", "Water", "Flow"]
   print("Full write")
   bs.recordAll(keys, {"Power": 123.45, "Photo": 3.7, "Pump": 1, "Water": 22.0, "Flow": 17.5})
   print("Wait 1 min")
   time.sleep(60)
   print("Reset write")
   bs.recordAll(keys, {"Power": 0, "Photo": 1.2, "Pump": 0, "Water": 15.0, "Flow": 0})
   print("Done")

if __name__ == '__main__':
    main()
