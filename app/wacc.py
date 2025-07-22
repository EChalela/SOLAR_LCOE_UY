import numpy as np
import matplotlib.pyplot as plt

# Definir la función de cálculo del LCOE
def calcular_lcoe(capital_cost, operating_cost, energy_production, discount_rate, lifetime):
    discount_rate = discount_rate / 100  # Convertir porcentaje a decimal
    num = capital_cost + operating_cost * sum(1 / ((1 + discount_rate) ** np.arange(1, lifetime + 1)))
    denom = energy_production * sum(1 / ((1 + discount_rate) ** np.arange(1, lifetime + 1)))
    return num / denom

# Parámetros fijos
capital_cost = 1500  # US$/kW
operating_cost = 20  # US$/kW/año
energy_production = 10000  # kWh/año
lifetime = 25  # años

# Escenarios de WAC (costo promedio ponderado de capital)
wac_scenarios = [4.2, 7.5, 10]  # en porcentaje

# Calcular LCOE para cada escenario de WAC
lcoe_values = [calcular_lcoe(capital_cost, operating_cost, energy_production, wac, lifetime) for wac in wac_scenarios]

# Crear gráfico
plt.figure(figsize=(8, 5))
plt.plot(wac_scenarios, lcoe_values, marker='o', linestyle='-', color='b', label="LCOE")

# Líneas horizontales de referencia
plt.axhline(y=min(lcoe_values), color='g', linestyle='--', label=f"Min: {min(lcoe_values):.4f} $/kWh")
plt.axhline(y=max(lcoe_values), color='r', linestyle='--', label=f"Max: {max(lcoe_values):.4f} $/kWh")

# Etiquetas y título
plt.xlabel("WAC (%)")
plt.ylabel("LCOE (US$/MWh)") # ver esto
plt.title("Impacto del WAC en el LCOE")
plt.xticks(wac_scenarios)
plt.legend()
plt.grid(True, linestyle="--", alpha=0.7)

# Mostrar gráfico
plt.show()
