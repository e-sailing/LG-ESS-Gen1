#!/bin/bash

gcc -Iinclude -c src/mqtt.c src/mqtt_pal.c src/pipe2mqtt.c
gcc -static -pthread -o pipe2mqtt *.o


#gcc -pthread -c mqtt.c mqtt_pal.c pipe2mqtt.c
#gcc -static -pthread -o pipe2mqtt *.o
