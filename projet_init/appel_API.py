import xarray as xr
import cdsapi
import copernicusmarine
import zipfile
import os


''' API COURANTS '''

copernicusmarine.subset(
  dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m",
  variables=["uo", "vo"],
  minimum_longitude=-6,
  maximum_longitude=1,
  minimum_latitude=43,
  maximum_latitude=51,
  start_datetime="2026-01-08T00:00:00",
  end_datetime="2026-01-08T12:00:00",
  minimum_depth=0.49402499198913574,
  maximum_depth=0.49402499198913574,
  username="nicolas@adicinfo.com",
  password="NBsoleil!?24coper",
  output_filename="data_API/cmems_current.nc",  # ← IMPORTANT: .nc pour NetCDF
  force_download=True
)

copernicusmarine.describe(dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m")


''' API VENTS '''

dataset = "cams-global-atmospheric-composition-forecasts"
request = {
    "variable": [
        "10m_u_component_of_wind",
        "10m_v_component_of_wind"
    ],
    "date": ["2026-01-08/2026-01-08"],
    "time": ["00:00"],
    "leadtime_hour": [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12"
    ],
    "type": ["forecast"],
    "data_format": "netcdf",
    "area": [51, -6, 43, 1]
}

# Créez le dossier data_API
os.makedirs("data_API", exist_ok=True)

config_path = os.path.expanduser("~/.cdsapirc")
if not os.path.exists(config_path):
    with open(config_path, 'w') as f:
        f.write("url: https://ads.atmosphere.copernicus.eu/api\n")
        f.write("key: f8a7a01b-071e-4fea-b710-8e8b962393f4\n")
    os.chmod(config_path, 0o600)
    print(f"✅ Fichier .cdsapirc créé: {config_path}")

'''
with zipfile.ZipFile("data_API/wind_API.zip", 'r') as zip_ref:
    zip_ref.extractall("data_API/")
print("Extraction terminée !")
'''

# Téléchargement
output_file = "data_API/data_sfc.nc"

# IMPORTANT: Supprimez l'ancien fichier s'il existe
if os.path.exists(output_file):
    print(f"⚠️ Suppression de l'ancien fichier: {output_file}")
    os.remove(output_file)

print("🔄 Téléchargement en cours...")
client = cdsapi.Client()
client.retrieve(dataset, request).download(output_file)

# Vérifiez que le téléchargement a réussi
if os.path.exists(output_file):
    file_size = os.path.getsize(output_file)
    print(f"✅ Téléchargement terminé: {file_size} bytes ({file_size/1024:.2f} KB)")
    
    # Vérifiez le header du fichier
    with open(output_file, 'rb') as f:
        header = f.read(4)
        print(f"Header du fichier: {header}")
        if header in [b'CDF\x01', b'CDF\x02', b'\x89HDF']:
            print("✅ Format NetCDF valide détecté")
        else:
            print(f"❌ Header invalide: {header.hex()}")
            print("Le fichier est probablement corrompu")
    
    # ATTENDEZ UN PEU avant d'ouvrir (parfois le fichier n'est pas totalement écrit)
    import time
    time.sleep(2)
    
    # Essayez d'ouvrir le fichier
    try:
        print("🔄 Ouverture du fichier...")
        dsAPI = xr.open_dataset(output_file)
        print("✅ Fichier ouvert avec succès!")
        print(dsAPI)
        
    except Exception as e:
        print(f"❌ Erreur lors de l'ouverture: {e}")
        
        # Essayez avec un backend alternatif
        print("🔄 Tentative avec h5netcdf...")
        try:
            dsAPI = xr.open_dataset(output_file, engine='h5netcdf')
            print("✅ Ouvert avec h5netcdf!")
            print(dsAPI)
        except Exception as e2:
            print(f"❌ h5netcdf a aussi échoué: {e2}")
            
            # Dernière tentative avec scipy
            print("🔄 Tentative avec scipy...")
            try:
                dsAPI = xr.open_dataset(output_file, engine='scipy')
                print("✅ Ouvert avec scipy!")
                print(dsAPI)
            except Exception as e3:
                print(f"❌ scipy a aussi échoué: {e3}")
                print("\n⚠️ Le fichier semble définitivement corrompu.")
                print("Suggestions:")
                print("1. Re-téléchargez avec data_format='grib' au lieu de 'netcdf'")
                print("2. Vérifiez votre connexion internet")
                print("3. Essayez de télécharger manuellement depuis le site CDS")
else:
    print(f"❌ Le fichier {output_file} n'a pas été créé")

''' TRANSFORMATION FICHIER VENTS '''

# 1. Chargez et corrigez votre fichier
dsAPI = xr.open_dataset('data_API/data_sfc.nc')
'''
# 2. Crée une nouvelle dimension 'time' à partir de 'valid_time'
time_values = dsAPI["valid_time"].values.flatten()  # Aplatit le tableau 2D en 1D

# 3. Réorganise les données pour utiliser 'time' comme dimension
ds_stacked = dsAPI.stack(time=("forecast_reference_time", "forecast_period"))

# 4. Supprime les anciennes coordonnées (qui sont maintenant des niveaux du MultiIndex)
ds_stacked = ds_stacked.reset_index(["forecast_reference_time", "forecast_period"])

# 5. Assigne les coordonnées 'time' correctes
ds_stacked = ds_stacked.assign_coords({"time": ("time", time_values)})

# 6. Renomme les variables u10/v10 en x_wind/y_wind
ds_stacked = ds_stacked.rename({"u10": "x_wind", "v10": "y_wind"})

# 7. Ajoute les attributs CF standards
ds_stacked['x_wind'].attrs['standard_name'] = 'eastward_wind'
ds_stacked['x_wind'].attrs['units'] = 'm/s'
ds_stacked['y_wind'].attrs['standard_name'] = 'northward_wind'
ds_stacked['y_wind'].attrs['units'] = 'm/s'

# 8. Sauvegarde le fichier corrigé
ds_stacked.to_netcdf('data_API/data_sfc_API_fixed.nc')

# Vérification
print("Fichier corrigé créé !")
print("Nouvelles dimensions:", ds_stacked.dims)
print("x_wind shape:", ds_stacked['x_wind'].shape)
print(ds_stacked)
'''


''' TESTS VISU '''
'''
# Charge le fichier NetCDF
ds = xr.open_dataset('data/data_sfc.nc')
dsfixed = xr.open_dataset('data/data_sfc_fixed.nc')
dsfixed2 = xr.open_dataset('data/data_sfc_fixed2.nc')
dsfixedAPI = xr.open_dataset('data/data_sfc_API_fixed.nc')
dsCurrent = xr.open_dataset('data/cmems_current.nc')

print('&&&&&&&&&&&&&&&&&&&&&&&&&&ds&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
print(ds)
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




