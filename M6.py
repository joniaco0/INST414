import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
df = pd.read_csv("Pitchers Stats 2 - Sheet1.csv")

# Clean percentage columns and convert to float
percent_columns = ['GB%', 'K%', 'BB%', 'K-BB%']
for col in percent_columns:
    df[col] = df[col].str.replace('%', '').astype(float)

# Select features and target
features = ['ERA', 'FIP', 'xFIP', 'WPA', 'GB%', 'K-BB%', 'IP']
target = 'WAR'

# Drop rows with missing values in selected columns
df_model = df[features + [target]].dropna()

# Separate into X and y
X = df_model[features]
y = df_model[target]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build and train pipeline
pipeline = make_pipeline(StandardScaler(), RandomForestRegressor(n_estimators=100, random_state=42))
pipeline.fit(X_train, y_train)

# Predict and evaluate
y_pred = pipeline.predict(X_test)
rmse = mean_squared_error(y_test, y_pred) ** 0.5

r2 = r2_score(y_test, y_pred)

print(f"RMSE: {rmse:.2f}")
print(f"R² Score: {r2:.2f}")

# Plot Actual vs Predicted WAR
plt.figure(figsize=(6, 6))
plt.scatter(y_test, y_pred, alpha=0.7)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
plt.xlabel('Actual WAR')
plt.ylabel('Predicted WAR')
plt.title('Actual vs. Predicted WAR')
plt.grid(True)
plt.tight_layout()
plt.show()

# Add predictions back to the DataFrame to inspect errors
results_df = df.loc[y_test.index].copy()
results_df['Predicted_WAR'] = y_pred
results_df['Error'] = abs(results_df['WAR'] - results_df['Predicted_WAR'])

# Show top 5 prediction errors
top_errors = results_df.sort_values(by='Error', ascending=False).head(5)
print("\nTop 5 Prediction Errors:")
print(top_errors[['Season', 'Name', 'Team', 'WAR', 'Predicted_WAR', 'Error']])

# Feature Importance Plot
model = pipeline.named_steps['randomforestregressor']
importances = model.feature_importances_
importance_df = pd.DataFrame({'Feature': features, 'Importance': importances})
importance_df = importance_df.sort_values(by='Importance', ascending=False)

plt.figure(figsize=(8, 5))
sns.barplot(x='Importance', y='Feature', data=importance_df)
plt.title('Feature Importance in Predicting WAR')
plt.tight_layout()
plt.show()

results = df.loc[y_test.index].copy()
results['Actual_WAR'] = y_test.values
results['Predicted_WAR'] = y_pred
results['Error'] = abs(results['Actual_WAR'] - results['Predicted_WAR'])

# Sort by least error and select top 10 most accurate predictions
top_accurate = results.sort_values(by='Error').head(10)

# Display the results
print(top_accurate[['Season', 'Name', 'Team', 'Actual_WAR', 'Predicted_WAR', 'Error']])