#!/bin/sh
#copy files from LG-ESS /lge-ems manualy to this folder
echo "db start copy"
python3 copyDB_LG.py ./
echo "end"