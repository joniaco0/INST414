import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Load your dataset
df = pd.read_csv("Pitchers414.csv")  # Replace with your file path

# Clean percentage columns and convert to float
df['K-BB%'] = df['K-BB%'].str.replace('%', '').astype(float)
df['GB%'] = df['GB%'].str.replace('%', '').astype(float)

# Select relevant features for clustering
features = df[['ERA','WAR', 'FIP', 'xFIP', 'WPA', 'K-BB%', 'GB%']].copy()

# Drop rows with missing values
features.dropna(inplace=True)

# Standardize the features
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# Determine optimal k using elbow method
wcss = []
k_values = range(1, 11)
for k in k_values:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(scaled_features)
    wcss.append(kmeans.inertia_)

# Plot elbow curve
plt.plot(k_values, wcss, marker='o')
plt.title('Elbow Method for Optimal k')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('WCSS')
plt.grid(True)
plt.show()

# Fit KMeans with chosen k
k = 4
kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
clusters = kmeans.fit_predict(scaled_features)

# Assign clusters back to original dataframe
clustered_df = df.loc[features.index].copy()
clustered_df['Cluster'] = clusters

# Reduce to 2D for PCA plotting
pca = PCA(n_components=2)
reduced_features = pca.fit_transform(scaled_features)
plot_df = pd.DataFrame(reduced_features, columns=['PC1', 'PC2'])
plot_df['Cluster'] = clusters

# Plot PCA scatter
plt.figure(figsize=(8, 6))
for cluster_id in plot_df['Cluster'].unique():
    cluster_data = plot_df[plot_df['Cluster'] == cluster_id]
    plt.scatter(cluster_data['PC1'], cluster_data['PC2'], label=f'Cluster {cluster_id}', alpha=0.7)
plt.title('PCA of Pitcher Clusters')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.legend()
plt.grid(True)
plt.show()

# Show top 3 pitchers in each cluster by WAR
notable_by_cluster = {}
for cluster_id in sorted(clustered_df['Cluster'].unique()):
    top_in_cluster = clustered_df[clustered_df['Cluster'] == cluster_id].sort_values(by='WAR', ascending=False).head(3)
    notable_by_cluster[f'Cluster {cluster_id}'] = top_in_cluster[['Season', 'Name', 'Team', 'ERA','WAR', 'FIP', 'xFIP', 'WPA', 'K-BB%', 'GB%']]

# Print results
for label, group in notable_by_cluster.items():
    print(f"\n{label}")
    print(group.to_string(index=False))
print("\nAverage Stats by Cluster:")
cluster_means = clustered_df.groupby('Cluster')[['ERA', 'WAR', 'FIP', 'xFIP', 'WPA', 'K-BB%', 'GB%']].mean().round(2)
print(cluster_means)