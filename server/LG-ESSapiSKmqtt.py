#!/usr/bin/python3

#import context
import json
import posixpath
import socket
import threading
import time
import urllib
import sys
from http.server import SimpleHTTPRequestHandler, HTTPServer
#import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

hostNameApi = ""
hostNameMqtt = "localhost"              #change to your need
hostPort = 9091                         #change to your need  this is the api port (for example http://localhost:9091/lgess)

# debug settings
printRaw = False
printValue = False
sK = False                              #change to your need (True or False)
mQtt = True                             #change to your need (True or False)


class Vars:
    def __init__(self):
        self.pvActivePower = 0
        self.pvPower = 0
        self.pvSoc = 0
        self.pvBatPower = 0
        self.pvValue = [0] * 46

        self.gridActiveImport = 0
        self.gridActiveExport = 0
        self.gridVoltage1 = 0
        self.gridVoltage2 = 0
        self.gridVoltage3 = 0
        self.gridActivePower = 0
        self.gridFrequency = 0


class VarHolder:
    def __init__(self):
        self.lock = threading.Lock()
        self.data = Vars()

    def setData(self, data):
        self.lock.acquire()
        try:
            self.data = data
        finally:
            self.lock.release()

    def getData(self):
        self.lock.acquire()
        try:
            return self.data
        finally:
            self.lock.release()


class MyRequestH(SimpleHTTPRequestHandler):

    def _html(self, message):
        # This just generates an HTML document that includes `message`
        # in the body. Override, or re-write this do do more interesting stuff.

        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def pathQueryFromUrl(self, url):
        (path, sep, query) = url.partition('?')
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path, encoding='utf-8'))
        query = urllib.parse.parse_qs(query, True)
        return path, query

    #	GET is for clients geting the predi
    def do_GET(self):
        vars = self.server.varHolder.getData()
        # print(vars.gridActivePower)
        (path, query) = self.pathQueryFromUrl(self.path)

        if path.startswith("/lgessgen1"):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            if vars.pvBatPower >= 0:
                pvBatPower = vars.pvBatPower
            if (vars.pvBatPower + vars.gridActivePower) < -1500:
                pvBatPower = vars.pvBatPower*0.8
            else:
                if vars.pvBatPower < 0:
                    pvBatPower = vars.pvBatPower/2           

            lgessgen1 = {
                "time": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
                "gridpower": vars.gridActivePower,
                "gridimport": vars.gridActiveImport,
                "gridexport": vars.gridActiveExport,
                "gridvoltage1": vars.gridVoltage1,
                "gridvoltage2": vars.gridVoltage2,
                "gridvoltage3": vars.gridVoltage3,
                "batterysoc": vars.pvSoc,  # 166
                "batterypower": vars.pvBatPower,  # 128
                "batterypowern": vars.pvBatPower,  # 128
                "batterykwh": 60 * vars.pvSoc,
                "residualpower": vars.pvActivePower,  # fehlt o.PVPower
                "pvpower": vars.pvPower  # 125   totalenergy 151
                }

            self.wfile.write(bytes(json.dumps(lgessgen1), "utf-8"))
            return
            
        elif path.startswith("/lgess"):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            if vars.pvBatPower >= 0:
                pvBatPower = vars.pvBatPower
            if (vars.pvBatPower + vars.gridActivePower) < -1500:
                pvBatPower = vars.pvBatPower*0.8
            else:
                if vars.pvBatPower < 0:
                    pvBatPower = vars.pvBatPower/2           

            test = {
                "time": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
                "grid": {
                    #"GridActivePower": vars.gridActivePower + pvBatPower
                    "ActivePower": vars.gridActivePower,
                    "Voltage1": vars.gridVoltage1,
                    "Voltage2": vars.gridVoltage2,
                    "Voltage3": vars.gridVoltage3
                },
                "battery": {
                    "Soc": vars.pvSoc,  # 166
                    "Power": vars.pvBatPower,  # 128
                    "PowerInv": -vars.pvBatPower,  # 128
                    "SocKW": 60 * vars.pvSoc
                },
                "load": {
                    "ActiveImport": vars.gridActiveImport,
                    "HousePowerConsumption": vars.pvActivePower  # fehlt o.PVPower
                },
                "pv": {
                    "ActiveExport": vars.gridActiveExport,
                    "Power": vars.pvPower  # 125   totalenergy 151
                }}

            self.wfile.write(bytes(json.dumps(test), "utf-8"))
            return


        if path.startswith("/json/all"):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            all = {
                "pv": {
                    "last_communication_time": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
                    # "pvValue0.3": vars.pvValue[0],
                    # "pvValue1.0": vars.pvValue[1],
                    # "pvValue2.252": vars.pvValue[2],
                    # "pvValue3.0": vars.pvValue[3],
                    # "pvValue3.0": vars.pvValue[3],
                    # "pvValue4.0": vars.pvValue[4],
                    # "pvValue5.0": vars.pvValue[5],
                    "pvValue6.Verbrauch": vars.pvValue[6],
                    "pvValue7": vars.pvValue[7],
                    "pvValue8.PV1Status": vars.pvValue[8],
                    "pvValue9.PV1V": vars.pvValue[9],
                    "pvValue10.PV1W": vars.pvValue[10],
                    "pvValue11.PV2Status": vars.pvValue[11],
                    "pvValue12.PV2V": vars.pvValue[12],
                    "pvValue13.PV2W": vars.pvValue[13],
                    "pvValue14": vars.pvValue[14],
                    "pvValue15.Zähler": vars.pvValue[15],
                    "pvValue16.Frequenz": vars.pvValue[16],
                    "pvValue17.AkkuV1": vars.pvValue[17],
                    "pvValue18.entladen-laden": vars.pvValue[18],
                    "pvValue19.laden-entladen": vars.pvValue[19],
                    # "pvValue20.0": vars.pvValue[20],
                    # "pvValue21.0": vars.pvValue[21],
                    "pvValue22.Status": vars.pvValue[22],
                    "pvValue23.AkkuV2": vars.pvValue[23],
                    "pvValue24.entladen-laden": vars.pvValue[24],
                    # "pvValue25.1": vars.pvValue[25],
                    "pvValue26.soc": vars.pvValue[26],
                    "pvValue27.maxsoc": vars.pvValue[27],
                    "pvValue28": vars.pvValue[28],
                    "pvValue29": vars.pvValue[29],
                    "pvValue30.Zähler": vars.pvValue[30],
                    "pvValue31.Zähler": vars.pvValue[31],
                    # "pvValue32.3024": vars.pvValue[32],
                    # "pvValue33.3024": vars.pvValue[33],
                    # "pvValue34.16843008": vars.pvValue[34],
                    # "pvValue35.113": vars.pvValue[35],
                    "pvValue36": vars.pvValue[36],
                    "pvValue37": vars.pvValue[37],
                    "pvValue38": vars.pvValue[38],
                    "pvValue39": vars.pvValue[39],
                    "pvValue40": vars.pvValue[40],
                    "pvValue41": vars.pvValue[41],
                    "pvValue42": vars.pvValue[42],
                    "pvValue43": vars.pvValue[43],
                    "pvValue44": vars.pvValue[44],
                    "pvValue45.Zähler": vars.pvValue[45]
                },
                "grid": {
                    "gridActiveImport": vars.gridActiveImport,
                    "gridActiveExport": vars.gridActiveExport,
                    "gridVoltage1": vars.gridVoltage1,
                    "gridVoltage2": vars.gridVoltage2,
                    "gridVoltage3": vars.gridVoltage3,
                    "gridActivePower": vars.gridActivePower,
                    "gridFrequency": vars.gridFrequency
                }}

            self.wfile.write(bytes(json.dumps(all), "utf-8"))
            return

        SimpleHTTPRequestHandler.do_GET(self)

def buffered_readline(mysocket):
    line = ""
    while True:
        # print(1)
        part = mysocket.recv(1).decode(encoding="ascii", errors="ignore")
        if part == '':
            raise Exception('closed')
        if part != '\n':
            line += str(part)
        elif part == '\n':
            break
    return line

def DataFromLGESS(varholder):
    # Get LG-ESS Data
    HOST = ''  # Symbolic name, meaning all available interfaces
    PORT = 5002  # Arbitrary non-privileged port

    question = 10000
    # gridActivePowerD = 0
    # gridActivePowerDA = [0,0,0,0,0,0,0,0,0,0]
    gridAsked = ['50\\x00', '50\\x04', '5b\\x00', '5b\\x02', '5b\\x04', '5b\\x14', '5b\\x2c']

    pidKnown = False
    pidAll = ["", ""]
    direction = 100
    directionAll = ["read", "writ"]
    mqttcount = 0

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Socket created')

    vars = Vars()

    # Bind socket to local host and port
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    print('Socket bind complete')

    # Start listening on socket
    s.listen(2)
    print('Socket now listening')

    #if mQtt:
    #    mqttClient= mqtt.Client("LG-ESS")
    #    mqttClient.connect(hostNameMqtt)

    while 1:
        conn, addr = s.accept()

        print('New connection')

        gridData = bytearray()
        pvData = bytearray()

        # now keep talking with the client
        while 1:
            try:
                data = buffered_readline(conn)
            except Exception as e:
                print('exception on read', e)
                try:
                    conn.close()
                except Exception as e:
                    print('exception on close', e)
                break
            # pid is from 4 to 9 char
            if not pidKnown:
                if pidAll[0] == "":
                    if (len(data) == 63) and (
                            data[12:63] == 'write(4, "\\x01\\x03\\x9c\\x72\\x00\\x5c\\xcb\\xb8", 8) = 8'):
                        pidAll[0] = data[4:10]
                else:
                    if data[4:10] != pidAll[0]:
                        pidAll[1] = data[4:10]
                        pidKnown = True
                        #print('pidAll', pidAll, 'get')
            else:
                if data[0] == '[' and data[4:10] in pidAll:
                    pid = pidAll.index(data[4:10]) * 10
                else:
                    if data[0] == '[':
                        print('Error pid:"' + data[4:10] + '" not in ', pidAll)
                        pidKnown = False
                        pidAll = ["", ""]
                    pid = 200

                # direction read/writ is from 12 to 15 char
                if data[12:16] in directionAll:
                    direction = directionAll.index(data[12:16]) + pid
                else:
                    if data[12] != '<':
                        print('Error direction:"' + data[12:16] + '" not in ', directionAll, ' all data:', data)
                    direction = 100

                if direction == 0:  # PCS read
                    datasplit = data.split('"')
                    if len(datasplit) > 2:
                        pvData += bytes.fromhex(datasplit[1].replace('\\x', ""))
                elif direction == 1:  # PCS write
                    if len(pvData) == 189:
                        i = 3
                        j = 0
                        while i < 186:
                            # pvValue.append(int.from_bytes(pvData[i:i + 4], byteorder='big', signed=True))
                            vars.pvValue[j] = int.from_bytes(pvData[i:i + 4], byteorder='big', signed=True)
                            i += 4
                            j += 1

                    if printRaw:
                        st = ''
                        for i in vars.pvValue:
                            st += str(i) + ';'
                        print(st + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

                    if len(vars.pvValue) > 40:
                        if vars.pvValue[25] > 0:
                            vars.pvPower = round((vars.pvValue[10] + vars.pvValue[13]) * 0.95, 0)
                            vars.pvSoc = round((vars.pvValue[26] - 45) * 100 / 905, 1)
                            vars.pvBatPower = vars.pvValue[19]
                            vars.pvActivePower = vars.gridActivePower+vars.pvPower+vars.pvBatPower
                            if sK:
                                SignalK = {"updates": [{"$source": "pv.5002", "values": [
                                    {"path": "pv.activepower", "value": vars.pvActivePower},
                                    {"path": "pv.power", "value": vars.pvPower},
                                    {"path": "pv.batpower", "value": vars.pvBatPower},
                                    {"path": "pv.soc", "value": vars.pvSoc}]}]}

                                try:
                                    sock.sendto(json.dumps(SignalK).encode(), ('127.0.0.1', 55555))
                                except Exception as err:
                                    print('Error sending to SignalK-Server.\n', err)
                                if printValue:
                                    print('pv:')
                                    print(SignalK)
                            if mQtt:
                                mqttcount += 1
                                if mqttcount > 3:
                                    mqttcount = 0
                                    
                                if mqttcount == 0:
                                    msgs = [
                                    ("lgess/pv/power",vars.pvPower,0,False),
                                    ("lgess/battery/power",-vars.pvBatPower,0,False),
                                    ("lgess/battery/level",vars.pvSoc),
                                    ("openWB/set/pv/1/W",round(vars.pvPower),0,False),
                                    ("openWB/set/houseBattery/W",-round(vars.pvBatPower),0,False),
                                    ("openWB/set/houseBattery/%Soc",round(vars.pvSoc))
                                    ]
                                    try:
                                        publish.multiple(msgs, hostNameMqtt)
                                    except:
                                        print("can't publish")
                                        mqttcount = -100
                                    #print(msgs)
                                
                    pvData = bytearray()
                elif direction == 10:  # PowerMeter read
                    datasplit = data.split('"')
                    if len(datasplit) > 2:
                        gridData += bytes.fromhex(datasplit[1].replace('\\x', ""))
                elif direction == 11:  # PowerMeter write
                    lenDatalist = len(gridData)
                    if printRaw:
                        print(gridData)
                        print('question,lenDatalist', question, lenDatalist)
                    # if question==0 and lenDatalist==13: gridActiveImport = gridData[7]*256**3 + gridData[8]*256**2 + gridData[9]*256 + gridData[10]
                    if question == 0 and lenDatalist == 13:
                        vars.gridActiveImport = (int.from_bytes(gridData[7:11], byteorder='big', signed=False)) / 100
                    elif question == 1 and lenDatalist == 13:
                        vars.gridActiveExport = (int.from_bytes(gridData[7:11], byteorder='big', signed=False)) / 100
                    elif question == 2 and lenDatalist == 9:
                        vars.gridVoltage1 = (gridData[5] * 256 + gridData[6]) / 10
                    elif question == 3 and lenDatalist == 9:
                        vars.gridVoltage2 = (gridData[5] * 256 + gridData[6]) / 10
                    elif question == 4 and lenDatalist == 9:
                        vars.gridVoltage3 = (gridData[5] * 256 + gridData[6]) / 10
                    elif question == 5 and lenDatalist == 9:
                        vars.gridActivePower = round(
                            (int.from_bytes(gridData[3:7], byteorder='big', signed=True)) / 100, 2)
                    elif question == 6 and lenDatalist == 7:
                        vars.gridFrequency = (gridData[3] * 256 + gridData[4]) / 100

                    if printRaw:
                        st = ''
                        hexi = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
                        for i in range(0, len(gridData)):
                            st += hexi[gridData[i] >> 4] + hexi[gridData[i] & 0x0F] + ' '
                        print(st)
                        print(data)
                    try:
                        question = gridAsked.index(data[32:38])
                    except:
                        question = 99

                    if question == 6:
                        varholder.setData(vars)

                    if question == 6:
                        if sK:
                            SignalK = {"updates": [{"$source": "grid.5002", "values": [
                                {"path": "grid.activeimportcounter", "value": vars.gridActiveImport},
                                {"path": "grid.activeexportcounter", "value": vars.gridActiveExport},
                                {"path": "grid.activepower", "value": vars.gridActivePower},
                                {"path": "grid.voltage1", "value": vars.gridVoltage1},
                                {"path": "grid.voltage2", "value": vars.gridVoltage2},
                                {"path": "grid.voltage3", "value": vars.gridVoltage3},
                                {"path": "grid.frequency", "value": vars.gridFrequency}]}]}

                            try:
                                sock.sendto(json.dumps(SignalK).encode(), ('127.0.0.1', 55555))
                            except Exception as err:
                                print('Error sending to SignalK-Server.\n', err)
                            if printValue:
                                print('grid:')
                                print(SignalK)
                            
                        if mQtt:
                            if mqttcount == 0:
                                msgs = [
                                ("lgess/grid/imported",vars.gridActiveImport,0,False),
                                ("lgess/grid/exported",vars.gridActiveExport,0,False),
                                ("lgess/grid/power",vars.gridActivePower,0,False),
                                ("lgess/grid/voltage1",vars.gridVoltage1,0,False),
                                ("lgess/grid/voltage2",vars.gridVoltage2,0,False),
                                ("lgess/grid/voltage3",vars.gridVoltage3,0,False),
                                ("lgess/grid/frequenz",vars.gridFrequency,0,False),
                                ("openWB/set/evu/WhImported",vars.gridActiveImport,0,False),
                                ("openWB/set/evu/WhExported",vars.gridActiveExport,0,False),
                                ("openWB/set/evu/W",round(vars.gridActivePower),0,False),
                                ("openWB/set/evu/VPhase1",vars.gridVoltage1,0,False),
                                ("openWB/set/evu/VPhase2",vars.gridVoltage2,0,False),
                                ("openWB/set/evu/VPhase3",vars.gridVoltage3,0,False),
                                ("openWB/set/evu/HzFrequenz",round(vars.gridFrequency),0,False)
                                ]
                                try:
                                    publish.multiple(msgs, hostNameMqtt)
                                except:
                                    print("can't publish")
                                #print(msgs)

                    gridData = bytearray()

        conn.close()


varHolder_ = VarHolder()

threadRead = threading.Thread(target=DataFromLGESS, args=[varHolder_], daemon=True)
threadRead.start()

httpd = HTTPServer((hostNameApi, hostPort), MyRequestH)
httpd.varHolder = varHolder_
httpd.serve_forever()
