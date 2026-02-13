from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from simulations import pipeline
import datetime


from simulations.pipeline import run_full_pipeline



app = FastAPI() #app est un objet de la classe FastAPI



app.mount("/app", StaticFiles(directory="app"), name="app")
#Tout ce qui est dans le dossier public/ sera accessible via l’URL
app.mount("/results", StaticFiles(directory="results"), name="results")

templates = Jinja2Templates(directory="app/html")
#mes pages HTML sont dans app/templates/



# -------------------------
# PAGE FORMULAIRE
# -------------------------
@app.get("/", response_class=HTMLResponse) # "/" = page d'accueil (sur laquelle on arrive en premier)
def form():
    return FileResponse("app/html/form.html")

# -------------------------
# TRAITEMENT DU FORMULAIRE
# -------------------------
@app.post("/run", response_class=HTMLResponse) # "/run" est l'URL sur laquelle le formulaire est envoyé (action="/run" dans le HTML)
async def run_simulation(
    # Paramètres du formulaire qu'on récupère :
    # Nom (correspond au champ name="nom" dans le formulaire HTML): son type = Form(...)
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

    # 👉 ici plus tard :
    result = pipeline.run_full_pipeline(params)

    """
    return templates.TemplateResponse(
        "form.html",
        {
            "request": request,
            "message": f"Simulation lancée avec {params}"
        }
    )
    """
    # On effectue toujours dans un bloc try/except pour gérer les erreurs qui pourraient survenir lors de la simulation (Python)
    try: 
        sim_id = run_full_pipeline(params) # Lancer la simulation et récupérer le chemin de la carte générée
        sim_id = sim_id.split("/")[-2] # on récupère juste le nom du dossier de la simulation

    except Exception as e: # Si error, on affiche un message d'erreur dans la page HTML (en récupérant le message d'erreur avec str(e))
        return templates.TemplateResponse(
            "form.html",
            {
                "request": request,
                "message": f"Erreur lors de la simulation: {str(e)}"
            }
        )
    
    return templates.TemplateResponse( # Si pas d'erreur, on affiche un message de succès avec un lien vers la page de résultats (en passant sim_id dans l'URL)
        "form.html",
        {
            "request": request,
            "message": f"Simulation terminée! <a href='/result/{sim_id}'>Voir la carte</a>"
            # /result/{sim_id} = URL de la page de résultats, avec sim_id qui est passé en paramètre pour afficher la bonne carte
        }
    )


# route pour afficher les résultats
@app.get("/result/{sim_id}", response_class=HTMLResponse)
async def show_result(request: Request, sim_id: str):

    map_url = f"/results/{sim_id}/map.html"

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "map_url": map_url
        }
    )