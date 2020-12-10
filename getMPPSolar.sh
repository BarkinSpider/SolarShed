#!/bin/bash

# This script assumes you already have the mpp-solar python program running correctly and node_exporter, Prometheus and Grafana working.
# See my other documents for information on that.
# All this simple script does is convert the output for mpp-solar into a .prom file in the /ramdisk folder, so node_-exporter can read it and load into
# the Prometheus database. You can then graph the values in real--time with Grafana.

# mpp-solar parsing script for 2 x 3048 MPP all--in--one devices connected for split phase.
# Joe Elliott
# v0.4b Nov 2020

# create CPU & LoadAvg with # while :; do :; done
# create DISK load with # find /usr -exec grep joe {} \;
# create Network load with # ping -f 8.8.8.8

debug=1
unitName="1440w-3x4-120W LifePO4-16s2p 48v-320a/h 15.4kW/h"
dataFileP1="MPP3048_P1"
dataFileP2="MPP3048_P2"
dataDir="/ramdisk/"

while : ; do
        # Collect the raw data from each Phase inverter.
        # Use double buffering to avoid race conditions.
        `/home/joe/mpp-solar -c QPGS0 > ${dataDir}${dataFileP1}.$$`
        `mv ${dataDir}${dataFileP1}.$$ ${dataDir}${dataFileP1}.txt`

        `/home/joe/mpp-solar -c QPGS1 > ${dataDir}${dataFileP2}.$$`
        `mv ${dataDir}${dataFileP2}.$$ ${dataDir}${dataFileP2}.txt`

        for mppDev in $dataFileP1 $dataFileP2
        do
                # Inverter power values
                gridVolts=`cat ${dataDir}${mppDev}.txt | \grep grid_voltage     | cut -f2 | sed 's/ //g'`
                batVolts=`cat  ${dataDir}${mppDev}.txt | \grep battery_voltage  | cut -f2 | sed 's/ //g'`
                pvVolts=`cat   ${dataDir}${mppDev}.txt | \grep pv_input_voltage | cut -f2 | sed 's/ //g'`
                pvAmps=`cat    ${dataDir}${mppDev}.txt | \grep pv_input_current | cut -f2 | sed 's/ //g'`
                batCap=`cat    ${dataDir}${mppDev}.txt | \grep battery_capacity | cut -f2 | sed 's/ //g'`
                acWatts=`cat   ${dataDir}${mppDev}.txt | \grep ac_output_active | cut -f2 | sed 's/ //g'`
                acLoadPC=`cat  ${dataDir}${mppDev}.txt | \grep load_percentage  | cut -f2 | sed 's/ //g'`

                # We need to calculate this value
                pvWatts=$(echo "scale=2; $pvVolts*$pvAmps" | bc)

                # Inverter status values (binary)
                sccOK=`cat         ${dataDir}${mppDev}.txt | \grep is_scc_ok                | cut -f2 | sed 's/ //g'`
                sccCharging=`cat   ${dataDir}${mppDev}.txt | \grep is_scc_charging          | cut -f2 | sed 's/ //g'`
                acCharging=`cat    ${dataDir}${mppDev}.txt | \grep is_ac_charging           | cut -f2 | sed 's/ //g'`
                acLost=`cat        ${dataDir}${mppDev}.txt | \grep is_line_lost             | cut -f2 | sed 's/ //g'`
                acLoadOn=`cat      ${dataDir}${mppDev}.txt | \grep is_load_on               | cut -f2 | sed 's/ //g'`
                batOverV=`cat      ${dataDir}${mppDev}.txt | \grep is_battery_over_voltage  | cut -f2 | sed 's/ //g'`
                batUnderV=`cat     ${dataDir}${mppDev}.txt | \grep is_battery_under_voltage | cut -f2 | sed 's/ //g'`
                confChange=`cat    ${dataDir}${mppDev}.txt | \grep is_configuration_changed | cut -f2 | sed 's/ //g'`

                # Inverter Status  values (strings)
                serNum=`cat        ${dataDir}${mppDev}.txt | \grep serial_number            | cut -f2 | sed 's/ //g'`
                workMode=`cat      ${dataDir}${mppDev}.txt | \grep work_mode                | cut -f2 | sed 's/ //g'`
                srcMode=`cat       ${dataDir}${mppDev}.txt | \grep charger_source_priority  | cut -f2 | sed 's/ //g'`
                faultCode=`cat     ${dataDir}${mppDev}.txt | \grep fault_code               | cut -f2 | sed 's/ //g'`

                # create the prom file. first value should truncate file. others append!
                printf "$mppDev{mode=\"gridVolts\"} $gridVolts\n" >  ${dataDir}$mppDev.prom.$$ 
                printf "$mppDev{mode=\"batVolts\"}  $batVolts\n"  >> ${dataDir}$mppDev.prom.$$ 
                printf "$mppDev{mode=\"pvVolts\"}   $pvVolts\n"   >> ${dataDir}$mppDev.prom.$$ 
                printf "$mppDev{mode=\"pvAmps\"}    $pvAmps\n"    >> ${dataDir}$mppDev.prom.$$ 
                printf "$mppDev{mode=\"batCap\"}    $batCap\n"    >> ${dataDir}$mppDev.prom.$$ 
                printf "$mppDev{mode=\"pvWatts\"}   $pvWatts\n"   >> ${dataDir}$mppDev.prom.$$ 
                printf "$mppDev{mode=\"acWatts\"}   $acWatts\n"   >> ${dataDir}$mppDev.prom.$$ 
                printf "$mppDev{mode=\"acLoadPC\"}  $acLoadPC\n"  >> ${dataDir}$mppDev.prom.$$ 

                printf "$mppDev{mode=\"sccOK\"} $sccOK\n"             >> ${dataDir}$mppDev.prom.$$ 
                printf "$mppDev{mode=\"sccCharging\"} $sccCharging\n" >> ${dataDir}$mppDev.prom.$$ 
                printf "$mppDev{mode=\"acCharging\"} $acCharging\n"   >> ${dataDir}$mppDev.prom.$$ 
                printf "$mppDev{mode=\"acLost\"} $acLost\n"           >> ${dataDir}$mppDev.prom.$$ 
                printf "$mppDev{mode=\"acLoadOn\"} $acLoadOn\n"       >> ${dataDir}$mppDev.prom.$$ 
                printf "$mppDev{mode=\"batOverV\"} $batOverV\n"       >> ${dataDir}$mppDev.prom.$$ 
                printf "$mppDev{mode=\"batUnderV\"} $batUnderV\n"     >> ${dataDir}$mppDev.prom.$$ 
                printf "$mppDev{mode=\"confChange\"} $confChange\n"   >> ${dataDir}$mppDev.prom.$$ 

                printf "$mppDev{mode=\"serNum\"} $serNum\n"                     >> ${dataDir}$mppDev.prom.$$ 
                printf "$mppDev{mode=\"workMode\",  myStr=\"$workMode\"}  0\n"  >> ${dataDir}$mppDev.prom.$$ 
                printf "$mppDev{mode=\"srcMode\",   myStr=\"$srcMode\"}   0\n"  >> ${dataDir}$mppDev.prom.$$ 
                printf "$mppDev{mode=\"faultCode\", myStr=\"$faultCode\"} 0\n"  >> ${dataDir}$mppDev.prom.$$ 

                if (( $debug )) ; then
                        printf "handled file:${dataDir}$mppDev batVolts:$batVolts pvVolts:$pvVolts batCap:$batCap gridVolts:$gridVolts pvAmps:$pvAmps pvWatts:$pvWatts acWatts:$acWatts acLoadPC:$acLoadPC\n"
                fi
        done

        `mv ${dataDir}${dataFileP1}.prom.$$ ${dataDir}${dataFileP1}.prom`
        `mv ${dataDir}${dataFileP2}.prom.$$ ${dataDir}${dataFileP2}.prom`

        sleep 4
done
