import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from scipy.spatial.distance import euclidean

df_original = pd.read_csv("C:/desktop/maindata_cleaned.csv")

df = df_original.copy()
df = df.apply(lambda x: x.str.replace('"', '') if x.dtype == "object" else x)
df[['PA', 'WAR', 'pythW', 'WARSHARE']] = df[['PA', 'WAR', 'pythW', 'WARSHARE']].apply(pd.to_numeric, errors='coerce')
df[['PA', 'WAR', 'pythW', 'WARSHARE']] = df[['PA', 'WAR', 'pythW', 'WARSHARE']].fillna(df[['PA', 'WAR', 'pythW', 'WARSHARE']].mean())

scaler = MinMaxScaler()
df[['PA', 'WAR', 'pythW', 'WARSHARE']] = scaler.fit_transform(df[['PA', 'WAR', 'pythW', 'WARSHARE']])

def calculate_similarity(player, season, df, df_original):
    player_data = df[(df['Name'] == player) & (df['Season'] == season)]
    
    if player_data.empty:
        print(f"Player {player} not found in the dataset for season {season}.")
        return [], None  

    player_vector = player_data[['PA', 'WAR', 'pythW', 'WARSHARE']].values.flatten()
    query_player_stats = df_original[(df_original['Name'] == player) & (df_original['Season'] == season)]

    similarities = []
    
    for _, row in df.iterrows():
        if row['Name'] != player:
            player_to_compare_vector = row[['PA', 'WAR', 'pythW', 'WARSHARE']].values
            if len(player_vector) == len(player_to_compare_vector):  
                similarity_score = euclidean(player_vector, player_to_compare_vector)
                similarities.append({
                    'Season': row['Season'],
                    'Name': row['Name'],
                    'Similarity Score': similarity_score
                })

    similarities.sort(key=lambda x: x['Similarity Score'])
    return similarities[:10], query_player_stats

query_results = {}
player_queries = [('Chris Taylor', 2022),('Brent Rooker',2023),('Barry Bonds',2001),('Barry Bonds',2004)]

for player, season in player_queries:
    query_results[f"{player} ({season})"], query_player_stats = calculate_similarity(player, season, df, df_original)

    if not query_player_stats.empty:
        print(f"\nQuery Player: {player} ({season})")
        print(f"Team: {query_player_stats['Team'].values[0]}")
        print(f"PA: {query_player_stats['PA'].values[0]}, WAR: {query_player_stats['WAR'].values[0]}, "
              f"PythW: {query_player_stats['pythW'].values[0]}, WARSHARE: {query_player_stats['WARSHARE'].values[0]}")
        print("\nTop 10 most similar players:\n")

    for rank, res in enumerate(query_results[f"{player} ({season})"], start=1):
        original_stats = df_original[(df_original['Name'] == res['Name']) & (df_original['Season'] == res['Season'])]

        if not original_stats.empty:
            print(f"{rank}. Season: {res['Season']}, Name: {res['Name']}, Similarity Score: {res['Similarity Score']:.6f}")
            print(f"   Team: {original_stats['Team'].values[0]}")
            print(f"   PA: {original_stats['PA'].values[0]}, WAR: {original_stats['WAR'].values[0]}, "
                  f"PythW: {original_stats['pythW'].values[0]}, WARSHARE: {original_stats['WARSHARE'].values[0]}")
            print("")
