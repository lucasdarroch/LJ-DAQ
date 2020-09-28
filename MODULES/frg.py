# -*- coding: utf-8 -*-
"""
Created on Wed May  6 12:31:43 2020

@author: lucasd
"""
###############################################################################
# The number of sensors
numFRG = 1
# Returns the sensor names
def names():
    names = ['FRG']
    return names
# Returns the number of sensors
def number(item):
    if item == 'FRG':
        return numFRG

###############################################################################  
# Assigns sensors to AIN through channels and registries, does extended features math
def main(handle):
    from labjack import ljm
    aAddresses = {}
    aDataTypes = {}
    aValues = {}
    # Setup and call eReadAddresses to read values from the LabJack.
    aAddresses['FRG'] = []  # [Pheifer Full Range Gauge]
    aAddresses['Voltage_FRG'] = [] # [FRG voltage]
    aDataTypes['FRG'] = [] # [Data types for pressure and voltage measurements]
    ###########################################################################
    # AIN for FRG
    AINp = 8
    AINn = AINp+1
    # Converts the FRG Voltage to deg K
    VAL = [1,10/6,-10/6*6.8]
    #VAL = [1,1,0]
    TYPE = [1,3,3]
    REG = [9000,10200,10500]
    # Clear EF dictionary entries
    aAddresses['AIN#_EF_INDEX'] = []  # [Set EF type address]
    aDataTypes['AIN#_EF_INDEX'] = []  # [Set EF type as int]
    aValues['AIN#_EF_INDEX'] = []  # [Set EF type, 1 for offset/slope]
    # Initialize EF negative channel
    aAddresses['AIN#_NEGATIVE_CH'] = []  # [Set EF negative channel for differential measurement]
    aDataTypes['AIN#_NEGATIVE_CH'] = []  # [Set EF negative channel type as int]
    aValues['AIN#_NEGATIVE_CH'] = []  # [Set EF negative channel, AIN(n+8) with MUX80]
    # Write K EF parameters
    for i in range(len(VAL)):
        aAddresses['AIN#_EF_INDEX'].append(REG[i]+2*AINp)
        aDataTypes['AIN#_EF_INDEX'].append(TYPE[i])
        aValues['AIN#_EF_INDEX'].append(VAL[i])
    aAddresses['AIN#_NEGATIVE_CH'].append(41000+i+AINp)
    aDataTypes['AIN#_NEGATIVE_CH'].append(ljm.constants.UINT16)
    aValues['AIN#_NEGATIVE_CH'].append(i+AINn)
    ljm.eWriteAddresses(handle, len(aAddresses['AIN#_EF_INDEX']), aAddresses['AIN#_EF_INDEX'], aDataTypes['AIN#_EF_INDEX'], aValues['AIN#_EF_INDEX'])
    ljm.eWriteAddresses(handle, len(['AIN#_NEGATIVE_CH']), aAddresses['AIN#_NEGATIVE_CH'], aDataTypes['AIN#_NEGATIVE_CH'], aValues['AIN#_NEGATIVE_CH'])
    # Write address for EF value
    aAddresses['FRG'].append(7000+2*AINp)
    aAddresses['Voltage_FRG'].append(7300+2*AINp)
    aDataTypes['FRG'].append(ljm.constants.FLOAT32)
    return aAddresses, aDataTypes, aValues
    ###########################################################################


























