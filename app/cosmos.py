from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Importar las funciones convertidas a Python
from analyze_ts_module import analyze_ts, report_ts, simulate_ts  # Suponiendo que guardaste las funciones en un módulo

# 📌 Cargar datos desde CSV
csv_file = "../data/clima_-34.028193_-55.393066.csv"
data = pd.read_csv(csv_file)

# 📌 Convertir la columna de fecha a datetime
data['date'] = pd.to_datetime(data['date'])

# 📌 Seleccionar columnas relevantes
data = data[['date', 'shortwave_radiation']]

# 📌 Promedio diario de radiación de onda corta
data_daily = data.groupby('date').agg({'shortwave_radiation': 'sum'}).reset_index()
data_daily['output'] = data_daily['shortwave_radiation'] * 0.153 * 6.545  # Factor de eficiencia y tamaño del arreglo

# **✅ Corrección: Renombrar la columna 'shortwave_radiation' a 'value'**
data_daily = data_daily.rename(columns={'shortwave_radiation': 'value'})

# 📊 **Visualización rápida de la serie temporal**
plt.figure(figsize=(12, 5))
plt.plot(data_daily['date'], data_daily['output'], label='Radiación Solar Diaria', color='blue')
plt.xlabel('Fecha')
plt.ylabel('Energía Generada (kWh)')
plt.title('Radiación Solar Diaria')
plt.legend()
plt.grid()
plt.show()

# 📌 **Ajustar modelo de series temporales con analyze_ts()**
shra_adj = analyze_ts(data_daily, season="month", dist="norm", acsID="fgn")

# 📌 **Generar reportes del ajuste**
report_ts(shra_adj, 'dist')  # Reporte de distribución
report_ts(shra_adj, 'acs')   # Reporte de autocorrelación
report_ts(shra_adj, 'stat')  # Reporte de estadísticas descriptivas

# 📌 **Medición de tiempo de simulación**
start_time = datetime.now()  # Marca de inicio

# 📌 **Simulación de series temporales**
np.random.seed(1995)  # Semilla para reproducibilidad

start_date = datetime(2024, 1, 1)
end_date = datetime(2044, 12, 31)
nsim = 1000  # Número de simulaciones

sim_radiation = []
for i in range(nsim):
    sim_df = simulate_ts(shra_adj, from_date=start_date, to_date=end_date)
    sim_df['id'] = str(i)  # Identificador de simulación
    sim_radiation.append(sim_df)

# 📌 **Combinar todas las simulaciones**
DBRadiationSimDaily = pd.concat(sim_radiation, ignore_index=True)

# 📌 **Calcular tiempo total de simulación**
end_time = datetime.now()  # Marca de fin
elapsed_time = end_time - start_time
print(f"⏳ Tiempo total de simulación: {elapsed_time}")

# 📊 **Graficar las series simuladas**
plt.figure(figsize=(12, 5))
for sim_id in np.random.choice(DBRadiationSimDaily['id'].unique(), 10, replace=False):
    subset = DBRadiationSimDaily[DBRadiationSimDaily['id'] == sim_id]
    plt.plot(subset['date'], subset['value'], alpha=0.3)

plt.xlabel('Fecha')
plt.ylabel('Radiación Simulada')
plt.title('Simulación de Radiación Solar (2024-2044)')
plt.grid()
plt.show()

# 📌 **Exportar los resultados a CSV**
DBRadiationSimDaily.to_csv("../data/salida_clima_-34.028193_-55.393066.csv", index=False)

print("✅ Simulación completada y resultados guardados en CSV.")
