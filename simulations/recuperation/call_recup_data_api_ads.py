import xarray as xr
import cdsapi
import os
os.environ['XARRAY_NETCDF_ENGINE'] = 'netcdf4'

import copernicusmarine
import zipfile
import datetime
import json
import netCDF4
import numpy as np
import glob
import pandas as pd
import math



###############################################
###############################################
# Attention au fichier cdsapi, il faut que le fichier soit au bon endroit, dans le HOME
# Voir https://ads.atmosphere.copernicus.eu/how-to-api pour plus d'infos sur la configuration du fichier .cdsapirc et l'accès à l'API ADS
###############################################
###############################################


#CONFIGURATION FICHIER .CDSAPIRC


def recup_data_ads(lat_min, lat_max, lon_min, lon_max, date_start, date_end):
    """
    Récupère les données de vent depuis l'API ADS et les sauvegarde dans un fichier NetCDF opérationnel pour Opendrift
    Args:
        lat_min (str): Latitude minimale de la zone
        lat_max (str): Latitude maximale de la zone
        lon_min (str): Longitude minimale de la zone
        lon_max (str): Longitude maximale de la zone
        date_start (str): Date de début au format "YYYY-MM-DD"
        date_end (str): Date de fin au format "YYYY-MM-DD"
    return:
        None
    """
    import subprocess

    # Nettoyage des anciens fichiers
    for f in glob.glob("simulations/data_in/wind*.nc"):
        if os.path.exists(f):
            os.remove(f)
            print(f"Supprimé : {f}")




    client = cdsapi.Client()

    dataset = "cams-global-atmospheric-composition-forecasts"
    request = {
        "variable": [
            "10m_u_component_of_wind",
            "10m_v_component_of_wind"
        ],
        "date": [f"{date_start}/{date_end}"],
        "time": ["00:00"],
        "leadtime_hour": ["0","1","2","3","4","5","6","7","8","9","10","11","12"],
        "type": ["forecast"],
        "data_format": "netcdf_zip",
        "area": [lat_max, lon_min, lat_min, lon_max]
    }

    client.retrieve(dataset, request).download("simulations/data_in/wind_API.zip")

    with zipfile.ZipFile("simulations/data_in/wind_API.zip", 'r') as zip_ref:
        zip_ref.extractall("simulations/data_in/")
    print("Extraction terminée !")


    #TRANSFORMATION FICHIER VENTS ADS POUR Opendrift

    # 1. Chargement et correction du fichier
    nc = netCDF4.Dataset('simulations/data_in/data_sfc.nc', 'r')

    data_vars = {}
    coords = {}

    coords['latitude'] = nc.variables['latitude'][:]
    coords['longitude'] = nc.variables['longitude'][:]
    coords['forecast_period'] = nc.variables['forecast_period'][:]
    coords['forecast_reference_time'] = nc.variables['forecast_reference_time'][:]

    data_vars['u10'] = (['forecast_period', 'forecast_reference_time', 'latitude', 'longitude'], 
                        nc.variables['u10'][:])
    data_vars['v10'] = (['forecast_period', 'forecast_reference_time', 'latitude', 'longitude'], 
                        nc.variables['v10'][:])
    data_vars['valid_time'] = (['forecast_reference_time', 'forecast_period'], 
                                nc.variables['valid_time'][:])

    nc.close()

    dsAPI = xr.Dataset(data_vars, coords=coords)

    # 2. Crée une nouvelle dimension 'time' à partir de 'valid_time'
    time_values = dsAPI["valid_time"].values.flatten()

    # 3. Réorganise les données
    ds_stacked = dsAPI.stack(time=("forecast_reference_time", "forecast_period"))
    ds_stacked = ds_stacked.reset_index(["forecast_reference_time", "forecast_period"])

    # 4. Convertis le temps en datetime64
    time_datetime = pd.to_datetime(time_values, unit='s')
    ds_stacked = ds_stacked.assign_coords({"time": ("time", time_datetime)})

    # 5. Renomme les variables
    ds_stacked = ds_stacked.rename({"u10": "x_wind", "v10": "y_wind"})

    # 6. Ajoute les attributs CF standards
    ds_stacked['x_wind'].attrs['standard_name'] = 'eastward_wind'
    ds_stacked['x_wind'].attrs['units'] = 'm/s'
    ds_stacked['y_wind'].attrs['standard_name'] = 'northward_wind'
    ds_stacked['y_wind'].attrs['units'] = 'm/s'

    # 7. Ajoute des attributs à la coordonnée time pour CF compliance
    ds_stacked['time'].attrs['standard_name'] = 'time'
    ds_stacked['time'].attrs['axis'] = 'T'

    # 8. Sauvegarde
    ds_stacked.to_netcdf('simulations/data_in/wind.nc')

    print("Fichier corrigé créé !")
    print("Nouvelles dimensions:", ds_stacked.dims)
    print("x_wind shape:", ds_stacked['x_wind'].shape)
    print(ds_stacked)


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

    

    recup_data_ads(str(parameters["lat"]-3.0), 
                        str(parameters["lat"]+3.0),
                        str(parameters["lon"]-3.0),
                        str(parameters["lon"]+3.0),
                        parameters["date"],
                        date_end)