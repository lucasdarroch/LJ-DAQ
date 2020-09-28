# -*- coding: utf-8 -*-
"""
Created on Wed May  6 12:31:43 2020

@author: lucasd
"""
###############################################################################
# The number of sensors
refK = 1;refLJ = 1
numK = refK+refLJ
numTC = 5
# Returns the sensor names
def names():
    names = ['K','TC']
    return names
# Returns the number of sensors
def number(item):
    if item == 'K':
        return numK
    if item == 'TC':
        return numTC

###############################################################################  
# Assigns sensors to AIN through channels and registries, does extended features math
def main(handle):
    from labjack import ljm
    aAddresses = {}
    aDataTypes = {}
    aValues = {}
    # Setup and call eReadAddresses to read values from the LabJack.
    aAddresses['TC'] = []  # [T-type temperature]
    aAddresses['Voltage_TC'] = [] # [T-type voltage]
    aAddresses['K'] = [] # [Reference temperature sensors]
    aDataTypes['TC'] = [] # [Data types for temperature and voltage measurements]
    aDataTypes['K'] = [] # [Data types for temperature and voltage measurements]
    ###########################################################################
    # AIN for LM34
    AINk = 13
    # Converts the LM34 Voltage to deg K
    VAL = [1,100*5/9,273.15-32*5/9]
    TYPE = [1,3,3]
    REG = [9000,10200,10500]
    # Clear EF dictionary entries
    aAddresses['AIN#_EF_INDEX'] = []  # [Set EF type address]
    aDataTypes['AIN#_EF_INDEX'] = []  # [Set EF type as int]
    aValues['AIN#_EF_INDEX'] = []  # [Set EF type, 1 for offset/slope]
    # Write K EF parameters
    for i in range(len(VAL)):
        aAddresses['AIN#_EF_INDEX'].append(REG[i]+2*AINk)
        aDataTypes['AIN#_EF_INDEX'].append(TYPE[i])
        aValues['AIN#_EF_INDEX'].append(VAL[i])
    ljm.eWriteAddresses(handle, len(aAddresses['AIN#_EF_INDEX']), aAddresses['AIN#_EF_INDEX'], aDataTypes['AIN#_EF_INDEX'], aValues['AIN#_EF_INDEX'])
    # Write address for EF value
    aAddresses['K'].append(7000+2*AINk)
    aDataTypes['K'].append(ljm.constants.FLOAT32)
    # Write address for LJ thermistor
    for i in range(refLJ):
        aAddresses['K'].append(60050+2*i)
        aDataTypes['K'].append(ljm.constants.FLOAT32)
    ###########################################################################
    # Setup AIN for T-type TC
    # TC registry value
    AINp = 0
    AINn = AINp+1
    # Alter CJC param
    REG[0] = 9600
    VAL[0] = 2*AINk
    # Initialize EF dictionary
    aAddresses['AIN#_EF_INDEX'] = []  # [Set EF type address for TC]
    aDataTypes['AIN#_EF_INDEX'] = []  # [Set EF type as int]
    aValues['AIN#_EF_INDEX'] = []  # [Set EF type, 24 for T-type]
    # Initialize EF negative channel
    aAddresses['AIN#_NEGATIVE_CH'] = []  # [Set EF negative channel for differential measurement]
    aDataTypes['AIN#_NEGATIVE_CH'] = []  # [Set EF negative channel type as int]
    aValues['AIN#_NEGATIVE_CH'] = []  # [Set EF negative channel, AIN(n+8) with MUX80]
    # Write TC EF parameters
    for i in range(numTC):
        aAddresses['AIN#_EF_INDEX'].append(9000+2*(2*i+AINp))
        aDataTypes['AIN#_EF_INDEX'].append(ljm.constants.UINT32)
        aValues['AIN#_EF_INDEX'].append(24)
        # Write CJC EF parameters
        for j in range(len(VAL)):
            aAddresses['AIN#_EF_INDEX'].append(REG[j]+2*(2*i+AINp))
            aDataTypes['AIN#_EF_INDEX'].append(TYPE[j])
            aValues['AIN#_EF_INDEX'].append(VAL[j])
#        aAddresses['AIN#_EF_INDEX'].append(9600+2*(i+AINp))
#        aDataTypes['AIN#_EF_INDEX'].append(ljm.constants.UINT32)
#        aValues['AIN#_EF_INDEX'].append(7000+2*AINk)
        aAddresses['AIN#_NEGATIVE_CH'].append(41000+2*i+AINp)
        aDataTypes['AIN#_NEGATIVE_CH'].append(ljm.constants.UINT16)
        aValues['AIN#_NEGATIVE_CH'].append(2*i+AINn)
    ljm.eWriteAddresses(handle, len(aAddresses['AIN#_EF_INDEX']), aAddresses['AIN#_EF_INDEX'], aDataTypes['AIN#_EF_INDEX'], aValues['AIN#_EF_INDEX'])
    ljm.eWriteAddresses(handle, len(['AIN#_NEGATIVE_CH']), aAddresses['AIN#_NEGATIVE_CH'], aDataTypes['AIN#_NEGATIVE_CH'], aValues['AIN#_NEGATIVE_CH'])
    # Loop over addresses
    # Thermocouple addresses
    for i in range(numTC):
        aAddresses['TC'].append(7000+2*(2*i+AINp))
        aAddresses['Voltage_TC'].append(7300+2*(2*i+AINp))
        aDataTypes['TC'].append(ljm.constants.FLOAT32)
    return aAddresses, aDataTypes, aValues

























