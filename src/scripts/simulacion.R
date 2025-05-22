library(tidyr)
library(readr)
library(dplyr)

# Cargar el archivo CSV combinado
data_combined <- read_csv("datos/clima_combinado.csv", show_col_types = FALSE)

# Verificar si hay problemas al leer el archivo
print(problems(data_combined))

# Limpiar y seleccionar las columnas relevantes para la simulación
clean_and_select <- function(df) {
  # Verificar si la fila 2 realmente tiene los nombres de las columnas correctos
  if (nrow(df) >= 2) {
    colnames(df) <- df[2, ]  # Fila 2 contiene los nombres de las columnas correctas
    df <- df[-c(1, 2), ]     # Eliminar las dos primeras filas
  } else {
    stop("El archivo no tiene suficientes filas para contener nombres de columnas.")
  }
  
  # Convertir los valores numéricos de las columnas adecuadas y eliminar NA
  df <- df %>% 
    select(Year, Month, Day, Hour, Temperature, `Relative Humidity`, `Wind Speed`, GHI) %>%
    mutate(across(c(Temperature, `Relative Humidity`, `Wind Speed`, GHI), as.numeric)) %>%
    drop_na()  # Eliminar filas con valores faltantes
  return(df)
}



# Generar 730 simulaciones para los años 2023 y 2024
set.seed(1995)  # Asegurar la reproducibilidad

num_simulations <- 730  # Número de días para dos años

simulated_data <- data.frame(
  Year = rep(c(2023, 2024), each = 365),
  Month = rep(rep(1:12, times = c(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)), 2)[1:num_simulations],
  Day = rep(1:31, length.out = num_simulations),
  Temperature = sample(data_combined$Temperature, num_simulations, replace = TRUE),
  `Relative Humidity` = sample(data_combined$`Relative Humidity`, num_simulations, replace = TRUE),
  `Wind Speed` = sample(data_combined$`Wind Speed`, num_simulations, replace = TRUE),
  GHI = sample(data_combined$GHI, num_simulations, replace = TRUE)
)

# Ver los primeros datos simulados
head(simulated_data)

# Guardar los datos simulados en un archivo CSV si es necesario
write_csv(simulated_data, "datos/simulated_daily_data.csv")

head(simulated_data) %>% View()

