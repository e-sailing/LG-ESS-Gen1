#!/bin/bash

while :
do
	#Ermittelung der pid
	ps | grep [P]CSMgr
	echo $0
	BFS=' ' read -a array1 <<< $(ps | grep [P]CSMgr)
	IFS=' ' read -a array2 <<< $(ps | grep [P]owerMeterMgr)
	sleep 1

	
	#pipe stream mitschreiben und weiterleiten
	./strace -p "${array1[0]}" -p "${array2[0]}" -s 512 -xx -e trace=read,write 2>&1 | nc 192.168.68.41 5002
	echo Keep running
	echo "Press CTRL+C to exit"
	sleep 5
done
