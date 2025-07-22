'''
import os
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import numpy as np


def obtener_datos_climaticos(lat, lon, start_date):
    """
    Obtiene datos climáticos de OpenMeteo para la latitud y longitud dadas,
    con un rango de fechas fijo hasta 2024-12-31.
    """
    # Configurar la sesión con caché y reintentos
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": "2024-12-31",  # Siempre hasta esta fecha
        "hourly": ["is_day", "sunshine_duration", "shortwave_radiation", "direct_radiation", "terrestrial_radiation",
                   "shortwave_radiation_instant", "direct_radiation_instant", "terrestrial_radiation_instant"],
        "timezone": "auto"
    }

    try:
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
    except Exception as e:
        print(f"Error en la conexión con OpenMeteo: {e}")
        return None

    # Verificar si la respuesta contiene datos
    if not response or not hasattr(response, 'Hourly') or not response.Hourly().Time():
        print("Error: No se recibieron datos válidos de OpenMeteo.")
        return None

    # Procesar datos horarios
    hourly = response.Hourly()
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True).tz_localize(None),
            periods=len(hourly.Variables(0).ValuesAsNumpy()),
            freq=pd.Timedelta(seconds=hourly.Interval())
        ),
        "is_day": hourly.Variables(0).ValuesAsNumpy(),
        "sunshine_duration": hourly.Variables(1).ValuesAsNumpy(),
        "shortwave_radiation": hourly.Variables(2).ValuesAsNumpy(),
        "direct_radiation": hourly.Variables(3).ValuesAsNumpy(),
        "terrestrial_radiation": hourly.Variables(4).ValuesAsNumpy(),
        "shortwave_radiation_instant": hourly.Variables(5).ValuesAsNumpy(),
        "direct_radiation_instant": hourly.Variables(6).ValuesAsNumpy(),
        "terrestrial_radiation_instant": hourly.Variables(7).ValuesAsNumpy()
    }

    return pd.DataFrame(data=hourly_data)


def generar_csv(lat, lon, end_date):
    """
    Genera un archivo CSV con los datos climáticos obtenidos desde 2013-01-01 hasta 2024-12-31.
    Luego se usa `end_date` para la simulación desde 2025-01-01 hasta `end_date`.
    """
    print("Generando el archivo de datos climáticos...")
    try:
        historical_data = obtener_datos_climaticos(lat, lon, "2013-01-01")
    except Exception as e:
        print(f"Error en la conexión con el servidor: {e}")
        return None

    if historical_data is None or historical_data.empty:
        print("Error: No se generó el archivo CSV debido a la falta de datos climáticos válidos.")
        return None

    # Guardar datos históricos
    os.makedirs("data", exist_ok=True)
    filename = f"data/clima_{lat}_{lon}.csv"
    historical_data.to_csv(filename, index=False)
    print("Archivo de datos climáticos generado exitosamente.")

    # Simular datos climáticos
    simulated_data = simular_datos_climaticos(filename, end_date)

    if not simulated_data.empty:
        df = pd.concat([historical_data, simulated_data], ignore_index=True)
        df.to_csv(filename, index=False)
        print("Simulación completada y datos guardados.")
    else:
        print("No se agregó simulación ya que los datos históricos ya cubren hasta el end_date.")

    return filename
'''
### desde aca andaba
# import os
# import openmeteo_requests
# import requests_cache
# import pandas as pd
# from retry_requests import retry
# import numpy as np
# import pycosmos
#
#
# def obtener_datos_climaticos(lat, lon, start_date):
#     """
#     Obtiene datos climáticos de OpenMeteo para la latitud y longitud dadas,
#     con un rango de fechas fijo hasta 2024-12-31.
#     """
#     # Configurar la sesión con caché y reintentos
#     cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
#     retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
#     openmeteo = openmeteo_requests.Client(session=retry_session)
#
#     url = "https://archive-api.open-meteo.com/v1/archive"
#     params = {
#         "latitude": lat,
#         "longitude": lon,
#         "start_date": start_date,
#         "end_date": "2024-12-31",  # Siempre hasta esta fecha
#         "hourly": ["is_day", "sunshine_duration", "shortwave_radiation", "direct_radiation", "terrestrial_radiation",
#                    "shortwave_radiation_instant", "direct_radiation_instant", "terrestrial_radiation_instant"],
#         "timezone": "auto"
#     }
#
#     try:
#         responses = openmeteo.weather_api(url, params=params)
#         response = responses[0]
#     except Exception as e:
#         print(f"Error en la conexión con OpenMeteo: {e}")
#         return None
#
#     # Verificar si la respuesta contiene datos
#     if not response or not hasattr(response, 'Hourly') or not response.Hourly().Time():
#         print("Error: No se recibieron datos válidos de OpenMeteo.")
#         return None
#
#     # Procesar datos horarios
#     hourly = response.Hourly()
#     hourly_data = {
#         "date": pd.date_range(
#             start=pd.to_datetime(hourly.Time(), unit="s", utc=True).tz_localize(None),
#             periods=len(hourly.Variables(0).ValuesAsNumpy()),
#             freq=pd.Timedelta(seconds=hourly.Interval())
#         ),
#         "shortwave_radiation": hourly.Variables(0).ValuesAsNumpy()
#     }
#
#     return pd.DataFrame(data=hourly_data)
#
#
# def simular_datos_climaticos(csv_file, end_date):
#     """
#     Realiza una simulación Montecarlo de datos climáticos basada en los datos históricos utilizando PyCoSMoS.
#     """
#     print("Realizando simulación de datos climáticos...")
#     df = pd.read_csv(csv_file)
#     df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
#     max_date = df["date"].max()
#     simulation_days = (pd.to_datetime(end_date).tz_localize(None) - max_date).days
#
#     if simulation_days <= 0:
#         print("No es necesario realizar la simulación, el end_date ya está cubierto por los datos históricos.")
#         return pd.DataFrame()
#
#     simulated_dates = pd.date_range(start=max_date + pd.Timedelta(days=1), periods=simulation_days)
#
#     try:
#         cosmos_model = pycosmos.TimeSeriesModel(df["shortwave_radiation"], distribution="norm", acs_id="fgn",
#                                                 seasonality="month")
#         simulated_radiation = np.array([cosmos_model.simulate(size=simulation_days) for _ in range(1000)])
#     except Exception as e:
#         print(f"Error en la simulación con PyCoSMoS: {e}")
#         return pd.DataFrame()
#
#     simulated_data = {"date": simulated_dates}
#     simulated_data["shortwave_radiation"] = np.mean(simulated_radiation, axis=0)
#     simulated_data["output"] = simulated_data["shortwave_radiation"] * 0.153 * 6.545  # Eficiencia y tamaño del arreglo
#
#     return pd.DataFrame(simulated_data)
#
#
# def generar_csv(lat, lon, end_date):
#     """
#     Genera un archivo CSV con los datos climáticos obtenidos desde 2013-01-01 hasta 2024-12-31.
#     Luego se usa `end_date` para la simulación desde 2025-01-01 hasta `end_date`.
#     """
#     print("Generando el archivo de datos climáticos...")
#     try:
#         historical_data = obtener_datos_climaticos(lat, lon, "2013-01-01")
#     except Exception as e:
#         print(f"Error en la conexión con el servidor: {e}")
#         return None
#
#     if historical_data is None or historical_data.empty:
#         print("Error: No se generó el archivo CSV debido a la falta de datos climáticos válidos.")
#         return None
#
#     # Guardar datos históricos
#     os.makedirs("data", exist_ok=True)
#     filename = f"data/clima_{lat}_{lon}.csv"
#     historical_data.to_csv(filename, index=False)
#     print("Archivo de datos climáticos generado exitosamente.")
#
#     # Simular datos climáticos
#     simulated_data = simular_datos_climaticos(filename, end_date)
#
#     if not simulated_data.empty:
#         df = pd.concat([historical_data, simulated_data], ignore_index=True)
#         df.to_csv(filename, index=False)
#         print("Simulación completada y datos guardados.")
#     else:
#         print("No se agregó simulación ya que los datos históricos ya cubren hasta el end_date.")
#
#     return filename

# Para pruebas locales:
# if __name__ == "__main__":
#     lat = -34.9  # Ejemplo: Montevideo
#     lon = -56.2
#     end_date = "2026-12-31"  # Año de proyección
#     generar_csv(lat, lon, end_date)

############## hasta aca andaba

import os
import pandas as pd
from openmeteo_requests import Client
import requests_cache
from retry_requests import retry
import numpy as np
import pycosmos

from app.om import obtener_datos_climaticos


def generar_csv(lat, lon, end_date):
    """
    Genera un archivo CSV con los datos climáticos obtenidos desde OpenMeteo
    y lo guarda en la carpeta `data/`. Si ya existe, no lo recalcula.
    """

    filename = f"data/clima_{lat}_{lon}.csv"

    # Si el archivo ya existe, no es necesario generarlo de nuevo
    if os.path.exists(filename):
        print(f"El archivo {filename} ya existe. Saltando generación.")
        return filename

    print("Generando el archivo de datos climáticos...")

    try:
        historical_data = obtener_datos_climaticos(lat, lon, "2013-01-01")
    except Exception as e:
        print(f"Error en la conexión con OpenMeteo: {e}")
        return None

    if historical_data is None or historical_data.empty:
        print("Error: No se generó el archivo CSV debido a la falta de datos climáticos válidos.")
        return None

    # Guardar datos
    os.makedirs("data", exist_ok=True)
    historical_data.to_csv(filename, index=False)
    print("Archivo de datos climáticos generado exitosamente.")

    return filename
