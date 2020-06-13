#!/usr/bin/env python3

# you may need to install this
# pip install -U minimalmodbus

# this script assumes you have 2 modbus serial connections
# to morninggroup AC data collectors.
# data is written in prometheus compatible format in /ramdisk 

import minimalmodbus
import serial, time, sys, os

debug=False

totalWatts = 0

thisWatts = 0
thisVolts = 0
thisAmps = 0
thisEnergy = 0
thisFreq = 0
thisPF = 0

voltsA  = 0
voltsB  = 0
ampsA   = 0
ampsB   = 0
wattsA  = 0
wattsB  = 0
energyA = 0
energyB = 0
pfA     = 0
pfB     = 0
freqA   = 0
freqB   = 0

totalWatts = 0

if (len(sys.argv) > 1):
        if (sys.argv[1] == "-d"):
                debug=True
                print("sys.argv[0]: Debug: enabled")


def readPowerMeter(dev):
    global totalWatts, thisWatts, thisVolts, thisAmps, thisEnergy, thisFreq, thisPF

    powerMeter = minimalmodbus.Instrument(dev, 1) 
    powerMeter.serial.baudrate = 9600
    powerMeter.serial.bytesize = 8
    powerMeter.serial.parity   = serial.PARITY_NONE
    powerMeter.serial.stopbits = 1
    powerMeter.serial.timeout = 1
    powerMeter.mode = minimalmodbus.MODE_RTU

    if (debug): print("Attempting to read power meter device:", dev, powerMeter)
    try:
        voltageReading = powerMeter.read_register(0, 0, 4)
        ampsReading = powerMeter.read_register(1, 0, 4)
        wattsReading = powerMeter.read_register(3, 0, 4)
        energyReading = powerMeter.read_register(5, 0, 4)
        frequencyReading = powerMeter.read_register(7, 0, 4)
        powerFactor = float(powerMeter.read_register(8, 0, 4))
        alarmStatus = powerMeter.read_register(9, 0, 4)

        if (debug):
            print("Voltage:", voltageReading/10, " v")
            print("Amps:", ampsReading/1000, " a")
            print("Watts:", wattsReading/10, " w")
            print("Energy:", energyReading/10, " w/h")
            print("Frequency:", frequencyReading/10, " hz")
            print("PowerFactor:", powerFactor/100, " pf")
            print("AlarmStatus:", alarmStatus, " 0=off")

        thisVolts    = voltageReading/10
        thisAmps     = ampsReading/1000
        thisWatts    = wattsReading/10
        thisEnergy   = energyReading/10
        thisFreq     = frequencyReading/10
        thisPF       = powerFactor/100
        totalWatts  += wattsReading/10

    except IOError:
        print("Failed to read from powerMeter:", dev)

while(True):
    cmdStr = ""

    # Run the function to read the power meter.
    if (debug): print("# Phase A")
    readPowerMeter("/dev/ttyUSB0")

    voltsA = thisVolts
    ampsA = thisAmps
    wattsA = thisWatts
    energyA = thisEnergy
    freqA = thisFreq
    pfA = thisPF

    if (debug): print("# Phase B")
    readPowerMeter("/dev/ttyUSB1")

    voltsB = thisVolts
    ampsB = thisAmps
    wattsB = thisWatts
    energyB = thisEnergy
    freqB = thisFreq
    pfB = thisPF

    if (debug): print("# wattsA:", wattsA, "wattsB:", "Total Consumption:", totalWatts, "w")

################## Volts ####################
    voltStr = "{:4.2f}".format(voltsA)
    voltName = '{mode=\"voltsA\"}'
    dataVoltStrA = f"QC_power{voltName} {voltStr}"

    voltStr = "{:4.2f}".format(voltsB)
    voltName = '{mode=\"voltsB\"}'
    dataVoltStrB = f"QC_power{voltName} {voltStr}"
################## Amps ####################
    ampsStr = "{:4.2f}".format(ampsA)
    ampsName = '{mode=\"ampsA\"}'
    dataAmpsStrA = f"QC_power{ampsName} {ampsStr}"

    ampsStr = "{:4.2f}".format(ampsB)
    ampsName = '{mode=\"ampsB\"}'
    dataAmpsStrB = f"QC_power{ampsName} {ampsStr}"
################## Watts ####################
    valStr = "{:4.2f}".format(wattsA)
    valName = '{mode=\"wattsA\"}'
    dataStrA = f"QC_power{valName} {valStr}"

    valStr = "{:4.2f}".format(wattsB)
    valName = '{mode=\"wattsB\"}'
    dataStrB = f"QC_power{valName} {valStr}"
################## Energy ####################
    energyStr = "{:4.2f}".format(energyA)
    energyName = '{mode=\"energyA\"}'
    dataEnergyStrA = f"QC_power{energyName} {energyStr}"

    energyStr = "{:4.2f}".format(energyB)
    energyName = '{mode=\"energyB\"}'
    dataEnergyStrB = f"QC_power{energyName} {energyStr}"
################## PF ####################
    pfStr = "{:4.2f}".format(pfA)
    pfName = '{mode=\"pfA\"}'
    dataPFStrA = f"QC_power{pfName} {pfStr}"

    pfStr = "{:4.2f}".format(pfB)
    pfName = '{mode=\"pfB\"}'
    dataPFStrB = f"QC_power{pfName} {pfStr}"
################## Freq ####################
    freqStr = "{:4.2f}".format(freqA)
    freqName = '{mode=\"freqA\"}'
    dataFreqStrA = f"QC_power{freqName} {freqStr}"

    freqStr = "{:4.2f}".format(freqB)
    freqName = '{mode=\"freqB\"}'
    dataFreqStrB = f"QC_power{freqName} {freqStr}"
################## Total Watts ####################
    valStr = "{:4.2f}".format(totalWatts)
    valName = '{mode=\"totalWatts\"}'
    dataStrC = f"QC_power{valName} {valStr}"
    if (debug): print("cmdStr:", cmdStr)

    with open('/ramdisk/QC_Watts.prom', mode='w') as file_object:
        print(dataStrA,       file=file_object)
        print(dataStrB,       file=file_object)
        print(dataStrC,       file=file_object)
        print(dataVoltStrA,   file=file_object)
        print(dataVoltStrB,   file=file_object)
        print(dataAmpsStrA,   file=file_object)
        print(dataAmpsStrB,   file=file_object)
        print(dataEnergyStrA, file=file_object)
        print(dataEnergyStrB, file=file_object)
        print(dataPFStrA,     file=file_object)
        print(dataPFStrB,     file=file_object)
        print(dataFreqStrA,   file=file_object)
        print(dataFreqStrB,   file=file_object)
 
    totalWatts = 0

    time.sleep(2)

# End.
