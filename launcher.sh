#!/bin/sh
# launcher.sh
# navigate to home directory, then to DAQ, execute __main__.py, then back to home

cd /
cd home/pi/DAQ
python3 __main__.py &
cd /
