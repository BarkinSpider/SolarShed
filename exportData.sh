#!/bin/bash

# This script converts the plain ASCII data output by getTracerData.py into a format
# that can be used by Grafana. The new file is written to the /ramdisk folder
# It converts the file /ramdisk/solarData.txt to /ramdisk/solarData.txt.prom
# 
# Here is an example wrapper script that brings it altogether, loading data into grafana indefinitely.
# >>>> runGetSolarData.sh <<<<

# Create the above script called runGetSolarData.sh, make it executable with '# chmod +x runGetSolarData.sh'
# Then run it as root ./runGetSolarData.sh 
# look for the new file being created /ramdisk/solarData.txt.prom and updated every 4 seconds
# node_exporter will automatically load this data into Prometheus for you.

# In Grafana, the Prometheus data can be seen under the label 'AB_SolarStats'
# Ensure Prometheus and node_exporter are working correctly.

# example test commands to create load on your Pi server for testing with node_exporter
# create CPU & LoadAvg activity with # while :; do :; done
# create DISK load with # find /usr -exec grep XXX {} \;
# create Network load with # ping -f 8.8.8.8

# Add a description string of your solar installation
unitName="1440w-3x4-120W LifePO4-8s4p 24v-640a/h 15.4kW/h"

# The source text file containing the output from the getTracerData.py script
ramDiskDir="/ramdisk"
dataFile="$ramDiskDir/solarData.txt"

batVolts=`cat $dataFile | \grep batteryChargeV | cut -f3 -d" "`
batwatts=`cat $dataFile | \grep batteryChargeP | cut -f3 -d" "`
batSOC=`cat $dataFile | \grep 'Battery S.O.C' | cut -f4 -d" "`
pvWatts=`cat $dataFile | \grep pvPower | cut -f3 -d" "`
pvVolts=`cat $dataFile | \grep pvVolt | cut -f3 -d" "`
sysStatus=`cat $dataFile | \grep 'Battery is' | cut -f3 -d" "`
batTemp=`cat $dataFile | \grep batteryTemp | cut -f3 -d" "`
devTemp=`cat $dataFile | \grep deviceTemp | cut -f3 -d" "`
genWatts=`cat $dataFile | \grep genEnergyToday | cut -f3 -d" "`
conWatts=`cat $dataFile | \grep consumedEnergyToday | cut -f3 -d" "`
loadWatts=`cat $dataFile | \grep loadPower | cut -f3 -d" "`
loadCurr=`cat $dataFile | \grep loadCurrent | cut -f3 -d" "`
loadVolts=`cat $dataFile | \grep loadVoltage | cut -f3 -d" "`
chargeStatVal=`cat $dataFile | \grep chargeStatus | cut -f2 -d" "`
chargeStatStr=`cat $dataFile | \grep chargeStatus | cut -f3 -d" "`
sysStatus=`cat $dataFile | \grep Battery\ is | cut -f3 -d" "`

:>$dataFile.prom.$$

 # numeric values
printf "AB_SolarStats{mode=\"batVolts\"} $batVolts\n" >> $dataFile.prom.$$
printf "AB_SolarStats{mode=\"batwatts\"} $batwatts\n" >> $dataFile.prom.$$
printf "AB_SolarStats{mode=\"batSOC\"} $batSOC\n"     >> $dataFile.prom.$$
printf "AB_SolarStats{mode=\"pvWatts\"} $pvWatts\n"   >> $dataFile.prom.$$
printf "AB_SolarStats{mode=\"pvVolts\"} $pvVolts\n"   >> $dataFile.prom.$$
printf "AB_SolarStats{mode=\"loadWatts\"} $loadWatts\n" >> $dataFile.prom.$$
printf "AB_SolarStats{mode=\"loadCurr\"} $loadCurr\n" >> $dataFile.prom.$$
printf "AB_SolarStats{mode=\"loadVolts\"} $loadVolts\n" >> $dataFile.prom.$$
printf "AB_SolarStats{mode=\"batTemp\"} $batTemp\n"   >> $dataFile.prom.$$
printf "AB_SolarStats{mode=\"devTemp\"} $devTemp\n"   >> $dataFile.prom.$$
printf "AB_SolarStats{mode=\"genWatts\"} $genWatts\n" >> $dataFile.prom.$$
printf "AB_SolarStats{mode=\"conWatts\"} $conWatts\n" >> $dataFile.prom.$$
printf "AB_SolarStats{mode=\"chargeStatVal\"} $chargeStatVal\n" >> $dataFile.prom.$$

# text values
printf "AB_SolarStats{myVar=\"chargeStatStr\",myStr=\"$chargeStatStr\"} $chargeStatVal\n" >> $dataFile.prom.$$
printf "AB_SolarStats{myVar=\"sysStatus\",myStr=\"$sysStatus\"} $chargeStatVal\n" >> $dataFile.prom.$$
printf "AB_SolarStats{myVar=\"unitName\",myStr=\"$unitName\"} 0\n" >> $dataFile.prom.$$

`mv $dataFile.prom.$$ $dataFile.prom`

# End
