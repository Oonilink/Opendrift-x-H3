# Opendrift-x-H3

## Table of Contents
1. [About The Project](#about-the-project)
2. [Getting Started](#getting-started)
3. [Acknowledgments](#acknowledgments)


# About The Project

The purpose of this project is to create a tool of object drift in marine environment, using the OpenDrift Python Library and the geospatial indexing system h3. 

## Built With
There are the main frameworks/libraries we used to design the project.

<img src="https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white" /><img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" /><img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" /><img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" /><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" /><img src="https://img.shields.io/badge/Folium-77B829?style=for-the-badge&logo=folium&logoColor=white" /><img src="https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E" /><img src="https://img.shields.io/badge/json-5E5C5C?style=for-the-badge&logo=json&logoColor=white" /><img src="https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=Leaflet&logoColor=white" /><img src="https://img.shields.io/badge/Numpy-777BB4?style=for-the-badge&logo=numpy&logoColor=white" /><img src="https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white" /><img src="https://img.shields.io/badge/Reddit-FF4500?style=for-the-badge&logo=reddit&logoColor=white" /><img src="https://img.shields.io/badge/Stack_Overflow-FE7A16?style=for-the-badge&logo=stack-overflow&logoColor=white" /><img src="https://img.shields.io/badge/homebrew-FBB040?style=for-the-badge&logo=homebrew&logoColor=white" /><img src="https://img.shields.io/badge/windows%20terminal-4D4D4D?style=for-the-badge&logo=windows%20terminal&logoColor=white" /><img src="https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white" />
- <img src="" />

# Getting Started

## Installation

1. Clone the repository : 

```git clone https://github.com/github_username/repo_name.git```

3. Install packages (in a venv)
```pip install -r requirements.txt```
4. Get a free API at       AND create a copernicus account.
   
6. Enter the keys in a ```.env``` file

```
TOKEN_METEO_FR=
COPERNICUSMARINE_USERNAME=
COPERNICUSMARINE_PASSWORD=
```
6. Launch of Uvicorn into the terminal, with the command :
```uvicorn app.main:app --reload``` 

7. Acces the adress : ```http://127.0.0.1:8000```(or an other one in local) by clicking it on the terminal
```
INFO:     Will watch for changes in these directories: ['path of the file']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```


# Acknowledgments

Here is the documents that helped us to realise our project. There are among those ressources, web sites, videos, tutorials and even forum discussions.

[CDSAPI setup](https://ads.atmosphere.copernicus.eu/how-to-api )

[othneildrew/Best-README-Template](https://github.com/othneildrew/Best-README-Template )

[Comparison of FastAPI with Django and Flask, 2025. GeeksforGeeks](https://www.geeksforgeeks.org/python/comparison-of-fastapi-with-django-and-flask/ )

[deepcharts/H3-Intro](https://github.com/deepcharts/H3-Intro )

[DEMCHENKO, Denys, 2023. 9 Companies that Use FastAPI](https://www.planeks.net/companies-using-fastapi/).

[GRAVEN - DÉVELOPPEMENT, 2024. Apprendre le Python #13 - Les Environnements Virtuels (venv)](https://www.youtube.com/watch?v=Hs07URZ7TMo)

[Le guide complet du débutant avec FastAPI, Vincent Jousse](https://vincent.jousse.org/blog/fr/tech/le-guide-complet-du-debutant-avec-fastapi-partie-1/).

[Que sont les données netCDF ?—ArcGIS Pro](https://pro.arcgis.com/fr/pro-app/latest/help/data/multidimensional/what-is-netcdf-data.htm)

