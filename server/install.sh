#!/bin/bash

cp LG-ESS.service /etc/systemd/system
systemctl daemon-reload
systemctl enable LG-ESS
systemctl start LG-ESS
