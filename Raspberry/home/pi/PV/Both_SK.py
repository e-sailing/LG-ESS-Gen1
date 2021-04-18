#!/usr/bin/env python3

import socket
import sys
import time
import datetime

#debug settings
printRaw = False
printValue = False

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
	
	gridActiveImport = 0
	gridActiveExport = 0
	gridVoltage1 = 0
	gridVoltage2 = 0
	gridVoltage3 = 0
	gridActivePower = 0
	gridFrequency = 0
	question = 10000
	#gridActivePowerD = 0
	#gridActivePowerDA = [0,0,0,0,0,0,0,0,0,0]
	gridAsked = ['50\\x00','50\\x04','5b\\x00','5b\\x02','5b\\x04','5b\\x14','5b\\x2c']

	#pvActivePower = [0,0,0,0,0,0,0,0,0,0]
	#pvPower = [0,0,0,0,0,0,0,0,0,0]
	#pvBatPower = [0,0,0,0,0,0,0,0,0,0]
	#pvActivePowerM = 0
	#pvPowerM = 0
	#pvBatPowerM = 0
	
	pidKnown = False
	pid = 0
	pidAll = ["",""]
	direction = 100
	directionAll = ["read","writ"]
	

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
		
		gridData =bytearray()
		pvData =bytearray()
		
		#now keep talking with the client
		while 1:
			pvValue = []
			try:
				data = buffered_readLine(conn)
			except Exception as e:
				print('exception on read', e)
				try:
					conn.close()
				except: 
					pass
				break
			#pid is from 4 to 9 char
			if not pidKnown:
				if pidAll[0] == "":				
					if (len(data)==63) and (data[12:63]=='write(4, "\\x01\\x03\\x9c\\x72\\x00\\x5c\\xcb\\xb8", 8) = 8'):
						pidAll[0] = data[4:10]
				else:
					if data[4:10] != pidAll[0]:
						pidAll[1] = data[4:10]
						pidKnown = True
						print('pidAll',pidAll,'get')
			else:
				if data[0] == '[' and data[4:10] in pidAll:
					pid = pidAll.index(data[4:10])*10
				else:
					if data[0] == '[':
						print('Error pid:"'+data[4:10]+'" not in ',pidAll)
						pidKnown = False
						pidAll = ["",""]
					pid = 200
				
				#direction read/writ is from 12 to 15 char
				if data[12:16] in directionAll:
					direction = directionAll.index(data[12:16])+pid
				else:
					if data[12] != '<':
						print('Error direction:"'+data[12:16]+'" not in ',directionAll,' all data:',data)
					direction = 100
					
				if direction == 0:  #PCS read
					datasplit = data.split('"')
					if len(datasplit) > 2:
						pvData+=bytes.fromhex(datasplit[1].replace('\\x', ""))
				elif direction == 1:  #PCS write
					if len(pvData) == 189:
						i = 3
						while i < 186:
							pvValue.append(int.from_bytes(pvData[i:i+4], byteorder='big', signed=True))
							i += 4

					if printRaw:
						st=''
						for i in pvValue:
							st += str(i)+';'						
						print(st + strftime("%Y-%m-%d %H:%M:%S", gmtime()))
							
					if len(pvValue)> 40:
						if pvValue[25] > 0:
							SignalK = '{"updates": [{"$source": "pv.5002","values":[ '
							Erg=''
							Erg += '{"path": "pv.activepower","value":'+str(pvValue[6])+'},'
							Erg += '{"path": "pv.power","value":'+f"{((pvValue[10]+pvValue[13])*0.96):.0f}"+'},'
							Erg += '{"path": "pv.batpower","value":'+str(pvValue[19])+'},'
							Erg += '{"path": "pv.soc","value":'+f"{((pvValue[26]-45)*100/905):.1f}"+'}]}]}\n'
							SignalK +=Erg
							
							try:
								sock.sendto(SignalK.encode(), ('127.0.0.1', 55555))
							except error:
								print('Error sending to SignalK-Server.\n',error)
							if printValue: 
								print('pv:')
								print(SignalK)
					pvData=bytearray()
				elif direction == 10: #PowerMeter read
					datasplit = data.split('"')			
					if len(datasplit) > 2:
						gridData+=bytes.fromhex(datasplit[1].replace('\\x', ""))
				elif direction == 11:  #PowerMeter write
					lenDatalist = len(gridData)
					if printRaw:
						print(gridData)
						print('question,lenDatalist',question,lenDatalist)
					#if question==0 and lenDatalist==13: gridActiveImport = gridData[7]*256**3 + gridData[8]*256**2 + gridData[9]*256 + gridData[10]
					if question==0 and lenDatalist==13: gridActiveImport = int.from_bytes(gridData[7:11], byteorder='big', signed=False)
					elif question==1 and lenDatalist==13: gridActiveExport = int.from_bytes(gridData[7:11], byteorder='big', signed=False)
					elif question==2 and lenDatalist==9: gridVoltage1 = gridData[5]*256 + gridData[6]
					elif question==3 and lenDatalist==9: gridVoltage2 = gridData[5]*256 + gridData[6]
					elif question==4 and lenDatalist==9: gridVoltage3 = gridData[5]*256 + gridData[6]
					elif question==5 and lenDatalist==9: gridActivePower = int.from_bytes(gridData[3:7], byteorder='big', signed=True)
					elif question==6 and lenDatalist==7: gridFrequency = gridData[3]*256 + gridData[4]
					
					if printRaw:
						st = ''
						hexi=['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'] 
						for i in range(0,len(gridData)):
							st += hexi[gridData[i]>>4]+hexi[gridData[i]&0x0F]+' '
						print(st)
						print(data)
					try:
						question=gridAsked.index(data[32:38])
					except:
						question = 99
					
					if question == 6:
						SignalK = '{"updates": [{"$source": "grid.5002","values":[ '
						Erg=''
						Erg += '{"path": "grid.activeimportcounter","value":'+f"{(gridActiveImport/100):.0f}"+'},'
						Erg += '{"path": "grid.activeexportcounter","value":'+f"{(gridActiveExport/100):.0f}"+'},'
						Erg += '{"path": "grid.activepower","value":'+f"{(gridActivePower/100):.0f}"+'},'
						Erg += '{"path": "grid.voltage1","value":'+f"{(gridVoltage1/10):.1f}"+'},'
						Erg += '{"path": "grid.voltage2","value":'+f"{(gridVoltage2/10):.1f}"+'},'
						Erg += '{"path": "grid.voltage3","value":'+f"{(gridVoltage3/10):.1f}"+'},'
						Erg += '{"path": "grid.frequency","value":'+f"{(gridFrequency/100):.1f}"+'}]}]}\n'
						SignalK +=Erg
						try:
							sock.sendto(SignalK.encode(), ('127.0.0.1', 55555))
						except error:
							print('Error sending to SignalK-Server.\n',error)
						if printValue: 
							print('grid:')
							print(SignalK)
						
					gridData=bytearray()
						
		conn.close()

if __name__ == '__main__':
	main()
	