import os
import requests
from dotenv import load_dotenv

# ============================================================================
# RÉCUPÉRATION DES DONNÉES AROME VIA L'API MÉTÉO FRANCE
# ============================================================================
# Ce script télécharge les prévisions météorologiques du modèle AROME
# (haute résolution, 0.01°) via le service WCS (Web Coverage Service) 
# de Météo France.
#
# Données disponibles : Vent (composantes U/V, rafales), Température, 
#                       Pluie, etc. à plusieurs niveaux et échéances
#
# Authentification : Token API Météo France (portail-api.meteofrance.fr)
# ============================================================================

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupère le token d'authentification API Météo France
token = os.getenv("TOKEN_METEO_FR")

# Vérifie que le token est bien présent dans le fichier .env
if not token:
    print("✗ ERREUR : TOKEN_METEO_FR non trouvé dans .env")
    print("  Assurez-vous que .env contient : TOKEN_METEO_FR=<votre_token>")
    exit(1)

# Configure les en-têtes HTTP pour la requête
# - 'apikey' : authentification avec le token
# - 'Accept' : type de réponse attendu (données binaires)
headers = {"apikey": token, "Accept": "application/octet-stream"}

# ============================================================================
# CONFIGURATION DU PARAMÈTRE À TÉLÉCHARGER
# ============================================================================

# CoverageId identifie le paramètre météo à télécharger
# Format : PARAMÈTRE__TYPE_NIVEAU___RÉSEAU_ISO8601
# Exemple : WIND_SPEED__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND___2025-11-29T00.00.00Z
#
# Explications :
#   - WIND_SPEED : force du vent (m/s)
#   - SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND : hauteur au-dessus du sol
#   - 2025-11-29T00.00.00Z : réseau du 29 nov 2025 à 00h UTC
#
# Autres paramètres disponibles :
#   - U_COMPONENT_OF_WIND__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND (composante U)
#   - V_COMPONENT_OF_WIND__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND (composante V)
#   - TEMPERATURE__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND (température)
#   - TOTAL_WATER_PRECIPITATION__GROUND_OR_WATER_SURFACE (pluie)
#
coverage_id = "WIND_SPEED__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND___2025-11-29T00.00.00Z"

# URL de base du service WCS GetCoverage de Météo France
# Format: https://public-api.meteofrance.fr/public/arome/1.0/wcs/<modèle-WCS>/GetCoverage
base_url = ("https://public-api.meteofrance.fr/public/arome/1.0/wcs/"
            "MF-NWP-HIGHRES-AROME-001-FRANCE-WCS/GetCoverage")

# ============================================================================
# PARAMÈTRES DE LA REQUÊTE WCS
# ============================================================================

params = {
    # Identifiant du service OGC
    "service": "WCS",
    
    # Version du standard WCS utilisée
    "version": "2.0.1",
    
    # Identifiant de la couverture (paramètre météo)
    "coverageid": coverage_id,
    
    # Format de sortie : GRIB2 (format standard pour les données météo)
    # Alternative : application/geoiff pour GeoTIFF
    "format": "application/wmo-grib",
    
    # Sélection spatiale et temporelle des données
    # Subset = "dimension(valeur)" ou "dimension(min,max)"
    "subset": [
        # Échéance temporelle : 29 nov 2025 à 00h UTC
        "time(2025-11-29T00:00:00Z)",
        
        # Hauteur : 10 mètres au-dessus du sol (couche limite)
        # (obligatoire pour réduire à 2D : lat/long uniquement)
        "height(10)",
        
        # Latitude : 43°N à 52.5°N (Manche, Atlantique Nord)
        "lat(43,52.5)",
        
        # Longitude : -9°E à 3.5°E (côtes françaises + atlantique)
        "long(-9,3.5)"
    ]
}

# Chemin du fichier de sortie
# Le fichier sera au format GRIB2 (extension .nc par convention, mais c'est du GRIB)
out_file = "data/arome_2025-11-29.nc"

# ============================================================================
# TÉLÉCHARGEMENT ET SAUVEGARDE
# ============================================================================

print("Téléchargement données AROME via API Météo France...")
print(f"Coverage: {coverage_id}")
print(f"Sortie: {out_file}\n")

try:
    # Envoie la requête GET au serveur WCS
    # timeout=60 : la requête échoue si pas de réponse après 60 secondes
    r = requests.get(base_url, params=params, headers=headers, timeout=60)
    
    # Affiche le code HTTP de réponse (200 = succès)
    print(f"HTTP {r.status_code}")
    
    # Vérifie que la requête a réussi (code 200)
    if r.status_code != 200:
        print(f"\n✗ Erreur HTTP {r.status_code}")
        print(f"Réponse serveur:\n{r.text[:1000]}")
        exit(1)
    
    # Vérifie qu'il n'y a pas d'erreur WCS dans la réponse
    # (l'API peut retourner 200 mais avec une exception XML)
    if b"ExceptionReport" in r.content or b"Exception" in r.content:
        print(f"\n✗ Erreur API (exception WCS):")
        print(r.text[:1000])
        exit(1)
    
    # Crée le dossier 'data' s'il n'existe pas
    os.makedirs("data", exist_ok=True)
    
    # Sauvegarde les données reçues dans le fichier
    with open(out_file, "wb") as f:
        f.write(r.content)
    
    # Calcule et affiche la taille du fichier en MB
    size_mb = len(r.content) / (1024 * 1024)
    print(f"✓ Fichier téléchargé: {out_file}")
    print(f"  Taille: {size_mb:.2f} MB")

# Gestion des erreurs de connexion/timeout
except requests.exceptions.Timeout:
    print("✗ Erreur: délai d'attente dépassé (timeout 60s)")
    print("  Le serveur n'a pas répondu à temps")
    exit(1)

# Gestion des erreurs de connexion réseau
except requests.exceptions.ConnectionError as e:
    print(f"✗ Erreur de connexion: {e}")
    print("  Vérifiez votre connexion internet")
    exit(1)

# Gestion des autres erreurs de requête HTTP
except requests.exceptions.RequestException as e:
    print(f"✗ Erreur requête: {e}")
    exit(1)

# Gestion des erreurs inattendues
except Exception as e:
    print(f"✗ Erreur inattendue: {type(e).__name__} - {e}")
    exit(1)
