
#!/usr/bin/env python
"""
Fjord
=====
"""
import ssl

import certifi
import os

from datetime import datetime
import numpy as np
import pandas as pd


ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())


from datetime import timedelta
from opendrift.readers import reader_global_landmask
from opendrift.readers import reader_netCDF_CF_generic
from opendrift.models.leeway import Leeway


import shutil
import netCDF4
ds = netCDF4.Dataset('data/norkyst800_subset_16Nov2015.nc')
print("norkyst800_subset_16Nov2015 ")
print(ds.variables.keys())
ds1 = netCDF4.Dataset('data/arome_subset_16Nov2015.nc')
print("arome_subset_16Nov2015 ")
print(ds1.variables.keys())
ds2 = netCDF4.Dataset('data/cmems_mod_glo_phy_my_0.083deg_P1D-m_1764318688812.nc')
print("cmems_mod_glo_phy_my_0.083deg_P1D-m_1764318688812 ")
print(ds2.variables.keys())


from netCDF4 import Dataset, num2date



ds = netCDF4.Dataset('data/arome_subset_16Nov2015.nc')
times = ds.variables['time']
dates = num2date(times[:], times.units)
print(dates[0], dates[-1])



ds = Dataset("data/arome_subset_16Nov2015.nc")

lat = ds.variables['latitude'][:]   # ou 'lat' selon le fichier
lon = ds.variables['longitude'][:]  # ou 'lon'
print("Latitude min / max :", np.min(lat), np.max(lat))
print("Longitude min / max :", np.min(lon), np.max(lon))


input_nc = 'data/arome_subset_16Nov2015.nc'
output_nc = 'data/arome_subset_16Nov2015_renamed.nc'

#Copie du fichier original
shutil.copy(input_nc, output_nc)

with Dataset(output_nc, 'r+') as ds:
    vars = ds.variables.keys()
    print("Variables trouvées :", vars)

    # Renommage pour OpenDrift
    if 'x_wind_10m' in vars:
        ds.renameVariable('x_wind_10m', 'x_wind')
        print("Renommé x_wind_10m → x_wind")

    if 'y_wind_10m' in vars:
        ds.renameVariable('y_wind_10m', 'y_wind')
        print("Renommé y_wind_10m → y_wind")

o = Leeway(loglevel=20)  # Set loglevel to 0 for debug information

#%%
# Add readers for wind and current
reader_arome = reader_netCDF_CF_generic.Reader('data/arome_subset_16Nov2015.nc')
reader_cmems = reader_netCDF_CF_generic.Reader('data/cmems_mod_glo_phy_my_0.083deg_P1D-m_1764318688812.nc')
o.add_reader([reader_cmems, reader_arome])

#%%
# Seed elements
time = reader_arome.start_time
time_common = max(reader_arome.start_time, reader_cmems.start_time)
print("Using seed time:", time_common)
object_type = 1  # 1: Person-in-water (PIW), unknown state (mean values)
o.seed_elements(lon=0, lat=50, radius=50, number=10, time=time_common, object_type=object_type)

#%%
# Running model for 12 hours, using small time step due to high resolution coastline
o.run(duration=timedelta(hours=12), outfile='simulation_result_fjord.nc', time_step=300, time_step_output=3600)

#%%
# Print and plot results
print(o)
o.animation()

#%%
# .. image:: /gallery/animations/example_fjord_0.gif

o.plot()

print("coucouuuuuu")



