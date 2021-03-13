# !/usr/bin/python3
# RealDataSource.py
"""
Looks like a back up copy of RealDataSource.py
while under development.
Probably out of date now and not used ...
"""
import DataSource as Ds

# for setting the pump value and reading the flow
import RPi.GPIO as GPIO
# http://raspberrypi.stackexchange.com/questions/34480/how-to-use-the-water-flow-sensor-with-raspberry
# NB need to calibrate
import time
import datetime
import sys
# for reading the analog input channels
# Import SPI library (for hardware SPI)
import Adafruit_GPIO.SPI as SPI
# MCP3008 library and math for calculations
import Adafruit_MCP3008 as MCP
import math
# for reading the thermometer
import os
import glob


class RealDataSource (Ds.DataSource):
    'This will be the RealDataSource class for the Solar panel package'
    '''
Generate values based on given names:
   Power = John's power meter - reading the MCP3008 analog input channels
   PumpP = John's power meter - reading the MCP3008 analog input channels
   Photo = John's photoresistor value - reading the MCP3008 analog input channels
   Pump  = John's switch pump on / off - so realy a data sink ... writing to the GPIO pin
   Water = John's water temperature reading - reading a device file
   Flow  = John's water flow rate meter - counting GPIO pulses
Seem to be using the following GPIO ports:
   18 - Analog clock
   22 - Flow sensor
   23 -)              / channel 6 - power
   24 -- Analog ports
   25 -)              \ channel 7 - photo
   27 - Pump 
   28 - Thermometer possibly

   added
   26 ultrasonic trigger
   19 ultrasonic echo
'''

    # Initialisation code
    def __init__(self, name):
        # set GPIO Pins
        self.pumpSwitch = 27
        self.CLK = 18
        self.MISO = 23
        self.MOSI = 24
        self.CS = 25
        self.TRIGGER = 26    # updated
        self.ECHO = 19        # upated
        self.FLOW_SENSOR = 22

        Ds.DataSource.__init__(self, name)
        if (name == "Power") or (name == "PumpP") or (name == "Photo"):
            # Software SPI configuration:
            self.mcp = MCP.MCP3008(
                clk=self.CLK, cs=self.CS, miso=self.MISO, mosi=self.MOSI)
            # Hardware SPI configuration:
#         self.SPI_PORT   = 0
#         self.SPI_DEVICE = 0
#         self.mcp = MCP.MCP3008(spi=SPI.SpiDev(self.SPI_PORT, self.SPI_DEVICE))
        elif name == "Pump":
            GPIO.setmode(GPIO.BCM)  # set the GPIO mode
            # initialise GPIO 27 has output and set low.
            GPIO.setup(self.pumpSwitch, GPIO.OUT)
            self.setValue(0)
        elif name == "Pool":
            # Initialize the GPIO Pins
            os.system('modprobe w1-gpio')  # Turns on the GPIO module
            os.system('modprobe w1-therm')  # Turns on the Temperature module
            # Find the correct device file that holds the temperature data
            base_dir = '/sys/bus/w1/devices/'
            self.device = '28-00000703ca7a'
            self.device_file = None
        elif name == "Water":
            # Initialize the GPIO Pins
            os.system('modprobe w1-gpio')  # Turns on the GPIO module
            os.system('modprobe w1-therm')  # Turns on the Temperature module
            # Find the correct device file that holds the temperature data
            base_dir = '/sys/bus/w1/devices/'
            # self.device = '28-0000070464ac' old device [replaced with longer probe]
            self.device = '28-000007039391'
            self.device_file = None
        elif name == "Flow":
            # initialise GPIO 22 for reading the sensor
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.FLOW_SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.count = 0
            self.lastTime = datetime.datetime.now()
            GPIO.add_event_detect(
                self.FLOW_SENSOR, GPIO.FALLING, callback=self.countPulse)
        elif name == "Depth":
            GPIO.setmode(GPIO.BCM)
            # set GPIO direction (IN / OUT)
            GPIO.setup(self.TRIGGER, GPIO.OUT)
            GPIO.setup(self.ECHO, GPIO.IN)

    def setValue(self, value):
        # print("Setting", self.getName(), "to", value)
        self.value = value  # like to use underlying dummy process ...
        # only relevant to the pump ...
        if self.getName() == "Pump":
            print("Setting", self.getName(), "to", value)
            if value == 0:  # off
                GPIO.output(self.pumpSwitch, GPIO.LOW)
            else:          # assume on
                GPIO.output(self.pumpSwitch, GPIO.HIGH)

    def getValue(self):
        if self.getName() == "Power":
            # looks like a calculation of power, via calories based on a reading from 0 to 1024
            SUPPLYVOLTAGE = 240
            # ICAL = 111.1*1047/1.2205750377
            # modified value from above based on impiracle testing! a.k.a. John said this number!
            ICAL = 20.3*1047/1.2205750377
            I_RATIO = ICAL * ((SUPPLYVOLTAGE / 1000.0) / 1023.0)
            # Calculate a root mean square of readings, seaded from 1/2 of max value
            NUMBER_OF_SAMPLES = 1000  # how log does 1000 readings take?
            sumI = 0
            sampleI = 512  # start at have height
            filteredI = 0
            for n in range(0, NUMBER_OF_SAMPLES):
                lastSampleI = sampleI
                # Software SPI read:
                sampleI = float(self.mcp.read_adc(6))
                # Hardware SPI read:
#            sampleI = readadc(cts, SPICLK, SPIMOSI, SPIMISO, SPICS)
                lastFilteredI = filteredI
                filteredI = 0.996 * (lastFilteredI + sampleI - lastSampleI)
                sqI = filteredI * filteredI
                sumI += sqI
            self.value = I_RATIO * math.sqrt(sumI / NUMBER_OF_SAMPLES)
#         print("watts= ", self.value)
        elif self.getName() == "PumpP":
            # looks like a calculation of power, via calories based on a reading from 0 to 1024
            SUPPLYVOLTAGE = 240
            # ICAL = 111.1*1047/1.2205750377
            # modified value from above based on impiracle testing! a.k.a. John said this number!
            ICAL = 20.3*1047/1.2205750377
            I_RATIO = ICAL * ((SUPPLYVOLTAGE / 1000.0) / 1023.0)
            # Calculate a root mean square of readings, seaded from 1/2 of max value
            NUMBER_OF_SAMPLES = 1000  # how log does 1000 readings take?
            sumI = 0
            sampleI = 512  # start at have height
            filteredI = 0
            for n in range(0, NUMBER_OF_SAMPLES):
                lastSampleI = sampleI
                # Software SPI read:
                sampleI = float(self.mcp.read_adc(5))
                # Hardware SPI read:
#            sampleI = readadc(cts, SPICLK, SPIMOSI, SPIMISO, SPICS)
                lastFilteredI = filteredI
                filteredI = 0.996 * (lastFilteredI + sampleI - lastSampleI)
                sqI = filteredI * filteredI
                sumI += sqI
            self.value = I_RATIO * math.sqrt(sumI / NUMBER_OF_SAMPLES)
#         print("watts= ", self.value)
        elif self.getName() == "Photo":
            # get the value for mcp channel 7 (the photoresistor)
            value = float(self.mcp.read_adc(7))
#         print("photoresistor value = ", value)
            # convert from scale of 1024 to 0
            # into scale of 0 to 20
            self.value = 20 * (1024 - value) / 1024
#         print("converted to value = ", self.value)
        elif self.getName() == "Water":
            # Convert the value of the sensor into a temperature
            lines = self.read_temp_raw()  # Read the temperature 'device file'
            # Keep re-reading until the first line ends in 'YES'
            # wait for 0.2s between reads - how log could this take?
            while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = self.read_temp_raw()
            # second line should end with "t= <temp>", <temp> in 1000'ths of degree C
            equals_pos = lines[1].find('t=')
            if equals_pos >= 0:  # but what if it isn't there?
                temp_string = lines[1][equals_pos+2:]
                self.value = float(temp_string) / 1000.0
        elif self.getName() == "Pool":
            # Convert the value of the sensor into a temperature
            lines = self.read_temp_raw()  # Read the temperature 'device file'
            # Keep re-reading until the first line ends in 'YES'
            # wait for 0.2s between reads - how log could this take?
            while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = self.read_temp_raw()
            # second line should end with "t= <temp>", <temp> in 1000'ths of degree C
            equals_pos = lines[1].find('t=')
            if equals_pos >= 0:  # but what if it isn't there?
                temp_string = lines[1][equals_pos+2:]
                self.value = float(temp_string) / 1000.0
        elif self.getName() == "Flow":
            # count pulses in fixed period to get a flow rate
            thisTime = datetime.datetime.now()
            countTime = thisTime - self.lastTime
            self.lastTime = thisTime
            clicks = self.count
            self.count = 0  # reset count
            countTime = countTime.total_seconds()
            # each click represents 1.7 * 2.25 ml, so convert to litres per minute
            # 1.7 reflects John's impirical testing
            self.value = ((clicks / countTime) * 60 * 1.7 * 2.25 / 1000)
        elif self.getName() == "Depth":
            # as we are unsure of the acuracy (but I think this is overkill:
            # use multiples of 50 to get acceptible results (in range)
            NUMBER_OF_SAMPLES = 50
            # then narrow the range (+/- 20%), and retry, and do that again (+/- 5%)
            # work in centimeters:
            lowlimit = 5    # no nearer than 5 cm
            hilimit = 100   # no further than 1m
            avedistance = 0.0
            indicate = 0
            for n in range(3):
                valid = 0
                sumread = 0
                if (n == 1):
                    lowlimit = avedistance * 0.8
                    hilimit = avedistance * 1.2
                elif (n == 2):
                    lowlimit = avedistance * .95
                    hilimit = avedistance * 1.05
                print("n =", n, "lowlimit = ", lowlimit, "hilimit = ",
                      hilimit, "avedistance = ", avedistance)
                readings = []
                for n1 in range(NUMBER_OF_SAMPLES):
                    localdistance = self.getRange()
                    readings.append(localdistance)
                    if (localdistance > lowlimit and localdistance < hilimit):
                        sumread += localdistance
                        valid += 1
                        #print ("localdistance = ", localdistance , "n= " , n, "n1 = ", n1, "valid = ", valid)
                    else:
                        print("Invalid range:", localdistance)
                print("Readings:", readings)
                if (valid > 0):
                    avedistance = sumread / valid
                    print("avedist  = ", avedistance, "valid = ", valid)
                else:
                    # this is very bad news!
                    print("zero readings. valid = ", valid)
            self.value = avedistance
        else:
            print("Getting", self.getName(), "as", self.value)
            # i.e. return current value (like to use underlying dummy)
            self.value = self.value
        return self.value

    def getRange(self):
        # should take .011 secs to travel 4 m, so wait .03sec as well outside our expected range
        # make sure sonic is off, and wait 30 ms for echos to fade
        GPIO.output(self.TRIGGER, 0)
        time.sleep(0.03)
        # make a ping
        # set Trigger to HIGH
        GPIO.output(self.TRIGGER, 1)
        # wait 0.01ms and set Trigger to LOW
        time.sleep(0.00001)
        GPIO.output(self.TRIGGER, 0)
        # save StartTime as soon as ping has gone
        while GPIO.input(self.ECHO) == 0:
            pass  # tight loop
            StartTime = time.time()
        # save time of arrival of first echo
        # while GPIO.input(GPIO_ECHO) == 1:
        while GPIO.input(self.ECHO) == 1:
            pass  # tight loop
            StopTime = time.time()
        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        return (TimeElapsed * 34300) / 2

    def countPulse(self, rest):
        # count a puls everytime the pin drops ...
        self.count += 1
        # not sure what this value is or to be used for
        # print("countPulse(rest) has rest =", rest)

    def findDevice(self):
        base_dir = '/sys/bus/w1/devices/'
        folders = glob.glob(base_dir + self.device)
        if len(folders) > 0:
            device_folder = folders[0]  # take first folder returned by glob()
            self.device_file = device_folder + '/w1_slave'
        else:
            self.device_file = None

    # A function that reads the temp sensors data
    # No checking for the file being there!
    def read_temp_raw(self):
        if self.device_file == None:
            self.findDevice()
        if self.device_file == None:
            lines = ['YES', 't=-100000']
        else:
            try:
                # Opens the temperature device file
                f = open(self.device_file, 'r')
                lines = f.readlines()  # Returns the text
                f.close()
            except:
                lines = ['YES', 't=-100000']
        return lines


def main():
    # this is for testing
    ds = RealDataSource("Dummy")
    print("New datasource:", ds.getName())
    print("Current value:", ds.getValue())
    for i in range(10):
        time.sleep(5)
        print("After 5 secs value:", ds.getValue())


# execute only if run as a script
if __name__ == "__main__":
    main()  # execute test code ...
