# -*- coding: utf-8 -*-
"""
Created on Wed May  13 16:59:43 2020

@author: lucas darroch
"""
import numpy as np

# Returns the DB name
def dbname():
    return 'ETS'
# Assigns sensors to AIN through channels and registries, does extended features math
def main(handle,numTC,numK):
    from labjack import ljm
    aAddresses = {}
    aDataTypes = {}
    aValues = {}
    # Setup AIN0-AIN10 for T-type TC
    # Set TC type
    aAddresses['AIN#_EF_INDEX'] = []  # [Set TC type address]
    aDataTypes['AIN#_EF_INDEX'] = []  # [Set TC type as int]
    aValues['AIN#_EF_INDEX'] = []  # [Set TC type, 24 for T-type]
    # Set negative channel
    aAddresses['AIN#_NEGATIVE_CH'] = []  # [Set TC negative channel for differential measurement]
    aDataTypes['AIN#_NEGATIVE_CH'] = []  # [Set TC negative channel type as int]
    aValues['AIN#_NEGATIVE_CH'] = []  # [Set TC negative channel, AIN(n+1)]
    TC_AINp = 48
    TC_AINn = TC_AINp+8
    for i in range(numTC):
        aAddresses['AIN#_EF_INDEX'].append(9000+2*(i+TC_AINp))
        aDataTypes['AIN#_EF_INDEX'].append(ljm.constants.UINT32)
        aValues['AIN#_EF_INDEX'].append(24)
        aAddresses['AIN#_NEGATIVE_CH'].append(41000+i+TC_AINp)
        aDataTypes['AIN#_NEGATIVE_CH'].append(ljm.constants.UINT16)
        aValues['AIN#_NEGATIVE_CH'].append(i+TC_AINn)
    ljm.eWriteAddresses(handle, numTC, aAddresses['AIN#_EF_INDEX'], aDataTypes['AIN#_EF_INDEX'], aValues['AIN#_EF_INDEX'])
    ljm.eWriteAddresses(handle, numTC, aAddresses['AIN#_NEGATIVE_CH'], aDataTypes['AIN#_NEGATIVE_CH'], aValues['AIN#_NEGATIVE_CH'])
    # Setup and call eReadAddresses to read values from the LabJack.
    aAddresses['TC'] = []  # [T-type temperature]
    aAddresses['Voltage_TC'] = [] # [T-type voltage]
    aAddresses['TEMPERATURE_DEVICE_K'] = [] # [Reference temperature sensors]
    aDataTypes['TC'] = [] # [Data types for temperature and voltage measurements]
    aDataTypes['TEMPERATURE_DEVICE_K'] = [] # [Data types for temperature and voltage measurements]
    # Loop over addresses
    for i in range(numTC):
        aAddresses['TC'].append(7000+2*(i+TC_AINp))
        aAddresses['Voltage_TC'].append(7300+2*(i+TC_AINp))
        aDataTypes['TC'].append(ljm.constants.FLOAT32)
    for i in range(numK):
        aAddresses['TEMPERATURE_DEVICE_K'].append(60050+2*i)
        aDataTypes['TEMPERATURE_DEVICE_K'].append(ljm.constants.FLOAT32)
    return aAddresses, aDataTypes, aValues