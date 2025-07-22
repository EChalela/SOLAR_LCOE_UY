import os
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

def obtener_datos_climaticos(lat, lon, end_date):
    """
    Obtiene datos climáticos de OpenMeteo para la latitud y longitud dadas,
    con un rango de fechas desde 2013-01-01 hasta el end_date proporcionado.
    """
    start_date = "2013-01-01"

    # Configurar la sesión con caché y reintentos
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": [
            "is_day", "sunshine_duration", "shortwave_radiation", "direct_radiation", "terrestrial_radiation",
            "shortwave_radiation_instant", "direct_radiation_instant", "terrestrial_radiation_instant"
        ],
        "timezone": "auto"
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    # Procesar datos horarios
    hourly = response.Hourly()
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )
    }

    # Asignar valores a las variables
    variables = [
        "is_day", "sunshine_duration", "shortwave_radiation", "direct_radiation", "terrestrial_radiation",
        "shortwave_radiation_instant", "direct_radiation_instant", "terrestrial_radiation_instant"
    ]

    for i, var in enumerate(variables):
        hourly_data[var] = hourly.Variables(i).ValuesAsNumpy()

    return pd.DataFrame(data=hourly_data)

def generar_csv(lat, lon, end_date):
    """
    Genera un archivo CSV con los datos climáticos obtenidos.
    """
    df = obtener_datos_climaticos(lat, lon, end_date)

    if df is not None:
        os.makedirs("datos", exist_ok=True)
        filename = f"datos/clima_{lat}_{lon}_{end_date}.csv"
        df.to_csv(filename, index=False)
        print(f"Archivo CSV generado: {filename}")
        return filename
    else:
        print("No se generó el archivo CSV debido a un error en la obtención de datos.")
        return None

# Para pruebas locales:
if __name__ == "__main__":
    lat = -34.9  # Ejemplo: Montevideo
    lon = -56.2
    end_date = "2026-12-31"  # Año de proyección
    generar_csv(lat, lon, end_date)