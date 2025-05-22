# Cargar librerías
library(plumber)
library(tidyverse)
library(lubridate)
library(CoSMoS)
library(tools)  # Para manipular nombres de archivos

#* @apiTitle Simulación de Radiación Solar
#* @apiDescription API para procesar y simular radiación solar a partir de datos de OpenMeteo.

#* Procesar datos de radiación y generar simulaciones
#* @param csv_file Ruta del archivo CSV de entrada
#* @post /procesar
function(csv_file) {
  # Leer datos de entrada
  data <- read_csv(csv_file)
  
  # Convertir el número entero a año, mes y día
  data <- data %>%
    mutate(
      anio = as.numeric(substr(as.character(date), 1, 4)),
      mes = as.numeric(substr(as.character(date), 6, 7)),
      dia = as.numeric(substr(as.character(date), 9, 10))
    )
  
  # Convertir a formato de fecha y seleccionar columnas relevantes
  data <- data %>%
    mutate(date = make_date(anio, mes, dia)) %>%
    select(date, anio, mes, dia, shortwave_radiation)
  
  # Promedio diario de radiación de onda corta
  data_daily <- data %>%
    group_by(date) %>%
    summarise(value = sum(shortwave_radiation, na.rm = TRUE)) %>%
    mutate(output = value * 0.153 * 6.545)
  
  # Ajustar modelo utilizando CoSMoS
  shra_adj <- analyzeTS(data_daily, dist = "norm", acsID = "fgn", season = "month")
  
  # Establecer semilla para reproducibilidad
  set.seed(1995)
  
  # Iniciar contador de tiempo
  t0 <- proc.time()
  
  # Simulación de la radiación
  sim_radiation <- list()
  nsim <- 1000
  for (i in 1:nsim) {
    sim <- simulateTS(aTS = shra_adj, from = as.POSIXct("2024-01-01"), to = as.POSIXct("2044-12-31")) %>%
      as_tibble() %>%
      mutate(date = ymd(date), id = as.character(i))
    sim_radiation[[i]] <- sim
  }
  
  # Detener contador de tiempo
  t1 <- proc.time()
  execution_time <- t1 - t0  # Tiempo de ejecución
  
  # Combinar las simulaciones
  DBRadiationSimDaily <- bind_rows(sim_radiation)
  
  # Construir el nombre del archivo de salida con sufijo "_r"
  file_path <- file_path_sans_ext(csv_file)  # Quita la extensión
  output_file <- paste0(file_path, "_r.csv")  # Agrega "_r"
  
  # Guardar resultados con el nuevo nombre
  write_csv(DBRadiationSimDaily, output_file)
  
  # Retornar mensaje de éxito con la ruta del archivo generado y el tiempo de ejecución
  return(list(
    message = "Proceso completado",
    output_file = output_file,
    execution_time_seconds = execution_time["elapsed"]
  ))
}
