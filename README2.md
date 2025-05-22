
# Simulación y Evaluación Económica de Energía Solar en Uruguay

Este proyecto evalúa la viabilidad económica de la energía solar fotovoltaica en Uruguay, mediante el análisis de datos climáticos, simulaciones de producción y estimaciones del Costo Nivelado de Energía (LCOE).

---

## 🧭 Flujo del Proyecto

### 1. Datos crudos (`/data/raw`)
- `RadiationSim2024_2044.csv`: proyecciones de radiación.
- `datos_horarios_con_temeperatura.csv`: datos climáticos horarios.
- `predicciones_anuales_1999_2044.csv` y otras: demanda energética proyectada por sector y año.

### 2. Preprocesamiento
- **Normalización y detección de outliers**: `normalizar y outliers.R`.
- **Transformaciones adicionales**: `eda.r`, `eda2.R`.

### 3. Análisis Exploratorio
- **Python**: `EDA_clima.ipynb` analiza variables meteorológicas horarias.
- **R**: `EDA_Simulaciones_perfil_Radiación_y_LCOE.ipynb` explora simulaciones solares y parámetros financieros.

### 4. Simulación y Evaluación Económica
- Simulación Monte Carlo de:
  - CAPEX (costo de inversión inicial).
  - WACC (tasa de descuento).
- Cálculo de:
  - Producción eléctrica anual.
  - Valor Presente Futuro (VPF).
  - LCOE (Costo Nivelado de la Energía).

### 5. Visualización
- Histogramas, densidades y curvas de distribución con `ggplot2`, `highcharter`, `matplotlib`, y `seaborn`.

### 6. Scripts clave (`/src/scripts`)
- `LCOE.R`: simulación de escenarios económicos.
- `simulacion.R`: limpieza de datos y generación de escenarios de clima.
- `funciones.R`: funciones auxiliares para visualización y simulación.
- `eda.r`: análisis exploratorio de datos simulados.

---

## 📁 Estructura del Proyecto

```
data/
├── raw/                  # Datos originales
├── processed/            # Datos procesados

notebooks/
├── EDA_clima.ipynb       # Exploración de datos climáticos
├── EDA_Simulaciones_perfil_Radiación_y_LCOE.ipynb
├── Eda_simulaciones.ipynb

src/
└── scripts/              # Scripts en R para simulación y análisis
```

---

## 🔧 Requisitos

- R (preferentemente ≥ 4.2)
- Python ≥ 3.8
- Librerías: tidyverse, triangle, highcharter, pandas, seaborn, matplotlib

---

## ✍️ Autor

Emanuel Chalela · Proyecto de tesis de maestría · Uruguay · 2024-2025
