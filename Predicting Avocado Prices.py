# -*- coding: utf-8 -*-
"""Predicting Avocado Prices.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/180qB0qpG7N_4tRkcHsoACAkz3_tvlDC0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from xgboost import XGBRegressor

# Load and preprocess data
df = pd.read_csv('/content/avocado.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date')

# Feature engineering
df['year'] = df['Date'].dt.year
df['month'] = df['Date'].dt.month
df['dayofweek'] = df['Date'].dt.dayofweek
df['dayofyear'] = df['Date'].dt.dayofyear
df['weekofyear'] = df['Date'].dt.isocalendar().week

# One-hot encoding for categorical variables
df = pd.get_dummies(df, columns=['type', 'region'], drop_first=True)

# Lag and rolling features
df['price_lag1'] = df['AveragePrice'].shift(1)
df['price_lag7'] = df['AveragePrice'].shift(7)
df['rolling_mean_7'] = df['AveragePrice'].rolling(window=7).mean()
df['rolling_std_7'] = df['AveragePrice'].rolling(window=7).std()

df.dropna(inplace=True)

# Split data
X = df.drop(['AveragePrice', 'Date'], axis=1)
y = df['AveragePrice']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Hyperparameter tuning using GridSearchCV
params = {
    'n_estimators': [100, 200],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1]
}

xgb = XGBRegressor(random_state=42)
grid = GridSearchCV(xgb, param_grid=params, cv=3, scoring='neg_mean_squared_error', verbose=1, n_jobs=-1)
grid.fit(X_train, y_train)

best_model = grid.best_estimator_

print("✅ Best Hyperparameters:")
print(grid.best_params_)

# Predict and evaluate
y_pred = best_model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"\n📊 Model Performance on Test Set:")
print(f"MAE: {mae:.3f}")
print(f"RMSE: {rmse:.3f}")
print(f"R²: {r2:.3f}")

# Plot actual vs predicted
plt.figure(figsize=(12,6))
plt.plot(y_test.values, label='Actual Price')
plt.plot(y_pred, label='Predicted Price')
plt.legend()
plt.title('Actual vs Predicted Avocado Prices (XGBoost)')
plt.xlabel('Sample Index')
plt.ylabel('Price ($)')
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot feature importance
importance_df = pd.DataFrame({
    'Feature': X.columns,
    'Importance': best_model.feature_importances_
}).sort_values(by='Importance', ascending=False)

plt.figure(figsize=(10,6))
sns.barplot(x='Importance', y='Feature', data=importance_df.head(15))
plt.title("Top 15 Feature Importances (XGBoost)")
plt.tight_layout()
plt.show()

