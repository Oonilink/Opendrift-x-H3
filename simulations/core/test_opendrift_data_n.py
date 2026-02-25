
#!/usr/bin/env python

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
    """
    Exécute une simulation Opendrift avec les données de vent et courants fournies
    Args:
        wind (str): Chemin vers le fichier NetCDF de vent
        current (str): Chemin vers le fichier NetCDF de courants
        params (dict): Dictionnaire contenant les paramètres de la simulation (lat, lon, date, durée)
        sim_folder (str): Dossier de sauvegarde des résultats de la simulation
    return:
        None (sauvegarde les résultats de la simulation dans sim_folder)
    """


    # Test lecture fichier vent et courants, cohérence temps et domaine

    try:
        reader_cmems = reader_netCDF_CF_generic.Reader('simulations/data_in/curents_cmems.nc')
        print("✓ Courants: OK")
        print(f"  Variables: {reader_cmems.variables}")
        print(f"  Période: {reader_cmems.start_time} à {reader_cmems.end_time}")
        print(f"  Domaine: lon [{reader_cmems.xmin}, {reader_cmems.xmax}], "
            f"lat [{reader_cmems.ymin}, {reader_cmems.ymax}]")
    except Exception as e:
        print(f"✗ Erreur courants: {e}")

    try:
        reader_arome = reader_netCDF_CF_generic.Reader('simulations/data_in/wind.nc')
        print("\n Vent: OK")
        print(f"  Variables: {reader_arome.variables}")
        print(f"  Période: {reader_arome.start_time} à {reader_arome.end_time}")
        print(f"  Domaine: lon [{reader_arome.xmin}, {reader_arome.xmax}], "
            f"lat [{reader_arome.ymin}, {reader_arome.ymax}]")
    except Exception as e:
        print(f" Erreur vent: {e}")

    # Vérifier que le point de semis est dans le domaine
    lon_seed, lat_seed = params["lon"], params["lat"]
    print(f"\nPoint de semis: lon={lon_seed}, lat={lat_seed}")



    o = Leeway(loglevel=20)  # Set loglevel to 0 for debug information
    o.set_config('general:use_auto_landmask', False)

    reader_landmask = reader_global_landmask.Reader()


    # Add readers for wind and current
    reader_arome = reader_netCDF_CF_generic.Reader(wind)
    reader_cmems = reader_netCDF_CF_generic.Reader(current)
    o.add_reader([reader_cmems, reader_arome, reader_landmask])

    
    # Seed elements
    time = reader_arome.start_time
    time_common = max(reader_arome.start_time, reader_cmems.start_time)
    print("Using seed time:", time_common)
    object_type = 1  # 1: Person-in-water (PIW), unknown state (mean values)
    o.seed_elements(lon=params["lon"], lat=params["lat"], radius=50, number=20, time=time_common, object_type=object_type)

    # Running model for x hours, using small time step due to high resolution coastline
    o.run(duration=timedelta(hours=int(params["duree"])), outfile=os.path.join(sim_folder, "trajectoire.nc"), time_step=300, time_step_output=3600)

    try:
        print("\nRunning simulation...")
        o.run(duration=timedelta(hours=int(params["duree"])), outfile=os.path.join(sim_folder, "trajectoire.nc"), time_step=300, time_step_output=3600)
        print("Simulation completed successfully")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")


    # Print and plot results
    #print(o)
    #o.plot()
