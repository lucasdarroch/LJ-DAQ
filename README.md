# LJ-DAQ
LabJack data aquisition script in python3

python3 __daq__.py to start collecting data
path to LabJack must be stated in __daq__.py

data archive handled by __cache__.py

database handled by __daq2db__.py

the inputs to be recorded are handled by modules:
outside of connecting to the labjack (__daq__.py) and database (__daq2db__.py)
the modules are the only scripts that should be edited
