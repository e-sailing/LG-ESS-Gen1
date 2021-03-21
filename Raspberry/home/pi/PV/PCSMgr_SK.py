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
