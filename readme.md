# LG ESS 6.4 kW 2016 (Gen 1)
## how to get Data from the controller when there is no output

There is no api or anything to communicate with the controller.
But you can enter the system as root user with putty. You can also use winscp to copy files from or to the controller.
To get history data you can copy the database /nvdata/DBFiles. This is a sqlite3 db.

The processes running can be viewed with the command top.
The communication between the different *Mgr processes are done with pipes. These pipes can be sniffed with strace.
I downloaded strace (https://github.com/yunchih/static-binaries/blob/master/strace) and copied it into the root folder.
Two bash scripts are used to start sending the pipes to a network address
The first script catches the communication with the PCS (PV power, used Power, soc, ...)
```
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
```
A linux system (Raspberry Pi) listens to the stream and decode it.
```
#!/usr/bin/env python3

import socket
import sys
from time import gmtime, strftime


def buffered_readLine(socket):
	line = ""
	while True:
		part = socket.recv(1).decode(encoding="ascii", errors="ignore")
		#print(part)
		if part != '\n':
			line+=str(part)
		elif part == '\n':
			break
	return line

def main():

	HOST = ''	# Symbolic name, meaning all available interfaces
	PORT = 5001	# Arbitrary non-privileged port
	activePower = [0,0,0,0,0,0,0,0,0,0]
	pvPower = [0,0,0,0,0,0,0,0,0,0]
	batPower = [0,0,0,0,0,0,0,0,0,0]
	activePowerM = 0
	pvPowerM = 0
	batPowerM = 0
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print('Socket created')

	#Bind socket to local host and port
	try:
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind((HOST, PORT))
	except socket.error as msg:
		print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
		sys.exit()
		
	print('Socket bind complete')

	#Start listening on socket
	s.listen(10)
	conn, addr = s.accept()

	print('Socket now listening')
	
	datalist =bytearray()
	#now keep talking with the client
	k = 0
	while 1:
		#readline
		#data = conn.recv(1024)
		value = []
		data = buffered_readLine(conn)
		if data[0:4] == 'read':
			datasplit = data.split('"')
			if len(datasplit) > 2:
				datalist+=bytes.fromhex(datasplit[1].replace('\\x', ""))
		
		if data[0:5] == 'write':
			if len(datalist) == 189:
				i = 3
				while i < 186:
					value.append((datalist[i]*256**3 + datalist[i+1]*256**2 + datalist[i+2]*256 + datalist[i+3]))
					i += 4

			#st=''
			#for i in value:
			#	j = int.from_bytes(i.to_bytes(4, 'little'), 'little', signed=True)
			#	st += str(j)+';'
			#st += strftime("%Y-%m-%d %H:%M:%S", gmtime())
			#print(st)
				
			#hexi=['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'] 
			#for i in range(0,len(datalist)):
			#	st += hexi[datalist[i]>>4]+hexi[datalist[i]&0x0F]+' '
			datalist=bytearray()

			#print(len(value))
			

			if len(value)> 40:
				if value[25] > 0:
					value19 = int.from_bytes(value[19].to_bytes(4, 'little'), 'little', signed=True)
					activePower[k] = value[6]
					pvPower[k] = value[10]+value[13]
					batPower[k] = value19

					activePowerM = 0
					pvPowerM = 0
					batPowerM = 0
					
					for j in range(0,10):						
						activePowerM += activePower[j]
						pvPowerM += pvPower[j]
						batPowerM += batPower[j]
					
					
					#print(value[6],value[10],value[13],value19,value[26])
					SignalK = '{"updates": [{"$source": "PCS.PV5001","values":[ '
					Erg=''
					Erg += '{"path": "PCS.activePower","value":'+str(value[6])+'},'
					Erg += '{"path": "PCS.activePowerD","value":'+f"{(activePowerM/10):.0f}"+'},'
					Erg += '{"path": "PCS.pvPower","value":'+str((value[10]+value[13]))+'},'
					Erg += '{"path": "PCS.pvPowerD","value":'+f"{(pvPowerM/10):.0f}"+'},'
					Erg += '{"path": "PCS.batPower","value":'+str(value19)+'},'
					Erg += '{"path": "PCS.batPowerD","value":'+f"{(batPowerM/10):.0f}"+'},'
					Erg += '{"path": "PCS.soc","value":'+f"{((value[26]-45)*100/905):.1f}"+'},'
					SignalK +=Erg[0:-1]+']}]}\n'
					sock.sendto(SignalK.encode(), ('127.0.0.1', 55555))
					k += 1
					if k>9: k=0

	conn.close()

if __name__ == '__main__':
	main()
```
If you look to the raw data you will notice, that this is a modbus communication. 
I send the data to a Signal K server (used for marine data).

The second script sends the data from the external powermeter (ABB 212...) (buy power + sell power -).
```
#!/bin/bash

while :
do
	#get the pid of PowerMeterMgr
	IFS=' ' read -a array <<< $(ps | grep [P]owerMeterMgr)
	echo "${array[0]}"
	#pipe stream to Raspberry Pi
	./strace -p "${array[0]}" -s 1024 -xx -e trace=read,write 2>&1 | nc 192.168.68.59 5002
	echo Keep running
	echo "Press CTRL+C to exit"
	sleep 5
done
```
The counter part on the Raspberry Pi is this:
```
#!/usr/bin/env python3

import socket
import sys
import time

def buffered_readLine(mysocket):
	line = ""
	i=0
	while True:
		#print(1)
			part = mysocket.recv(1).decode(encoding="ascii", errors="ignore")
			if part == '':
				raise Exception('closed')
			if part != '\n':
				line+=str(part)
			elif part == '\n':
				break
	return line

def main():

	HOST = ''	# Symbolic name, meaning all available interfaces
	PORT = 5002	# Arbitrary non-privileged port
	
	activeImport = 0
	activeExport = 0
	voltage1 = 0
	voltage2 = 0
	voltage3 = 0
	activePower = 0
	frequency = 0
	question = 10000
	activePowerM = 0
	activePowerA = [0,0,0,0,0,0,0,0,0,0]
	
	Asked = ['50\\x00','50\\x04','5b\\x00','5b\\x02','5b\\x04','5b\\x14','5b\\x2c']

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print('Socket created')

	#Bind socket to local host and port
	try:
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind((HOST, PORT))
	except socket.error as msg:
		print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
		sys.exit()
		
	print('Socket bind complete')

	#Start listening on socket
	s.listen(2)
	print('Socket now listening')
	
	while 1:
		conn, addr = s.accept()

		print('New connection')
		
		datalist =bytearray()
		#now keep talking with the client
		k = 0
		while 1:
			#readline
			#data = conn.recv(1024)
			time.sleep(0.02)
			value = []
			try:
				data = buffered_readLine(conn)
			except Exception as e:
				print('exception on read', e)
				try:
					conn.close()
				except: 
					pass
				break
			if data[0:4] == 'read':
				datasplit = data.split('"')
				if len(datasplit) > 2:
					datalist+=bytes.fromhex(datasplit[1].replace('\\x', ""))
			
			if data[0:5] == 'write':
				try:
					#print('länge:',len(datalist),'  Frage:',question)
					if question==0: activeImport = datalist[7]*256**3 + datalist[8]*256**2 + datalist[9]*256 + datalist[10]
					elif question==1: activeExport = datalist[7]*256**3 + datalist[8]*256**2 + datalist[9]*256 + datalist[10]
					elif question==2: voltage1 = datalist[5]*256 + datalist[6]
					elif question==3: voltage2 = datalist[5]*256 + datalist[6]
					elif question==4: voltage3 = datalist[5]*256 + datalist[6]
					elif question==5: 
						activePower = datalist[3]*256**3 + datalist[4]*256**2 + datalist[5]*256 + datalist[6]
						activePower = int.from_bytes(activePower.to_bytes(4, 'little'), 'little', signed=True)
				except: pass
			
				#st = ''
				#hexi=['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'] 
				#for i in range(0,len(datalist)):
				#	st += hexi[datalist[i]>>4]+hexi[datalist[i]&0x0F]+' '
				#print(''.join('{:-02X}'.format(a) for a in datalist))
				#print(st)
				#print(data)
				#print(data[20:26])
				datalist=bytearray()
				question=Asked.index(data[20:26])
				
				if question == 6:
				
					activePowerM = 0
					activePowerA[k] = activePower
						
					for j in range(0,10):						
						activePowerM += activePowerA[j]
				
					#print(activeImport,activeExport,voltage1,voltage2,voltage3,activePower, strftime("%Y-%m-%d %H:%M:%S", gmtime()))
					SignalK = '{"updates": [{"$source": "PMM.PV5002","values":[ '
					Erg=''
					Erg += '{"path": "PMM.activeImport","value":'+f"{(activeImport/100):.0f}"+'},'
					Erg += '{"path": "PMM.activeExport","value":'+f"{(activeExport/100):.0f}"+'},'
					Erg += '{"path": "PMM.activePower","value":'+f"{(activePower/100):.0f}"+'},'
					Erg += '{"path": "PMM.activePowerD","value":'+f"{(activePowerM/1000):.0f}"+'},'
					Erg += '{"path": "PMM.voltage1","value":'+f"{(voltage1/1000):.0f}"+'},'
					Erg += '{"path": "PMM.voltage2","value":'+f"{(voltage2/1000):.0f}"+'},'
					Erg += '{"path": "PMM.voltage3","value":'+f"{(voltage3/1000):.0f}"+'},'
					SignalK +=Erg[0:-1]+']}]}\n'
					try:
						sock.sendto(SignalK.encode(), ('127.0.0.1', 55555))
					except error:
						print('Error sending to SignalK-Server.\n',error)

					k += 1
					if k>9: k=0
								
		conn.close()

if __name__ == '__main__':
	main()
```
Please change the IP address to your needs.
In Signal K you should add a connection of type signalk on 55555.
