#!/bin/bash
# this bash script should be started in a terminal by "./Both_Mgr.sh

# kill all older Both_Mgr processes
for pid in $(pidof -x Both_Mgr.sh); do
    if [ $pid != $$ ]; then
        echo "[$(date)] : Both_Mgr.sh : Process is already running"
		echo "with PID $pid. It will be replaced by this process."
		kill -9 $pid
        #exit 1
    fi
done

# kill all processes started by older Both_Mgr
killall strace

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
