#!/usr/bin/env python3

# v0.4e 3/1/21 - Joe Elliott

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
sleepTime = 10
devName = '/dev/ttyUSB0'

if (len(sys.argv) > 1):
        if (sys.argv[1] == "-d"):
                debug=True
                sleepTime = 2
                print("sys.argv[0]: Debug: enabled")

renogy = minimalmodbus.Instrument(devName, 1)
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
        # Print the details of the power meter here, also include the config needed to talk to the unit.
        print('Details of the serial connection:')
        print("Renogy:", renogy)

def readRenogy(fileObj):
        try:
                if (debug):
                        register = renogy.read_register(0x00A)
                        maxV = register >> 8
                        maxC = register & 0x00ff
                        if (debug): print("Max sys voltage:", float(maxV), "v")
                        if (debug): print("Max sys amps:", float(maxC), "a")

                        register = renogy.read_register(0x00B)
                        maxD = register >> 8
                        prodType = register & 0x00ff
                        if (debug): print("max discharge:", float(maxD), "a")
                        if (debug): print("sys type:", prodType, "00=controller 1=inverter")

                register = renogy.read_register(0x100)
                if (debug): print("Battery SOC:", float(register), "%")
                valName  = "mode=\"SOC\""
                valName  = "{" + valName + "}"
                dataStr  = f"Renogy{valName} {float(register)}"
                print(dataStr, file=fileObj)

                batVolts = renogy.read_register(0x101)
                batVolts = batVolts/10
                if (debug): print("Battery Voltage:", float(batVolts), "v")
                valName  = "mode=\"batVolts\""
                valName  = "{" + valName + "}"
                dataStr  = f"Renogy{valName} {batVolts}"
                print(dataStr, file=fileObj)

                register = renogy.read_register(0x102)
                if (debug): print("Charging Amps:", float(register/100), "a")

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
                if (debug): print("controller temp:", float(devTemp), "C")
                valName  = "mode=\"sccTemp\""
                valName  = "{" + valName + "}"
                dataStr  = f"Renogy{valName} {float(devTemp)}"
                print(dataStr, file=fileObj)

                loadWatts = renogy.read_register(0x106)
                if (debug): print("Load watts:", loadWatts, "w")
                valName  = "mode=\"loadWatts\""
                valName  = "{" + valName + "}"
                dataStr  = f"Renogy{valName} {loadWatts}"
                print(dataStr, file=fileObj)

                register = renogy.read_register(0x107)
                if (debug): print("PV volts:", float(register/10), "v")
                valName  = "mode=\"pvVolts\""
                valName  = "{" + valName + "}"
                dataStr  = f"Renogy{valName} {float(register/10)}"
                print(dataStr, file=fileObj)

                register = renogy.read_register(0x108)
                if (debug): print("PV amps:", float(register/100), "a")
                valName  = "mode=\"pvAmps\""
                valName  = "{" + valName + "}"
                dataStr  = f"Renogy{valName} {float(register/100)}"
                print(dataStr, file=fileObj)

                pvWatts = renogy.read_register(0x109)
                if (debug): print("PV watts:", pvWatts, "w")
                valName  = "mode=\"pvWatts\""
                valName  = "{" + valName + "}"
                dataStr  = f"Renogy{valName} {pvWatts}"
                print(dataStr, file=fileObj)

                register = renogy.read_register(0x10B)
                if (debug): print("bat max volts:", float(register)/10, "v")
                valName  = "mode=\"maxBatV\""
                valName  = "{" + valName + "}"
                dataStr  = f"Renogy{valName} {float(register/10)}"
                print(dataStr, file=fileObj)

                register = renogy.read_register(0x10C)
                if (debug): print("bat min volts:", float(register)/10, "v")
                valName  = "mode=\"minBatV\""
                valName  = "{" + valName + "}"
                dataStr  = f"Renogy{valName} {float(register/10)}"
                print(dataStr, file=fileObj)

                register = renogy.read_register(0x10F)
                if (debug): print("todays charge power:", float(register)/1, "w")
                valName  = "mode=\"todayChgPwr\""
                valName  = "{" + valName + "}"
                dataStr  = f"Renogy{valName} {float(register/1)}"
                print(dataStr, file=fileObj)

                register = renogy.read_register(0x110)
                if (debug): print("todays discharge power:", float(register)/1, "w")
                valName  = "mode=\"todayDischgPwr\""
                valName  = "{" + valName + "}"
                dataStr  = f"Renogy{valName} {float(register/1)}"
                print(dataStr, file=fileObj)

                register = renogy.read_register(0x120)
                chargeStateNum = register & 0x00ff
                chargeStateStr = CHARGING_STATE.get(chargeStateNum)
                if (debug): print("Charge state:", chargeStateNum, chargeStateStr)
                valName  = "mode=\"chargeState\""
                valName  = "{" + valName + ", myStr=\"" + chargeStateStr + "\"}"
                dataStr  = f"Renogy{valName} {chargeStateNum}"
                print(dataStr, file=fileObj)


                register = renogy.read_register(0xE004)
                batTypeStr = BATTERY_TYPE.get(register)
                if (debug): print("Bat Type:", batTypeStr)
                valName  = "mode=\"batType\""
                valName  = "{" + valName + ", myStr=\"" + batTypeStr + "\"}"
                dataStr  = f"Renogy{valName} {register}"
                print(dataStr, file=fileObj)


                register = renogy.read_register(0x113)
                if (debug): print("todays gen power:", float(register)/10, "w/h")
                valName  = "mode=\"todayGenPwr\""
                valName  = "{" + valName + "}"
                dataStr  = f"Renogy{valName} {float(register/10)}"
                print(dataStr, file=fileObj)

                register = renogy.read_register(0x114)
                if (debug): print("todays consumed power:", float(register)/10, "w/h")
                valName  = "mode=\"todayConsumPwr\""
                valName  = "{" + valName + "}"
                dataStr  = f"Renogy{valName} {float(register/10)}"
                print(dataStr, file=fileObj)

                register = renogy.read_register(0x115)
                if (debug): print("up days:", register, "days")
                valName  = "mode=\"upDays\""
                valName  = "{" + valName + "}"
                dataStr  = f"Renogy{valName} {register}"
                print(dataStr, file=fileObj)

                register = renogy.read_register(0x117)
                if (debug): print("battery full cnt:", register, "#")
                valName  = "mode=\"batFullCnt\""
                valName  = "{" + valName + "}"
                dataStr  = f"Renogy{valName} {register}"
                print(dataStr, file=fileObj)

                return

                register = renogy.read_register(0xE003)
                sysV = register >> 8
                recV = register & 0x00ff
                if (debug): print("Sys bat voltage:", sysV, "v FF(255)==Auto")
                if (debug): print("Recon bat voltage:", recV, "v")

                register = renogy.read_register(0xE002)
                if (debug): print("Bat capacity:", register, "ah")

                register = renogy.read_register(0xE005)
                if (debug): print("over voltage:", float(register/10), "v")

                register = renogy.read_register(0xE006)
                if (debug): print("charge voltage:", float(register/10), "v")

                register = renogy.read_register(0xE007)
                if (debug): print("equalize voltage:", float(register/10), "v")

                register = renogy.read_register(0xE008)
                if (debug): print("boost voltage:", float(register/10), "v")

                register = renogy.read_register(0xE009)
                if (debug): print("float voltage:", float(register/10), "v")

                register = renogy.read_register(0xE00A)
                if (debug): print("boost recovery voltage:", float(register/10), "v")

                register = renogy.read_register(0xE00B)
                if (debug): print("over discharge recovery voltage:", float(register/10), "v")

                register = renogy.read_register(0xE00C)
                if (debug): print("under voltage warn:", float(register/10), "v")

                register = renogy.read_register(0xE00D)
                if (debug): print("over discharge:", float(register/10), "v")

                register = renogy.read_register(0xE00E)
                if (debug): print("discharge warn voltage:", float(register/10), "v")

                register = renogy.read_register(0xE012)
                if (debug): print("Boost time:", register, "mins")

        except IOError:
                print("Failed to read from instrument")

# Run the function to read the power meter.

while True:
        if (debug): print("Opened new tmp file /ramdisk/Renogy.prom.tmp")
        file_object = open('/ramdisk/Renogy.prom.tmp', mode='w')

        # write data here

        if (debug): print("\nReading Renogy Wanderer data...")
        readRenogy(file_object)

        file_object.flush()
        file_object.close()
        outLine = os.system('/bin/mv /ramdisk/Renogy.prom.tmp /ramdisk/Renogy.prom')

        time.sleep(sleepTime)
        
