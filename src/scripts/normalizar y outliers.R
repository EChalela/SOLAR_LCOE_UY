# Load necessary libraries
library(dplyr)

# Load your dataset
data <- read.csv("datos/simulated_data_2023_2024.csv")

# Normalize the columns
data <- data %>%
  mutate(
    Temperature_Norm = (Temperature - mean(Temperature, na.rm = TRUE)) / sd(Temperature, na.rm = TRUE),
    Relative.Humidity_Norm = (Relative.Humidity - mean(Relative.Humidity, na.rm = TRUE)) / sd(Relative.Humidity, na.rm = TRUE),
    Wind.Speed_Norm = (Wind.Speed - mean(Wind.Speed, na.rm = TRUE)) / sd(Wind.Speed, na.rm = TRUE),
    GHI_Norm = (GHI - mean(GHI, na.rm = TRUE)) / sd(GHI, na.rm = TRUE)
  )

# Detect outliers (values more than 3 standard deviations away from the mean)
data <- data %>%
  mutate(
    Temperature_Outlier = abs(Temperature - mean(Temperature, na.rm = TRUE)) > 3 * sd(Temperature, na.rm = TRUE),
    Relative.Humidity_Outlier = abs(Relative.Humidity - mean(Relative.Humidity, na.rm = TRUE)) > 3 * sd(Relative.Humidity, na.rm = TRUE),
    Wind.Speed_Outlier = abs(Wind.Speed - mean(Wind.Speed, na.rm = TRUE)) > 3 * sd(Wind.Speed, na.rm = TRUE),
    GHI_Outlier = abs(GHI - mean(GHI, na.rm = TRUE)) > 3 * sd(GHI, na.rm = TRUE)
  )

# Save the modified dataset
write.csv(data, "datos/normalized_data_with_outliers.csv", row.names = FALSE)

# View the first few rows of the modified data
head(data)
