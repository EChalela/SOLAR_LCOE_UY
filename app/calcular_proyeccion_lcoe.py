import requests

def calcular_lcoe_r(data_dir, input_file, capital_cost, operating_cost, energy_production, discount_rate, lifetime, projection_date):
    """
    Llama a la API de R para calcular la simulación de radiación solar y el LCOE.

    Parámetros:
        - data_dir (str): Ruta donde están los datos.
        - input_file (str): Nombre del archivo CSV de entrada.
        - capital_cost (float): Costo de capital en US$/kW.
        - operating_cost (float): Costo operativo en US$/kW/año.
        - energy_production (float): Energía producida en kWh/año.
        - discount_rate (float): Tasa de descuento en porcentaje.
        - lifetime (int): Vida útil del sistema en años.
        - projection_date (str): Fecha final de proyección en formato "YYYY-MM-DD".

    Retorna:
        - Un diccionario con el resultado de la API o un mensaje de error.
    """

    url = "http://127.0.0.1:8000/procesar"
    payload = {
        "data_dir": data_dir,
        "input_file": input_file,
        "capital_cost": capital_cost,
        "operating_cost": operating_cost,
        "energy_production": energy_production,
        "discount_rate": discount_rate,
        "lifetime": lifetime,
        "projection_date": projection_date
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Lanza un error si la respuesta no es 200 OK
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Error al conectar con la API de R: {e}"}
