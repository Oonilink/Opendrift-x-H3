
#!/usr/bin/env python
"""
Fjord
=====
"""
import ssl

import certifi
import os

from datetime import datetime


ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())


from datetime import timedelta
from opendrift.readers import reader_global_landmask
from opendrift.readers import reader_netCDF_CF_generic
from opendrift.models.leeway import Leeway
from netCDF4 import Dataset, num2date
from opendrift.readers import reader_global_landmask






from opendrift.readers import reader_netCDF_CF_generic
###############################
# Test lecture fichier courants, cohérence temps et domaine
###############################
def run_simulation(wind, current, params, sim_folder):
    try:
        reader_cmems = reader_netCDF_CF_generic.Reader('simulations/data_in/curents_cmems.nc')
        print("✓ Courants: OK")
        print(f"  Variables: {reader_cmems.variables}")
        print(f"  Période: {reader_cmems.start_time} à {reader_cmems.end_time}")
        print(f"  Domaine: lon [{reader_cmems.xmin}, {reader_cmems.xmax}], "
            f"lat [{reader_cmems.ymin}, {reader_cmems.ymax}]")
    except Exception as e:
        print(f"✗ Erreur courants: {e}")

    # Test lecture fichier vent
    try:
        reader_arome = reader_netCDF_CF_generic.Reader('simulations/data_in/wind.nc')
        print("\n✓ Vent: OK")
        print(f"  Variables: {reader_arome.variables}")
        print(f"  Période: {reader_arome.start_time} à {reader_arome.end_time}")
        print(f"  Domaine: lon [{reader_arome.xmin}, {reader_arome.xmax}], "
            f"lat [{reader_arome.ymin}, {reader_arome.ymax}]")
    except Exception as e:
        print(f"✗ Erreur vent: {e}")

    # Vérifier que le point de semis est dans le domaine
    lon_seed, lat_seed = params["lon"], params["lat"]
    print(f"\nPoint de semis: lon={lon_seed}, lat={lat_seed}")



    o = Leeway(loglevel=20)  # Set loglevel to 0 for debug information
    o.set_config('general:use_auto_landmask', False)


    reader_landmask = reader_global_landmask.Reader()  # ← LIGNE 2



    #%%
    # Add readers for wind and current
    reader_arome = reader_netCDF_CF_generic.Reader(wind)
    reader_cmems = reader_netCDF_CF_generic.Reader(current)
    o.add_reader([reader_cmems, reader_arome, reader_landmask])

    #%%
    # Seed elements
    time = reader_arome.start_time
    time_common = max(reader_arome.start_time, reader_cmems.start_time)
    print("Using seed time:", time_common)
    object_type = 1  # 1: Person-in-water (PIW), unknown state (mean values)
    o.seed_elements(lon=params["lon"], lat=params["lat"], radius=50, number=20, time=time_common, object_type=object_type)

    #%%
    # Running model for 12 hours, using small time step due to high resolution coastline
    o.run(duration=timedelta(hours=int(params["duree"])), outfile=os.path.join(sim_folder, "trajectoire.nc"), time_step=300, time_step_output=3600)

    #%%
    # Print and plot results
    print(o)
   

    #%%
    # .. image:: /gallery/animations/example_fjord_0.gif

    o.plot()

    print("coucouuuuuu")




    # Running model for 12 hours
    print("Running simulation...")
    try:
        o.run(duration=timedelta(hours=12), 
            outfile='simulation_result_fjord.nc', 
            time_step=300, 
            time_step_output=3600)
        print("✓ Simulation completed successfully!")
        print(o)
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")