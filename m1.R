library(tidyverse)
library(dplyr)
library(readr)
baseball <- read.csv("https://raw.githubusercontent.com/joniaco0/INST414/main/WARdata.csv")
standings <- read.csv("https://raw.githubusercontent.com/joniaco0/INST414/main/MLB_Data_with_Abbreviations%20-%20MLB_Data_with_Abbreviations%20(1).csv")
standings <- standings |> rename(Team = Tm)
baseball$Season <- as.integer(baseball$Season)
merged_data <- baseball |>
  left_join(standings, by = c("Team", "Season"))
merged_data
merged_data$WAR <- as.numeric(merged_data$WAR)
corrections <- merged_data |>
  mutate(Team = case_when(
    Team %in% c("FLA", "MIA") ~ "MIA",
    Team %in% c("ANA", "LAA") ~ "LAA",
    Team %in% c("TBR", "TBD") ~ "TBR",
    Team %in% c("WSN", "MON") ~ "WSN",
    TRUE ~ Team # Keep other teams unchanged
  ))
maindata <- corrections |> select(Season, Name, PA, Team, WAR, pythW,pythL) |> mutate(WARSHARE = WAR/pythW)
maindata <- maindata %>%
  distinct(Team, Season, Name, .keep_all = TRUE)  # Keeps the first occurrence of duplicates

library(dplyr)
library(ggiraph)
library(ggplot2)
# Process data to avoid double counting
combined_data <- maindata %>%
  filter(Season >= 2000) %>%
  mutate(
    WinsAbove500 = pythW - 0.5 * (pythW + pythL),
    Relative_WAR = WAR - 2
  ) %>%
  group_by(Team, Season) %>%
  summarize(
    Total_WinsAbove500 = sum(WinsAbove500, na.rm = TRUE),
    Total_Relative_WAR = sum(Relative_WAR, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  arrange(Team, Season) %>%
  group_by(Team) %>%
  mutate(
    CumulativeWinsAbove500 = cumsum(Total_WinsAbove500),
    CumulativeRelativeWAR = cumsum(Total_Relative_WAR),
    Highlight = ifelse(Team == "MIA" | Team == "OAK", "Highlighted", "Normal"),
    css_id = paste0("line-", Team)
  ) %>%
  ungroup()

long_data <- combined_data |>
  pivot_longer(
    cols = c(CumulativeWinsAbove500, CumulativeRelativeWAR),
    names_to = "Metric",
    values_to = "CumulativeValue"
  )

# Interactive ggplot object with original lines
gg_combined <- ggplot(long_data, aes(
  x = Season,
  y = CumulativeValue,
  group = Team
)) +
  geom_line_interactive(
    aes(
      color = ifelse(Team == "MIA", "MIA",
                     ifelse(Team == "OAK", "OAK", "Other")),  # Highlight specific teams
      alpha = ifelse(Team %in% c("MIA", "OAK"), 1, 0.3),  # Adjust opacity
      tooltip = Team,  # Tooltip only displays the team name
      data_id = Team   # Identifier for interactivity
    ),
    size = ifelse(long_data$Team %in% c("MIA", "OAK"), 1.5, 0.8)  # Thicker lines for MIA and OAK
  ) +
  scale_color_manual(
    values = c(
      "MIA" = "blue",   # Highlight MIA in blue
      "OAK" = "green",  # Highlight OAK in green
      "Other" = "gray"  # All other teams in gray
    )
  ) +
  scale_alpha_identity() +  # Map alpha values directly
  facet_wrap(~ Metric, scales = "free_y", ncol = 1) +  # Separate panels for each metric
  labs(
    title = "The Marlins and A's drift apart from each other",
    x = "Season",
    y = "Cumulative Value",
    color = "Team"
  ) +
  theme_minimal() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1, size = 10),  # Rotate and adjust season labels
    axis.title = element_text(size = 12),  # Larger axis titles
    legend.position = "bottom",
    strip.text = element_text(size = 14, face = "bold")  # Emphasize facet titles
  )

# Custom CSS for hover effects
custom_css <- "
  .ggiraph-hover { 
    stroke-width: 3px; 
    opacity: 1; 
  }
  .ggiraph-active line {
    opacity: 0.5; /* Keep non-hovered lines more visible */
  }
  line:hover { 
    opacity: 1; 
    stroke-width: 3px; 
  }
"

# Convert ggplot to interactive ggiraph object
interactive_combined_plot <- girafe(ggobj = gg_combined)

# Add interactivity options
interactive_combined_plot <- girafe_options(
  interactive_combined_plot,
  opts_hover(css = custom_css),
  opts_hover_inv(css = "opacity: 0.2;"),
  opts_tooltip(
    opacity = 0.9,
    css = "background-color: white; padding: 5px; border: 1px solid gray; border-radius: 5px; font-size: 12px;"
  ),
  opts_sizing(rescale = TRUE, width = 0.7)  # Fit graph to RStudio Viewer
)
interactive_combined_plot
# Data transformation
normalized_data <- combined_data |>
  mutate(
    Norm_WinsAbove500 = (CumulativeWinsAbove500 - min(CumulativeWinsAbove500)) / 
      (max(CumulativeWinsAbove500) - min(CumulativeWinsAbove500)),
    Norm_RelativeWAR = (CumulativeRelativeWAR - min(CumulativeRelativeWAR)) / 
      (max(CumulativeRelativeWAR) - min(CumulativeRelativeWAR))
  )

# Calculate the difference between the normalized metrics
normalized_data <- normalized_data |>
  mutate(
    Difference = Norm_RelativeWAR - Norm_WinsAbove500
  )

# Aggregate the differences to identify teams with the largest discrepancies
team_discrepancies <- normalized_data |>
  group_by(Team) |>
  summarize(
    Avg_Difference = mean(Difference, na.rm = TRUE),
    Total_Difference = sum(Difference, na.rm = TRUE)
  ) |>
  arrange(desc(Total_Difference))

# Create the ggplot chart (non-interactive)
interactive_chart <- ggplot(normalized_data, aes(x = Difference, y = Season, group = Team)) +
  geom_line(
    aes(
      color = ifelse(Team == "MIA", "MIA",
                     ifelse(Team == "OAK", "OAK", "Other")),  # Highlight MIA and OAK
    ),
    alpha = ifelse(normalized_data$Team %in% c("MIA", "OAK"), 1, 0.5),  # Highlight opacity for MIA and OAK
    size = ifelse(normalized_data$Team %in% c("MIA", "OAK"), 1.5, 1)  # Thicker lines for highlighted teams
  ) +
  scale_color_manual(
    values = c(
      "MIA" = "blue",    # MIA highlighted in blue
      "OAK" = "green",   # OAK highlighted in green
      "Other" = "gray"   # Other teams in gray
    )
  ) +
  labs(
    title = "Discrepancy Between WAR and Wins Above .500 Over Seasons",
    x = "Difference (Normalized WAR - Wins Above .500)",
    y = "Season",
    color = "Team Highlight"
  ) +
  theme_minimal() +
  theme(
    legend.position = "bottom",
    axis.text.y = element_text(angle = 0, hjust = 1),  # Adjust y-axis text angle for clarity
    axis.title = element_text(size = 10),  # Reduced title size
    axis.text = element_text(size = 8),    # Reduced axis label size
    plot.title = element_text(size = 12, face = "bold"),
    plot.margin = margin(10, 10, 10, 10)  # Adjust margins if needed
  )

# Save the ggplot chart with adjusted size
ggsave("discrepancy_chart.png", plot = interactive_chart, width = 6, height = 4, dpi = 300)
interactive_chart
# Create the interactive plot with OAK in green, MIA in blue, and others in gray
gg_cluster <- ggplot(team_stats, aes(x = pythW, y = weighted_WAR)) +
  geom_point_interactive(
    aes(
      color = ifelse(
        Team == "OAK", "OAK",
        ifelse(Team == "MIA", "MIA", "Other")
      ),
      tooltip = paste(Team, "\n", "Season:", Season),
      data_id = Team
    ),
    size = 4,
    alpha = 0.7
  ) +
  scale_color_manual(
    values = c("OAK" = "green", "MIA" = "blue", "Other" = "gray")
  ) +
  labs(
    title = "Correlation of WAR with Pythagorean Wins for Selected Teams",
    x = "Pythagorean Wins (PythW)",
    y = "Weighted WAR",
    color = "Team"
  ) +
  theme_minimal() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),
    axis.title = element_text(size = 12),
    legend.position = "bottom"
  )

# Convert ggplot to interactive ggiraph object
interactive_gg_cluster <- girafe(ggobj = gg_cluster)

# Add interactive options
interactive_gg_cluster <- girafe_options(
  interactive_gg_cluster,
  opts_hover(css = "opacity: 0.9;"),
  opts_tooltip(css = "background-color: white; padding: 5px; border: 1px solid gray; border-radius: 5px; font-size: 12px;"),
  opts_sizing(rescale = TRUE, width = 0.7)
)

interactive_gg_cluster
