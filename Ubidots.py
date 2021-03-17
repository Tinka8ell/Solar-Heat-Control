# !/usr/bin/python3
# Ubidots.py
"""
Object that represents the ubidots repository.
This wrappers the ApiClient used to access ubidots.
The class contains the tokens needed for the client and variables.
These are read from a backing file on first access.
Each new instance, creates the ApiClient(connects to ubidots)
and the variables used to store and retrieve data from ubidots.
"""

from datetime import datetime

from ubidots import ApiClient


class Ubidots():
    'This will be the Ubidots ApiClient wrapper'

    # local 'class' copy of token data taken from backing store
    TOKENS = None 

    # Initialisation code
    def __init__(self, logging=False):
        self._logging = logging
        if self._logging:
            current = datetime.now()
        if self.TOKENS is None:
            if self._logging:
                print("Ubidots reading tokens")
            # one time read of tokens
            self.TOKENS = {}
            with open('ubidots.txt') as f:
                line = f.readline()
                while len(line) > 0:
                    if line.endswith('\n'):
                        line = line[:-1].strip()  # remove it
                        # print("Removing trailing nl from:", line)
                    key, value = line.split(" = ")
                    self.TOKENS[key] = value
                    line = f.readline()
            if self._logging:
                print("Ubidots tokens are:", self.TOKENS)
        self.api = ApiClient(token=self.TOKENS['token'])
        self.vars = {}
        for key in self.TOKENS.keys():
            if key != 'token':
                var = self.api.get_variable(self.TOKENS[key])
                self.vars[key] = var
        if self._logging:
            setupTime = datetime.now() - current
            print("Ubidots set up took: " + str(setupTime))
        return

    def getProperty(self, name):
        if name not in self.vars.keys():
            raise KeyError("Ubidots (recordIt) unknown key: " + name)
        value = None
        try:
            # read ubiots variable
            values = self.vars[name].get_values(1)
            strValue = str(values[0]['value'])
            value = float(strValue)
        except ConnectionError as exc:
            if self._logging:
                print(datetime.now().isoformat(' '),
                      "Ubidots (getProperty) connection error:", exc,
                      "Failed to read: Key:", name)
            raise
        except Exception as exc:
            if self._logging:
                print(datetime.now().isoformat(' '),
                      "Ubidots (getProperty) big error:", exc,
                      "Failed to read: Key:", name)
            raise
        return value

    def getProperties(self, keys):
        if self._logging:
            current = datetime.now()
        values = {}
        for key in keys:
            values[key] = self.getProperty(key)
        if self._logging:
            getTime = datetime.now() - current
            print("Ubidots get properties took: " + str(getTime),
                  "returned: " + str(values))
        return values

    def recordIt(self, key, value):
        if key not in self.vars.keys():
            raise KeyError("Ubidots (recordIt) unknown key: " + key)
        try:
            response = self.vars[key].save_value({"value": value})
        except ConnectionError as exc:
            if self._logging:
                print(datetime.now().isoformat(' '),
                      "Ubidots (recordIt) connection error:", exc,
                      "Failed to read: Key:", name)
            raise
        except Exception as exc:
            if self._logging:
                print(datetime.now().isoformat(' '),
                      "Ubidots (recordIt) big error:", exc,
                      "Failed to read: Key:", name)
            raise
        return

    def recordAll(self, values):
        if self._logging:
            current = datetime.now()
        for key in values.keys():
            self.recordIt(key, values.get(key, None))
        if self._logging:
            setTime = datetime.now() - current
            print("Ubidots record all took: " + str(setTime),
                  "storing: " + str(values))
        return
    
    def allKeys(self):
        return list(self.vars.keys())


