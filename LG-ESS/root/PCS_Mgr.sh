#!/bin/bash

while :
do
	#get pid of PCSMgr
	ps | grep [P]CSMgr
	echo $0
	BFS=' ' read -a array <<< $(ps | grep [P]CSMgr)
	sleep 1
	echo "${array[0]}"
	echo "${array[1]}"
	echo "${array[2]}"
	
	#pipe stream to network address
	./strace -p "${array[0]}" -s 1024 -xx -e trace=read,write 2>&1 | nc 192.168.68.59 5001
	echo Keep running
	echo "Press CTRL+C to exit"
	sleep 5
done
