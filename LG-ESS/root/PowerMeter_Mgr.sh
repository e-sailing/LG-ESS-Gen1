#!/bin/bash

while :
do
	#get pid of PowerMeterMgr
	IFS=' ' read -a array <<< $(ps | grep [P]owerMeterMgr)
	echo "${array[0]}"
	#pipe stream to network address
	./strace -p "${array[0]}" -s 1024 -xx -e trace=read,write 2>&1 | nc 192.168.68.59 5002
	echo Keep running
	echo "Press CTRL+C to exit"
	sleep 5
done
