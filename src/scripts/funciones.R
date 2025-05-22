library(dplyr)
library(lubridate)
library(ggplot2)
library(stringr)
library(gridExtra)
library(rio)
library(readr)
library(tidyverse)
library(triangle)
library(highcharter)
library(htmlwidgets)
library(webshot2)
library(htmlwidgets)
library(htmltools)
library(magick)
library(rsvg)
library(fs)
library(highcharter)
library(webshot2)
library(htmlwidgets)
library(fs)



plot_histograma_tendencia <- function(df, columna, nombre_columna, titulo = "Histograma", subtitulo = NULL) {
  var <- df[[columna]]
  
  # Histograma
  bins <- hist(var, breaks = 30, plot = FALSE)
  df_hist <- data.frame(x = bins$mids, y = bins$counts)
  
  # Densidad escalada al histograma
  dens <- density(var)
  df_dens <- data.frame(
    x = dens$x,
    y = dens$y * diff(bins$breaks[1:2]) * length(var)
  )
  
  # Gráfico con highcharter
  highchart() %>%
    hc_add_series(df_hist, type = "column", hcaes(x = x, y = y), color = "lightblue", name = nombre_columna) %>%
    hc_add_series(df_dens, type = "line", hcaes(x = x, y = y), color = "red", name = "Densidad") %>%
    hc_title(text = titulo) %>%
    hc_subtitle(text = subtitulo) %>%
    hc_xAxis(
      title = list(text = nombre_columna),
      lineWidth = 2,          # Grosor del eje X
      lineColor = "#000000",  # Color del eje X
      tickWidth = 2           # Grosor de los ticks en eje X
    ) %>%
    hc_yAxis(
      title = list(text = "Frecuencia"),
      lineWidth = 2,          # Grosor del eje Y
      lineColor = "#000000",  # Color del eje Y
      tickWidth = 2           # Grosor de los ticks en eje Y
    ) %>%
    hc_plotOptions(column = list(borderColor = "blue")) %>%
    hc_add_theme(hc_theme_smpl())
}


guardar_highchart <- function(grafico, nombre_archivo, carpeta = "graficos_finales") {
  library(highcharter)
  library(webshot2)
  library(htmlwidgets)
  library(fs)
  
  # Crear carpeta si no existe
  dir_create(carpeta)
  
  # Rutas de archivo
  archivo_html <- file.path(carpeta, paste0(nombre_archivo, ".html"))
  archivo_png  <- file.path(carpeta, paste0(nombre_archivo, ".png"))
  
  # Guardar como HTML
  saveWidget(grafico, file = archivo_html, selfcontained = FALSE)
  
  # Capturar como imagen PNG
  webshot2::webshot(
    url = archivo_html,
    file = archivo_png,
    vwidth = 1000,
    vheight = 600,
    delay = 1
  )
  
  message("✅ Archivos guardados correctamente:\n🌐 HTML: ", archivo_html,
          "\n🖼️ PNG: ", archivo_png)
}

graficar_energia_solar <- function(
    path_csv = "datos/OpenMeteo/datos_horarios_2013_2023.csv",
    carpeta_salida = "graficos_finales",
    nombre_archivo = "Energia_Solar_Diaria_Uruguay",
    factor_conversion = 0.153 * 6.545
) {
  library(readr)
  library(dplyr)
  library(lubridate)
  library(highcharter)
  library(htmlwidgets)
  library(webshot2)
  
  # Preparar datos
  data <- read_csv(path_csv, show_col_types = FALSE) %>%
    mutate(
      anio = year(date),
      mes = month(date),
      dia = day(date),
      date = as_date(date)
    ) %>%
    select(date, anio, mes, dia, shortwave_radiation)
  
  data_daily <- data %>%
    group_by(date) %>%
    summarise(value = sum(shortwave_radiation, na.rm = TRUE), .groups = "drop") %>%
    mutate(output = value * factor_conversion)
  
  # Idioma en español
  hc_es <- getOption("highcharter.lang")
  hc_es$months <- c("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
  hc_es$shortMonths <- substr(hc_es$months, 1, 3)
  hc_es$weekdays <- c("Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado")
  options(highcharter.lang = hc_es)
  
  # Crear gráfico
  grafico <- hchart(data_daily, "line", hcaes(x = date, y = output), color = "#1f78b4") %>%
    hc_title(text = "Generación de Energía Solar (kWh/día) en Uruguay") %>%
    hc_subtitle(text = "Cálculo basado en radiación de onda corta") %>%
    hc_xAxis(title = list(text = "Fecha"), type = "datetime") %>%
    hc_yAxis(title = list(text = "Generación (kWh)"), min = 0) %>%
    hc_tooltip(pointFormat = "Generación: <b>{point.y:.2f} kWh</b>") %>%
    hc_add_theme(hc_theme_smpl()) %>%
    hc_chart(lang = hc_es)
  
  # Guardar como HTML y PNG
  archivo_html <- file.path(carpeta_salida, paste0(nombre_archivo, ".html"))
  archivo_png <- file.path(carpeta_salida, paste0(nombre_archivo, ".png"))
  
  dir.create(carpeta_salida, showWarnings = FALSE)
  saveWidget(grafico, file = archivo_html, selfcontained = TRUE)
  webshot2::webshot(url = archivo_html, file = archivo_png, vwidth = 1200, vheight = 800)
  
  cat("✅ Gráficos guardados correctamente:\n")
  cat("🌐 HTML:", archivo_html, "\n")
  cat("🖼️ PNG :", archivo_png, "\n")
}

# Función para generar las fechas y el GHI
generar_fechas_bkp <- function(fecha_str, ghi_data) {
  fecha_inicial <- as.Date(fecha_str, format = "%d/%m/%y")
  
  if (is.na(fecha_inicial)) {
    stop("La fecha proporcionada no tiene un formato válido. Usa el formato 'dd/mm/yy'.")
  }
  
  anio <- format(fecha_inicial, "%Y")
  fecha_final <- as.Date(paste0(anio, "-12-31"), format = "%Y-%m-%d")
  
  fechas_horas <- seq.POSIXt(
    from = as.POSIXct(fecha_inicial),
    to = as.POSIXct(paste0(fecha_final, " 23:00:00")),
    by = "hour"
  )
  
  df <- data.frame(
    fecha = fechas_horas,
    hora = as.integer(format(fechas_horas, "%H")),
    dia = as.integer(format(fechas_horas, "%d")),
    mes = as.integer(format(fechas_horas, "%m")),
    anio = as.integer(format(fechas_horas, "%Y")),
    estacion_idStr = "Carrasco",
    TempAire_normalizado = NA,
    HumRelativa_normalizado = NA,
    GHI = NA
  )
  
  df <- df %>%
    mutate(GHI = ifelse(hora >= 9 & hora <= 18, dnorm(hora, mean = 13.5, sd = 2.5) * 1000, 0))
  
  df <- df %>%
    rowwise() %>%
    mutate(GHI = ifelse(GHI > 0, {
      mes_actual <- mes
      promedio_mes <- ghi_data %>%
        filter(month(fecha) == mes_actual) %>%
        summarise(promedio_GHI = mean(GHI, na.rm = TRUE)) %>%
        pull(promedio_GHI)
      
      if (is.na(promedio_mes)) {
        GHI
      } else {
        rnorm(1, mean = promedio_mes, sd = 0.1 * promedio_mes)
      }
    }, 0))
  
  return(df)
}

# Función para generar las fechas y el GHI
generar_fechas <- function(fecha_str, ghi_data, clima_data) {
  # Validar y convertir la fecha inicial
  fecha_inicial <- as.Date(fecha_str, format = "%d/%m/%y")
  if (is.na(fecha_inicial)) {
    stop("La fecha proporcionada no tiene un formato válido. Usa el formato 'dd/mm/yy'.")
  }
  
  # Determinar el año y fecha final
  anio <- format(fecha_inicial, "%Y")
  fecha_final <- as.Date(paste0(anio, "-12-31"), format = "%Y-%m-%d")
  
  # Crear secuencia de fechas por hora para todo el año
  fechas_horas <- seq.POSIXt(
    from = as.POSIXct(fecha_inicial),
    to = as.POSIXct(paste0(fecha_final, " 23:00:00")),
    by = "hour"
  )
  
  # Crear el DataFrame inicial
  df <- data.frame(
    fecha = fechas_horas,
    hora = as.integer(format(fechas_horas, "%H")),
    dia = as.integer(format(fechas_horas, "%d")),
    mes = as.integer(format(fechas_horas, "%m")),
    anio = as.integer(format(fechas_horas, "%Y")),
    estacion_idStr = "Carrasco",
    TempAire_normalizado = NA,
    HumRelativa_normalizado = NA,
    GHI = NA
  )
  
  # Asignar valores de GHI simulados según la hora del día
  df <- df %>%
    mutate(GHI = ifelse(hora >= 9 & hora <= 18, 
                        dnorm(hora, mean = 13.5, sd = 2.5) * 1000, 0))
  
  # Simular valores de TempAire_normalizado y HumRelativa_normalizado
  df <- df %>%
    rowwise() %>%
    mutate(
      # Simulación de temperatura tomando el mismo mes y mes anterior del año pasado
      TempAire_normalizado = ifelse(
        is.na(TempAire_normalizado),
        simular_valor_climatico(mes, hora, clima_data, "TempAire_normalizado"),
        TempAire_normalizado
      ),
      # Simulación de humedad relativa de forma similar
      HumRelativa_normalizado = ifelse(
        is.na(HumRelativa_normalizado),
        simular_valor_climatico(mes, hora, clima_data, "HumRelativa_normalizado"),
        HumRelativa_normalizado
      )
    )
  
  return(df)
}

# Función auxiliar para simular los valores climáticos
simular_valor_climatico <- function(mes, hora, clima_data, variable) {
  # Obtener los datos relevantes del mismo mes del año pasado
  datos_mismo_mes <- clima_data %>%
    filter(month(fecha) == mes & estacion_idStr == "Carrasco")
  
  # Obtener los datos del mes anterior del año pasado
  mes_anterior <- ifelse(mes == 1, 12, mes - 1)  # Ajustar para enero -> diciembre
  datos_mes_anterior <- clima_data %>%
    filter(month(fecha) == mes_anterior & estacion_idStr == "Carrasco")
  
  # Calcular los promedios por hora para los dos conjuntos de datos
  promedio_mismo_mes <- datos_mismo_mes %>%
    group_by(hora) %>%
    summarise(media = mean(get(variable), na.rm = TRUE)) %>%
    filter(hora == hora) %>%
    pull(media)
  
  promedio_mes_anterior <- datos_mes_anterior %>%
    group_by(hora) %>%
    summarise(media = mean(get(variable), na.rm = TRUE)) %>%
    filter(hora == hora) %>%
    pull(media)
  
  # Promediar los dos valores si existen
  media_final <- mean(c(promedio_mismo_mes, promedio_mes_anterior), na.rm = TRUE)
  
  # Ajustar la desviación estándar según la hora del día y la estación del año
  desviacion <- if (hora >= 21 | hora <= 6) {
    0.05 * media_final  # Menor variabilidad durante la noche
  } else {
    0.1 * media_final   # Mayor variabilidad durante el día
  }
  
  # Simular un valor usando una distribución normal alrededor de la media
  valor_simulado <- rnorm(1, mean = media_final, sd = desviacion)
  
  return(valor_simulado)
}


# Función para graficar GHI para una fecha específica
graficar_GHI_por_fecha <- function(fecha_str, data) {
  fecha_filtrada <- as.Date(fecha_str, format = "%d/%m/%Y")
  
  datos_filtrados <- data %>%
    filter(as.Date(fecha) == fecha_filtrada)
  
  if (nrow(datos_filtrados) == 0) {
    stop("No hay datos disponibles para la fecha proporcionada.")
  }
  
  ggplot(datos_filtrados, aes(x = fecha, y = GHI)) +
    geom_line(color = "blue") +
    labs(
      title = paste("Evolución de GHI para la fecha:", fecha_str),
      x = "Fecha y Hora",
      y = "GHI"
    ) +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
}

# Función para graficar GHI de un mes en función del número entero 'añomes'
graficar_GHI_anio_mes_num <- function(anio_mes_num, data) {
  # Convertir el número entero a año y mes
  anio <- as.numeric(substr(as.character(anio_mes_num), 1, 4))
  mes <- as.numeric(substr(as.character(anio_mes_num), 5, 6))
  
  # Verificar que el año y mes sean válidos
  if (is.na(anio) || is.na(mes) || mes < 1 || mes > 12) {
    stop(
      "El valor proporcionado para 'añomes' no es válido. Debe ser un número en el formato 'YYYYMM'."
    )
  }
  
  # Convertir la columna 'fecha' a tipo Date (si no lo está)
  data <- data %>%
    mutate(fecha = as.Date(fecha))
  
  # Filtrar el dataset por el mes y año seleccionados
  data_filtrada <- data %>%
    filter(year(fecha) == anio & month(fecha) == mes)
  
  # Verificar si hay datos disponibles
  if (nrow(data_filtrada) == 0) {
    stop("No hay datos disponibles para el mes proporcionado.")
  } else {
    # Agregar una columna con solo el día del mes
    data_filtrada <- data_filtrada %>%
      mutate(dia = day(fecha))
    
    # Graficar el GHI en función de los días del mes
    ggplot(data_filtrada, aes(x = factor(dia), y = GHI)) +
      geom_line(color = "blue", group = 1) +
      labs(
        title = paste("Evolución de GHI máximo por día en:", anio_mes_num),
        x = "Día",
        y = "GHI"
      ) +
      theme_minimal() +
      theme(
        axis.text.x = element_text(angle = 90, hjust = 1, size = 8)  # Texto vertical y más pequeño
      )
  }
}


# Función para generar las fechas y el GHI, además de completar temperatura y humedad
generar_fechas2 <- function(fecha_str, ghi_data, temp_humedad_data) {
  # Validación de la fecha de entrada
  fecha_inicial <- as.Date(fecha_str, format = "%d/%m/%y")
  
  if (is.na(fecha_inicial)) {
    stop("La fecha proporcionada no tiene un formato válido. Usa el formato 'dd/mm/yy'.")
  }
  
  anio <- format(fecha_inicial, "%Y")
  fecha_final <- as.Date(paste0(anio, "-12-31"), format = "%Y-%m-%d")
  
  # Generación de las fechas por hora
  fechas_horas <- seq.POSIXt(
    from = as.POSIXct(fecha_inicial),
    to = as.POSIXct(paste0(fecha_final, " 23:00:00")),
    by = "hour"
  )
  
  # Crear dataframe inicial
  df <- data.frame(
    fecha = fechas_horas,
    hora = as.integer(format(fechas_horas, "%H")),
    dia = as.integer(format(fechas_horas, "%d")),
    mes = as.integer(format(fechas_horas, "%m")),
    anio = as.integer(format(fechas_horas, "%Y")),
    estacion_idStr = "Carrasco",
    TempAire_normalizado = NA,
    HumRelativa_normalizado = NA,
    GHI = NA
  )
  
  # Calcular el GHI utilizando distribución normal
  df <- df %>%
    mutate(GHI = ifelse(hora >= 9 & hora <= 18, 
                        dnorm(hora, mean = 13.5, sd = 2.5) * 1000, 0))
  
  # Ajustar los valores de GHI usando el promedio mensual
  df <- df %>%
    rowwise() %>%
    mutate(GHI = ifelse(GHI > 0, {
      mes_actual <- mes
      promedio_mes <- ghi_data %>%
        filter(month(fecha) == mes_actual) %>%
        summarise(promedio_GHI = mean(GHI, na.rm = TRUE)) %>%
        pull(promedio_GHI)
      
      if (is.na(promedio_mes)) {
        GHI
      } else {
        rnorm(1, mean = promedio_mes, sd = 0.1 * promedio_mes)
      }
    }, 0))
  
  # Completar temperatura y humedad con datos del mes anterior y año anterior
  df <- df %>%
    left_join(
      temp_humedad_data %>%
        group_by(dia, mes, hora) %>%
        summarise(
          TempAire_promedio = mean(TempAire_normalizado, na.rm = TRUE),
          HumRelativa_promedio = mean(HumRelativa_normalizado, na.rm = TRUE)
        ),
      by = c("dia", "mes", "hora")
    ) %>%
    mutate(
      TempAire_normalizado = ifelse(is.na(TempAire_normalizado), 
                                    TempAire_promedio, 
                                    TempAire_normalizado),
      HumRelativa_normalizado = ifelse(is.na(HumRelativa_normalizado), 
                                       HumRelativa_promedio, 
                                       HumRelativa_normalizado)
    ) %>%
    select(-TempAire_promedio, -HumRelativa_promedio)
  
  return(df)
}
graficar_variable_fecha <- function(data, date_input, variable) {
  # Verificar que la variable esté en el dataset
  if (!variable %in% colnames(data)) {
    stop(paste("La variable", variable, "no está presente en el dataset."))
  }
  
  # Verificar que el date_input sea un objeto Date
  if (!inherits(date_input, "Date")) {
    stop("El parámetro 'date_input' debe ser un objeto de tipo Date.")
  }
  
  # Convertir la columna 'date' a tipo POSIXct para manejar fechas con horas (si no lo está)
  if (!inherits(data$date, "POSIXct")) {
    data <- data %>%
      mutate(date = as.POSIXct(date))
  }
  
  # Filtrar el dataset por la fecha (solo la parte del día, ignorando la hora)
  data_filtrada <- data %>%
    filter(as.Date(date) == date_input)
  
  # Verificar si hay datos disponibles
  if (nrow(data_filtrada) == 0) {
    stop("No hay datos disponibles para la fecha proporcionada.")
  }
  
  # Graficar la variable seleccionada en función de las horas del día
  ggplot(data_filtrada, aes(x = date, y = .data[[variable]])) +
    geom_line(color = "yellow", group = 1) +
    labs(
      title = paste("Evolución de", variable, "el día:", date_input),
      x = "Hora",
      y = variable
    ) +
    scale_x_datetime(date_labels = "%H:%M", date_breaks = "1 hour") +  # Mostrar horas en el eje X
    theme_minimal() +
    theme(
      axis.text.x = element_text(angle = 45, hjust = 1, size = 8)  # Ajustar el texto en el eje X
    )
}

graficar_variable_anio_mes_num <- function(anio_mes_num, data, variable) {
  # Convertir el número entero a año y mes
  anio <- as.numeric(substr(as.character(anio_mes_num), 1, 4))
  mes <- as.numeric(substr(as.character(anio_mes_num), 5, 6))
  
  # Verificar que el año y mes sean válidos
  if (is.na(anio) || is.na(mes) || mes < 1 || mes > 12) {
    stop(
      "El valor proporcionado para 'añomes' no es válido. Debe ser un número en el formato 'YYYYMM'."
    )
  }
  
  # Verificar que la variable esté en el dataset
  if (!variable %in% colnames(data)) {
    stop(paste("La variable", variable, "no está presente en el dataset."))
  }
  
  # Convertir la columna 'fecha' a tipo Date (si no lo está)
  data <- data %>%
    mutate(date = as.Date(date))
  
  # Filtrar el dataset por el mes y año seleccionados
  data_filtrada <- data %>%
    filter(year(date) == anio & month(date) == mes)
  
  # Verificar si hay datos disponibles
  if (nrow(data_filtrada) == 0) {
    stop("No hay datos disponibles para el mes proporcionado.")
  } else {
    # Agregar una columna con solo el día del mes
    data_filtrada <- data_filtrada %>%
      mutate(dia = day(date))
    
    # Graficar la variable seleccionada en función de los días del mes
    ggplot(data_filtrada, aes(x = factor(dia), y = .data[[variable]])) +
      geom_line(color = "blue", group = 1) +
      labs(
        title = paste("Evolución de", variable, "por día en:", anio_mes_num),
        x = "Día",
        y = variable
      ) +
      theme_minimal() +
      theme(
        axis.text.x = element_text(angle = 90, hjust = 1, size = 8)  # Texto vertical y más pequeño
      )
  }
}

graficar_variable_anio_mes_num_multigrafico <- function(anio_mes_num, data, variable) {
  # Convertir el número entero a año y mes
  anio <- as.numeric(substr(as.character(anio_mes_num), 1, 4))
  mes <- as.numeric(substr(as.character(anio_mes_num), 5, 6))
  
  # Verificar que el año y mes sean válidos
  if (is.na(anio) || is.na(mes) || mes < 1 || mes > 12) {
    stop(
      "El valor proporcionado para 'añomes' no es válido. Debe ser un número en el formato 'YYYYMM'."
    )
  }
  
  # Verificar que la variable esté en el dataset
  if (!variable %in% colnames(data)) {
    stop(paste("La variable", variable, "no está presente en el dataset."))
  }
  
  # Convertir la columna 'date' a tipo Date (si no lo está)
  if (!inherits(data$date, "Date")) {
    data <- data %>%
      mutate(date = as.Date(date))
  }
  
  # Filtrar el dataset por el mes y año seleccionados
  data_filtrada <- data %>%
    filter(year(date) == anio & month(date) == mes)
  
  # Verificar si hay datos disponibles
  if (nrow(data_filtrada) == 0) {
    stop("No hay datos disponibles para el mes proporcionado.")
  }
  
  # Agregar una columna con solo el día del mes
  data_filtrada <- data_filtrada %>%
    mutate(dia = day(date))
  
  # Graficar la variable seleccionada en función de los días del mes
  ggplot(data_filtrada, aes(x = date, y = .data[[variable]])) +
    geom_line(color = "blue", group = 1) +
    facet_wrap(~ dia, ncol = 5, scales = "free_x") +  # Dividir gráficos por día, con 5 gráficos por fila
    labs(
      title = paste("Evolución de", variable, "en", anio, "-", mes),
      x = "Hora del Día",
      y = variable
    ) +
    theme_minimal() +
    theme(
      axis.text.x = element_text(angle = 45, hjust = 1, size = 8),  # Ajustar el texto en el eje X
      plot.title = element_text(hjust = 0.5)  # Centrar el título
    )
}
