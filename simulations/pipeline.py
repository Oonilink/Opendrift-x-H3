import os
import hashlib
import json

from simulations.recuperation.call_recup_data_api_copernicus import recup_data_copernicus
from simulations.recuperation.call_recup_data_api_ads import recup_data_arome_meteo_f, fusionner_uv
from simulations.core.manche_example import run_simulation
from simulations.plotting.carte_interactive import create_map


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
    wind = recup_data_arome_meteo_f(params)
    current = recup_data_copernicus(params)

    #5️ lancer simulation
    sim_file = run_simulation(wind, current, params, sim_folder)

    #6️ créer carte
    create_map(sim_file, map_path)

    return map_path


if __name__ == "__main__":
    params = {
        "date": "2026-02-08",
        "lat": 47.0,
        "lon": -1.0,
        "duree": 48
    }
    run_full_pipeline(params)