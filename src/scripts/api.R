# Cargar librerías necesarias
library(plumber)
library(tidyverse)
library(lubridate)
library(CoSMoS)
library(tools)

#* @apiTitle Simulación de Radiación Solar y Cálculo de LCOE
#* @apiDescription API para procesar datos de OpenMeteo, simular radiación solar y calcular LCOE.

#* Procesar datos de radiación y calcular LCOE
#* @param data_dir Ruta base donde están los datos
#* @param input_file Nombre del archivo CSV de entrada
#* @param capital_cost Costo de capital (US$/kW)
#* @param operating_cost Costo operativo (US$/kW/año)
#* @param energy_production Energía producida (kWh/año)
#* @param discount_rate Tasa de descuento (%)
#* @param lifetime Vida útil (años)
#* @param projection_date Fecha fin de simulación (AAAA-MM-DD)
#* @post /lcoe
function(data_dir, input_file, capital_cost, operating_cost, energy_production, discount_rate, lifetime, projection_date) {
  tryCatch({
    # Verificar si data_dir está vacío
    if (is.null(data_dir) || data_dir == "") {
      stop("El directorio de datos está vacío. Debe agregarlo como parámetro.")
    }
    setwd(data_dir)

    # Convertir parámetros a numéricos
    capital_cost <- as.numeric(capital_cost)
    operating_cost <- as.numeric(operating_cost)
    energy_production <- as.numeric(energy_production)
    discount_rate <- as.numeric(discount_rate) / 100
    lifetime <- as.numeric(lifetime)

    # Validar que projection_date sea una fecha válida
    projection_date <- tryCatch(as.POSIXct(projection_date), error = function(e) NA)
    if (is.na(projection_date)) {
      stop("La fecha de proyección no es válida. Debe estar en formato AAAA-MM-DD.")
    }

    # Verificar que los valores sean válidos
    if (any(is.na(c(capital_cost, operating_cost, energy_production, discount_rate, lifetime)))) {
      stop("Uno o más parámetros son inválidos.")
    }

    # Leer datos de entrada
    csv_file <- file.path(data_dir, input_file)
    if (!file.exists(csv_file)) {
      stop("El archivo de entrada no existe.")
    }

    data <- read_csv(csv_file)

    # Convertir a formato de fecha
    data <- data %>%
      mutate(
        anio = as.numeric(substr(as.character(date), 1, 4)),
        mes = as.numeric(substr(as.character(date), 6, 7)),
        dia = as.numeric(substr(as.character(date), 9, 10)),
        date = make_date(anio, mes, dia)
      ) %>%
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
      sim <- simulateTS(aTS = shra_adj, from = as.POSIXct("2025-01-01"), to = projection_date) %>%
        as_tibble() %>%
        mutate(date = ymd(date), id = as.character(i))
      sim_radiation[[i]] <- sim
    }

    # Detener contador de tiempo
    t1 <- proc.time()
    execution_time <- t1 - t0

    # Combinar las simulaciones
    DBRadiationSimDaily <- bind_rows(sim_radiation)

    # Guardar resultados
    output_file <- paste0(file_path_sans_ext(input_file), "_r.csv")
    output_file_path <- file.path(data_dir, output_file)
    write_csv(DBRadiationSimDaily, output_file_path)

    # Cálculo del LCOE
    lcoe <- (capital_cost + operating_cost * sum(1 / ((1 + discount_rate)^(1:lifetime)))) /
      (energy_production * sum(1 / ((1 + discount_rate)^(1:lifetime))))

    return(list(
      message = "Proceso completado",
      output_file = output_file_path,
      execution_time_seconds = execution_time["elapsed"],
      lcoe = lcoe
    ))
  }, error = function(e) {
    return(list(error = paste("Error:", e$message)))
  })
}

setwd('/Users/echalela/RStudioProjects/Simulaciones-R/')

# Iniciar API de plumber
r <- plumber::plumb("api.R")
r$run(port = 8001, host = "0.0.0.0")
