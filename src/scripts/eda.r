# Instalar los paquetes necesarios si no los tienes instalados
# install.packages("GGally")
# install.packages("ggcorrplot")

# Cargar las librerías necesarias
library(ggplot2)
library(dplyr)
library(readr)
library(GGally)    # Para ggpairs
install.packages("ggcorrplot", dep = T)
library(ggcorrplot) # Para ggcorrplot
library(scales)    # Para escalas en gráficos

# Cargar los datos simulados
simulated_daily_data <- readr::read_csv("datos/simulated_daily_data.csv")
simulated_hourly_data <- readr::read_csv("datos/simulated_hourly_data.csv")

# Verificar los nombres de las columnas y renombrar si es necesario
names(simulated_daily_data)
names(simulated_daily_data) <- make.names(names(simulated_daily_data))  # Cambiar espacios por puntos y eliminar caracteres especiales

# Si aún hay errores, muestra los nombres de las columnas
print(names(simulated_daily_data))

# Convertir las fechas para los datos diarios
simulated_daily_data$Date <- as.Date(paste(simulated_daily_data$Year, simulated_daily_data$Month, simulated_daily_data$Day, sep = "-"))

# Convertir a datetime para los datos horarios
simulated_hourly_data$Datetime <- as.POSIXct(paste(simulated_hourly_data$Year, simulated_hourly_data$Month, simulated_hourly_data$Day, simulated_hourly_data$Hour, sep = "-"), format = "%Y-%m-%d-%H")

### 1. Histograma de la temperatura diaria ###
hist_temperature <- ggplot(simulated_daily_data, aes(x = Temperature)) +
  geom_histogram(binwidth = 1, fill = "blue", color = "black", alpha = 0.7) +
  labs(title = "Distribución de la Temperatura Diaria", x = "Temperatura (°C)", y = "Frecuencia") +
  theme_minimal()

# Mostrar el gráfico
print(hist_temperature)

# Guardar el gráfico
ggsave("images/histogram_temperature.png", plot = hist_temperature, width = 7, height = 7)

### 2. Histograma de la humedad relativa diaria ###
hist_humidity <- ggplot(simulated_daily_data, aes(x = Relative.Humidity)) +  # Usamos el nombre de columna corregido
  geom_histogram(binwidth = 5, fill = "green", color = "black", alpha = 0.7) +
  labs(title = "Distribución de la Humedad Relativa Diaria", x = "Humedad Relativa (%)", y = "Frecuencia") +
  theme_minimal()

# Mostrar el gráfico
print(hist_humidity)

# Guardar el gráfico
ggsave("images/histogram_humidity.png", plot = hist_humidity, width = 7, height = 7)

### 3. Boxplot de la temperatura diaria por mes ###
boxplot_temperature <- ggplot(simulated_daily_data, aes(x = factor(Month), y = Temperature)) +
  geom_boxplot(fill = "orange", color = "black", alpha = 0.7) +
  labs(title = "Boxplot de la Temperatura por Mes", x = "Mes", y = "Temperatura (°C)") +
  scale_x_discrete(labels = month.abb) +  # Etiquetas de meses abreviadas
  theme_minimal()

# Mostrar el gráfico
print(boxplot_temperature)

# Guardar el gráfico
ggsave("images/boxplot_temperature_by_month.png", plot = boxplot_temperature, width = 7, height = 7)

### 4. Boxplot de la velocidad del viento diaria por mes ###
boxplot_wind_speed <- ggplot(simulated_daily_data, aes(x = factor(Month), y = Wind.Speed)) +  # Nombre corregido de la columna
  geom_boxplot(fill = "purple", color = "black", alpha = 0.7) +
  labs(title = "Boxplot de la Velocidad del Viento por Mes", x = "Mes", y = "Velocidad del Viento (m/s)") +
  scale_x_discrete(labels = month.abb) +
  theme_minimal()

# Mostrar el gráfico
print(boxplot_wind_speed)

# Guardar el gráfico
ggsave("images/boxplot_wind_speed_by_month.png", plot = boxplot_wind_speed, width = 7, height = 7)

# Revisar nombres de columnas
print(names(simulated_daily_data))

# Verificar si las columnas tienen los nombres correctos
# Esto es importante ya que `make.names()` pudo haber cambiado los nombres
# Por ejemplo: 'Relative Humidity' -> 'Relative.Humidity'

### 5. Matriz de correlación ###
# Verificar los nombres y seleccionar las columnas correctas
cor_matrix <- simulated_daily_data %>%
  select(Temperature, Relative.Humidity, Wind.Speed, GHI) %>%  # Nombres corregidos
  cor(use = "complete.obs")  # Ignorar NA

# Imprimir la matriz de correlación para verificar
print(cor_matrix)

# Crear el gráfico de correlación
correlation_plot <- ggcorrplot(cor_matrix, lab = TRUE) +  # Función de ggcorrplot
  labs(title = "Matriz de Correlaciones de las Variables Diarias")

# Mostrar el gráfico
print(correlation_plot)

# Guardar el gráfico
ggsave("images/correlation_matrix.png", plot = correlation_plot, width = 7, height = 7)

### 6. Gráfico de pares ###
# Verificar la selección de las columnas antes de crear el gráfico
pairs_plot <- ggpairs(simulated_daily_data %>% select(Temperature, Relative.Humidity, Wind.Speed, GHI)) +
  labs(title = "Gráfico de Pares de las Variables Diarias")

# Mostrar el gráfico
print(pairs_plot)

# Guardar el gráfico
ggsave("images/pairs_plot.png", plot = pairs_plot, width = 10, height = 10)

### 7. Gráfico de tendencias ###
# Tendencias de GHI por hora
ghi_trend <- ggplot(simulated_hourly_data, aes(x = Datetime, y = GHI)) +
  geom_line(color = "orange") +
  labs(title = "Tendencia de GHI por Hora", x = "Fecha y Hora", y = "GHI (W/m²)") +
  theme_minimal()

# Mostrar el gráfico
print(ghi_trend)

# Guardar el gráfico
ggsave("images/ghi_trend.png", plot = ghi_trend, width = 10, height = 6)

# Tendencia de la velocidad del viento por hora
wind_speed_trend <- ggplot(simulated_hourly_data, aes(x = Datetime, y = Wind.Speed)) +
  geom_smooth(color = "purple") +
  labs(title = "Tendencia de la Velocidad del Viento por Hora", x = "Fecha y Hora", y = "Velocidad del Viento (m/s)") +
  theme_minimal()

# Mostrar el gráfico
print(wind_speed_trend)

# Guardar el gráfico
ggsave("images/wind_speed_trend.png", plot = wind_speed_trend, width = 10, height = 6)

