
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

## 🚀 API de simulación

El script `src/scripts/api.R` expone el endpoint `/lcoe` mediante Plumber.
Para iniciar el servicio es posible definir el puerto y el host mediante
variables de entorno:

```bash
export R_API_PORT=8001
export R_API_HOST=0.0.0.0
Rscript src/scripts/api.R
```

La API quedará disponible en `http://$R_API_HOST:$R_API_PORT/lcoe` y
retorna el LCOE calculado junto con la ruta del archivo generado.

### Ejemplo de integración con Python

Un cliente sencillo puede invocar el endpoint usando la librería
`requests`:

```python
import requests

payload = {
    "data_dir": "/ruta/datos",
    "input_file": "archivo.csv",
    "capital_cost": 3000,
    "operating_cost": 50,
    "energy_production": 5000,
    "discount_rate": 5,
    "lifetime": 20,
    "projection_date": "2045-12-31"
}

r = requests.post("http://localhost:8001/lcoe", json=payload)
print(r.json())
```

También puede ejecutarse el script
[`examples/call_r_api.py`](examples/call_r_api.py) para realizar la
petición con parámetros de ejemplo.

---

## ✍️ Autores

Repositorio correspondiente a la entrega de Trabajo Final de Maestría en Ciencia de Datos sobre Modelos Estocásticos para la microgeneración de energía fotovoltaica en Uruguay.

Autores:
 - Chalela, Emanuel: echalela@correo.ucu.edu.uy
 - Keulyian, Laura: MARIA.KEUYLIAN@correo.ucu.edu.uy
 - Sgüillaro, Enzo: ENZO.SGUILLARO@correo.ucu.edu.uy

Universidad Católica del Uruguay www.ucu.edu.uy
