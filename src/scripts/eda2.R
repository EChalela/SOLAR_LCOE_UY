install.packages(c("DataExplorer","skimr", "GGally", "funModeling", "summarytools", "explore"), dep = T)
library(DataExplorer)
DataExplorer::create_report(data_combined,output_file = "reportes/report_data_combined.html")
DataExplorer::create_report(simulated_daily_data, output_file = "reportes/report_simulated_daily.html")
library(skimr)
skimr::skim(data_combined)

library(GGally)
GGally::ggpairs(data_combined)
