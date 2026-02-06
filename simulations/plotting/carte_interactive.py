
import ssl
import certifi
import os
import folium
import numpy as np
import pandas as pd
from folium.plugins import TimestampedGeoJson
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib

ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())
from h3.api.basic_int import latlng_to_cell, cell_to_boundary, cell_to_latlng
import xarray as xr


def create_map(fichier_nc):
    """
    Docstring pour create_map
    
    :param fichier_nc: fichier NetCDF contenant les résultats de la simulation

    """
    ######### LECTURE DU NETCDF (aucune simulation exécutée) ###########
    ds = xr.open_dataset(fichier_nc)
    lat = ds["lat"].values   # tableau [temps, particules]
    lon = ds["lon"].values

    print(ds.data_vars)
    print(" \n")
    print(lat[0].size)
    print(ds["age_seconds"])

    #Récupération de la dimension pour avoir le nombre d'objet dans la simulation
    #nb_trajectoire = ds.dims["trajectory"]
    nb_trajectoire = ds["trajectory"].size
    #Récupération du nombre d'étape
    #Comme lat est de la forme (n,p), on prend le premier element(premier objet)
    #Et on regarde combien d'étapes(de temps) il y a
    nb_epoque = lat[0].size

    # On va utiliser la première position du premier objet comme point central de la carte
    lat_init = float(lat[0,0])
    lon_init = float(lon[0,0])


    ########couleur
    # Palette tab20 avec nb_trajectoire couleurs
    cmap = matplotlib.colormaps.get_cmap("tab20")
    colors = [mcolors.to_hex(cmap(i / nb_trajectoire)) for i in range(nb_trajectoire)]






    resolution = 10
    h3_index_init = latlng_to_cell(lat_init, lon_init, resolution)
    center = cell_to_latlng(h3_index_init)


    #%%
    # .. image:: /gallery/animations/example_fjord_0.gif



    # --- INITIALISATION CARTE FOLIUM ---
    m = folium.Map(location=center, zoom_start=12)

    # On parcourt toutes les particules au premier pas de temps
    # (ou vous pouvez changer l'index temps)
    t = 0   # 0 = première étape temporelle


    # --- Construction GeoJSON pour animation ---
    features = []

    for t in range(nb_epoque-1):

        #time_value est une variable intermédiaire qui contient la date réelle du pas de temps courant, extraite depuis le fichier NetCDF
        #Elle sert à donner à Folium :non pas un index numérique (0,1,2…),
        #mais la vraie date de la simulation (2015-11-16T03:00:00, par exemple).
        #time_value est une variable intermédiaire qui contient la date réelle du pas de temps courant, extraite depuis le fichier NetCDF
        time_value = pd.to_datetime(ds["time"].values[t]).isoformat()

        for i in range(nb_trajectoire):

            la = float(lat[i, t])
            lo = float(lon[i, t])

            if np.isnan(la) or np.isnan(lo):
                continue

            # Convertir en cellule H3
            h = latlng_to_cell(la, lo, resolution)
            boundary = cell_to_boundary(h)
            coords = [(b_lon, b_lat) for (b_lat, b_lon) in boundary]

            # Fermeture du polygone
            coords.append(coords[0])

            # GeoJSON Feature

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
                },
                "properties": {
                    "time": time_value,
                    "style": {
                        "color": colors[i],
                        "fillColor": colors[i],
                        "fillOpacity": 0.6,
                        "weight": 2
                    }
                }
            })


    # --- Animation temporelle ---
    TimestampedGeoJson(
        {
            "type": "FeatureCollection",
            "features": features,
        },
        period="PT1H",              # durée entre pas de temps (ici: 1h)
        add_last_point=True,
        auto_play=False,
        loop=False,
        max_speed=1,
        loop_button=True,
        date_options="HH:mm:ss",
        time_slider_drag_update=True,
    ).add_to(m)

    """

    for t in range(nb_epoque - 1):
        for i in range(nb_trajectoire):   # pour chaque particule
            la = np.asarray(lat[i, t]).item()
            lo = np.asarray(lon[i, t]).item()

        #vérif si nan
            if np.isnan(la) or np.isnan(lo):
                continue

            # Convertit en H3
            h = latlng_to_cell(la, lo, resolution)

            # Récupère les coordonnées de la cellule H3
            boundary = cell_to_boundary(h)
            boundary = [(b_lat, b_lon) for (b_lat, b_lon) in boundary]
            boundary.append(boundary[0])  # ferme le polygone

            # Ajout à la carte
            folium.Polygon(
                locations=boundary,
                color="blue",
                weight=2,
                fill=True,
                fill_opacity=0.4
            ).add_to(m)
    """
    # Sauvegarde carte
    m.save("test_carte/carte_h3_2.html")



