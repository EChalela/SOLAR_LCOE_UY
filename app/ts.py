import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.tsa.arima_process import ArmaProcess
from datetime import datetime, timedelta


def analyzeTS(df, column="value", dist="norm"):
    """
    Analiza una serie temporal, ajustando una distribución y calculando autocorrelaciones.
    """
    data = df[column].dropna()

    # Ajustar la distribución
    if dist == "norm":
        params = stats.norm.fit(data)
        dist_obj = stats.norm(*params)
    elif dist == "gamma":
        params = stats.gamma.fit(data)
        dist_obj = stats.gamma(*params)
    elif dist == "lognorm":
        params = stats.lognorm.fit(data)
        dist_obj = stats.lognorm(*params)
    else:
        raise ValueError(f"Distribución {dist} no soportada")

    # Calcular autocorrelaciones
    lag_acf = acf(data, nlags=40, fft=True)
    lag_pacf = pacf(data, nlags=40)

    # Estadísticas descriptivas
    stats_summary = {
        "media": np.mean(data),
        "mediana": np.median(data),
        "desviacion_std": np.std(data),
        "asimetria": stats.skew(data),
        "curtosis": stats.kurtosis(data),
        "min": np.min(data),
        "max": np.max(data)
    }

    return {"params_dist": params, "acf": lag_acf, "pacf": lag_pacf, "stats_summary": stats_summary}


def simulateTS(df, column="value", dist="norm", from_date=None, to_date=None, nsim=1000):
    """
    Simula una serie temporal basada en una distribución ajustada y autocorrelación.
    """
    data = df[column].dropna()

    # Ajustar la distribución
    if dist == "norm":
        params = stats.norm.fit(data)
        dist_obj = stats.norm(*params)
    elif dist == "gamma":
        params = stats.gamma.fit(data)
        dist_obj = stats.gamma(*params)
    elif dist == "lognorm":
        params = stats.lognorm.fit(data)
        dist_obj = stats.lognorm(*params)
    else:
        raise ValueError(f"Distribución {dist} no soportada")

    # Modelo AR(1) para autocorrelación
    acf_values = sm.tsa.acf(data, nlags=10)
    ar_params = np.array([1, -acf_values[1]])
    ma_params = np.array([1])
    arma_process = ArmaProcess(ar_params, ma_params)

    max_date = df["date"].max()
    simulation_days = (to_date - max_date).days

    if simulation_days <= 0:
        print("No es necesario realizar la simulación, el to_date ya está cubierto por los datos históricos.")
        return pd.DataFrame()

    simulated_dates = pd.date_range(start=max_date + timedelta(days=1), periods=simulation_days)
    simulated_series = []
    for i in range(nsim):
        simulated_values = arma_process.generate_sample(nsample=simulation_days)
        simulated_values = dist_obj.ppf(stats.norm.cdf(simulated_values))
        sim_df = pd.DataFrame({"date": simulated_dates, "value": simulated_values, "id": str(i)})
        simulated_series.append(sim_df)

    return pd.concat(simulated_series, ignore_index=True)


# Cargar datos desde un CSV
df = pd.read_csv("data/clima_-34.028193_-55.393066.csv")
df["date"] = pd.to_datetime(df["date"])

# Análisis de la serie temporal
resultado = analyzeTS(df, column="shortwave_radiation", dist="norm")
print("Parámetros de la distribución ajustada:", resultado["params_dist"])
print("Estadísticas descriptivas:", resultado["stats_summary"])

# Simulación de datos futuros
from_date = datetime(2024, 1, 1)
to_date = datetime(2044, 12, 31)
simulated_data = simulateTS(df, column="shortwave_radiation", dist="norm", from_date=from_date, to_date=to_date,
                            nsim=1000)

# Guardar resultados
df.to_csv("data/analisis_clima_-34.028193_-55.393066.csv", index=False)
simulated_data.to_csv("data/simulated_clima_-34.028193_-55.393066.csv", index=False)

# Graficar simulaciones
plt.figure(figsize=(12, 5))
for sim_id in np.random.choice(simulated_data['id'].unique(), 10, replace=False):
    subset = simulated_data[simulated_data['id'] == sim_id]
    plt.plot(subset['date'], subset['value'], alpha=0.3)

plt.xlabel('Fecha')
plt.ylabel('Radiación Simulada')
plt.title('Simulación de Radiación Solar (2024-2044)')
plt.grid()
plt.show()
