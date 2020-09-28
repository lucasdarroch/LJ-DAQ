# -*- coding: utf-8 -*-
"""
Created on Wed May  13 16:59:43 2020

@author: lucasd
"""
###############################################################################
# The number of sensors
numRES = 7
# Returns the sensor names
def names():
    names = ['RES']
    return names
# Returns the number of sensors
def number(item):
    if item == 'RES':
        return numRES
###############################################################################    
# Assigns sensors to AIN through channels and registries, does extended features math
def main(handle):
    from labjack import ljm
    aAddresses = {}
    aDataTypes = {}
    aValues = {}
    # Setup AIN for EF
    # Set EF type
    aAddresses['AIN#_EF_INDEX'] = []  # [Set EF type address]
    aDataTypes['AIN#_EF_INDEX'] = []  # [Set EF type as int]
    aValues['AIN#_EF_INDEX'] = []  # [Set EF type, 0 for None]
    AINp = 0
    for i in range(numRES):
        aAddresses['AIN#_EF_INDEX'].append(9000+2*(i+AINp))
        aDataTypes['AIN#_EF_INDEX'].append(ljm.constants.UINT32)
        aValues['AIN#_EF_INDEX'].append(0)
    ljm.eWriteAddresses(handle, numRES, aAddresses['AIN#_EF_INDEX'], aDataTypes['AIN#_EF_INDEX'], aValues['AIN#_EF_INDEX'])
    # Setup and call eReadAddresses to read values from the LabJack.
    aAddresses['RES'] = []  # [Fill level]
    aDataTypes['RES'] = [] # [Data types for temperature and voltage measurements]
    # Loop over addresses
    for i in range(numRES):
        aAddresses['RES'].append(2*(i+AINp))
        aDataTypes['RES'].append(ljm.constants.FLOAT32)
    return aAddresses, aDataTypes, aValues
