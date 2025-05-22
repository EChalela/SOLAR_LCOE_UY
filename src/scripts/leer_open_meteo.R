source("funciones.R")

om_2020 <- rio::import("datos/OpenMeteo/open-meteo-33.01S55.99W103m_2020.csv", skip = 3, header = TRUE)
om_2021 <- rio::import("datos/OpenMeteo/open-meteo-33.01S55.99W103m_2021.csv", skip = 3, header = TRUE)
om_2022 <- rio::import("datos/OpenMeteo/open-meteo-33.01S55.99W103m_2022.csv", skip = 3, header = TRUE)
om_2023 <- rio::import("datos/OpenMeteo/open-meteo-33.01S55.99W103m_2023.csv", skip = 3, header = TRUE)
om_2024_oct15 <- rio::import("datos/OpenMeteo/open-meteo-33.01S55.99W103m_2024_20241015.csv", skip = 3, header = TRUE)
om <-rbind(om_2020, om_2021, om_2022,om_2023, om_2024_oct15)
rm(om_2020, om_2021, om_2022,om_2023, om_2024_oct15)

rio::export(om, "datos/OpenMeteo/om.csv")
