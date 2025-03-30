import pandas as pd
import networkx as nx
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import euclidean_distances
import matplotlib.pyplot as plt

# Load the dataset
data = pd.read_csv('C:/desktop/maindata.csv')

# Filter the data to include only Oakland Athletics players
oakland_data = data[data['Team'] == 'OAK'].reset_index(drop=True)

# Normalize the relevant statistics for similarity computation
scaler = MinMaxScaler()
oakland_data[['PA', 'WAR', 'pythW', 'WARSHARE']] = scaler.fit_transform(
    oakland_data[['PA', 'WAR', 'pythW', 'WARSHARE']]
)

# Compute the Euclidean distance matrix based on the selected features
dist_matrix = euclidean_distances(oakland_data[['PA', 'WAR', 'pythW', 'WARSHARE']])

# Create an empty NetworkX graph
G = nx.Graph()

# Add nodes to the graph, representing each Oakland player
for _, player in oakland_data.iterrows():
    G.add_node(player['Name'], season=player['Season'], WAR=player['WAR'], WARSHARE=player['WARSHARE'])

# Set a similarity threshold for adding edges
threshold = 0.3  # A lower threshold means stricter similarity

# Add edges between Oakland players based on the similarity threshold
total_players = len(oakland_data)
for i in range(total_players):
    for j in range(i + 1, total_players):
        if dist_matrix[i, j] < threshold:
            G.add_edge(oakland_data.loc[i, 'Name'], oakland_data.loc[j, 'Name'], weight=1 - dist_matrix[i, j])

# Identify the top 3 most central players based on degree centrality
degree_centrality = nx.degree_centrality(G)
top_3_players = sorted(degree_centrality, key=degree_centrality.get, reverse=True)[:3]
print("Top 3 most central Oakland players:", top_3_players)

# Generate a graph for each top player with only their valid teammates
for player in top_3_players:
    # Get seasons when this player was with Oakland
    player_seasons = oakland_data[oakland_data['Name'] == player]['Season'].unique()

    # Filter teammates who played in the same seasons
    valid_teammates = oakland_data[oakland_data['Season'].isin(player_seasons)]['Name'].unique()

    # Create a subgraph with only this player and their teammates
    subgraph = G.subgraph(valid_teammates)

    # Visualize the network
    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(subgraph, seed=42)

    # Define node sizes and colors
    node_sizes = [800 if node == player else 300 for node in subgraph.nodes]
    node_colors = ['red' if node == player else 'blue' for node in subgraph.nodes]

    # Draw the graph
    nx.draw(subgraph, pos, with_labels=True, node_size=node_sizes, font_size=12, edge_color='gray', 
            node_color=node_colors, alpha=0.5)

    plt.title(f"OAK Player Similarity Network (Centered on {player})")
    plt.show()
# Convert PA, WAR, and WARSHARE to numeric values (force errors to NaN)
original_stats = data[data['Team'] == 'OAK'][['Name', 'Season', 'PA', 'WAR', 'WARSHARE']].reset_index(drop=True)
original_stats[['PA', 'WAR', 'WARSHARE']] = original_stats[['PA', 'WAR', 'WARSHARE']].apply(pd.to_numeric, errors='coerce')

# Print the original PA, WAR, and WARSHARE for each season for the top 3 most central players
oakland_data = data[data['Team'] == 'OAK'].reset_index(drop=True)

# Convert PA, WAR, and WARSHARE to numeric values, handling errors
oakland_data[['PA', 'WAR', 'WARSHARE']] = oakland_data[['PA', 'WAR', 'WARSHARE']].apply(pd.to_numeric, errors='coerce')

# Compute the overall average for PA, WAR, and WARSHARE in the Oakland dataset
average_pa = oakland_data['PA'].mean()
average_war = oakland_data['WAR'].mean()
average_warshare = oakland_data['WARSHARE'].mean()

# Display the results
print("\nOverall average PA, WAR, and WARSHARE for Oakland Athletics players:")
print(f"Average PA: {average_pa:.2f}")
print(f"Average WAR: {average_war:.2f}")
print(f"Average WARSHARE: {average_warshare:.4f}")