from itertools import chain
from glob import glob

import os
import xarray as xr
import numpy as np

def compute_remineralisation_master(expc_data_loc,expc_data_name,timeslice_times,areafile):
        # INPUTS
        # expc_data_loc - full path to netcdf file
        # expc_data_name - netcdf file name
        # timeslices_times - start and finish times of timesclice averaging in pairs, e.g., ["1960","1970"] or ["1960","1970","1980","1990"]


        # OUTPUTS
        # te_timeseries_expc_data_name.nc
        # te_timeslice_start_timeslice_finish_expc_data_name.nc

        ### hard coded user options
        export_horizon=100 # export horizon (m)
        poc_horizon=1000 # te depth horizon (m)

        print('>>> loading data')
        ### load data
        poc=xr.open_mfdataset(expc_data_loc+expc_data_name)

        ### get arrays
        epc100=poc.sel(lev=100,method='nearest')['expc']
        POC_at_horizon=poc.sel(lev=1000,method='nearest')['expc']

        print('>>> calculating annual averages (sloooow)')
        ### annual averaging
        # compute here to save memory in following steps
        epc_data=epc100.rolling(time=12, center=True).mean().compute()
        POC_data=POC_at_horizon.rolling(time=12, center=True).mean().compute()

        print('>>> calculating transfer efficiency')
        ### calculate transfer efficiency
        # MA
        #division = lambda x, y: x / y
        #te = xr.apply_ufunc(division, POC_data, epc_data,dask='parallelized')
        # JDW
        te=POC_data/epc_data

        # calculate e-folding depth
        # in progress - see Rui!

        print('>>> output data')
        # convert to global mean timeseries
        if len(areafile) == 1:
                # without area weighting
                te_timeseries=te.mean(dim=['i','j'])
                te_timeseries.to_netcdf('te_timeseries_'+expc_data_name)

                else:
                # weight by area
                area = xr.open_mfdataset(areafile)
                area_data = area['areacello']
                area_data.compute()
                weights = area_data/area_data.sum(dim=['i','j'])
                weights = weights.fillna(0)
                weighted_te = te.weighted(weights)
                # convert to global mean timeseries
                te_timeseries=weighted_te.sum(dim=['i','j'])
                te_timeseries.to_netcdf('te_timeseries_'+expc_data_name)



        # get timeslice data
        years=te.time.dt.year
        for n in range(0,len(timeslice_times),2):

                if (years==int(timeslice_times[n])).any and (years==int(timeslice_times[n+1])).any:
                        te_timeslice=te.sel(time=slice(timeslice_times[n], timeslice_times[n+1])).mean(dim='time')
                        te_timeslice.to_netcdf('te_'+timeslice_times[n]+'_'+timeslice_times[n+1]+expc_data_name)

        ###### END #####

### set path to folder containing the data ###
path = '/gws/pw/j05/cop26_hackathons/bristol/project03/input_nc/multimodel/ssp370/'

### list of files in the folder ###
files = os.listdir(path)
# take only those that start with 'expc'
files = [files[i] for i in range(len(files)) if files[i][0:4] == 'expc']

for ifile in files:
        print(ifile)

        areafile = '0' #for now without area weighting to be consistent

#       if 'UKESM' in ifile:
#               areafile = '/badc/cmip6/data/CMIP6/CMIP/MOHC/UKESM1-0-LL/piControl/r1i1p1f2/Ofx/areacello/gn/latest/areacello_Ofx_UKESM1-0-LL_piControl_r1i1p1f2_gn.nc'
#       elif 'MPI-ESM1-2-HR' in ifile:
#               areafile = '/badc/cmip6/data/CMIP6/CMIP/MPI-M/MPI-ESM1-2-HR/piControl/r1i1p1f2/Ofx/areacello/gn/latest/areacello_Ofx_MPI-ESM1-2-HR_piControl_r1i1p1f2_gn.nc'
#       elif 'MPI-ESM1-2-LR' in ifile:
#               areafile = '/badc/cmip6/data/CMIP6/CMIP/MPI-M/MPI-ESM1-2-LR/piControl/r1i1p1f2/Ofx/areacello/gn/latest/areacello_Ofx_MPI-ESM1-2-LR_piControl_r1i1p1f2_gn.nc'
#       elif 'IPSL-CM6A-LR' in ifile:
#               areafile = '/badc/cmip6/data/CMIP6/CMIP/IPSL/IPSL-CM6A-LR/piControl/r1i1p1f2/Ofx/areacello/gn/latest/areacello_Ofx_IPSL-CM6A-LR_piControl_r1i1p1f2_gn.nc'
#       elif 'IPSL-CM5A2-INCA' in ifile:
#               areafile = '/badc/cmip6/data/CMIP6/CMIP/IPSL/IPSL-CM5A2-INCA/piControl/r1i1p1f2/Ofx/areacello/gn/latest/areacello_Ofx_IPSL-CM5A2-INCA_piControl_r1i1p1f2_gn.nc'
#       elif 'CMCC-ESM2' in ifile:
#               areafile = '/badc/cmip6/data/CMIP6/CMIP/CMCC/CMCC-ESM2/piControl/r1i1p1f2/Ofx/areacello/gn/latest/areacello_Ofx_CMCC-ESM2_piControl_r1i1p1f2_gn.nc'
#       else:
#               areafile = '0'


        compute_remineralisation_master(path,ifile,['2015','2025','2090','2100'],areafile)

                                                                                                                                                                                                                1,1           Top
