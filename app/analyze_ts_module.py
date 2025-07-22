import numpy as np
import pandas as pd
from scipy.stats import *
#import scipy.stats as stats, norm, beta
from statsmodels.tsa.stattools import acf
from scipy.optimize import curve_fit

def actf(rhox, b, c):
    """
    Función de transformación de autocorrelación.
    """
    return ((1 + b * rhox) ** (1 - c) - 1) / ((1 + b) ** (1 - c) - 1)

def fitactf(actpnts, discrete=False):
    """
    Ajusta la función actf a los puntos de autocorrelación.

    Parámetros:
        actpnts (pd.DataFrame): DataFrame con columnas 'rhoz' y 'rhox'.
        discrete (bool, opcional): Si es True, utilizar una versión discreta de actf (a definir si necesario).

    Retorna:
        dict: Contiene los coeficientes ajustados 'b' y 'c' y los puntos de entrada 'actfpoints'.
    """

    # Datos de entrada para el ajuste
    rhox = actpnts["rhox"].values
    rhoz = actpnts["rhoz"].values

    # Valores iniciales para b y c
    initial_params = [1, 0]

    # Límites para los parámetros
    bounds = ([0.001, 0], [np.inf, np.inf])

    # Ajuste de la función actf a los puntos de autocorrelación
    params, _ = curve_fit(actf, rhox, rhoz, p0=initial_params, bounds=bounds)


def analyze_ts(TS, season='month', dist='gamma', acsID='weibull', n_points=30, lag_max=30):
    """
    Analiza una serie temporal ajustando distribuciones y autocorrelaciones.

    Parámetros:
    - TS: DataFrame con 'date' y 'value'.
    - season: Periodicidad de la serie ('month', 'week', etc.).
    - dist: Tipo de distribución ('gamma', 'beta', etc.).
    - acsID: Identificador del modelo de autocorrelación.
    - n_points: Número de puntos para ajuste.
    - lag_max: Máximo lag para autocorrelación.

    Retorna:
    - Diccionario con los datos ajustados.
    """

    # 1️⃣ Calcular autocorrelación estacional
    empirical_acf = acf(TS['value'], nlags=lag_max, fft=True)

    # 2️⃣ Ajustar la autocorrelación empírica
    fitted_acf = stats.exponweib.fit(empirical_acf)  # Simulación de ajuste Weibull

    # 3️⃣ Dividir los datos por estación
    TS['season'] = TS['date'].dt.month if season == 'month' else TS['date'].dt.week
    seasonal_groups = TS.groupby('season')

    # 4️⃣ Ajustar distribuciones a cada estación
    fitted_dists = {}
    for s, group in seasonal_groups:
        params = stats.gamma.fit(group['value'])  # Ejemplo con distribución gamma
        fitted_dists[s] = params

    return {
        "data": TS,
        "dist_fits": fitted_dists,
        "acf_fits": fitted_acf
    }


import matplotlib.pyplot as plt


def report_ts(analyzed_ts, method='dist'):
    """
    Genera reportes de la serie analizada.

    Parámetros:
    - analyzed_ts: Salida de analyze_ts().
    - method: Tipo de reporte ('stat', 'dist', 'acs').

    Retorna:
    - Gráficos o tablas según lo seleccionado.
    """

    if method == 'stat':
        print("Estadísticas Descriptivas:\n", analyzed_ts["data"].describe())

    elif method == 'dist':
        # Graficar la distribución ajustada vs empírica
        plt.figure(figsize=(8, 6))
        for season, params in analyzed_ts["dist_fits"].items():
            x = np.linspace(0, max(analyzed_ts["data"]['value']), 100)
            fitted = stats.gamma.pdf(x, *params)
            plt.plot(x, fitted, label=f'Season {season}')

        plt.hist(analyzed_ts["data"]['value'], bins=30, density=True, alpha=0.4, color='gray', label='Empirical')
        plt.legend()
        plt.title("Distribución Ajustada vs. Empírica")
        plt.show()

    elif method == 'acs':
        # Graficar autocorrelaciones
        lags = range(len(analyzed_ts["acf_fits"]))
        plt.figure(figsize=(8, 6))
        plt.plot(lags, analyzed_ts["acf_fits"], marker='o', linestyle='--', label='Ajustada')
        plt.title("Autocorrelación Estacional Ajustada")
        plt.xlabel("Lag")
        plt.ylabel("Autocorrelación")
        plt.legend()
        plt.show()

# def simulate_ts(analyzed_ts, from_date=None, to_date=None):
#     """
#     Simula una nueva serie temporal basada en los análisis previos.
#
#     Parámetros:
#     - analyzed_ts: Salida de analyze_ts().
#     - from_date: Fecha de inicio (formato 'YYYY-MM-DD').
#     - to_date: Fecha de fin (formato 'YYYY-MM-DD').
#
#     Retorna:
#     - DataFrame con la serie simulada.
#     """
#
#     simulated_dates = pd.date_range(from_date, to_date, freq='D')
#     simulated_values = []
#
#     for date in simulated_dates:
#         season = date.month  # Asumimos estacionalidad mensual
#         params = analyzed_ts["dist_fits"].get(season, (1, 1))  # Parámetros por estación
#         value = stats.gamma.rvs(*params)  # Generar valor aleatorio
#         simulated_values.append(value)
#
#     return pd.DataFrame({'date': simulated_dates, 'value': simulated_values})
#

import numpy as np
import pandas as pd
from scipy.special import erfcinv
from scipy.integrate import quad


def moments(dist, distarg, raw=False, central=True, coef=False, distbounds=(-np.inf, np.inf), p0=0, order=[1, 2]):
    """
    Calcula los momentos estadísticos de la distribución dada.
    """
    if dist == "beta":
        a, b = distarg["a"], distarg["b"]
        mu1 = a / (a + b)
        mu2 = (a * (a + 1)) / ((a + b) * (a + b + 1))
    else:
        mu1 = distarg["mean"]
        mu2 = distarg["var"] + mu1 ** 2  # Segundo momento central
    return [{"mu1": mu1, "mu2": mu2}]


def acti(x, y, rhoz, p0, dist, distarg):
    """
    Función de correlación activa.
    """
    return x * y * rhoz  # Simplificación, reemplazar con función correcta si necesario

def actf(rhox, b, c):
    """
    Calcula rhoz en función de rhox, b y c.

    Parámetros:
        rhox (float o array): Valor de rhox.
        b (float): Parámetro de ajuste.
        c (float): Parámetro de ajuste.

    Retorna:
        float o array: Valor de rhoz.
    """
    rhoz = ((1 + b * rhox) ** (1 - c) - 1) / ((1 + b) ** (1 - c) - 1)
    return rhoz

def actpnts(margdist, margarg, p0=0, distbounds=(-np.inf, np.inf)):
    """
    Calcula puntos de correlación activa según la distribución marginal.

    Parámetros:
        margdist (str): Tipo de distribución ("beta", "normal", etc.).
        margarg (dict): Parámetros de la distribución.
        p0 (float): Probabilidad de cero.
        distbounds (tuple): Límites de la distribución.

    Retorna:
        pd.DataFrame: DataFrame con valores de rhoz y rhox.
    """

    # Definir la tabla de rhoz inicial
    rho = pd.DataFrame({
        "rhoz": np.concatenate((np.arange(0.1, 1.0, 0.1), [0.95])),
        "rhox": np.zeros(10)
    })

    # Determinar límites de integración
    _min = -7.5 if p0 == 0 else -np.sqrt(2) * erfcinv(2 * p0)
    _max = 7.5

    # Obtener momentos estadísticos de la distribución
    m = moments(dist=margdist, distarg=margarg, raw=False, central=True, coef=False, distbounds=distbounds, p0=p0,
                order=[1, 2])

    # Calcular rhox
    for i in range(len(rho)):
        rhoz_value = rho.loc[i, "rhoz"]

        def inner_integral(y):
            return quad(lambda x: acti(x, y, rhoz_value, p0, margdist, margarg), _min, _max, limit=10000, epsrel=1e-5)[
                0]

        temp = quad(lambda y: inner_integral(y), _min, _max, limit=10000, epsrel=1e-5)[0]

        # Calcular rhox
        rho.loc[i, "rhox"] = (temp - m[0]["mu1"] ** 2) / m[0]["mu2"]

    return rho


import numpy as np
import pandas as pd


def YW(acs_values):
    """
    Función auxiliar que representa el Yule-Walker para estimar coeficientes AR.
    """
    p = len(acs_values) - 1
    r = np.array(acs_values[1:])
    R = np.array([acs_values[:p]]).T
    alpha = np.linalg.pinv(R) @ r  # Pseudoinversa para evitar singularidad
    return alpha.flatten()


def acs(id, **kwargs):
    """
    Llama dinámicamente a una función 'acf' específica basada en el ID.

    Parámetros:
        id (str): Identificador que se concatena con 'acf' para formar el nombre de la función a ejecutar.
        kwargs (dict): Argumentos que se pasan a la función ACF correspondiente.

    Retorna:
        Resultado de la función acf correspondiente al ID.
    """

    function_name = f"acf{id}"  # Construcción del nombre de la función
    if function_name in globals():
        return globals()[function_name](**kwargs)
    else:
        raise ValueError(f"La función '{function_name}' no está definida en el espacio de nombres.")


def AR1(p, acs):
    """
    Genera ruido Gaussiano con autocorrelación AR(1).
    """
    return np.random.normal(0, np.sqrt(1 - np.sum(acs[1:p + 1] * acs[1:p + 1])), p)


def seasonal_ar(x, ACS, season="month"):
    """
    Simula una serie temporal con autocorrelación estacional.

    Parámetros:
        x (pd.Series o array-like): Fechas de la serie temporal.
        ACS (dict): Estructura de autocorrelación para cada temporada.
        season (str, opcional): Tipo de estacionalidad (por defecto "month").

    Retorna:
        pd.DataFrame: DataFrame con fechas, valores Gaussianos generados y su temporada.
    """

    # Crear DataFrame con fechas y estacionalidad
    time = pd.DataFrame({"time": x})
    time["year"] = time["time"].dt.year
    time["season"] = time["time"].dt.month if season == "month" else time["time"].dt.day
    time["n"] = time.groupby(["year", "season"])["time"].transform("count")

    # Convertir estructura de autocorrelación
    alpha = {key: YW(value) for key, value in ACS.items()}

    # Obtener primera simulación
    first_season = time["season"].iloc[0]
    season_key = [key for key in ACS.keys() if key.endswith(str(first_season))][0]
    out_values = pd.DataFrame({"value": AR1(len(alpha[season_key]), ACS[season_key][1])})
    out_values["id"] = 0

    esd = [np.sqrt(1 - np.sum(alpha[key] * ACS[key][1:])) for key in alpha]

    # Simulación de la serie estacional
    for season_value in time["season"].unique():
        if season_value not in [int(key.split(season)[-1]) for key in ACS.keys()]:
            continue

        season_key = [key for key in ACS.keys() if key.endswith(str(season_value))][0]
        p = len(alpha[season_key])
        val = out_values["value"].iloc[-p:].to_numpy()
        aux = len(val)
        n = time[time["season"] == season_value]["n"].iloc[0]
        gn = np.random.normal(0, esd[season_value - 1], n + p)

        a_rev = alpha[season_key][::-1]
        for i in range(p, n + p):
            val = np.append(val, np.sum(val[i - p:i] * a_rev) + gn[i])

        new_data = pd.DataFrame({"value": val[p:], "id": season_value})
        out_values = pd.concat([out_values, new_data], ignore_index=True)

    # Construir el DataFrame final
    out_values = out_values[out_values["id"] != 0]
    result = pd.DataFrame({"date": x, "gauss": out_values["value"], "season": out_values["id"]})

    return result


def simulate_ts(aTS, from_date=None, to_date=None):
    """
    Simulación de series temporales basada en los atributos de aTS,
    replicando la funcionalidad de simulateTS en R.

    Parámetros:
        aTS (dict): Objeto de serie temporal ajustada con atributos necesarios.
        from_date (datetime, opcional): Fecha de inicio de la simulación.
        to_date (datetime, opcional): Fecha de fin de la simulación.

    Retorna:
        pd.DataFrame: Serie temporal simulada con fechas y valores.
    """

    # Extraer atributos del objeto aTS
    dist = aTS.get("dist")
    acsID = aTS.get("acsID")
    season = aTS.get("season")
    dates = pd.DataFrame(aTS.get("date"), columns=["date"])
    x = aTS.get("data")
    r = report_ts(aTS, method="stat")
    f = aTS.get("dfits")
    a = aTS.get("afits")

    # Definir límites de la distribución
    if dist == "beta":
        distbounds = (0, 1)
    else:
        distbounds = (-np.inf, np.inf)

    # Calcular ACS (Autocorrelation Structure)
    ACS = {}
    for i, series in enumerate(x):
        p0 = r.iloc[i]["p0"]
        p = actpnts(margdist=f[i]["dist"], margarg=f[i], p0=p0, distbounds=distbounds)
        fp = fitactf(p)

        lag = np.arange(len(a[i]["eACS"]))
        id_ = a[i]["ID"]
        as_ = acs(id=id_, t=lag, **a[i])  # Asumiendo que la función acs está implementada en Python
        ACS[i] = actf(as_, fp["actfcoef"][0], fp["actfcoef"][1])

    # Definir fechas de simulación
    if from_date is None:
        from_date = dates.iloc[0]["date"]
    if to_date is None:
        to_date = dates.iloc[-1]["date"]

    date_range = pd.date_range(start=from_date, end=to_date, freq=pd.infer_freq(dates["date"]))

    # Simular series con autocorrelación estacional
    gausian = seasonal_ar(date_range, ACS)  # Asumiendo implementación en Python
    gausian["season"] = gausian["date"].dt.month  # Suponiendo estacionalidad mensual

    # Construir tabla de parámetros
    para = pd.DataFrame({key: np.concatenate([f[i][key] for i in range(len(f))]) for key in f[0].keys()})
    para["season"] = np.arange(1, len(para) + 1)
    para["p0"] = r["p0"].values

    # Fusionar con la simulación
    aux = gausian.merge(para, on="season", how="left").sort_values("date")
    aux["uval"] = (norm.cdf(aux["gauss"]) - aux["p0"]) / (1 - aux["p0"])
    aux.loc[aux["uval"] < 0, "uval"] = 0

    # Aplicar distribución de salida
    if dist == "beta":
        for season_id in para["season"]:
            params = para.loc[para["season"] == season_id].drop(columns=["p0", "season"]).to_dict(orient="records")[0]
            aux.loc[aux["season"] == season_id, "value"] = beta.ppf(aux["uval"], **params)
    else:
        for season_id in para["season"]:
            params = para.loc[para["season"] == season_id].drop(columns=["p0", "season"]).to_dict(orient="records")[0]
            aux.loc[aux["season"] == season_id, "value"] = norm.ppf(aux["uval"], **params)

    return aux[["date", "value"]]
