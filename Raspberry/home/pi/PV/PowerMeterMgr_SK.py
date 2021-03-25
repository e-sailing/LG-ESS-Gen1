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
					Erg += '{"path": "PMM.voltage1","value":'+f"{(voltage1/10):.1f}"+'},'
					Erg += '{"path": "PMM.voltage2","value":'+f"{(voltage2/10):.1f}"+'},'
					Erg += '{"path": "PMM.voltage3","value":'+f"{(voltage3/10):.1f}"+'},'
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
	