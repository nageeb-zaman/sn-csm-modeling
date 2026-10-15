#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 15:20:24 2016

@author: Gururaj Wagle

Commonly used functions, some borrowed from internet
"""
import numpy as np
from scipy.interpolate import interp1d

# =============================================================================
# Input: Path to mesa.dayNNN_post_Lbol_max.data file
# Returns np.ndarray object with profile properties
# =============================================================================
def load_stella_prof(file):
    dt_stella_prof=np.dtype([('ind',int),('m_cell_g',float),('m_center_g',float),
                      ('r_center_cm',np.double),('v_center_cmps',float),
                      ('avg_rho',float),
                      ('Prad',float),('Tavg',float),('Trad',float),
                      ('avg_opa',float),('tau',float),('m_outer_g',float),
                      ('r_outer_cm',float),('h1',float),('he3',float),
                      ('he4',float),('c12',float),('n14',float),('o16',float),
                      ('ne20',float),('na23',float),('mg24',float),('si28',float),
                      ('s32',float),('ar36',float),('ca40',float),('ti44',float),
                      ('cr48',float),('cr60',float),('fe52',float),('fe54',float),
                      ('fe56',float),('co56',float),('ni56',float),('Lum',float),
                      ('n_bar',float),('n_e',float)])

    print("\nReading the input file %s\n" % (file))

    data_stella = np.loadtxt(file,skiprows=7,dtype=dt_stella_prof)

# ...........................................#
# Edit by Nageeb Zaman
# Checking to see if there are duplicate data in Radius in stella output
# If duplicate data is present call refine_data function to get rid of them interpolate the the data
    duplicate_data_ind = []
    l = len(data_stella['ind'])
    count = 0
    for i in range(1,l):
        if(data_stella['r_center_cm'][i] == data_stella['r_center_cm'][i-1]):
            count = count + 1
            duplicate_data_ind.append(i)
    if(count > 0):
        print("Duplicate data (n=%d) found in radius" % count)
        print("Truncating the duplicate data and interploiating them..")
        data_stella = refine_data(data_stella)
        

    return data_stella
#

# Edit by Nageeb Zaman  =======================================================
# Input: Raw data array from the stella file
# Returns np.ndarray where the duplicate data has been truncated and interpolated.
# =============================================================================
def refine_data(data_stella):

    l = len(data_stella['ind']) 
    unique_z_num = []
    unique_r_center = []

    for i in range(1,l):
            if(data_stella['r_center_cm'][i] != data_stella['r_center_cm'][i-1]):
                unique_z_num.append(i)
                unique_r_center.append(data_stella['r_center_cm'][i])

    inter = interp1d(unique_z_num,unique_r_center,kind = 'linear',fill_value="extrapolate")
    data_stella['r_center_cm'] = inter(data_stella['ind'])

    for i in range(0,l-1):
        data_stella['r_outer_cm'][i] = 0.5*(data_stella['r_center_cm'][i]+data_stella['r_center_cm'][i+1])
    data_stella['r_outer_cm'][l-1] = data_stella['r_center_cm'][l-1]
    
    return data_stella
#


# =============================================================================
# Find index to the nearest value from an array
# =============================================================================
def find_nearest_ind(array,value):
    dd = [(abs(a-value),idx) for (idx,a) in enumerate(array)]
    dd.sort()
    # idx = np.searchsorted(array, value, side="left")
    # if idx > 0 and (idx == len(array) or
    #                 math.fabs(value - array[idx-1]) <
    #                 math.fabs(value - array[idx])):
    #     return idx-1
    # else:
    #    return idx
    return dd[0][1]
#
# =============================================================================
# Safe log to avoid divided by zero error
# =============================================================================
def safe_log(x):
    if x <= 0:
        return 0
    return np.log10(x)
#
# =============================================================================
# Safe log of an array to avoid divided by zero error
# =============================================================================
def safe_log_array(x):
    y = np.zeros(x.shape)
    if len(x.shape)==1:
        for i in range(len(x)):
            if x[i]<=0:
                y[i] = np.nan
            else:
                y[i] = np.log10(x[i])
    elif len(x.shape)==2:
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                if x[i,j]<=0:
                    y[i,j] = np.nan
                else:
                    y[i,j] = np.log10(x[i,j])
    else:
        print("1d or 2d arrays only")
        return
    return y
#
# =============================================================================
# Check if string has a number
# =============================================================================
def hasNum(string):
    return any(char.isdigit() for char in string)
#
# =============================================================================
# Function to replace a line in a file
# =============================================================================
def replace_line(file,line_number,text):
    with open(file) as f:
        lines = f.readlines()
        if line_number <=len(lines):
            lines[line_number-1] = text+"\n"
            with open(file,"w") as f:
                for line in lines:
                    f.write(line)
        else:
            print("line %d not in %s, it has %d lines"
                  % (line_number,file,len(lines)))
#
