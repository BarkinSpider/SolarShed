#!/usr/bin/python
#
#### Python 2 code - dont use Python 3! #######
##### I will update this to Python 3 shortly ########
#
# Description: Read tracer series RS485 serial output on Pi4/Zero USB/serial port and write
# the data to a STDOUT. Redirect this to file with
# ./getTracerData.py > /ramdisk/solarData.txt
#
# Ensure the xr_usb_serial_common kernel module has been loaded before running this script.
# this script will attempt to load the module for you if it located in the following folder
# /home/solar/xr_usb_serial_common-1a/xr_usb_serial_common.ko
#
# Dec 2019 - J. Elliott v0.4b
#
# to be implemented later ---
#    //manually turn on
#    public function setLoadOn() {
#        $this->tracer->sendRawQuery("\x01\x05\x00\x02\xff\x00\x2d\xfa", false);
#    }
#
#    //manually turn off 
#    public function setLoadOff() {
#        $this->tracer->sendRawQuery("\x01\x05\x00\x02\x00\x00\x6c\x0a", false);
#    }
#
import os
import sys
import time
import serial
import ctypes
#
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.mei_message import *      # ReadDeviceInformationRequest()
from pyepsolartracer.registers import registers,coils
#
DEBUG=0

c_uint8 = ctypes.c_uint8

class Flags_bits( ctypes.LittleEndianStructure ):
    _fields_ = [
                ("runningOk",     c_uint8, 1),  # asByte & 1
                ("fault",         c_uint8, 1),  # asByte & 2
                ("chargeStatus",  c_uint8, 2),  # asByte & 4
                ("pvError",       c_uint8, 1),  # asByte & 5
               ]

class Flags( ctypes.Union ):
    _anonymous_ = ("bit",)
    _fields_    = [
                    ("bit",    Flags_bits ),
                    ("asByte", c_uint8    )
                  ]
flags = Flags()

# configure the client logging
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO) # DEBUG or INFO

client = ModbusClient(  method = 'rtu',
                        port = '/dev/ttyXRUSB0',
                        baudrate = 115200,
                        stopbits = serial.STOPBITS_ONE,
                        parity=serial.PARITY_NONE,
                        bytesize = 8,
                        timeout=2)

connection = client.connect()
if (connection == 1):
        if (DEBUG): print("connection: {}").format(connection)
else:
        print("connection: trying insmod")
        cmd = "/sbin/insmod /home/solar/xr_usb_serial_common-1a/xr_usb_serial_common.ko"

        returned_value = os.system(cmd)  # returns the exit code in unix
        print('returned value:', returned_value)
        if (returned_value == 0):       #all ok
                print('insmod installed USB driver ok')
        else:
                print('insmod installing USB driver failed. XXXX')
                sys.exit()

request = ReadDeviceInformationRequest(unit=1)
response = client.execute(request)
# print "Response:"
print(repr(response.information)) + "\n"

####################################

result = client.read_input_registers(0x3100, 8, unit=1)
#print "Result 0x3100:", result
if (result.registers):

        pvVoltage               = float(result.registers[0] / 100.0)
        pvCurrent               = float(result.registers[1] / 100.0)
        pvPowerL                = float(result.registers[2] / 100.0)
        pvPowerH                = float(result.registers[3])
        batteryChargeV          = float(result.registers[4] / 100.0)
        batteryChargeC          = float(result.registers[5] / 100.0)
        batteryChargePowerL     = float(result.registers[6] / 100.0)
        batteryChargePowerH     = float(result.registers[7])

        if (pvPowerH != 0):
                pvPowerL += 640
        if (batteryChargePowerH != 0):
                batteryChargePowerL += 640

        print("0x3100: pvVoltage:{}v").format(pvVoltage)
        print("0x3101: pvCurrent:{}a").format(pvCurrent)
        print("0x3102: pvPowerL:{}w").format(pvPowerL)
        #print "0x3103: pvPowerH:",             pvPowerH,       "v"
        print("0x3104: batteryChargeV:{}v").format(batteryChargeV)
        print("0x3105: batteryChargeC:{}a").format(batteryChargeC)
        print("0x3106: batteryChargePowerL:{}w").format(batteryChargePowerL)
        #print "0x3107: batteryChargePowerH:",  batteryChargePowerH, "v"

else:
        print("No data for 0x3100!")

####################################

result = client.read_input_registers(0x310C, 7, unit=1)
#print "Result 0x310C:", result
if (result.registers):
        loadVoltage             = float(result.registers[0]) / 100.0
        loadCurrent             = float(result.registers[1]) / 100.0
        loadPowerL              = float(result.registers[2]) / 100.0
        loadPowerH              = float(result.registers[3]) / 100.0
        batteryTemp             = float(result.registers[4]) / 100.0
        deviceTemp              = float(result.registers[5]) / 100.0
        compTemp                = float(result.registers[6]) / 100.0

        if (loadPowerH != 0):
                loadPowerL += 640

        print("0x310C: loadVoltage:{}v").format(loadVoltage)
        print("0x310D: loadCurrent:{}a").format(loadCurrent)
        print("0x310E: loadPowerL:{}w").format(loadPowerL)
        #print "0x310F: loadPowerH:",           loadPowerH,     "w"
        print("0x3110: batteryTemp:{}c {}f").format(batteryTemp, ((1.8*batteryTemp)+32))
        print("0x3111: deviceTemp:{}c {}f").format(deviceTemp, ((1.8*deviceTemp)+32))
        #print "0x3112: compTemp:",             compTemp  ,     "v"
else:
        print("No data for 0x3100!")

result = client.read_input_registers(0x311A, 2, unit=1)
#print "Result 0x311A:", result
if (result.registers):
        batSOC                  = float(result.registers[0])
        remoteBatTemp           = result.registers[1]

        print("0x311A: Battery S.O.C:{}%").format(batSOC)
        #print "0x311B: remoteBatTemp:",        remoteBatTemp, "c"
else:
        print("No data for 0x311A!")

####################################

result = client.read_input_registers(0x3300, 31, unit=1)

if (result.registers):
        pvMaxInVolts            = result.registers[0]
        pvMinInVolts            = result.registers[1]
        batMaxVolts             = result.registers[2]
        batMinVolts             = result.registers[3]
        consumedEnergyTodayL    = result.registers[4]
        consumedEnergyTodayH    = result.registers[5]
        genEnergyTodayL         = result.registers[12]
        genEnergyTodayH         = result.registers[13]

        if (consumedEnergyTodayH != 0):
                consumedEnergyTodayH += 640
        if (genEnergyTodayH != 0):
                genEnergyTodayL += 640

        print("0x3300: pvMaxInVolts:{}v").format(float(pvMaxInVolts) / 100)
        print("0x3301: pvMinInVolts:{}v").format(float(pvMinInVolts) / 100)
        print("0x3302: batMaxVolts:{}v").format(float(batMaxVolts) / 100)
        print("0x3303: batMinVolts:{}v").format(float(batMinVolts) / 100)
        print("0x3304: consumedEnergyTodayL:{}w/h").format(consumedEnergyTodayL * 10)
        #print "0x3305: consumedEnergyTodayH:", consumedEnergyTodayH,           "w"
        print("0x330C: genEnergyTodayL:{}w/h").format(genEnergyTodayL * 10)
        #print "0x330D: genEnergyTodayH:",      genEnergyTodayH,                "w"
else:
        print("No data for 0x3200!")

####################################

result = client.read_input_registers(0x3200, 2, unit=1)

if (result.registers):
        batteryStatus           = result.registers[0]
        equipStatus             = result.registers[1]

# Battery status bit pattern 0x3200
# D3-D0: 01H Overvolt , 00H Normal , 02H Under Volt, 03H Low Volt Disconnect, 04H Fault
# D7-D4: 00H Normal, 01H Over Temp.(Higher than the warning settings), 02H Low Temp.( Lower than the warning settings),
# D8: Battery inerternal resistance abnormal 1, normal 0
# D15: 1-Wrong identification for rated voltage
#
# Inverter status bit pattern 0x3201
# D15-D14: Input volt status. 00 normal, 01 no power connected, 02H Higher volt input, 03H Input volt error.
# D13: Charging MOSFET is short.
# D12: Charging or Anti-reverse MOSFET is short.
# D11: Anti-reverse MOSFET is short.
# D10: Input is over current.
# D9: The load is Over current.
# D8: The load is short.
# D7: Load MOSFET is short.
# D4: PV Input is short.
# D3-2: Charging status. 00 NoCharging, 01 Float, 10 Boost(Bulk), 11 Equalization.
# D1: 0 Normal, 1 Fault.
# D0: 1 Running, 0 Standby.


        print("0x3200: batteryStatus:{}bits").format(format(batteryStatus, 'b').zfill(16))
        print("0x3201: equipStatus:{}bits").format(format(equipStatus, 'b').zfill(16))

        flags.asByte = equipStatus

        if (flags.bit.chargeStatus == 0):
                chargeStatusStr = "Standby"
        elif (flags.bit.chargeStatus == 1):
                chargeStatusStr = "Float"
        elif (flags.bit.chargeStatus == 2):
                chargeStatusStr = "Bulk"
        elif (flags.bit.chargeStatus == 3):
                chargeStatusStr = "Equalize"
        else:
                chargeStatusStr = "Error"

        print("runningOk: %i"    % flags.bit.runningOk)
        print("fault: %i"        % flags.bit.fault)
        print("chargeStatus: %i" % flags.bit.chargeStatus, chargeStatusStr)
        print("pvError: %i"      % flags.bit.pvError)

else:
        print("No data for 0x3200!")

###################################################################

result = client.read_holding_registers(0x9000, 15, unit=1)

if (result.registers):
        batType         = result.registers[0]
        batCap          = result.registers[1]
        batComp         = result.registers[2]
        hiVDiscon       = result.registers[3]
        chargeLimitV    = result.registers[4]
        overVRecon      = result.registers[5]
        eqVolts         = result.registers[6]
        boostV          = result.registers[7]
        floatV          = result.registers[8]
        boostReconV     = result.registers[9]
        loVRecon        = result.registers[10]
        underVRecover   = result.registers[11]
        underVWarn      = result.registers[12]
        loVDiscon       = result.registers[13]
        dischargeLimitV = result.registers[14]

        print("0x9000: batType:{}").format(batType)
        print("0x9001: batCap:{}ah").format(batCap)
        print("0x9002: batComp:{}").format(batComp)
        print("0x9003: hiVDiscon:{}v").format(float(hiVDiscon) / 100)
        print("0x9004: chargeLimitV:{}v").format(float(chargeLimitV) / 100)
        print("0x9005: overVRecon:{}v").format(float(overVRecon) / 100)
        print("0x9006: eqVolts:{}v").format(float(eqVolts) / 100)
        print("0x9007: boostV:{}v").format(float(boostV) / 100)
        print("0x9008: floatV:{}v").format(float(floatV) / 100)
        print("0x9009: boostReconV:{}v").format(float(boostReconV) / 100)
        print("0x900A: loVRecon:{}v").format(float(loVRecon) / 100)
        print("0x900B: underVRecover:{}v").format(float(underVRecover) / 100)
        print("0x900C: underVWarn:{}v").format(float(underVWarn) / 100)
        print("0x90OD: loVDiscon:{}v").format(float(loVDiscon) / 100)
        print("0x900E: dischargeLimitV:{}v").format(float(dischargeLimitV) / 100)
else:
        print("No data for 0x9000!")

###################################################################

result = client.read_input_registers(0x331B, 2, unit=1)

if (result.registers):
        batteryCurrentL         = result.registers[0]
        batteryCurrentH         = result.registers[1]

        if (batteryCurrentH != 0):
                batteryCurrentL += 640

        if (batteryCurrentH):
                print("\nBattery is Discharging at %s Watts" % loadPowerL)
        else:
                print("\nBattery is Charging in %s mode at %s Watts" % (chargeStatusStr, batteryChargePowerL))

else:
        print("No data for 0x331B!")

###################################################################

client.close()
sys.exit()
#
# End
