from opendrift.models.oceandrift import OceanDrift
from datetime import datetime, timedelta

# Initialise le modèle
o = OceanDrift(loglevel=30)  # loglevel=30 pour moins de logs

# Initialise des particules (exemple minimal)
o.seed_elements(lon=4.5, lat=60.0, number=10, time=datetime.now())

# Exécute la simulation
o.run(duration=timedelta(hours=1), time_step=600)

# Affiche les résultats
print("Simulation terminée !")
print(f"Nombre de particules : {len(o.elements.lon)}")
o.plot()  # Génère une carte des trajectoires
