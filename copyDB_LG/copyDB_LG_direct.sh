#!/bin/sh
#when the db doesn't exists
result=$(ls /media/lge-ems | grep "ems_DEU.db-shm")

if [ -z $result ]
then
	sudo sshfs -o allow_other root@lge-ems.local:/nvdata/DBFiles /media/lge-ems
	echo "lge-ems connected"
fi

echo "db start copy"
python3 /home/pi/LG-ESS-Gen1/copyDB_LG/copyDB_LG.py /media/lge-ems
echo "end"