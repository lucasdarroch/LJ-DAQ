# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 14:23:12 2020

@author: lucasd
its a buffer
"""


import os
import sys
import time
import subprocess
import numpy as np
import datetime as dt
import __daq__ as daq

import logging
from logging.handlers import RotatingFileHandler
import traceback


# Import data from daq
# Where is the data file that will populate the buffer
DATA = daq.buffer_output()[0]
# Where should the log file go
LOG = daq.buffer_output()[1]
# What is the name of the datafile name that will populate the buffer
fstr = daq.buffer_output()[2]
# What is the scan rate for the DAQ script
scanRate = daq.buffer_output()[3]
scanTime = 1/scanRate # s
# What is the maximum datafile size?
chunkTime = daq.buffer_output()[4]
chunkSpace = int(chunkTime/scanTime)
# What is the name of the time identifier
tstr = daq.buffer_output()[5]
# What are the sensors?
sensor = {}
sensor['ident'] = daq.buffer_output()[6]

# Setup buffer
# What is the buffer filename?
buffName = 'LJbuffer.csv'
buffr = os.path.join(DATA,buffName)
# What is the buffer log filename?
buffLog = 'bufferLog_%s.txt'%dt.datetime.utcnow().timestamp()
log = os.path.join(LOG,buffLog)
# Make Log File
logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.ERROR)
handler = RotatingFileHandler(log, maxBytes=10000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# What intervals should be used for averaging the data?
avgTime = 45 # sec
avgSpace = int(avgTime/scanTime)
# How long should the buffer be open for?
buffTime = 30*60 # min*sec/min
buffSpace = int(buffTime/avgTime)
s2min = 1/60 # Convert seconds to minutes
# What time is it?
ts = [0,0]
# Data push scan rate
pushRate = 1/5 # Hz
pushTime = 1/pushRate # s

# Buffer analysis
# How many resistors have gradient for fill level analysis
resGrad = 3
# Is the gradient activated
gradStatus = True
gradCount = 0
# Is the autofill system activated
autoStatus = False
autoCount = 0

results = {}
results['ident'] = []
results['ident'].append(tstr)
for strname in sensor['ident']:
    results['ident'].append(strname)

analysis = {}
analysis['overFill'] = 'RES7'
analysis['ident'] = []
for i in range(resGrad):
    analysis['ident'].append('GRAD%s'%(i+1))

# Output to autovalve
def autovalve():
    return DATA, LOG, buffName, analysis['overFill'], analysis['ident'], avgTime

##############################################################################

if __name__ == '__main__':
    try:
        # Bad loop counter
        count = 0
        # Kill old buffer
        for file in os.listdir(DATA):
            if file[-12:] == buffr[-12:]:
                os.remove(os.path.join(DATA,file))
        N = [-1]
        while True:
            # Bad loop exit
            if count > 10:
                g = open(log,'a+')
                g.write('At %s, the buffer had failed to open the datafile %i times sequentially.\n'%(dt.datetime.utcnow().timestamp(),count))
                g.close()
                pass
            # Get time
            ts[0] = dt.datetime.utcnow().timestamp()
            # Create the datafile
            if not os.path.exists(buffr):
                f = open(buffr,'w+')
                f.write('# LJ Data Buffer. Uses a view window of %i minutes, and averages data into chunks of %i seconds.' %(buffTime*s2min,avgTime))
                f.write('\n%s'%tstr)
                for strname in sensor['ident']:
                    f.write(';%s'%strname)
                if gradStatus == True:
                    for strname in analysis['ident']:
                        f.write(';%s'%strname)
                f.close()
            # Try to find and load data file
            try:
                for file in os.listdir(DATA):
                    if file[:7] == fstr:
                        filename = file
                data = np.genfromtxt(os.path.join(DATA,filename),comments='#',delimiter=';',skip_header=1,names=True)
                count = 0
            except:
                count += 1
                time.sleep(pushTime)
                continue
            # Rowspace for data chunks
            rowSpace = data.size
            # Perform operations on data file
            n = int(rowSpace/avgSpace)
            if n == N[-1]:
                # Setup failure counter
                fail = 0
                for strname in results['ident']:
                    if data['%s'%strname].shape == ():
                        fail += 1
                    elif not data['%s'%strname][N[-1]*avgSpace:rowSpace].any():
                        fail += 1
                if not fail == 0:
                    continue
                else:
                    f = open(buffr,'r')
                    lines = f.readlines()
                    lines = lines[:-1]
                    f.close()
                    f = open(buffr,'w')
                    for line in lines:
                        f.write(line)
                    for strname in results['ident']:
                        if not strname == analysis['overFill']:
                            results['%s'%strname] = np.average(data['%s'%strname][N[-1]*avgSpace:rowSpace])
                        if strname == analysis['overFill']:
                            results['%s'%strname] = max(data['%s'%strname][N[-1]*avgSpace:rowSpace])
                        if strname == tstr:
                            f.write('%.5f'%results['%s'%strname])
                        if not strname == tstr:
                            f.write(';%.5f'%results['%s'%strname])
                    f.close()
            else:
                # Remove oldest entry if buffer is full
                if len(N) > buffSpace:
                    if gradStatus == True:
                        gdata = np.genfromtxt(buffr,comments='#',delimiter=';',skip_header=1,names=True,usecols=np.arange(len(results['ident'])))
                        for strname in analysis['ident']:
                            analysis['%s'%strname] = np.gradient(gdata['RES%s'%(analysis['ident'].index(strname)+1)],avgTime)
                    f = open(buffr,'r')
                    lines = f.readlines()
                    if gradStatus == True:
                        line2index = 2
                        if not gradCount == 0:
                            for strname in analysis['ident']:
                                lines[-1] += ';%.5f'%(analysis['%s'%strname][-1])
                        if gradCount == 0:
                            for j in range(len(lines)):
                                if j > 1:
                                    for strname in analysis['ident']:
                                        lines[j] = lines[j].rstrip()
                                        lines[j] += ';%.5f'%(analysis['%s'%strname][j-line2index])
                                if (j > 0 and j != (len(lines)-1)):
                                    lines[j] += '\n'
                            gradCount += 1
                    lines = lines[:2]+lines[3:]
                    f.close()
                    f = open(buffr,'w')
                    for line in lines:
                        f.write(line)
                    f.close()
                    N = N[1:]
                    if (autoStatus == True and autoCount == 0):
                        subprocess.run('python3 __autovalve__.py &',shell=True)
                        autoCount += 1
                # Setup failure counter
                fail = 0
                # Add new index
                N.append(n)
                for strname in results['ident']:
                    if data['%s'%strname].shape == ():
                        fail += 1
                    elif not data['%s'%strname][N[-1]*avgSpace:rowSpace].any():
                        fail += 1
                if not fail == 0:
                    f = open(buffr,'r')
                    lines = f.readlines()
                    line = lines[-1]
                    f.close()
                    f = open(buffr,'a')
                    f.write('\n%s'%line)
                    f.close()
                    continue
                else:
                    # Open buffer file
                    f = open(buffr,'a')
                    for strname in results['ident']:
                        if not strname == analysis['overFill']:
                            results['%s'%strname] = np.average(data['%s'%strname][N[-1]*avgSpace:rowSpace])
                        if strname == analysis['overFill']:
                            results['%s'%strname] = max(data['%s'%strname][N[-1]*avgSpace:rowSpace])
                        if strname == tstr:
                            f.write('\n%.5f'%results['%s'%strname])
                        if not strname == tstr:
                            f.write(';%.5f'%results['%s'%strname])
                    f.close()
            # Wait until end of scanPeriod
            ts[1] = dt.datetime.utcnow().timestamp()
            procTime = ts[1]-ts[0]
            if (scanTime-procTime) > 0:
                waitTime = scanTime-procTime
                time.sleep(waitTime)
    except Exception as e:
        logger.error(str(e))
        logger.error(traceback.format_exc())






