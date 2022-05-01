# getTracerData.py README

## Reason

There was a huge need to have this script running without any issues under latest Python3 (Python 3.10.4) with all the necessary dependencies.

## External dependency

This script required registers and coils from a separate project. In order to make this script work I've included that module into this repo. If there's a better way, please don't hesitate to notify me about it.
pyepsolartracer origin: [pyepsolartracer](https://github.com/kasbert/epsolar-tracer/tree/master/pyepsolartracer)

## Remarks

The output of data (a.k.a prints to stdout) was left as in the original file. Adjust in your own need. I tried to keep the formating as the previous Python 2 version.

## Notes

I've noticed few things that are needed to adjust in order to get the script working:
- in `getTracerData.py` there's a hardcoded path in line 73 to the kernel module, adjust that if needed
- create a ramdisk (refer to `exportData.sh`)
- in `exportData.sh` there are plenty of hardcoded paths, adjust it aswell
- if running this script as standard user, ensure that the user has executable permissions both to `exportData.sh` and `getTracerData.py`
- in case of errors accessing the /dev/USBxxx device as the standard user, you may add the user either to `tty` or `dialup` groups and relog (ex. `sudo usermod -a -G tty yourname`)

## Example output

```shell
{0: b'EPsolar Tech co., Ltd', 1: b'TriRon3210', 2: b'V01.56+V01.22'}

0x3100: pvVoltage: 0.61 v
0x3101: pvCurrent: 0.00 a
0x3102: pvPowerL: 0.00 w
0x3104: batteryChargeV: 13.23 v
0x3105: batteryChargeC: 0.00 a
0x3106: batteryChargePowerL: 0.00 w
0x310C: loadVoltage: 0.00 v
0x310D: loadCurrent: 0.00 a
0x310E: loadPowerL: 0.00 w
0x3110: batteryTemp: 15.61 c 60.10 f
0x3111: deviceTemp: 16.97 c 62.55 f
0x311A: Battery S.O.C: 85.00 %
0x3300: pvMaxInVolts: 56.33 v
0x3301: pvMinInVolts: 0.61 v
0x3302: batMaxVolts: 14.34 v
0x3303: batMinVolts: 13.16 v
0x3304: consumedEnergyTodayL: 0 w/h
0x330C: genEnergyTodayL: 500 w/h
0x3200: batteryStatus: 0000000000000000 bits
0x3201: equipStatus: 0000000000000001 bits
runningOk: 1
fault: 0
chargeStatus: 0 Standby
pvError: 0
0x9000: batType: 0
0x9001: batCap: 280 ah
0x9002: batComp: 0
0x9003: hiVDiscon: 15.60 v
0x9004: chargeLimitV: 14.40 v
0x9005: overVRecon: 14.70 v
0x9006: eqVolts: 14.20 v
0x9007: boostV: 14.20 v
0x9008: floatV: 13.60 v
0x9009: boostReconV: 13.30 v
0x900A: loVRecon: 12.80 v
0x900B: underVRecover: 12.80 v
0x900C: underVWarn: 12.00 v
0x90OD: loVDiscon: 11.10 v
0x900E: dischargeLimitV: 10.60 v

Battery is Charging in Standby mode at 0.0 Watts
```