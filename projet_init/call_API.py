import xarray as xr
import cdsapi
import os
os.environ['XARRAY_NETCDF_ENGINE'] = 'netcdf4'  # ← Ajoute cette ligne AVANT copernicusmarine

import copernicusmarine
import zipfile

import json
import netCDF4
import numpy as np
import glob
import pandas as pd


'''
#TEST
33.13
14.60
37.85
8.63
'''




#CONFIGURATION FICHIER .CDSAPIRC

url = "https://ads.atmosphere.copernicus.eu/api"
key = "340ed7ce-a15e-47e4-9559-5b38c9c1269a"

config_path = os.path.expanduser("/home/nbeuno26/.cdsapirc")

try:
    # Créez ou écrasez le fichier
    with open(config_path, 'w') as f:
        f.write(f"url: {url}\n")
        f.write(f"key: {key}\n")

    print(f"Fichier .cdsapirc créé/mis à jour: {config_path}")

    # Vérifiez le contenu
    with open(config_path, 'r') as f:
        print("\nContenu du fichier:")
        print(f.read())


except Exception as e:
    print(f"Erreur lors de la création du fichier: {e}")

#PSEUDO ET MDP COPERNICUS

pseudo_mdp_file = "data_API/pseudo_mdp.json"
if not os.path.exists(pseudo_mdp_file):
    json.dump({"pseudo": "?", "password": "?"}, open(pseudo_mdp_file, 'w'))
pseudo_mdp = json.load(open(pseudo_mdp_file))


#API COURANTS

import subprocess

# Nettoyage
for f in glob.glob("data_API/cmems_current*.nc"):
    if os.path.exists(f):
        os.remove(f)
        print(f"Supprimé : {f}")

# Téléchargement via CLI
result = subprocess.run([
    "copernicusmarine", "subset",
    "--dataset-id", "cmems_mod_glo_phy_anfc_0.083deg_PT1H-m",
    "--variable", "uo", "--variable", "vo",
    "--minimum-longitude", "9",
    "--maximum-longitude", "14",
    "--minimum-latitude", "33",
    "--maximum-latitude", "37",
    "--start-datetime", "2026-02-03T00:00:00",
    "--end-datetime", "2026-02-03T12:00:00",
    "--minimum-depth", "0.49402499198913574",  # ← Valeur exacte
    "--maximum-depth", "0.49402499198913574",  # ← Valeur exacte
    "--username", pseudo_mdp['pseudo'],
    "--password", pseudo_mdp['password'],
    "--output-filename", "data_API/cmems_current.nc"
], capture_output=True, text=True)

if result.returncode == 0:
    print("✅ Téléchargement des courants réussi !")
else:
    print(f"❌ Erreur : {result.stderr}")

#copernicusmarine.describe(dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m")


#API VENTS

client = cdsapi.Client()

dataset = "cams-global-atmospheric-composition-forecasts"
request = {
    "variable": [
        "10m_u_component_of_wind",
        "10m_v_component_of_wind"
    ],
    "date": ["2026-02-03/2026-02-03"],
    "time": ["00:00"],
    "leadtime_hour": ["0","1","2","3","4","5","6","7","8","9","10","11","12"],
    "type": ["forecast"],
    "data_format": "netcdf_zip",
    "area": [37, 9, 33, 14]
}

client.retrieve(dataset, request).download("data_API/wind_API.zip")

with zipfile.ZipFile("data_API/wind_API.zip", 'r') as zip_ref:
    zip_ref.extractall("data_API/")
print("Extraction terminée !")


#TRANSFORMATION FICHIER VENTS

#TRANSFORMATION FICHIER VENTS

# 1. Chargez et corrigez votre fichier
nc = netCDF4.Dataset('data_API/data_sfc.nc', 'r')

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

# 4. ✅ Convertis le temps en datetime64
time_datetime = pd.to_datetime(time_values, unit='s')
ds_stacked = ds_stacked.assign_coords({"time": ("time", time_datetime)})

# 5. Renomme les variables
ds_stacked = ds_stacked.rename({"u10": "x_wind", "v10": "y_wind"})

# 6. Ajoute les attributs CF standards
ds_stacked['x_wind'].attrs['standard_name'] = 'eastward_wind'
ds_stacked['x_wind'].attrs['units'] = 'm/s'
ds_stacked['y_wind'].attrs['standard_name'] = 'northward_wind'
ds_stacked['y_wind'].attrs['units'] = 'm/s'

# 7. ✅ Ajoute des attributs à la coordonnée time pour CF compliance
ds_stacked['time'].attrs['standard_name'] = 'time'
ds_stacked['time'].attrs['axis'] = 'T'

# 8. Sauvegarde
ds_stacked.to_netcdf('data_API/data_sfc_API_fixed.nc')

print("Fichier corrigé créé !")
print("Nouvelles dimensions:", ds_stacked.dims)
print("x_wind shape:", ds_stacked['x_wind'].shape)
print(ds_stacked)



''' TESTS VISU '''
'''
# Charge le fichier NetCDF
ds = xr.open_dataset('data/data_sfc.nc')
dsfixed = xr.open_dataset('data/data_sfc_fixed.nc')
dsfixed2 = xr.open_dataset('data/data_sfc_fixed2.nc')
dsfixedAPI = xr.open_dataset('data/data_sfc_API_fixed.nc')
dsCurrent = xr.open_dataset('data/cmems_current.nc')

print('&&&&&&&&&&&&&&&&&&&&&&&&&&ds&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
#print(ds)
print('&&&&&&&&&&&&&&&&&&&&&&&&&&dsAPI&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
print(dsAPI)
print('&&&&&&&&&&&&&&&&&&&&&&&&&&dsfixed&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
print(dsfixed)
print('&&&&&&&&&&&&&&&&&&&&&&&&&&dsfixed&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
print(dsfixed2)
print('&&&&&&&&&&&&&&&&&&&&&&&&&&dsfixedAPI&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
print(dsfixedAPI)
print('&&&&&&&&&&&&&&&&&&&&&&&&&&dsCurrent&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
print(dsCurrent)
'''




