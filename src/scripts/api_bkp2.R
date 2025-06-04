# Cargar librerías
library(plumber)
library(tidyverse)
library(lubridate)
library(CoSMoS)
library(tools)

#* @apiTitle Simulación de Radiación Solar y Cálculo de LCOE
#* @apiDescription API para procesar datos de OpenMeteo, simular radiación solar y calcular el LCOE.

#* @filter cors
cors <- function(req, res) {
  res$setHeader("Access-Control-Allow-Origin", "*")
  res$setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
  res$setHeader("Access-Control-Allow-Headers", "Content-Type")
  if (req$REQUEST_METHOD == "OPTIONS") {
    res$status <- 200
    return(res)
  }
  plumber::forward()
}

#* Procesar datos de radiación, generar simulaciones y calcular LCOE
#* @param data_dir Ruta base donde están los datos
#* @param input_file Nombre del archivo CSV de entrada
#* @param capital_cost Costo de capital (US$/kW)
#* @param operating_cost Costo operativo (US$/kW/año)
#* @param energy_production Energía producida (kWh/año)
#* @param discount_rate Tasa de descuento (%)
#* @param lifetime Tiempo de vida útil (años)
#* @param projection_date Fecha fin de simulación (AAAA-MM-DD)
#* @post /procesar
function(data_dir,
         input_file,
         capital_cost,
         operating_cost,
         energy_production,
         discount_rate,
         lifetime,
         projection_date) {
  if (is.null(data_dir) || data_dir == "") {
    return(list(error = "El directorio de datos está vacío. Debe agregarlo como parámetro."))
  }
  # Convertir parámetros numéricos
  capital_cost <- as.numeric(capital_cost)
  operating_cost <- as.numeric(operating_cost)
  energy_production <- as.numeric(energy_production)
  discount_rate <- as.numeric(discount_rate) / 100  # Convertir porcentaje a decimal
  lifetime <- as.numeric(lifetime)
  
  # Validar que projection_date sea una fecha válida
  if (!lubridate::is.Date(ymd(projection_date))) {
    return(list(error = "La fecha de proyección no es válida. Debe estar en formato AAAA-MM-DD."))
  }
  
  # Convertir projection_date a formato Date
  projection_date <- as.POSIXct(projection_date)
  
  # Verificar que los valores sean válidos
  if (any(is.na(
    c(
      capital_cost,
      operating_cost,
      energy_production,
      discount_rate,
      lifetime
    )
  ))) {
    return(list(error = "Todos los parámetros deben ser valores numéricos válidos"))
  }
  

  
  # Construir la ruta del archivo de entrada
  csv_file <- file.path(data_dir, input_file)
  
  # Verificar si el archivo existe
  if (!file.exists(csv_file)) {
    return(list(error = "El archivo de entrada no existe", file = csv_file))
  }
  
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
  shra_adj <- analyzeTS(data_daily,
                        dist = "norm",
                        acsID = "fgn",
                        season = "month")
  
  # Establecer semilla para reproducibilidad
  set.seed(1995)
  
  # Iniciar contador de tiempo
  t0 <- proc.time()
  
  # Simulación de la radiación con la fecha de proyección
  sim_radiation <- list()
  nsim <- 1000
  for (i in 1:nsim) {
    sim <- simulateTS(aTS = shra_adj,
                      from = as.POSIXct("2025-01-01"),
                      to = projection_date) %>%
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
  file_path <- file_path_sans_ext(input_file)  # Quita la extensión
  output_file <- paste0(file_path, "_r.csv")  # Agrega "_r"
  output_file_path <- file.path(data_dir, output_file)
  
  # Guardar resultados con el nuevo nombre
  write_csv(DBRadiationSimDaily, output_file_path)
  
  # Cálculo del LCOE
  lcoe <- (capital_cost + operating_cost * sum(1 / ((1 + discount_rate)^(1:lifetime)))) /
    (energy_production * sum(1 / ((1 + discount_rate)^(1:lifetime))))
  
  # Retornar mensaje de éxito con la ruta del archivo generado, el tiempo de ejecución y el LCOE calculado
  return(
    list(
      message = "Proceso completado",
      output_file = output_file_path,
      execution_time_seconds = execution_time["elapsed"],
      lcoe = lcoe
    )
  )
}

# Iniciar API de plumber con configuración de entorno
port <- as.numeric(Sys.getenv("R_API_PORT", "8001"))
host <- Sys.getenv("R_API_HOST", "0.0.0.0")
r <- plumber::plumb("api.R")  # No se necesita la ruta absoluta
r$run(port = port, host = host)
