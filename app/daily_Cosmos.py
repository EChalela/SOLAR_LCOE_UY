import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy.stats import norm
from tqdm import tqdm
from datetime import datetime, timedelta
import time  # 📌 Importar módulo para medición de tiempo

# 📌 **Cargar datos del archivo CSV**
csv_input = "../data/clima_-34.028193_-55.393066.csv"
data = pd.read_csv(csv_input)

# 📌 **Convertir fecha y extraer año, mes, día y hora**
data['date'] = pd.to_datetime(data['date'])
data['anio'] = data['date'].dt.year
data['mes'] = data['date'].dt.month
data['dia'] = data['date'].dt.day
data['hora'] = data['date'].dt.hour  # Extraer la hora

# 📌 **Seleccionar columnas relevantes**
data = data[['date', 'anio', 'mes', 'dia', 'hora', 'shortwave_radiation']]

# 📌 **Promedio por hora de radiación de onda corta**
data_hourly = data.groupby('date').agg({'shortwave_radiation': 'sum'}).reset_index()
data_hourly['value'] = data_hourly['shortwave_radiation']
data_hourly['output'] = data_hourly['value'] * 0.153 * 6.545  # Factor eficiencia 15.3%, 6.545m²

# 📌 **Ajuste de Distribución Normal**
mu, sigma = norm.fit(data_hourly['value'])  # Ajuste a una distribución normal
print(f"📌 Parámetros de la distribución Normal: Media={mu:.2f}, Desviación={sigma:.2f}")

# 📌 **Simulación de la radiación solar 2024-2044 por Hora**
np.random.seed(1995)  # Establecer semilla para reproducibilidad

start_date = datetime(2024, 1, 1, 0, 0)  # Empezar a las 00:00
end_date = datetime(2044, 12, 31, 23, 0)  # Terminar a las 23:00
hours_to_simulate = int((end_date - start_date).total_seconds() / 3600)  # Total de horas a simular

nsim = 1000  # Número de simulaciones
sim_radiation = []

# 📌 **Iniciar medición de tiempo para la simulación**
start_sim_time = time.time()

print("🔄 Simulando series temporales (por hora)...")

for i in tqdm(range(nsim)):
    # Generar datos simulados usando la distribución ajustada (Normal)
    sim_dates = pd.date_range(start=start_date, periods=hours_to_simulate, freq='H')
    sim_values = np.random.normal(mu, sigma, hours_to_simulate)  # Generar datos sintéticos por hora

    # Crear DataFrame de simulación
    sim_df = pd.DataFrame({'date': sim_dates, 'value': sim_values, 'id': str(i)})
    sim_radiation.append(sim_df)

# 📌 **Terminar medición de tiempo para la simulación**
end_sim_time = time.time()
total_sim_time = end_sim_time - start_sim_time
sim_minutes = int(total_sim_time // 60)
sim_seconds = int(total_sim_time % 60)

# 📌 **Imprimir el tiempo total de simulación**
print(f"⏳ Tiempo total de simulación: {sim_minutes} minutos y {sim_seconds} segundos.")

# 📌 **Iniciar medición de tiempo para la combinación y guardado en CSV**
start_save_time = time.time()

print("🔄 Combinando simulaciones y guardando en archivo CSV...")

# 📌 **Combinar todas las simulaciones**
DBRadiationSimHourly = pd.concat(sim_radiation, ignore_index=True)

# 📌 **Exportar los resultados a CSV**
output_csv = "../data/salida_clima_-34.028193_-55.393066.csv"
DBRadiationSimHourly.to_csv(output_csv, index=False)

# 📌 **Terminar medición de tiempo para la combinación y guardado**
end_save_time = time.time()
total_save_time = end_save_time - start_save_time
save_minutes = int(total_save_time // 60)
save_seconds = int(total_save_time % 60)

# 📌 **Imprimir el tiempo total de combinación y guardado**
print(f"⏳ Tiempo total de combinación y guardado: {save_minutes} minutos y {save_seconds} segundos.")

print(f"✅ Simulación completada y resultados guardados en: {output_csv}")
