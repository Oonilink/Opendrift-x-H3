'''import h3 from h3
from h3.api.basic_int import (
    latlng_to_cell,
    cell_to_latlng,
    cell_to_boundary
)'''
import h3
import folium
from datetime import datetime
import numpy as np
import pandas as pd

from datetime import timedelta
from opendrift.readers import reader_global_landmask
from opendrift.readers import reader_netCDF_CF_generic
from opendrift.models.leeway import Leeway

o = Leeway(loglevel=20)  # Set loglevel to 0 for debug information

# Add readers for wind and current
reader_arome = reader_netCDF_CF_generic.Reader('data_API/data_sfc_API_fixed.nc')
reader_norkyst = reader_netCDF_CF_generic.Reader('data_API/cmems_current.nc')
o.add_reader([reader_norkyst, reader_arome])

# Seed elements
time = reader_arome.start_time
object_type = 1  # 1: Person-in-water (PIW), unknown state (mean values)
o.seed_elements(lon=10.67, lat=35.95, radius=50, number=5000, time=time, object_type=object_type)

# Running model for 12 hours, using small time step due to high resolution coastline
o.run(duration=timedelta(hours=12), time_step=300, time_step_output=3600)

# Print and plot results
print(o)
o.animation()

# .. image:: /gallery/animations/example_fjord_0.gif

o.plot()

lon_result = o.result['lon']  # Tableau 2D : [temps, particule]
lat_result = o.result['lat']  # Tableau 2D : [temps, particule]
status_result = o.result['status']  # Statut à chaque pas de temps (0=active, 1=stranded, etc.)
print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
print(lon_result)
print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
print(len(lon_result))
print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
print(lat_result)
print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
print(len(lat_result))
print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
print(status_result)
print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
print(len(status_result))
print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')


# Récupère les longitudes (tableau 2D : [trajectory, time])
lonss = lon_result.values  # Convertit en tableau NumPy
latss = lat_result.values

# Utilise pandas pour remplir les NaN avec la dernière valeur valide (par ligne)
df_lons = pd.DataFrame(lonss)
lons_sans_nan = df_lons.ffill(axis=1)  # Remplace les NaN par la dernière valeur valide sur chaque ligne
df_lats = pd.DataFrame(latss)
lats_sans_nan = df_lats.ffill(axis=1)

# Convertit le résultat en tableau NumPy
lons_final = lons_sans_nan.values
print(lons_final)  # Affiche le tableau sans NaN
print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
lats_final = lats_sans_nan.values
print(lats_final)


#lons = o.elements.lon
#lats = o.elements.lat
#print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
#print(lons)
print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
print(len(lons_final))
#print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
#print(lats)
print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
print(len(lats_final))
print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')

print("coucouuuuuu")

resolution = 9

#inti de la carte Foilum
#h3_index_init = latlng_to_cell(61.117594, 6.55, resolution)
h3_index_init = h3.latlng_to_cell(61.117594, 6.55, resolution)

#center_inti = cell_to_latlng(h3_index_init)
center_inti = h3.cell_to_latlng(h3_index_init)

print(f"Center intitialisation (lat, lng): {center_inti}")
m = folium.Map(location=center_inti, zoom_start=9)

for i in range(4999):

    # Convert coordinates to H3 index
    h3_index = h3.latlng_to_cell(lats_final[i][12], lons_final[i][12], resolution)
    print(f"H3 Index: {h3_index}")

    # Get center coordinates of the cell
    center = h3.cell_to_latlng(h3_index)
    print(f"Center (lat, lng): {center}")

    # Get boundary of the cell
    boundary = h3.cell_to_boundary(h3_index)
    boundary = [(lat, lng) for lat, lng in boundary]  # ensure (lat, lon) order
    boundary.append(boundary[0])  # close polygon

    # Map with Folium

    folium.Polygon(locations=boundary, color='green', weight=1, fill=True, fill_opacity=0.4).add_to(m)

m.save("carte_h3_test.html")