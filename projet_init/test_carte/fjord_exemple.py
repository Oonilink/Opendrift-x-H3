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
import xarray as xr
import shutil
from pathlib import Path



ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())


from datetime import timedelta
from opendrift.readers import reader_global_landmask
from opendrift.readers import reader_netCDF_CF_generic
from opendrift.models.leeway import Leeway




o = Leeway(loglevel=20)  # Set loglevel to 0 for debug information






#%%
# Add readers for wind and current
reader_vent = reader_netCDF_CF_generic.Reader("data/arome_uv_2026-01-11T00:00:00Z.nc")
reader_courant = reader_netCDF_CF_generic.Reader('data_copernicus/courants_manche_atl_-9.0-3.5_43.0-52.5_2026-01-11.nc')
o.add_reader([reader_courant, reader_vent])

#%%
# Seed elements
time = reader_vent.start_time
object_type = 1  # 1: Person-in-water (PIW), unknown state (mean values)
o.seed_elements(lon=-1, lat=50, radius=50, number=10, time=time, object_type=object_type)

#%%
# Running model for 12 hours, using small time step due to high resolution coastline
o.run(duration=timedelta(hours=11), outfile='test_carte/simulation_result_fjord.nc', time_step=300, time_step_output=3600)

#%%
# Print and plot results
print(o)
o.animation()

#%%
# .. image:: /gallery/animations/example_fjord_0.gif

o.plot()

"""
final_lons = o.elements.lon
final_lats = o.elements.lat

# Temps final
final_time = o.time[-1]

# Exemple : afficher les 5 premières particules
for i in range(min(5, len(final_lons))):
    print(f"Particule {i}: lon={final_lons[i]}, lat={final_lats[i]}, temps={final_time}")

lons = o.elements.lon[-1]
lats = o.elements.lat[-1]
print(lons)
print(lats)


ds = o.get_dataset()
final_step = ds.isel(time=-1)

final_lons = final_step.lon.values
final_lats = final_step.lat.values
final_time = final_step.time.values

print("Temps final:", final_time)
print("Longitudes finales:", final_lons)
print("Latitudes finales:", final_lats)
print(ds)
"""

print("coucouuuuuu")



