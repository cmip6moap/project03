#!/usr/bin/env python3

# Read o2 and estimate AOU
from itertools import chain
from glob import glob

import matplotlib.pyplot as plt
import xarray as xr
import numpy as np

# READ files for oxygen, piControl run
dir_o2 = '/badc/cmip6/data/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Omon/o2/gn/latest'
dataset_o2 = xr.open_mfdataset(dir_o2 + '/*.nc')

# READ files for temperature, piControl run
dir_T = '/badc/cmip6/data/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Omon/thetao/gn/latest'
dataset_T = xr.open_mfdataset(dir_T + '/*.nc')

# READ files for salinity, piControl run
dir_S = '/badc/cmip6/data/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Omon/so/gn/latest'
dataset_S = xr.open_mfdataset(dir_S + '/*.nc')

# If you want assign variables for simplicity (you do not need to)
lon=dataset_o2['longitude']
lat=dataset_o2['latitude']
oxygen = dataset_o2['o2']
time=dataset_o2['time']
T=dataset_T['thetao']
S=dataset_S['so']

# function Estimate the saturated oxygen
def o2sat(T,S):
    T1 = (T + 273.15) / 100;
    # o2 from mmol m-3 to UM/kg assume a density of 1025
    # but we can refine that estimating the actual density
    # o2_kg = (1E-3 * o2 / 1025 ) *1E6

    osat = -177.7888 + 255.5907 / T1 + 146.4813 * np.log(T1) - 22.2040 * T1;
    osat = osat + S * (-0.037362 + T1 * (0.016504 - 0.0020564 * T1));
    osat = np.exp(osat);
    # o2_sat from ml/kg to mmol/m^-3  
    # assume a density of 1025
    # but we can refine that estimating the actual density
    osat = osat * 1025 / 22.392;
    return osat

oxygen_sat = o2sat(T,S)

AOU = oxygen_sat - oxygen

# check if is consistent with o2sat from file
dir_sat = '/badc/cmip6/data/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Omon/o2sat/gn/latest'
dataset_sat = xr.open_mfdataset(dir_sat + '/*.nc')
ox_sat_OR = dataset_sat['o2sat']
