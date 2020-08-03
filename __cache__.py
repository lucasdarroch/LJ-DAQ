# -*- coding: utf-8 -*-
"""
Created on Thu May  7 18:47:35 2020

@author: lucasd
"""

import os
import sys
import gzip

import __dbfilter__ as dbfilter

# Database name
dbName = dbfilter.dbname()
filename = sys.argv[1]
cachename = sys.argv[2]

# Try to send data to the DB
try:
    import __daq2db__ as daq2db
    newname = dbfilter.deadtime(filename)
    daq2db.main(dbName,newname)
except Exception:
    pass

newname = dbfilter.deadtime(filename)

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

