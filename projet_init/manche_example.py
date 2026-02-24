#!/usr/bin/env python
"""
Fjord
=====
Simulation PIW avec vent AROME et courants Copernicus.
"""

import ssl
import certifi
from datetime import timedelta
from opendrift.readers import reader_netCDF_CF_generic
from opendrift.models.leeway import Leeway
import xarray as xr

# Force usage du certificat correct pour HTTPS
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())




def run_simulation():

    # Initialisation du modèle Leeway
    o = Leeway(loglevel=20)  # 0 pour debug complet


    input_file = "data_copernicus/courants_manche_atl_-9.0-3.5_43.0-52.5_2026-01-11.nc"
    output_file = "data_copernicus/courants_opendrift_ready.nc"

    ds = xr.open_dataset(input_file)

    # Sélection du niveau surface (profondeur la plus proche de zéro)
    ds_surf = ds.isel(depth=0, drop=True)

    # Renommage des variables pour OpenDrift
    ds_surf = ds_surf.rename({
        "uo": "eastward_sea_water_velocityy",
        "vo": "northward_sea_water_velocity"
    })


    # Sauvegarde du fichier final
    ds_surf.to_netcdf(output_file)

    print("Fichier converti avec succès :", output_file)



    # ------------------------------------------------------------------
    # Readers pour vent et courant
    # ------------------------------------------------------------------
    reader_vent = reader_netCDF_CF_generic.Reader("data/arome_uv_2026-01-11T00:00:00Z.nc")
    reader_courant = reader_netCDF_CF_generic.Reader("data_copernicus/courants_opendrift_ready.nc")

    # Ajouter les readers au modèle
    o.add_reader(reader_vent)
    o.add_reader(reader_courant)

    # ------------------------------------------------------------------
    # Seed elements
    # ------------------------------------------------------------------
    time = reader_vent.start_time  # synchronise avec le vent
    object_type = 1  # Person-in-water (PIW)
    o.seed_elements(lon=-1, lat=50, radius=50, number=10, time=time, object_type=object_type)

    # ------------------------------------------------------------------
    # Lancer la simulation
    # ------------------------------------------------------------------
    o.run(
        duration=timedelta(hours=11),
        outfile='test_carte/simulation_result_fjord.nc',
        time_step=300,
        time_step_output=3600
    )

    # ------------------------------------------------------------------
    # Résultats
    # ------------------------------------------------------------------
    print(o)
    o.plot()        # Carte statique
    o.animation()   # Animation si désirée

    # Extraction des positions finales
    ds = o.get_dataset()
    final_step = ds.isel(time=-1)
    final_lons = final_step.lon.values
    final_lats = final_step.lat.values
    final_time = final_step.time.values

    print("Temps final:", final_time)
    print("Longitudes finales:", final_lons)
    print("Latitudes finales:", final_lats)
