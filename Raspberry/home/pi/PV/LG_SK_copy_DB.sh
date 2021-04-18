#!/bin/sh
#check process Both_SK.py (PowerMeterMgr_SK.py and PCSMgr_SK.py old) is working if not start it
resultBoth=$(ps aux | grep [B]oth_SK)

echo $resultBoth
cd /home/pi/PV-laden

if [ -z "$resultBoth" ]; then
	./Both_SK.py &
	echo "Both (PowerMeter and PCS) started"
else
	echo "Both (PowerMeter and PCS) already running"
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