source("funciones.R")
# average 5.44 paper

# Simulación Monte Carlo
set.seed(1995)
Par_MonteCarlo <- tibble(
  id = seq(1, 1000),
  inv = rtriangle(1000, 2230, 4150, 3190),   # CAPEX
  rate = runif(1000, 0.04, 0.1)              # WACC
)

# Histograma de CAPEX
bins <- hist(Par_MonteCarlo$inv, breaks = 30, plot = FALSE)
df_hist <- data.frame(x = bins$mids, y = bins$counts)

# Densidad
dens <- density(Par_MonteCarlo$inv)
df_dens <- data.frame(
  x = dens$x,
  y = dens$y * diff(bins$breaks[1:2]) * length(Par_MonteCarlo$inv)
)

# # Crear gráfico con Highcharter
# grafica_capex <- highchart() %>%
#   hc_add_series(df_hist, type = "column", hcaes(x = x, y = y),
#                 color = "lightblue", name = "CAPEX") %>%
#   hc_add_series(df_dens, type = "line", hcaes(x = x, y = y),
#                 color = "red", name = "Densidad") %>%
#   hc_title(text = "Simulación Monte Carlo CAPEX - Uruguay (2024-244)") %>%
#   hc_subtitle(text = "Distribución triangular: min = 2230, max = 4150, modo = 3190") %>%
#   hc_xAxis(title = list(text = "CAPEX")) %>%
#   hc_yAxis(title = list(text = "Frecuencia")) %>%
#   hc_plotOptions(column = list(borderColor = "blue")) %>%
#   hc_add_theme(hc_theme_smpl())

# Crear gráfico con Highcharter con ejes más gruesos
grafica_capex <- highchart() %>%
  hc_add_series(df_hist, type = "column", hcaes(x = x, y = y),
                color = "lightblue", name = "CAPEX") %>%
  hc_add_series(df_dens, type = "line", hcaes(x = x, y = y),
                color = "red", name = "Densidad") %>%
  hc_title(text = "Simulación Monte Carlo CAPEX - Uruguay (2024-2044)") %>%
  hc_subtitle(text = "Distribución triangular: l = 2230, r = 4150, m = 3190") %>%
  hc_xAxis(
    title = list(text = "CAPEX"),
    lineWidth = 2,          # Grosor del eje X
    lineColor = "#000000",  # Color del eje X
    tickWidth = 2           # Grosor de los ticks
  ) %>%
  hc_yAxis(
    title = list(text = "Frecuencia"),
    lineWidth = 2,          # Grosor del eje Y
    lineColor = "#000000",  # Color del eje Y
    tickWidth = 2           # Grosor de los ticks
  ) %>%
  hc_plotOptions(column = list(borderColor = "blue")) %>%
  hc_add_theme(hc_theme_smpl())


# Histograma de CAPEX
guardar_highchart(
  grafico = grafica_capex,
  nombre_archivo = "CAPEX_Uruguay"
)


# 📊 Crear histograma del WACC con línea de tendencia
grafica_wacc <- plot_histograma_tendencia(
  df = Par_MonteCarlo,
  columna = "rate",
  nombre_columna = "WACC",
  titulo = "Simulación Monte Carlo WACC - Uruguay (2024-2044)",
  subtitulo = "Distribución uniforme entre 4% y 10%"
)

guardar_highchart(
  grafico = grafica_wacc,
  nombre_archivo = "WACC_Uruguay"
)

graficar_energia_solar()


#setwd('/Users/echalela/RStudioProjects/Simulaciones-R/')
DB_rad <- read_csv("datos/OpenMeteo/RadiationSim2024_2044.csv")


Scenarios <- DB_rad |> group_by(id) |>
  mutate(year = year(date),
         Output = (value / 1000) * 0.153 * 6.455 * 1) |>
  group_by(id, year) |>
  summarise(yearlyoutput = sum(Output)) |>
  group_by(id) |>
  left_join(Par_MonteCarlo) |>
  mutate(t = year - 2020, FDf =  yearlyoutput * (1 / (1 + rate)^t)) |>
  summarise(Inv = mean(inv), VPf = sum(FDf)) |>
  mutate(LCOE = (Inv / VPf) * 1000)


scenario <- Scenarios |>
  ggplot(aes(x = factor(id), y = LCOE)) +  # Cambiar `Type` por `id`
  geom_point() +
  labs(title = "LCOE por Escenario", x = "Escenario (ID)", y = "LCOE (US$/kWh)") +
  theme_minimal()

scenario
#
# scenario2 <-
# Scenarios |>
#   ggplot(aes(LCOE)) +
#   geom_histogram(color = "blue", fill = "lightblue") +
#   labs(title = "Histograma de LCOE",
#        x = "LCOE US$/kWh",
#        y = "Frecuencia") +
#   theme_minimal()
#
# scenario2

# Graficar el histograma de LCOE con eje X etiquetado
scenario2 <- ggplot(Scenarios, aes(x = LCOE)) +
  geom_histogram(
    aes(y = after_stat(density)),
    color = "blue",
    fill = "lightblue",
    binwidth = 30
  ) +
  geom_density(color = "red", linewidth = 1) +
  labs(title = "Histograma de LCOE", x = "LCOE (US$/kWh)", # Etiqueta del eje X
       y = "Frecuencia") +
  theme_minimal()

scenario2

library(highcharter)
library(dplyr)

# ✅ **Convertir LCOE a numérico**
Scenarios <- Scenarios %>% mutate(LCOE = as.numeric(LCOE))

# ✅ **Definir bins dinámicamente usando `pretty()`**
breaks <- pretty(Scenarios$LCOE, n = 20)  # Genera 20 bins adaptados al rango

# ✅ **Calcular histograma manualmente**
hist_data <- hist(Scenarios$LCOE, plot = FALSE, breaks = breaks)

# ✅ **Convertir datos del histograma a un data frame**
hist_df <- data.frame(
  x = hist_data$mids,  # Puntos medios de los bins
  y = hist_data$density # Frecuencia normalizada
)

# ✅ **Calcular densidad**
density_df <- density(Scenarios$LCOE)
density_df <- data.frame(x = density_df$x, y = density_df$y)

# ✅ **Gráfico con Highcharter**
hchart(hist_df, "column", hcaes(x = x, y = y), color = "lightblue", name = "Frecuencia") %>%
  hc_add_series(data = density_df, type = "line", hcaes(x = x, y = y), color = "red", name = "Densidad") %>%
  hc_title(text = "Histograma de LCOE en Uruguay") %>%
  hc_xAxis(title = list(text = "LCOE (US$/kWh)")) %>%
  hc_yAxis(title = list(text = "Frecuencia")) %>%
  hc_tooltip(pointFormat = "<b>{series.name}</b><br>LCOE: {point.x}<br>Frecuencia/Densidad: {point.y:.4f}") %>%
  hc_add_theme(hc_theme_smpl())

