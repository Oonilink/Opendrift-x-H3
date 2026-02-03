from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE / "public"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="public")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
