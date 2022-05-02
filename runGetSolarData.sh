#!/bin/bash
#
## Adjust paths: ######
workdir = "/home/solar"
ramDiskDir="/ramdisk"
#######################

echo starting Epever LifePO4 serial data collection
while : ; do
    $workdir/getTracerData.py > /ramdisk/solarData.txt.$$
    sleep 1
    date >> $ramDiskDir/solarData.txt.$$
    mv $ramDiskDir/solarData.txt.$$ $ramDiskDir/solarData.txt
    $workdir/exportData.sh
    sleep 4
done
