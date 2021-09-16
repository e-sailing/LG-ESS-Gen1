# LG ESS 6.4 kW 2016 (Gen 1)
## how to get Data from the controller when there is no output

![](C:\Users\stell\Documents\GitHub\LG-ESS-Gen1\doc\LG-ESS Gen1.jpg)

There is no api or anything to communicate with the controller.
But you can enter the system as root user with putty or ssh. To copy files from or to the controller use FileZilla or WinSCP.

To get history data you can copy the database /nvdata/DBFiles. This is a sqlite3 DB. Every 15 minutes it writes a new record. Because of the limited capacity old data will be deleted.



As a prerequisite for the following steps, the git repository should be cloned.



### History data

To save history data on a raspberry pi in a mariaDB and view it on grafana, use the folder copyDB_LG (mariaDB should have a username user with a password user  ). Start the process by:



`cd copyDB_LG` 

`./copyDB_LG.sh`





### Actual data

Actual data is Also accessible.

The processes running can be viewed with the command top.
The communication between the different *Mgr processes are done with pipes. These pipes can be sniffed with strace.

In the folder LG-ESS/root there are two files which should be copied to the LG-ESS.

![](C:\Users\stell\Documents\GitHub\LG-ESS-Gen1\doc\rpi-filezilla.png)

(The strace comes from https://github.com/yunchih/static-binaries/blob/master/strace) 

The ip address must be edited in the bash script Both_Mgr.sh to the ip address of your raspberry pi!

To start sending to the raspberry, ssh into your LG-ESS

`ssh root@lge-ems.local`

`./Both_Mgr.sh &`



Prepare the raspberry pi to receive.

- if mqtt is set to True in the python script LG-ESSapiSKmqtt.py,  a mqtt mosquitto server must be installed
- if sK is set True a Signal K server must be installed and a connection in Signal K with port 55555 must be opened



Check if it works. Open a terminal.

`sudo pip3 install paho-mqtt`

`cd LG-ESS-Gen1/server`

`sudo python3 LG-ESSapiSKmqtt.py`

Open the browser and enter "localhost:9090/json/all"

There should be a list of data

If the server should start on every boot use:

`sudo bash install.sh`



### API

there are two commands to get json data from the api

<ip>:9090/json/all

is a raw list of all data

`pv	
    last_communication_time	"2021-09-16T08:26:15.000Z"
    pvValue6.Verbrauch	297
    pvValue7	625
    pvValue8.PV1Status	1
    pvValue9.PV1V	344
    pvValue10.PV1W	496
    pvValue11.PV2Status	1
    pvValue12.PV2V	351
    pvValue13.PV2W	485
    pvValue14	2364
    pvValue15.Zähler	13995346
    pvValue16.Frequenz	5001
    pvValue17.AkkuV1	1985
    pvValue18.entladen-laden	26
    pvValue19.laden-entladen	-519
    pvValue22.Status	1
    pvValue23.AkkuV2	1984
    pvValue24.entladen-laden	25
    pvValue26.soc	180
    pvValue27.maxsoc	940
    pvValue28	230
    pvValue29	215
    pvValue30.Zähler	44254
    pvValue31.Zähler	42335
    pvValue36	30
    pvValue37	19
    pvValue38	35
    pvValue39	35
    pvValue40	35
    pvValue41	2
    pvValue42	4
    pvValue43	220
    pvValue44	4
    pvValue45.Zähler	152
grid	
    gridActiveImport	7982.14
    gridActiveExport	7154.12
    gridVoltage1	235
    gridVoltage2	233
    gridVoltage3	233.5
    gridActivePower	-0.26
    gridFrequency	50.02`



<ip>:9090/lgess

is a list of important data

`grid	
    last_communication_time	"2021-09-16T08:30:42.000Z"
    GridActivePower	0.13
battery	
    PvSoc	16
    PvBatPower	-587
    PvBatPowerInv	587
    PvSocKW	960
load	
    GridActiveImport	7982.14
    HousePowerConsumption	307
pv	
    GridActiveExport	7154.12
    PvPower	999`



### MQTT

A picture of the data captured from mqtt-explorer

![](C:\Users\stell\Documents\GitHub\LG-ESS-Gen1\doc\MQTT-explorer.png)