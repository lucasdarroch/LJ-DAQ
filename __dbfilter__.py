# -*- coding: utf-8 -*-
"""
Created on Tue May 12 18:07:35 2020

@author: lucasd
"""
import numpy as np
from scipy import stats as st

# Returns the DB name
def dbname():
    return 'ets'
# Determines the condition for switching on the deadtime filter
def condition(sensor,time):
    # Magic numbers
    skew = 1E-6
    gskew = 1E-6
    k = 0
    mean = np.average(sensor)
    mode = st.mode(sensor)[0][0]
    std = st.tstd(sensor)
    grad = np.gradient(sensor,time)/mean
    gmean = np.average(grad)
    gmode = st.mode(grad)[0][0]
    gstd = st.tstd(grad)
    if np.abs(1-mode/mean)*np.abs(std/mean) > skew:
        k += 1
    if np.abs(gmean-gmode)*gstd > gskew:
        k += 1
    return k
# Inputs a csv file, runs filter, writes newfile, returns newfile address
def deadtime(filename,rowSpace):
    data = np.genfromtxt(filename,comments='#',delimiter=';',skip_header=1,names=True)
    time = data[data.dtype.names[0]]
    colSpace = len(data.dtype.names)
    k = 0
    for j in range(1,colSpace):
        sensor = data[data.dtype.names[j]]
        k += condition(sensor,time)
        if k > 0:
            break
    if k == 0:
        newname = filename[:-4]+'_filter'+filename[-4:]
        f = open(newname,'w+')
        f.write("# Data processed by the deadtime filter\n")
        f.write("%s"%data.dtype.names[0])
        for j in range(1,colSpace):
            f.write(";%s"%data.dtype.names[j])
        avTime = np.average(time)
        f.write("\n%.5f"%avTime)
        for j in range(1,colSpace):
            val = np.average(data[data.dtype.names[j]])
            f.write(";%.5f"%val)
        f.close()
        rowSpace = 1
    else:
        newname = filename
    return newname, rowSpace
