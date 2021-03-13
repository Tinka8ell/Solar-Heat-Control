# !/usr/bin/python3
# UbidotsBackingStore.py
"""
Final backing store used by the Solar project.
Backing store using ubidots so it can be monitored and controlled
remotely and also generate nice graphs and stuff.
"""

from datetime import datetime

from ubidots import ApiClient

from BackingStore import BackingStore 

class UbidotsBackingStore(BackingStore):
    'This will be the Ubidots backing store class for the Solar panel package'

    TOKENS = None # local 'class' copy of token data

    # Initialisation code
    def __init__(self):
        super().__init__()
        current = datetime.now()
        if self.TOKENS is None:
            print("Reading tokens")
            # one time read of tokens
            self.TOKENS = {}
            with open('ubidots.txt') as f:
                line = f.readline()
                while len(line) > 0:
                    if line.endswith('\n'):
                        line = line[:-1].strip() # remove it
                        # print("Removing trailing nl from:", line)
                    key, value = line.split(" = ")
                    self.TOKENS[key] = value
                    line = f.readline()
            # print("Tokens are:", self.TOKENS)
        self.api = ApiClient(token=self.TOKENS['token'])
        self.vars = {}
        for key in self.TOKENS.keys():
            if key != 'token':
                var = self.api.get_variable(self.TOKENS[key])
                self.vars[key] = var
        setupTime = datetime.now() - current
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
            except ConnectionError as exc:
                print("Connection error:", exc)
                print("Skipping read from ubidots at",
                      datetime.now().isoformat(' '))
                print("Failed to read: Key:", name)
                # don't recover if error
                raise
            except Exception as exc:
                print("Big error:", exc)
                print("Skipping read from ubidots at",
                      datetime.now().isoformat(' '))
                print("Failed to read: Key:", name)
                # don't recover if error
                raise
        else:  # otherwise use test data ...
            value = self.testData.get(name, 0)
        return value

    # get all named control values
    def getProperties(self):
        current = datetime.now()
        # control values are:
        keys = ["Period", "Threshold", "Off"]
        values = {}
        for key in keys:
            values[key] = self.getProperty(key)
        getTime = datetime.now() - current
        print("Ubidots get properies took: " + str(getTime))
        print("returned: " + str(values))
        return values

    # record all the values using the given keys
    def recordAll(self, keys, values):
        current = datetime.now()
        for key in keys:
            self.recordIt(key, values.get(key, None))
        setTime = datetime.now() - current
        print("Ubidots set properies took: " + str(setTime))

    # record a value using the given key
    def recordIt(self, key, value):
        if value is None:
            print("Error: value not set for", key)
        else:
            try:
                response = self.vars[key].save_value({"value": value})
            except ConnectionError as exc:
                print("Connection error:", exc)
                print("Skipping write to ubidots at",
                      datetime.now().isoformat(' '))
                print("Failed to write: Key:", key, "=", value)
                raise
            except Exception as exc:
                print("Big error:", exc)
                print("Skipping write to ubidots at",
                      datetime.now().isoformat(' '))
                print("Failed to write: Key:", key, "=", value)
                raise
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
    bs.recordAll(keys, {"Power": 123.45, "Photo": 3.7,
                        "Pump": 1, "Water": 22.0, "Flow": 17.5})
    print("wait 1 min")
    time.sleep(60)
    print("small write")
    bs.recordAll(keys, {"Photo": 7.8, "Water": 15.0,
                        "Flow": 12.3, "Temp": 32.1})
    print("wait 1 min")
    time.sleep(60)
    print("reset write")
    bs.recordAll(keys, {"Power": 0, "Photo": 1.2,
                        "Pump": 0, "Water": 15.0, "Flow": 0})
    print("wait 1 min")
    time.sleep(60)
    print("write one")
    bs.recordIt("Photo", 0.7)


if __name__ == '__main__':
    main()
