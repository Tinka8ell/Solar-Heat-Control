# !/usr/bin/python3
#UbidotsBackingStore.py
# Backing store using ubidots

from ubidots import ApiClient
import BackingStore as Bs

import time, datetime

class UbidotsBackingStore(Bs.BackingStore):
   'This will be the Ubidots backing store class for the Solar panel package'

   # Initialisation code
   def __init__(self):
      Bs.BackingStore.__init__(self)
      current = datetime.datetime.now()
      # Create an ApiClient object
      self.api = ApiClient(token='yJuJvi27c0CHde9kGf7VZ6CSGCTTZZ')

      # Get all the Ubidots Variables:
      # John's power meter - variable5 = api.get_variable('58ccef12762542259a52564a')
      Power = self.api.get_variable('58ccef12762542259a52564a')
      # John's power meter - variable5 = api.get_variable('58ccef12762542259a52564a')
      PumpP = self.api.get_variable('58f77f7576254205ccf1809b')
      # John's photoresistor value - variable = api.get_variable('58cab87676254236fd1da01c')
      Photo = self.api.get_variable('58cab87676254236fd1da01c')
      # John's threshold on value - variable2 = api.get_variable("58cac4ad76254236fbe2541d")
      Threshold = self.api.get_variable("58cac4ad76254236fbe2541d")
      # John's threshold off value - variable2 = api.get_variable("58f910d176254238876c5670")
      Off = self.api.get_variable("58f910d176254238876c5670")
      # John's switch pump on / off - variable3 = api.get_variable("58cac36f76254236fd1e14c3")
      Pump = self.api.get_variable("58cac36f76254236fd1e14c3")
      # John's pool water temperature reading = variable = api.get_variable('58cb232676254236faacf06c')
      Pool = self.api.get_variable('58f777f276254205cdce8c15')
      # John's water temperature reading = variable = api.get_variable('58cb232676254236faacf06c')
      Water = self.api.get_variable('58cb232676254236faacf06c')
      # John's water flow rate meter = variable = api.get_variable('58cf0bee762542735c52735b')
      Flow = self.api.get_variable('58cf0bee762542735c52735b')
      # John's water depth meter = variable = api.get_variable('59174d0e76254269c376b728')
      Depth = self.api.get_variable('59174d0e76254269c376b728')
      # My sample period currently in seconds 
      Period = self.api.get_variable('58d2591676254255c7015aaf')
      self.vars = {"Power": Power,
                   "PumpP": PumpP,
                   "Photo": Photo,
                   "Threshold": Threshold,
                   "Off": Off,
                   "Pump": Pump,
                   "Pool": Pool,
                   "Water": Water,
                   "Flow": Flow,
                   "Depth": Depth,
                   "Period": Period}
      setupTime = datetime.datetime.now() - current
      print("Ubidots set up took: " + str(setupTime))

   # get a named control value
   def getProperty(self, name):
      value = None
      # All others read from ubidots
      var = self.vars.get(name)
      if var:
         try:
         # read ubiots variable
            values = var.get_values(1)
            strValue = str(values[0]['value'])
            value = float(strValue)
         except ConnectionError as Argument:
            print("Connection error:", Argument)
            print("Skipping read from ubidots at", datetime.datetime.now().isoformat(' '))
            print("Failed to read: Key:", name)
            # don't recover if error
            raise
         except Exception as Argument:
            print("Big error:", Argument)
            print("Skipping read from ubidots at", datetime.datetime.now().isoformat(' '))
            print("Failed to read: Key:", name)
            # don't recover if error
            raise
      else: # otherwise use test data ...
         value = self.testData.get(name, 0)
      return value

   # get all named control values
   def getProperties(self):
      # control values are:
      current = datetime.datetime.now()
      keys = ["Period", "Threshold", "Off"]
      values = {}
      for key in keys:
         values[key] = self.getProperty(key)
      getTime = datetime.datetime.now() - current
      print("Ubidots get properies took: " + str(getTime))
      print("returned: " + str(values))
      return values

   # record all the values using the given keys
   def recordAll(self, keys, values):
      # this assumes that the keys are always in the same order!
      current = datetime.datetime.now()
      for key in keys:
          self.recordIt(key, values.get(key, None))
      setTime = datetime.datetime.now() - current
      print("Ubidots set properies took: " + str(setTime))

   # record a value using the given key
   def recordIt(self, key, value):
      if value is None:
         print("Error: value not set for", key)
      else:
         try:
            response = self.vars[key].save_value({"value": value})
         except ConnectionError as Argument:
            print("Connection error:", Argument)
            print("Skipping write to ubidots at", datetime.datetime.now().isoformat(' '))
            print("Failed to write: Key:", key, "=", value)
         except Exception as Argument:
            print("Big error:", Argument)
            print("Skipping write to ubidots at", datetime.datetime.now().isoformat(' '))
            print("Failed to write: Key:", key, "=", value)
      # print("Key:", key, "=", value)

def main():
    # This is just for testing
   bs = UbidotsBackingStore()
   print("getProperties() returned")
   print(bs.getProperties())
   print("period =", bs.getProperty("Period"))
   print("threshold =", bs.getProperty("Threshold"))
   
   keys = ["Power", "Photo", "Pump", "Water", "Flow"]
   print("full write")
   bs.recordAll(keys, {"Power": 123.45, "Photo": 3.7, "Pump": 1, "Water": 22.0, "Flow": 17.5})
   print("wait 1 min")
   time.sleep(60)
   print("small write")
   bs.recordAll(keys, {"Photo": 7.8, "Water": 15.0, "Flow": 12.3, "Temp": 32.1})
   print("wait 1 min")
   time.sleep(60)
   print("reset write")
   bs.recordAll(keys, {"Power": 0, "Photo": 1.2, "Pump": 0, "Water": 15.0, "Flow": 0})
   print("wait 1 min")
   time.sleep(60)
   print("write one")
   bs.recordIt("Photo", 0.7)
   

if __name__ == '__main__':
    main()
