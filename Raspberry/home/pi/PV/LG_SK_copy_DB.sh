#!/bin/sh
#check process PowerMeterMgr_SK.py and PCSMgr_SK.py are working if not start them
resultPMM=$(ps aux | grep [P]owerMeterMgr_SK)
resultPCS=$(ps aux | grep [P]CSMgr_SK)

echo $resultPMM
echo $resultPCS
cd /home/pi/PV-laden

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


#copy DB
result=$(ls /media/lge-ems | grep "ems_DEU.db-shm")

if [ -z $result ]
then
	sudo sshfs -o allow_other root@192.168.68.83:/nvdata/DBFiles /media/lge-ems
	echo "lge-ems eingebunden"
fi

#when myramdisk doesn't exists
result=$(df | grep "myramdisk")
if [ -z "$result" ]
then
	sudo mount -t tmpfs -o size=20m myramdisk /media/RAM
	echo "Ramdisk erzeugt"
fi

#rm /media/RAM/*.*
cp /media/lge-ems/*.* /media/RAM
echo "db kopiert"
python3 /home/pi/write_LG4.py
echo "neue Datensätze an MySQL angehängt"