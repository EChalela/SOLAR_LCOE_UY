install.packages("jsonlite", dep = T)
library(jsonlite)

# Cargar el archivo JSON desde una URL o desde un archivo local
# Supongamos que tienes un archivo 'datos.json'
json_data <- fromJSON("datos/open_meteo_2019_2023.json")

# Convertir el JSON a un DataFrame
df_json <- as.data.frame(json_data)
rm(json_data)
