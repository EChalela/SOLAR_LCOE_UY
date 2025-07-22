from datetime import datetime

import PyCosmo
import pycosmos
import pandas as pd
import numpy as np
from fontTools.misc.plistlib import end_date
''''

def simular_datos_climaticos(csv_file, end_date):
    """
    Realiza una simulación Montecarlo de datos climáticos basada en los datos históricos utilizando PyCoSMoS.
    """
    print("Realizando simulación de datos climáticos...")
    df = pd.read_csv(csv_file)
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    max_date = df["date"].max()
    simulation_days = (pd.to_datetime(end_date).tz_localize(None) - max_date).days

    if simulation_days <= 0:
        print("No es necesario realizar la simulación, el end_date ya está cubierto por los datos históricos.")
        return pd.DataFrame()

    simulated_dates = pd.date_range(start=max_date + pd.Timedelta(days=1), periods=simulation_days)

    try:
        cosmos_model = pycosmos.TimeSeriesModel(df["shortwave_radiation"], distribution="norm", acs_id="fgn",
                                                seasonality="month")
        simulated_radiation = np.array([cosmos_model.simulate(size=simulation_days) for _ in range(1000)])
    except Exception as e:
        print(f"Error en la simulación con PyCoSMoS: {e}")
        return pd.DataFrame()

    simulated_data = {"date": simulated_dates}
    simulated_data["shortwave_radiation"] = np.mean(simulated_radiation, axis=0)
    simulated_data["output"] = simulated_data["shortwave_radiation"] * 0.153 * 6.545  # Eficiencia y tamaño del arreglo

    return pd.DataFrame(simulated_data)

csv_file = "../data/clima_-34.028193_-55.393066.csv"
end_date = datetime(2025, 12, 31)
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#from pycosmos import PyCoSMoS, analyzeTS, simulateTS, reportTS
from pycosmos import CosmosProject
# Crear una instancia de PyCoSMoS
from datetime import datetime, timedelta

# Crear instancia de PyCosmo
cosmo = CosmosProject(project_id='EES')
#cosmo.print_params()

# Cargar datos del archivo CSV
data = pd.read_csv("../data/clima_-34.028193_-55.393066.csv")
# Convertir la columna de fecha a datetime

# Convertir la columna de fecha a datetime
data['date'] = pd.to_datetime(data['date'])

# Extraer año, mes y día
data['anio'] = data['date'].dt.year
data['mes'] = data['date'].dt.month
data['dia'] = data['date'].dt.day

# Seleccionar columnas relevantes
data = data[['date', 'anio', 'mes', 'dia', 'shortwave_radiation']]

# Promedio diario de radiación de onda corta
data_daily = data.groupby('date').agg({'shortwave_radiation': 'sum'}).reset_index()
data_daily['output'] = data_daily['shortwave_radiation'] * 0.153 * 6.545

# Visualización rápida de la serie temporal
plt.figure(figsize=(12, 5))
plt.plot(data_daily['date'], data_daily['output'], label='Radiación Solar Diaria', color='blue')
plt.xlabel('Fecha')
plt.ylabel('Energía Generada (kWh)')
plt.title('Radiación Solar Diaria')
plt.legend()
plt.grid()
plt.show()

# Ajustar modelo utilizando PyCoSMoS
shra_adj = cosmo.analyzeTS(data_daily, dist="norm", acsID="fgn", season="month")
cosmo.reportTS(shra_adj, 'dist')
cosmo.reportTS(shra_adj, 'acs')
cosmo.reportTS(shra_adj, 'stat')

# Establecer semilla para la reproducibilidad
np.random.seed(1995)

# Simulación de la radiación
nsim = 1000
sim_radiation = []
start_date = datetime(2024, 1, 1)
end_date = datetime(2044, 12, 31)

for i in range(nsim):
    sim = cosmo.simulateTS(shra_adj, from_date=start_date, to_date=end_date)
    sim_df = pd.DataFrame({'date': pd.date_range(start=start_date, periods=len(sim), freq='D'),
                           'value': sim, 'id': str(i)})
    sim_radiation.append(sim_df)

# Combinar las simulaciones
DBRadiationSimDaily = pd.concat(sim_radiation, ignore_index=True)

# Graficar las series simuladas
plt.figure(figsize=(12, 5))
for sim_id in np.random.choice(DBRadiationSimDaily['id'].unique(), 10, replace=False):
    subset = DBRadiationSimDaily[DBRadiationSimDaily['id'] == sim_id]
    plt.plot(subset['date'], subset['value'], alpha=0.3)

plt.xlabel('Fecha')
plt.ylabel('Radiación Simulada')
plt.title('Simulación de Radiación Solar (2024-2044)')
plt.grid()
plt.show()
# Exportar resultados a CSV
DBRadiationSimDaily.to_csv("../data/salida_clima_-34.028193_-55.393066.csv", index=False)
