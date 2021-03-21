#!/bin/sh
#check process PowerMeterMgr_SK.py and PCSMgr_SK.py are working if not start them
resultPMM=$(ps a | grep [P]owerMeterMgr_SK)
resultPCS=$(ps a | grep [P]CSMgr_SK)

echo $resultPMM
echo $resultPCS

if [ -z "$resultPMM" ]; then
	./PowerMeterMgr_SK.py &
	echo "PowerMeterMgr_SK started"
else
	echo "PowerMeterMgr_SK already running"
fi

#echo ${#resultPCS}
#if [ "${#resultPCS}" > 10 ]; then
if [ -z "$resultPCS" ]; then
	./PCSMgr_SK.py &
	echo "PCSMgr_SK gestartet"
else
	echo "PCSMgr_SK already running"
fi
