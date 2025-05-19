library(tidyverse)
library(dplyr)
library(readr)
library(fastDummies)

baseball <- read.csv("https://raw.githubusercontent.com/joniaco0/jour479x_fall_2024/refs/heads/main/data/WARdata.csv")
standings <- read.csv("https://raw.githubusercontent.com/joniaco0/jour479x_fall_2024/refs/heads/main/data/MLB_Data_with_Abbreviations%20-%20MLB_Data_with_Abbreviations.csv")

standings <- standings |> rename(Team = Tm)
baseball$Season <- as.integer(baseball$Season)

merged_data <- baseball |>
  left_join(standings, by = c("Team", "Season"))

merged_data$WAR <- as.numeric(merged_data$WAR)

corrections <- merged_data |>
  mutate(Team = case_when(
    Team %in% c("FLA", "MIA") ~ "MIA",
    Team %in% c("ANA", "LAA") ~ "LAA",
    Team %in% c("TBR", "TBD") ~ "TBR",
    Team %in% c("WSN", "MON") ~ "WSN",
    TRUE ~ Team
  ))

maindata <- corrections |> 
  select(Season, Name, PA, Team, WAR, pythW, pythL) |>
  mutate(WARSHARE = WAR / pythW)

maindata <- maindata %>%
  distinct(Team, Season, Name, .keep_all = TRUE)

write_csv(maindata, "maindata_cleaned.csv")
