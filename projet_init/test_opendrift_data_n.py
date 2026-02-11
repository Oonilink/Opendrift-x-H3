
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



from netCDF4 import Dataset, num2date




o = Leeway(loglevel=20)  # Set loglevel to 0 for debug information

#%%
# Add readers for wind and current
reader_arome = reader_netCDF_CF_generic.Reader('simulations/data_in/wind.nc')
reader_cmems = reader_netCDF_CF_generic.Reader('simulations/data_in/curents_cmems.nc')
o.add_reader([reader_cmems, reader_arome])

#%%
# Seed elements
time = reader_arome.start_time
time_common = max(reader_arome.start_time, reader_cmems.start_time)
print("Using seed time:", time_common)
object_type = 1  # 1: Person-in-water (PIW), unknown state (mean values)
o.seed_elements(lon=-1, lat=47, radius=50, number=10, time=time_common, object_type=object_type)

#%%
# Running model for 12 hours, using small time step due to high resolution coastline
o.run(duration=timedelta(hours=12), outfile='simulation_result_fjord.nc', time_step=300, time_step_output=3600)

#%%
# Print and plot results
print(o)
#o.animation()

#%%
# .. image:: /gallery/animations/example_fjord_0.gif

#o.plot()

print("coucouuuuuu")



