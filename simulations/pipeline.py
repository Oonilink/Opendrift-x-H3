import os
import hashlib
import json
import datetime
import math

from recuperation.call_recup_data_api_copernicus import recup_data_copernicus
from recuperation.call_recup_data_api_ads import recup_data_ads
from core.test_opendrift_data_n import run_simulation
from plotting.carte_interactive import create_map



RESULTS_DIR = "results/results_simulations"


def hash_params(params):
    s = json.dumps(params, sort_keys=True)
    return hashlib.md5(s.encode()).hexdigest()



def run_full_pipeline(params):

    #1️ créer identifiant unique pour params qui nomme les simulations
    sim_id = hash_params(params)

    sim_folder = os.path.join(RESULTS_DIR, sim_id)
    map_path = os.path.join(sim_folder, "map.html")

    #2️ si déjà calculé() → retourner direct
    if os.path.exists(map_path):
        return map_path

    #3️ sinon créer dossier
    os.makedirs(sim_folder, exist_ok=True)

    # sauvegarder params
    with open(os.path.join(sim_folder, "params.json"), "w") as f:
        json.dump(params, f, indent=2)

    #4️ récupérer données
    #wind = recup_data_ads(params)
    #Permet d'avoir une date de fin dynamique en fonction de la date de début et de la durée souhaitée
    # arrondi au jour supérieur si heure > 00:00 pour éviter les problèmes de disponibilité des données
    date_start_dt = datetime.datetime.strptime(params["date"], "%Y-%m-%d")
    nb_days = math.ceil(params["duree"] / 24)
    date_end = (date_start_dt + datetime.timedelta(days=nb_days)).strftime("%Y-%m-%d")

    recup_data_ads(str(params["lat"]-3.0), 
                        str(params["lat"]+3.0),
                        str(params["lon"]-3.0),
                        str(params["lon"]+3.0),
                        params["date"],
                        date_end)

        #Permet d'avoir une date de fin dynamique en fonction de la date de début et de la durée souhaitée
        # arrondi au jour supérieur si heure > 00:00 pour éviter les problèmes de disponibilité des données
    date_start_dt = datetime.datetime.strptime(params["date"], "%Y-%m-%d")
    nb_days = math.ceil(params["duree"] / 24)
    date_end = (date_start_dt + datetime.timedelta(days=nb_days)).strftime("%Y-%m-%d")

    recup_data_copernicus(str(params["lat"]-3.0), 
                        str(params["lat"]+3.0),
                        str(params["lon"]-3.0),
                        str(params["lon"]+3.0),
                        params["date"],
                        date_end)
    #current = recup_data_copernicus(params)

    #5️ lancer simulation
    #sim_file = run_simulation(wind, current, params, sim_folder)
    run_simulation("simulations/data_in/wind.nc", "simulations/data_in/curents_cmems.nc", params, sim_folder)
    #wind.nc et curents_cmems/nc sont les noms par défaut des fichiers générés par les fonctions de récupération

    #6️ créer carte
    create_map(os.path.join(sim_folder, "trajectoire.nc"), map_path)

    return map_path


if __name__ == "__main__":
    params = {
        "date": "2026-02-11",
        "lat": 45.0,
        "lon": -4.0,
        "duree": 12
    }
    run_full_pipeline(params)