#!/bin/sh
#when the db doesn't exists
result=$(ls /media/lge-ems | grep "ems_DEU.db-shm")

if [ -z $result ]
then
	sudo sshfs -o allow_other root@lge-ems.local:/nvdata/DBFiles /media/lge-ems
	echo "lge-ems connected"
fi

#when myramdisk doesn't exists
result=$(df | grep "myramdisk")
if [ -z "$result" ]
then
	sudo mount -t tmpfs -o size=20m myramdisk /media/RAM
	echo "Ramdisk initialized"
fi

#rm /media/RAM/*.*
echo "db start copy"
cp /media/lge-ems/*.* /media/RAM
python3 /home/pi/LG-ESS-Gen1/copyDB_LG/copyDB_LG.py
echo "end"