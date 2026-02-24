import os
from dotenv import load_dotenv

from pprint import pprint
import xarray as xr
import os
os.environ['XARRAY_NETCDF_ENGINE'] = 'netcdf4'  # ← Ajoute cette ligne AVANT copernicusmarine
import math
import copernicusmarine
import zipfile
import datetime
import json
import netCDF4
import numpy as np
import glob
import pandas as pd


def recup_data_copernicus(lat_min, lat_max, lon_min, lon_max, date_start, date_end):

    load_dotenv()

    # Prefer service env names used by copernicusmarine, fallback to legacy names
    username = os.getenv("COPERNICUSMARINE_SERVICE_USERNAME") or os.getenv("COPERNICUSMARINE_USERNAME") or os.getenv("COPERNICUSMARINE_USER")
    password = os.getenv("COPERNICUSMARINE_SERVICE_PASSWORD") or os.getenv("COPERNICUSMARINE_PASSWORD")

    if not username or not password:
        raise RuntimeError(
            "Missing Copernicus credentials. Set COPERNICUSMARINE_SERVICE_USERNAME and "
            "COPERNICUSMARINE_SERVICE_PASSWORD (or COPERNICUSMARINE_USERNAME/PASSWORD) in .env"
        )


    import copernicusmarine


    #API COURANTS

    import subprocess

    # Nettoyage
    for f in glob.glob("simulations/data_in/curents_cmems.nc"):
        if os.path.exists(f):
            os.remove(f)
            print(f"Supprimé : {f}")

    # Téléchargement via CLI
    result = subprocess.run([
        "copernicusmarine", "subset",
        "--dataset-id", "cmems_mod_glo_phy_anfc_0.083deg_PT1H-m",
        "--variable", "uo", "--variable", "vo",
        "--minimum-longitude", lon_min,
        "--maximum-longitude", lon_max,
        "--minimum-latitude", lat_min,
        "--maximum-latitude", lat_max,
        "--start-datetime", date_start,
        "--end-datetime", date_end,
        "--minimum-depth", "0.49402499198913574",  # ← Valeur exacte
        "--maximum-depth", "0.49402499198913574",  # ← Valeur exacte
        "--username", username,
        "--password", password,
        "--output-filename", "simulations/data_in/curents_cmems.nc"
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Téléchargement des courants réussi !")
    else:
        print(f"❌ Erreur : {result.stderr}")

#copernicusmarine.describe(dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m")



if __name__ == "__main__":
    parameters = { "date": "2026-02-08",
                "lat": 50.0, 
                "lon": -1.0,
                "duree": 12 }
    
    #Permet d'avoir une date de fin dynamique en fonction de la date de début et de la durée souhaitée
    
    # arrondi au jour supérieur si heure > 00:00 pour éviter les problèmes de disponibilité des données
    date_start_dt = datetime.datetime.strptime(parameters["date"], "%Y-%m-%d")

    nb_days = math.ceil(parameters["duree"] / 24)

    date_end = (date_start_dt + datetime.timedelta(days=nb_days)).strftime("%Y-%m-%d")

    recup_data_copernicus(str(parameters["lat"]-3.0), 
                        str(parameters["lat"]+3.0),
                        str(parameters["lon"]-3.0),
                        str(parameters["lon"]+3.0),
                        parameters["date"],
                        date_end)
