# -*- coding: utf-8 -*-
"""
Created on Wed May 13 12:48:54 2020

@author: darro
"""


import numpy as np
import matplotlib.pyplot as plt
from scipy import stats as st

data = np.recfromcsv('DATA/LJdata_1589416958.csv',comments='#',delimiter=';',skip_header=1,names=True)

npNames = ['mean','med','max','min']
stNames = ['mode','std','skew','kurt']
extra = ['skew2']#,'change']
names = npNames+stNames+extra


def statistics(data,temp):
    stat = {}
    for dat in temp:
        data[dat] = data[dat]
        stat['%s_mean'%dat] = np.mean(data[dat])
        stat['%s_med'%dat] = np.median(data[dat])
        stat['%s_mode'%dat] = st.mode(data[dat])[0][0]
        stat['%s_max'%dat] = np.max(data[dat])
        stat['%s_min'%dat] = np.min(data[dat])
        stat['%s_std'%dat] = st.tstd(data[dat])
        stat['%s_skew'%dat] = st.skew(data[dat])
        stat['%s_kurt'%dat] = st.kurtosis(data[dat])
        stat['%s_skew2'%dat] = np.abs(1-stat['%s_mode'%dat]/stat['%s_mean'%dat])*stat['%s_std'%dat]/stat['%s_mean'%dat]
#        stat['%s_skew2'%dat] = np.abs(stat['%s_mean'%dat]-stat['%s_mode'%dat])*stat['%s_std'%dat]
#        stat['%s_change'%dat] = (stat['%s_max'%dat]-stat['%s_min'%dat])/stat['%s_std'%dat]
    for dat in temp:
        grad = np.gradient(data[dat]/stat['%s_mean'%dat],data['utc_time'])
        stat['grad_%s_mean'%dat] = np.mean(grad)
        stat['grad_%s_med'%dat] = np.median(grad)
        stat['grad_%s_mode'%dat] = st.mode(grad)[0][0]
        stat['grad_%s_max'%dat] = np.max(grad)
        stat['grad_%s_min'%dat] = np.min(grad)
        stat['grad_%s_std'%dat] = st.tstd(grad)
        stat['grad_%s_skew'%dat] = st.skew(grad)
        stat['grad_%s_kurt'%dat] = st.kurtosis(grad)
#        stat['grad_%s_skew2'%dat] = np.abs(1-stat['grad_%s_mode'%dat]/stat['grad_%s_mean'%dat])*stat['grad_%s_std'%dat]/stat['grad_%s_mean'%dat]
        stat['grad_%s_skew2'%dat] = np.abs(stat['grad_%s_mean'%dat]-stat['grad_%s_mode'%dat])*stat['grad_%s_std'%dat]
#        stat['grad_%s_change'%dat] = (stat['grad_%s_max'%dat]-stat['grad_%s_min'%dat])/stat['grad_%s_std'%dat]
    return stat

def plotdata(data,names):
    plots = {}
    temp = data.dtype.names[1:]
    stat = statistics(data,temp)
    for name in names:
        plots['fig_%s'%name], plots['ax_%s'%name] = plt.subplots(1,1,figsize=(8,5))
        plots['ax_%s'%name].set_title('%s'%name)
        plots['grad_fig_%s'%name], plots['grad_ax_%s'%name] = plt.subplots(1,1,figsize=(8,5))
        plots['grad_ax_%s'%name].set_title('grad_%s'%name)
        for dat in temp:
            plots['ax_%s'%name].semilogy(dat,stat['%s_%s'%(dat,name)],'k+')
            plots['grad_ax_%s'%name].semilogy(dat,stat['grad_%s_%s'%(dat,name)],'k+')
            print(stat['grad_%s_mean'%dat],'+/-',stat['grad_%s_std'%dat])
        #plt.savefig('PLOTS/%s.png'%name)

#stat = statistics(data)       
plotdata(data,extra)
