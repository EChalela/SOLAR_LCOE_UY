import rpy2.robjects as ro
from rpy2.robjects import pandas2ri

# Activar la conversión automática entre pandas y R dataframes
pandas2ri.activate()

import os

csv_file = os.path.abspath("../data/clima_-34.028193_-55.393066.csv")
output_file = os.path.abspath("../data/salida_clima_-34.028193_-55.393066.csv")

# Script en R para ejecutar desde Python
r_script = """
# Función para verificar e instalar paquetes en R
check_install_packages <- function(packages) {
  for (pkg in packages) {
    if (!requireNamespace(pkg, quietly = TRUE)) {
      install.packages(pkg, dependencies = TRUE)
    }
  }
}

# Lista de paquetes a verificar
packages_to_check <- c("tidyverse", "lubridate", "CoSMoS")

# Ejecutar la función para instalar los paquetes si es necesario
check_install_packages(packages_to_check)

# Cargar las librerías después de la instalación
lapply(packages_to_check, library, character.only = TRUE)

csv_file <- "{csv_file}"
output_file <- "{output_file}"
setwd(dirname("{csv_file}"))  # Cambia al directorio del CSV
print(paste("Directorio actual en R:", getwd()))


# Cargar datos del archivo CSV
data <- read_csv(csv_file)

# Convertir el número entero a año, mes y día
data <- data %>%
  mutate(
    anio = as.numeric(substr(as.character(date), 1, 4)),
    mes = as.numeric(substr(as.character(date), 6, 7)),
    dia = as.numeric(substr(as.character(date), 9, 10))
  )

# Convertir a formato de fecha
data <- data %>%
  mutate(date = make_date(anio, mes, dia)) %>%
  select(date, anio, mes, dia, shortwave_radiation)

# Promedio diario de radiación de onda corta
data_daily <- data %>%
  group_by(date) %>%
  summarise(value = sum(shortwave_radiation, na.rm = TRUE)) %>%
  mutate(output = value * 0.153 * 6.545)

# Verificar si hay valores nulos o anómalos en data_daily
print(summary(data_daily))
print(sum(is.na(data_daily$value))) # Cantidad de valores NA

# Graficar la serie temporal
quickTSPlot(data_daily$value)

# Ajustar modelo utilizando CoSMoS
#shra_adj <- CoSMoS::analyzeTS(data_daily, dist = "norm", acsID = "fgn", season = "month") VER ESTO EL acsID
#shra_adj <- CoSMoS::analyzeTS(data_daily, dist = "norm", acsID = "ar1", season = "week")
#shra_adj <- CoSMoS::analyzeTS(data_daily, dist = "norm", acsID = "AR1", season = "month")
shra_adj <- CoSMoS::analyzeTS(data_daily, dist = "norm", acsID = AR1, season = "month")


CoSMoS::reportTS(shra_adj, 'dist')
CoSMoS::reportTS(shra_adj, 'acs')
CoSMoS::reportTS(shra_adj, 'stat')

# Establecer semilla
set.seed(1995)

# Simulación de la radiación
sim_radiation <- list()
nsim <- 1000
t0 <- proc.time()
for (i in 1:nsim) {{
  sim <- simulateTS(aTS = shra_adj, from = as.POSIXct("2024-01-01"), to = as.POSIXct("2044-12-31")) %>%
    as_tibble() %>%
    mutate(date = ymd(date), id = as.character(i))
  sim_radiation[[i]] <- sim
}}
t1 <- proc.time()
print(t1 - t0)

# Combinar las simulaciones
DBRadiationSimDaily <- bind_rows(sim_radiation)

# Graficar las series simuladas
ggplot(DBRadiationSimDaily) +
  geom_line(aes(x = date, y = value, colour = id)) +
  theme_light() +
  theme(legend.position = "none")

# Guardar los resultados
write_csv(DBRadiationSimDaily, output_file)
"""

# Ejecutar el script en R desde Python
ro.r(r_script)

print(f"Simulación completada. Resultados guardados en {output_file}")
