# -*- coding: utf-8 -*-
"""
Created on Wed May  6 11:20:51 2020

@author: lucasd
"""
import os
import time
import subprocess
import sys
import datetime as dt
from labjack import ljm

# Magic numbers
# Input scan rate
scanRate = 1 # Hz
scanTime = 1/scanRate # s
# Get current timestamp
ts = [0,0,0,0];ts[0] = time.time();ts[3] = time.time() 
today = dt.date.today().strftime("%Y-%m-%d")
# Output file duration
chunkTime = 900 # s
# Archival duration (604800 = weekly)
archTime = 604800 # s
fstr = 'LJdata_'
tstr = 'timestamp'    
rowSpace = 0
colSpace = 0

# Setup environment
# Define the path and output directories
PATH = os.getcwd()
DATA = os.path.join(PATH,'DATA')
LOG = os.path.join(DATA,'LOG')
CRASH = os.path.join(DATA,'CRASH')
ARCHIVE = os.path.join(DATA,'ARCHIVE')
MODULES = os.path.join(PATH,'MODULES')
PLOTS = os.path.join(PATH,'PLOTS')
# Make the directory for the data and plots
if not os.path.exists(DATA):
    os.mkdir(DATA)
if not os.path.exists(LOG):
    os.mkdir(LOG)
if not os.path.exists(CRASH):
    os.mkdir(CRASH)
if not os.path.exists(ARCHIVE):
    os.mkdir(ARCHIVE)
if not os.path.exists(MODULES):
    os.mkdir(MODULES)
if not os.path.exists(PLOTS):
    os.mkdir(PLOTS)

# Add the modules to the system path
sys.path.append(MODULES)

##############################################################################
# COMPACT THIS SECTION #######################################################
##############################################################################
# Add the sensor modules
import thermocouple
import level
import frg

# Find the names of the sensors and how many there are
sensor = {}
sensor['names'] = []
sensor['ident'] = []
for name in thermocouple.names():
    sensor['names'].append(name)
    sensor['num%s'%name] = thermocouple.number(name)
    for num in range(sensor['num%s'%name]):
        sensor['ident'].append(name+'%s'%(num+1))
for name in level.names():
    sensor['names'].append(name)
    sensor['num%s'%name] = level.number(name)
    for num in range(sensor['num%s'%name]):
        sensor['ident'].append(name+'%s'%(num+1))
for name in frg.names():
    sensor['names'].append(name)
    sensor['num%s'%name] = frg.number(name)
    for num in range(sensor['num%s'%name]):
        sensor['ident'].append(name+'%s'%(num+1))

# Pass values to buffer
def buffer_output():
    return DATA, LOG, fstr, scanRate, chunkTime, tstr, sensor['ident']
def cache_output():
    return DATA, CRASH

##############################################################################
# COMPACT THIS SECTION #######################################################       
##############################################################################

# Data stream and record
results = {}
if __name__ == '__main__':
    
    # LJ setup
    # Connect to the labjack
    LJ_dict = {}
    LJ_dict['handle_1'] = ljm.openS("any", "any", "470019751")  # [TC, K] device type, connection type, serial no.
    LJ_dict['handle_2'] = ljm.openS("ANY", "ANY", "470019220")  # [RES, FRG] device type, connection type, serial no.
    # Get LJ handle
    LJ_dict['info_1'] = ljm.getHandleInfo(LJ_dict['handle_1'])
    LJ_dict['info_2'] = ljm.getHandleInfo(LJ_dict['handle_2'])
    # Create dictionaries to store channel/registry information
    aAddresses, aDataTypes, aValues = {},{},{}
    # Find the channel/registry information for each of the sensor suites
    aAddresses.update(thermocouple.main(LJ_dict['handle_1'])[0]);aDataTypes.update(thermocouple.main(LJ_dict['handle_1'])[1]);aValues.update(thermocouple.main(LJ_dict['handle_1'])[2])
    aAddresses.update(level.main(LJ_dict['handle_2'])[0]);aDataTypes.update(level.main(LJ_dict['handle_2'])[1]);aValues.update(level.main(LJ_dict['handle_2'])[2])
    aAddresses.update(frg.main(LJ_dict['handle_2'])[0]);aDataTypes.update(frg.main(LJ_dict['handle_2'])[1]);aValues.update(frg.main(LJ_dict['handle_2'])[2])
    
    # Find crashed data
    for file in os.listdir(DATA):
        if file[-4:] == '.csv':
            os.rename(os.path.join(DATA,file),os.path.join(CRASH,file))
                
    # Launch buffer
    subprocess.run('python3 __buffer__.py &',shell=True)
    
    # Launch DAQ Loop
    while True:
        # Get time and define datafile
        ts[1] = time.time()
        shortname = 'LJdata_%i.csv'%ts[0]
        filename = os.path.join(DATA,shortname)
        # Create the datafile
        if not os.path.exists(filename):
            f = open(filename,'w+')
            f.write("# Raw data recorded on %i, with Device type: %i, Connection type: %i, Serial number: %i, IP address: %s, Port: %i, Max bytes per MB: %i" %(ts[0],LJ_dict['info_1'][0], LJ_dict['info_1'][1], LJ_dict['info_1'][2], ljm.numberToIP(LJ_dict['info_1'][3]), LJ_dict['info_1'][4], LJ_dict['info_1'][5]))
            f.write("# Raw data recorded on %i, with Device type: %i, Connection type: %i, Serial number: %i, IP address: %s, Port: %i, Max bytes per MB: %i\n" %(ts[0],LJ_dict['info_2'][0], LJ_dict['info_2'][1], LJ_dict['info_2'][2], ljm.numberToIP(LJ_dict['info_2'][3]), LJ_dict['info_2'][4], LJ_dict['info_2'][5]))
            f.write("%s"%tstr)
            for strname in sensor['ident']:
                f.write(";%s"%strname)
            f.close()
        # Write to the datafile
        if os.path.exists(filename):
            for name in sensor['names']:
                if name in thermocouple.names():
                    results[name] = ljm.eReadAddresses(LJ_dict['handle_1'], sensor['num%s'%name], aAddresses[name], aDataTypes[name])
                if name in frg.names() or name in level.names():
                    results[name] = ljm.eReadAddresses(LJ_dict['handle_2'], sensor['num%s'%name], aAddresses[name], aDataTypes[name])
            f = open(filename,'a+')
            f.write("\n%0.1f"%ts[1])
            colSpace = 1
            for name in sensor['names']:
                for j in range(sensor['num%s'%name]):
                    f.write(";%0.5f"%results[name][j])
                    colSpace += 1
            f.close()
            rowSpace += 1
        # Send datafile to DB and ARCHIVE
        if (ts[1]-ts[0]) > chunkTime:
            SUBARCH = os.path.join(ARCHIVE,today)    
            if not os.path.exists(SUBARCH):
                os.mkdir(SUBARCH)
            cachename = os.path.join(SUBARCH,'LJdata_%i.csv.gz'%ts[0])
            subprocess.run('python3 __cache__.py %s %s %s %s'%(shortname,cachename,rowSpace,colSpace),shell=True)
            rowSpace = 0;colSpace = 0
            if (ts[1]-ts[3]) > archTime:
                ts[3] = ts[1]
                today = dt.date.today().strftime("%Y-%m-%d")
            ts[0] = ts[1]
        # Wait until end of scanPeriod
        ts[2] = time.time()
        procTime = ts[2]-ts[1]
        if (scanTime-procTime) > 0:
            waitTime = scanTime-procTime
            time.sleep(waitTime)

