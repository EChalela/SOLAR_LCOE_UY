library(CoSMoS)




DBwh <- bind_rows(DB) |>
  mutate(date = ymd_h(paste(Year,"-",Month,"-",Day,"-", " ",Hour) )) |>
  rename(value = `Wind Speed`) |>
  select(date, value) |>
  as.data.table()


quickTSPlot(DB$value)


wspd_adj <- analyzeTS(DB)


reportTS(wspd_adj, 'dist')
reportTS(wspd_adj, 'acs')
reportTS(wspd_adj, 'stat')


checkTS(wspd_adj)
