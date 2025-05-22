library(tidyr)
library(readr)
library(dplyr)

# Cargar archivo CSV
data_combined <- read_csv("datos/clima_combinado.csv", show_col_types = FALSE)

# Verificar problemas
print(problems(data_combined))

# Función para limpiar y seleccionar columnas
clean_and_select <- function(df) {
  if (nrow(df) >= 2) {
    colnames(df) <- df[2, ]  # Asignar nombres de columnas desde la fila 2
    df <- df[-c(1, 2), ]     # Eliminar las dos primeras filas
  } else {
    stop("El archivo no tiene suficientes filas.")
  }
  
  df <- df %>%
    select(Year, Month, Day, Hour, Temperature, `Relative Humidity`, `Wind Speed`, GHI) %>%
    mutate(across(c(Temperature, `Relative Humidity`, `Wind Speed`, GHI), as.numeric)) %>%
    drop_na()
  return(df)
}

# Generar simulaciones horarias para 2023 y 2024
set.seed(1995)
num_hours <- 730 * 24  # Horas en dos años

simulated_hourly_data <- data.frame(
  Year = rep(rep(c(2023, 2024), each = 365), each = 24),
  Month = rep(rep(1:12, times = c(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)), each = 24, 2)[1:num_hours],
  Day = rep(rep(1:31, length.out = 365), each = 24, 2)[1:num_hours],
  Hour = rep(0:23, times = num_hours / 24),
  Temperature = sample(data_combined$Temperature, num_hours, replace = TRUE),
  `Relative Humidity` = sample(data_combined$`Relative Humidity`, num_hours, replace = TRUE),
  `Wind Speed` = sample(data_combined$`Wind Speed`, num_hours, replace = TRUE),
  GHI = sample(data_combined$GHI, num_hours, replace = TRUE)
)

# Ver los primeros resultados
head(simulated_hourly_data)

# Guardar los resultados en CSV
write_csv(simulated_hourly_data, "datos/simulated_hourly_data.csv")

