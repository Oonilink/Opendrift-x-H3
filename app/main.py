from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from simulations.pipeline import run_full_pipeline

app = FastAPI()

# Montage des fichiers statiques (sans doublons)
app.mount("/app", StaticFiles(directory="app"), name="app")
app.mount("/results", StaticFiles(directory="results"), name="results")
app.mount("/public", StaticFiles(directory="public"), name="public")

templates = Jinja2Templates(directory="app/html")


# -------------------------
# PAGE FORMULAIRE
# -------------------------
@app.get("/", response_class=HTMLResponse)
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

    return templates.TemplateResponse(
        "form.html",
        {
            "request": request,
            "message": f"Simulation terminée ! <a href='/result/{sim_id}'>Voir la carte</a>"
        }
    )


# -------------------------
# PAGE RÉSULTATS
# -------------------------
@app.get("/result/{sim_id}", response_class=HTMLResponse)
async def show_result(request: Request, sim_id: str):
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "sim_id": sim_id,
            "map_url": f"/results/results_simulations/{sim_id}/map.html"
        }
    )