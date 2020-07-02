#!/usr/bin/env python3

# v0.4a 30/5/20 - Joe Elliott

# This is Alpha Code - writes data to folder /ramdisk in a format to be read by node_exporter, Prometheus/Grafana.
# Modify the serial interface below to match your system setup.

# If you encounter errors like - AttributeError: module 'serial' has no attribute 'Serial'
# pip3 uninstall pyserial
# pip3 uninstall serial
# pip3 uninstall minimalmodbus
# pip3 install pyserial
# pip3 install minimalmodbus

import minimalmodbus
import serial
import sys, os, io
import time

debug = False
# Enter your serial interface below.
renogy = minimalmodbus.Instrument('/dev/usb1', 1) 
renogy.serial.baudrate = 9600
renogy.serial.bytesize = 8
renogy.serial.parity   = serial.PARITY_NONE
renogy.serial.stopbits = 1
renogy.serial.timeout = 2
renogy.debug = debug

BATTERY_TYPE = {
    1: 'open',
    2: 'sealed',
    3: 'gel',
    4: 'lithium',
    5: 'self-customized'
}

CHARGING_STATE = {
    0: 'deactivated',
    1: 'activated',
    2: 'mppt',
    3: 'equalizing',
    4: 'boost',
    5: 'floating',
    6: 'current limiting'
}

if (debug): print(minimalmodbus._get_diagnostic_string())

if (debug):
        # Print the details of the Wanderer here, also include the config needed to talk to the unit.
        print('Details of the serial connection:')
        print("Renogy:", renogy)

def readRenogy(fileObj):
        try:
                if (debug):
                        register = renogy.read_register(0x00A)
                        maxV = register >> 8
                        maxC = register & 0x00ff
                        print("Max sys voltage:", float(maxV), "v")
                        print("Max sys amps:", float(maxC), "a")

                        register = renogy.read_register(0x00B)
                        maxD = register >> 8
                        prodType = register & 0x00ff
                        print("max discharge:", float(maxD), "a")
                        print("sys type:", prodType, "00=controller 1=inverter")

                register = renogy.read_register(0x100)
                print("Battery SOC:", float(register), "%")

                batVolts = renogy.read_register(0x101)
                batVolts = batVolts/10
                if (True): print("Battery Voltage:", float(batVolts), "v")
                valName  = "mode=\"batVolts\""
                valName  = "{" + valName + "}"
                dataStr  = f"Renogy{valName} {batVolts}"
                print(dataStr, file=fileObj)

                register = renogy.read_register(0x102)
                print("Charging Amps:", float(register/100), "a")

                if (False):     # for chargers with remote temp sensors
                        register = renogy.read_register(0x103)
                        battery_temp_bits = register & 0x00ff
                        temp_value = battery_temp_bits & 0x0ff
                        sign = battery_temp_bits >> 7
                        battery_temp = -(temp_value - 128) if sign == 1 else temp_value
                        print("battery temp:", float(battery_temp), "C")

                register = renogy.read_register(0x103)
                controller_temp_bits = register >> 8
                temp_value = controller_temp_bits & 0x0ff
                sign = controller_temp_bits >> 7
                devTemp = -(temp_value - 128) if sign == 1 else temp_value
                print("controller temp:", float(devTemp), "C")

                loadWatts = renogy.read_register(0x106)
                if (True): print("Load watts:", loadWatts, "w")
                valName  = "mode=\"loadWatts\""
                valName  = "{" + valName + "}"
                dataStr  = f"Renogy{valName} {loadWatts}"
                print(dataStr, file=fileObj)

                register = renogy.read_register(0x107)
                print("PV volts:", float(register/10), "v")

                register = renogy.read_register(0x108)
                print("PV amps:", float(register/100), "a")

                pvWatts = renogy.read_register(0x109)
                if (True): print("PV watts:", pvWatts, "w")
                valName  = "mode=\"pvWatts\""
                valName  = "{" + valName + "}"
                dataStr  = f"Renogy{valName} {pvWatts}"
                print(dataStr, file=fileObj)

                register = renogy.read_register(0x10B)
                print("bat max volts:", float(register)/10, "v")

                register = renogy.read_register(0x10C)
                print("bat min volts:", float(register)/10, "v")

                register = renogy.read_register(0x10F)
                print("todays charge power:", float(register)/1, "w")

                register = renogy.read_register(0x110)
                print("todays discharge power:", float(register)/1, "w")

                register = renogy.read_register(0x120)
                chargeStateNum = register & 0x00ff
                chargeStateStr = CHARGING_STATE.get(chargeStateNum)
                print("Charge state:", chargeStateNum, chargeStateStr)
                valName  = "mode=\"chargeState\""
                valName  = "{" + valName + ", myStr=\"" + chargeStateStr + "\"}"
                dataStr  = f"Renogy{valName} {chargeStateNum}"
                print(dataStr, file=fileObj)


                register = renogy.read_register(0xE004)
                print("Bat Type:", BATTERY_TYPE.get(register), "")

                return # Code below was for testing on other versions

                register = renogy.read_register(0x113)
                print("todays gen power:", float(register)/10000, "kw/h")

                register = renogy.read_register(0x114)
                print("todays consumed power:", float(register)/10000, "kw/h")

                register = renogy.read_register(0x115)
                print("up days:", register, "days")

                register = renogy.read_register(0x117)
                print("battery full cnt:", register, "#")

                register = renogy.read_register(0xE003)
                sysV = register >> 8
                recV = register & 0x00ff
                print("Sys bat voltage:", sysV, "v FF(255)==Auto")
                print("Recon bat voltage:", recV, "v")

                register = renogy.read_register(0xE002)
                print("Bat capacity:", register, "ah")

                register = renogy.read_register(0xE005)
                print("over voltage:", float(register/10), "v")

                register = renogy.read_register(0xE006)
                print("charge voltage:", float(register/10), "v")

                register = renogy.read_register(0xE007)
                print("equalize voltage:", float(register/10), "v")

                register = renogy.read_register(0xE008)
                print("boost voltage:", float(register/10), "v")

                register = renogy.read_register(0xE009)
                print("float voltage:", float(register/10), "v")

                register = renogy.read_register(0xE00A)
                print("boost recovery voltage:", float(register/10), "v")

                register = renogy.read_register(0xE00B)
                print("over discharge recovery voltage:", float(register/10), "v")

                register = renogy.read_register(0xE00C)
                print("under voltage warn:", float(register/10), "v")

                register = renogy.read_register(0xE00D)
                print("over discharge:", float(register/10), "v")

                register = renogy.read_register(0xE00E)
                print("discharge warn voltage:", float(register/10), "v")

                register = renogy.read_register(0xE012)
                print("Boost time:", register, "mins")

        except IOError:
                print("Failed to read from instrument")

# Run the function to read the power meter.

while True:
        if (debug): print("Opened new tmp file /ramdisk/Renogy.prom.tmp")
        file_object = open('/ramdisk/Renogy.prom.tmp', mode='w')

        # write data here

        if (True): print("\nReading Renogy Wanderer data...")
        readRenogy(file_object)

        file_object.flush()
        file_object.close()
        outLine = os.system('/bin/mv /ramdisk/Renogy.prom.tmp /ramdisk/Renogy.prom')

        time.sleep(10)
