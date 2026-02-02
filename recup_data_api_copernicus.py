import os
from dotenv import load_dotenv

from pprint import pprint


def recup_data_copernicus(lat_min, lat_max, lon_min, lon_max, date_start, date_end):

    load_dotenv()

    # Prefer service env names used by copernicusmarine, fallback to legacy names
    username = os.getenv("COPERNICUSMARINE_SERVICE_USERNAME") or os.getenv("COPERNICUSMARINE_USERNAME") or os.getenv("COPERNICUSMARINE_USER")
    password = os.getenv("COPERNICUSMARINE_SERVICE_PASSWORD") or os.getenv("COPERNICUSMARINE_PASSWORD")

    if not username or not password:
        raise RuntimeError(
            "Missing Copernicus credentials. Set COPERNICUSMARINE_SERVICE_USERNAME and "
            "COPERNICUSMARINE_SERVICE_PASSWORD (or COPERNICUSMARINE_USERNAME/PASSWORD) in .env"
        )

    # Export both legacy and service variable names so copernicusmarine won't prompt
    os.environ["COPERNICUSMARINE_SERVICE_USERNAME"] = username
    os.environ["COPERNICUSMARINE_SERVICE_PASSWORD"] = password
    os.environ["COPERNICUSMARINE_USERNAME"] = username
    os.environ["COPERNICUSMARINE_PASSWORD"] = password

    import copernicusmarine


    #catalogue_001_024 = copernicusmarine.describe(product_id="GLOBAL_ANALYSISFORECAST_PHY_001_024", disable_progress_bar=True)
    #for dataset in catalogue_001_024.products[0].datasets:
    #    print(dataset.dataset_id)

    #catalogue_001_024 = copernicusmarine.describe(product_id="GLOBAL_MULTIYEAR_PHY_001_030", disable_progress_bar=True)
    #for dataset in catalogue_001_024.products[0].datasets:
    #    print(dataset.dataset_id)

    lat_min = float(lat_min)
    lat_max = float(lat_max)
    lon_min = float(lon_min)
    lon_max = float(lon_max)


    copernicusmarine.subset(
        dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m",  # dataset avec courants
        variables=["uo", "vo"],                          # on ne prend que les courants
        minimum_longitude=lon_min,
        maximum_longitude=lon_max,
        minimum_latitude=lat_min,
        maximum_latitude=lat_max,
        start_datetime=date_start,
        end_datetime=date_end,
        minimum_depth=0,          # surface
        maximum_depth=5,          # près de surface
        output_filename = f"courants_manche_atl_{lon_min}-{lon_max}_{lat_min}-{lat_max}_{date_start}.nc",
        output_directory="data_copernicus"
    )



if __name__ == "__main__":
    recup_data_copernicus("43.0", "52.5", "-9.0", "3.5", "2026-01-11", "2026-01-12")