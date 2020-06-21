#!/usr/bin/env python3

# getChargeryData.py
# Description: open RS232 serial port and read Chargery BMS data.
# Output data in a format to be consumed by nodeexporter/prometheus/grafana
# in folder /ramdisk
# v0.4b 5-16-20 Joe Elliott joe@inetd.com
# Protocol at http://chargery.com/uploadFiles/bms24_additional_protocol%20V1.22.pdf

import serial
import sys, os, io
import time
import binascii

devName='/dev/ttyUSB0'

modeList= ["Discharge", "Charge", "Storage"]
gotCellData = False;
gotSysData  = False; 
debug=False

if (len(sys.argv) > 1):
        if (sys.argv[1] == "-d"):
                debug=True
                print("sys.argv[0]: Debug: enabled")

def bin2hex(str1):
        bytes_str = bytes(str1)
        return binascii.hexlify(bytes_str)

def get_voltage_value(byte1, byte2):
        return float((float(byte1 * 256) + float(byte2)) / 1000)

def get_current_value(byte1, byte2):
        return float((float(byte1 * 256) + float(byte2)) / 10)

def get_temp_value(byte1, byte2):
        return float((float(byte1 * 256) + float(byte2)) / 10)

def getCellData(fileObj, hexLine, strLen):
        decStrLen = len(hexLine)
        minLen = 44     # minimal bytes for the 8s inc header (each byte is 2 chars)
        dataStart = 8   # cell voltage data starts at byte 9 in 2 byte chunks (hi-lo)
        cellNum = 1
        aggVolts = 0    # total voltage of the battery
        global gotCellData

        if (debug): print("getCellData: called - ", hexLine)

        if (debug):
                header  = hexLine[0:4]          # header
                command = hexLine[4:6]          # command
                dataLen = hexLine[6:8]          # data length
                print("header:", header)
                print("command:", command)
                print("dataLen:", int(dataLen, 16), "bytes")

        if (decStrLen < strLen) or (decStrLen < minLen):
                if (debug): print("Truncated cell block - len:", len(hexLine), "Expected:", strLen)
                return(True)
        else:
                if (debug): print("hexLine len", len(hexLine))

        for cell in range(dataStart, dataStart + 32, 4):
                cellVolts = get_voltage_value(int(hexLine[cell:cell+2], 16), int(hexLine[cell+2:cell+4], 16))
                if (debug): print("Cell ", cellNum, ":", cellVolts, "v")
                # format the data for node_exporter to read into prometheus
                #valName  = "mode={}{}".format("CellNum", cellNum)
                valName  = "mode=\"CellNum" + str(cellNum) + "\""
                valName = "{" + valName + "}"
                dataStr  = f"BMS_A{valName} {cellVolts}"
                print(dataStr, file=fileObj)

                aggVolts += cellVolts
                cellNum += 1

        soc = int(hexLine[cell], 16)

        valName  = "mode=\"SOC2\""
        valName = "{" + valName + "}"
        dataStr  = f"BMS_A{valName} {soc}"
        print(dataStr, file=fileObj)

        aggVolts = "{:4.2f}".format(aggVolts)
        valName  = "mode=\"aggVolts\""
        valName  = "{" + valName + "}"
        dataStr  = f"BMS_A{valName} {aggVolts}"
        print(dataStr, file=fileObj)

        if (debug):
                print("Battery SOC:", soc, "%")
                print("Checksum:", int(hexLine[cell+1], 16))
                print("Battery voltage:", aggVolts, "v")

        gotCellData = True;
        return(False)

def getSysData(fileObj, hexLine, strLen):
        decStrLen = len(hexLine)
        dataStart = 8   # data starts at byte 8 in 2 byte chunks (hi-lo)        minLen = 30     # minimal bytes inc header (each byte is 2 chars)
        global gotSysData

        if (debug): print("getSysData: called - ", hexLine)

        if (decStrLen < strLen) or (decStrLen < minLen):
                if (debug): print("Truncated system block - len:", len(hexLine), "Expected:", strLen)
                return(True)
        else:
                if (debug): print("hexLine len", len(hexLine))

        # first 3 fields for debug only)
        header     = hexLine[0:4]       # header
        command    = hexLine[4:6]       # command
        dataLen    = hexLine[6:8]       # data length

        endVolt_hi = hexLine[8:10]      # End voltage of cell
        endVolt_lo = hexLine[10:12]     # End voltage of cell
        mode       = hexLine[12:14]     # Current mode
        amps_hi    = hexLine[14:16]     # Current amps
        amps_lo    = hexLine[16:18]     # Current amps
        temp1_hi   = hexLine[18:20]     # Temp 1
        temp1_lo   = hexLine[20:22]     # Temp 1
        temp2_hi   = hexLine[22:24]     # Temp 2
        temp2_lo   = hexLine[24:26]     # Temp 2
        soc        = hexLine[26:28]     # SOC
        chksum     = hexLine[28:30]     # Checksum

        maxVolts = get_voltage_value(int(endVolt_hi, 16), int(endVolt_lo, 16))
        currentFlow = get_current_value(int(amps_hi, 16), int(amps_lo, 16))
        modeName = modeList[int(mode, 16)]
        modeInt = int(mode, 16)
        temp1 = get_temp_value(int(temp1_hi, 16), int(temp1_lo, 16))
        temp2 = get_temp_value(int(temp2_hi, 16), int(temp2_lo, 16))
        socInt = int(soc, 16)

        if (debug):
                print("dataLen:", int(dataLen, 16), "bytes")
                print("End voltage of cell:",  maxVolts, "v")
                print("mode:", modeInt, modeName)
                print("Temp 1:", temp1, "c")
                print("Temp 2:", temp2, "c")
                print("SOC:", socInt, "%")
                print("Checksum:", int(chksum, 16))

        #aggVolts = "{:4.2f}".format(aggVolts)

        #print("mode:", mode)
        if (int(mode) == 0):
                currentFlow = currentFlow * -1 # flow is in or out of the battery?
                #print("currentFlow:", currentFlow)

        valName  = "mode=\"current\""
        valName  = "{" + valName + "}"
        dataStr  = f"BMS_A{valName} {currentFlow}"
        print(dataStr, file=fileObj)

        valName  = "mode=\"maxVolts\""
        valName  = "{" + valName + "}"
        dataStr  = f"BMS_A{valName} {maxVolts}"
        print(dataStr, file=fileObj)

        valName  = "mode=\"modeInt\", myStr=\""
        valName  = valName + modeName + "\""
        valName  = "{" + valName + "}"
        dataStr  = f"BMS_A{valName} {modeInt}"
        print(dataStr, file=fileObj)

        valName  = "mode=\"temp1\""
        valName  = "{" + valName + "}"
        dataStr  = f"BMS_A{valName} {temp1}"
        print(dataStr, file=fileObj)

        valName  = "mode=\"temp2\""
        valName  = "{" + valName + "}"
        dataStr  = f"BMS_A{valName} {temp2}"
        print(dataStr, file=fileObj)

        valName  = "mode=\"SOC\""
        valName  = "{" + valName + "}"
        dataStr  = f"BMS_A{valName} {socInt}"
        print(dataStr, file=fileObj)

        if (debug):
                print("header:", header)
                print("command:", command)
                print("dataLen:", int(dataLen, 16), "bytes")
                print("End voltage of cell_hi:", int(endVolt_hi, 16), "v")
                print("End voltage of cell_lo:", int(endVolt_lo, 16), "v")
                print("mode:", int(mode, 16))
                print("amps_hi:", int(amps_hi, 16), "a")
                print("amps_lo:", int(amps_lo, 16), "a")
                print("Temp 1_hi:", int(temp1_hi, 16), "c")
                print("Temp 1_lo:", int(temp1_lo, 16), "c")
                print("Temp 2_hi:", int(temp2_hi, 16), "c")
                print("Temp 2_lo:", int(temp2_lo, 16), "c")
                print("SOC:", int(soc, 16), "%")
                print("Checksum:", int(chksum, 16))

        gotSysData = True;
        return(False)

################ main ##################

# id id type len data                          checksum
# 24 24 57   0F  10 68 02 00 00 FF 21 FF 21 00 68
# 24 24 56   16  00 0A 00 0A 00 09 00 0B 00 0D 00 11 00 01 00 15 00 10
# len includes id & type

# data is written to the serial port every second or less, waiting too long results in garbled lines.
# Read fast and often to get the best results. System and Cell data is written at different frequencies.

ser = serial.Serial(devName, 115200, bytesize=8, parity='N', stopbits=1, timeout=0.1)
if (debug): print("Opened:", ser.name)

while (ser.is_open):
        #myBin = ser.read()     # read 1 byte
        myBin  = ser.read(256)  # read up to 15 bytes
        #myBin = ser.readline(255)      # read a '\n' terminated line??
        myPid  = os.getpid()    # for temp file buffering

        hexLine = bin2hex(myBin)
        hexLine = hexLine.decode('utf-8')       # remove leading b in Python3
        dataLen = len(hexLine)

        if (gotSysData or gotCellData):
                if (debug): print("Skip new tmp file")
        else:
                if (debug): print("Opened new tmp file /ramdisk/BMS_A.prom.tmp")
                file_object = open('/ramdisk/BMS_A.prom.tmp', mode='w')

        if (debug): print("Read ", len(hexLine), "bytes: ", hexLine, "gotSysData:", gotSysData, "gotCellData:", gotCellData)

        if (dataLen > 14):
                byteA = hexLine[0:2]    # header
                byteB = hexLine[2:4]    # header
                byteC = hexLine[4:6]    # packet type 56 | 57
                byteD = hexLine[6:8]    # packet len

                if (byteA == "24" and byteB == "24"):

                        if (gotSysData and gotCellData):
                                # We have a complete set, before we overwrite, copy the temp file to its final dest
                                if (debug): print("BINGO!!! - complete set - copying file to /ramdisk/BMS_A.prom")
                                file_object.flush()
                                file_object.close()
                                outLine = os.system('/bin/mv /ramdisk/BMS_A.prom.tmp /ramdisk/BMS_A.prom')
                                if (debug): outLine = os.system('/bin/cat /ramdisk/BMS_A.prom')
                                #if (debug): sys.exit()
                                # open new temp file as we have data to write
                                file_object = open('/ramdisk/BMS_A.prom.tmp', mode='w')
                                if (debug): print("Opened new tmp file /ramdisk/BMS_A.prom.tmp")
                                gotSysData  = False;    # start all over again
                                gotCellData = False;

                        if (byteC == "56"):
                                if (debug): print("Found Cell block", byteA, byteB, byteC, hexLine)
                                if (not gotCellData):
                                        getCellData(file_object, hexLine, int(byteD, 16))
                        elif (byteC == "57"):
                                if (debug): print("Found System block", byteA, byteB, byteC, hexLine)
                                if (not gotSysData):
                                        getSysData(file_object, hexLine, int(byteD, 16))
                        else:
                                if (debug): print("Found Unexpected command block", byteA, byteB, byteC, hexLine)
                else:
                        if (debug): print("Found Unexpected header block", byteA, byteB, byteC, hexLine)
        else:
                if (debug): print("Read Empty line", len(hexLine), "bytes: ", hexLine)

ser.close()

# End.
