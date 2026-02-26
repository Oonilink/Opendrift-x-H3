from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from simulations.pipeline import run_full_pipeline
import os
import json


#Configuration de Fast API
app = FastAPI()

app.mount("/app", StaticFiles(directory="app"), name="app")
app.mount("/results", StaticFiles(directory="results"), name="results")
app.mount("/public", StaticFiles(directory="public"), name="public")

templates = Jinja2Templates(directory="app/html")

RESULTS_DIR = "results/results_simulations"


def get_simulations():
    """
    Récupère la liste de toutes les simulations complètes.
    Args:
        None
    return:
        list: Liste de dictionnaires qui contiennent chacuns les paramètres d'une simulation et son identifiant
    
    """
    simulations = []
    if os.path.exists(RESULTS_DIR):
        for sim_id in os.listdir(RESULTS_DIR):
            params_path = os.path.join(RESULTS_DIR, sim_id, "params.json")
            map_path = os.path.join(RESULTS_DIR, sim_id, "map.html")
            if os.path.exists(params_path) and os.path.exists(map_path):
                with open(params_path) as f:
                    params = json.load(f)
                simulations.append({"sim_id": sim_id, "params": params})
    simulations.sort(key=lambda x: x["params"]["date"], reverse=True)
    return simulations


# -------------------------
# PAGE D'ACCUEIL = liste des simulations
# -------------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "simulations": get_simulations()}
    )


# -------------------------
# PAGE FORMULAIRE
# -------------------------
@app.get("/form", response_class=HTMLResponse)
async def form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


# -------------------------
# TRAITEMENT DU FORMULAIRE
# -------------------------
@app.post("/run", response_class=HTMLResponse)
async def run_simulation(
    request: Request,
    date: str = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    duree: int = Form(...)
):
    params = {
        "date": date,
        "lat": lat,
        "lon": lon,
        "duree": duree
    }

    print("PARAMS RECUS:", params)

    try:
        map_path = run_full_pipeline(params)
        sim_id = map_path.split("/")[-2]
    except Exception as e:
        print("ERREUR SIMULATION:", e)
        return templates.TemplateResponse(
            "form.html",
            {
                "request": request,
                "message": f"Erreur lors de la simulation: {str(e)}"
            }
        )

    # Après une simulation réussie, on redirige vers l'accueil avec la nouvelle liste
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "simulations": get_simulations(),
            "message": f"Simulation terminée ! <a href='/result/{sim_id}'>Voir la carte</a>"
        }
    )


# -------------------------
# PAGE RÉSULTATS
# -------------------------
@app.get("/result/{sim_id}", response_class=HTMLResponse)
async def show_result(request: Request, sim_id: str):
    # Lire le params.json de la simulation
    params_path = os.path.join(RESULTS_DIR, sim_id, "params.json")
    with open(params_path) as f:
        params = json.load(f)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "sim_id": sim_id,
            "map_url": f"/results/results_simulations/{sim_id}/map.html",
            "params": params
        }
    )