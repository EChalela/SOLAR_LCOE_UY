import numpy as np
import matplotlib.pyplot as plt
import warnings
from SALib.sample.sobol import sample
from SALib.analyze import sobol

# Ignorar advertencias innecesarias
warnings.simplefilter(action="ignore", category=FutureWarning)

# Función para calcular el LCOE
def calcular_lcoe(capital_cost, operating_cost, energy_production, discount_rate, lifetime):
    discount_rate = discount_rate / 100  # Convertir porcentaje a decimal
    num = capital_cost + operating_cost * sum(1 / ((1 + discount_rate) ** np.arange(1, lifetime + 1)))
    denom = energy_production * sum(1 / ((1 + discount_rate) ** np.arange(1, lifetime + 1)))
    return num / denom

# Definir el problema para el análisis de sensibilidad
problem = {
    "num_vars": 5,
    "names": ["Capital Cost", "Operating Cost", "Energy Production", "Discount Rate", "Lifetime"],
    "bounds": [[500, 5000], [5, 50], [1000, 20000], [4, 10], [15, 25]]
}

# Generar muestras usando Sobol (1024 para evitar advertencias)
param_values = sample(problem, 1024)

# Evaluar el modelo en las muestras
Y = np.array([calcular_lcoe(*params) for params in param_values])

# Realizar el análisis de sensibilidad de Sobol
Si = sobol.analyze(problem, Y)

# Extraer contribución de la varianza
S1 = Si['S1']  # Efecto individual de cada variable
ST = Si['ST']  # Efecto total (incluyendo interacciones)

# Convertir a porcentaje
S1_percent = S1 * 100
ST_percent = ST * 100

# Determinar la variable con mayor impacto
max_index = np.argmax(ST_percent)
max_var = problem["names"][max_index]
max_contribution = ST_percent[max_index]

# Imprimir resultados
print("\n🔹 Análisis de Sensibilidad de Sobol - Contribución de la Varianza al LCOE:")
for i, name in enumerate(problem["names"]):
    print(f"{name}: {S1_percent[i]:.2f}% (S1), {ST_percent[i]:.2f}% (ST)")

print(f"\n✅ La variable con mayor impacto en el LCOE es **{max_var}** con una contribución del **{max_contribution:.2f}%**.")

# 📊 Gráfico de sensibilidad
plt.figure(figsize=(10, 6))
plt.bar(problem["names"], ST_percent, color="skyblue", edgecolor="black")
plt.xlabel("Variables de Entrada del LCOE")
plt.ylabel("Contribución a la Varianza (%)")
plt.title("Análisis de Sensibilidad del LCOE")
plt.xticks(rotation=20)
plt.grid(axis="y", linestyle="--", alpha=0.7)

# Mostrar el valor en cada barra
for i, v in enumerate(ST_percent):
    plt.text(i, v + 1, f"{v:.2f}%", ha="center", fontsize=12, fontweight="bold")

# Mostrar gráfico
plt.show()
