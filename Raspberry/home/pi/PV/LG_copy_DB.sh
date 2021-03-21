#!/bin/sh
#when the db doesn't exists
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