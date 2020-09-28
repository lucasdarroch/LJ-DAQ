# -*- coding: utf-8 -*-
"""
Created on Thu May  7 18:47:35 2020

@author: lucasd
"""

import os
import sys
import gzip

import __daq__ as daq
import __dbfilter__ as dbfilter
import __daq2db__ as daq2db

# Path
DATA, CRASH = daq.cache_output()
# Database name
dbName = dbfilter.dbname()
 
def argv():
    return dbName, DATA, CRASH

def batch(DATA,newname):
    #print('batch starting')
    # How many entries can be uploaded at a time
    lim = 4300
    # How many rows of data can be uploaded at a time
    r0 = int(lim/colSpace)-1
    # How many iterations to upload all the data (int+remainder)
    N = int(rowSpace/r0)
    # Open the filtered data to be uploaded
    f = open(newname,'r')
    # Find the lines of data
    lines =  f.readlines()
    f.close()
    # If there is more than one block to be uploaded
    if N > 0:
        # Iterate of blocks
        for i in range(int(N)):
            # Temporarily store the block name
            temp = shortname[:-4]+'_proc%s.csv'%i
            g = open(os.path.join(DATA,temp),'w+')
            # Write the sensor names
            g.write(lines[dNames])
            # Write the lines of data
            for j in range(dStart+i*r0,dStart+(i+1)*r0):
                g.write(lines[j])
            g.close()
            # Upload the block
            try:
                daq2db.upload(temp)
            except:
                print('db push failed')
                pass
            # Delete the block
            os.remove(os.path.join(DATA,temp))
    # This section is for the data that does not fill a block
    temp = shortname[:-4]+'_proc%s.csv'%N
    g = open(os.path.join(DATA,temp),'w+')
    g.write(lines[dNames])
    for j in range(dStart+int(N)*r0,dStart+rowSpace):
        g.write(lines[j])
    g.close()
    try:
        daq2db.upload(temp)
    except Exception:
        print('db push failed')
        pass
    os.remove(os.path.join(DATA,temp))

if __name__ == "__main__":
    # Input variables from __main__
    shortname = sys.argv[1]
    cachename = sys.argv[2]
    rowSpace = int(sys.argv[3])
    colSpace = int(sys.argv[4])
    # Absolute path to data
    filename = os.path.join(DATA,shortname)
    # What line in the data file contains the sensor names
    dNames = 1
    # What line does the data begin on
    dStart = 2
    # Try to send data to the DB
    try:
        #print('starting filter')
        newname, rowSpace = dbfilter.deadtime(filename,rowSpace)
        #print('filter passed')
        #if os.path.exists(newname):
        #    print('newname exists')
        batch(DATA,newname)
        #print('batch passed')
    except Exception:
        print('DB push failed')
        pass
    #print(filename)
    #if os.path.exists(filename):
        #print('filename path exists')
    # Archive the data
    with open(filename,'rb') as f, gzip.open(cachename,'wb+') as g:
        for line in f:
            g.write(line)
    # Cleanup
    os.remove(filename)
    try:
        os.remove(newname)
    except Exception:
        pass




