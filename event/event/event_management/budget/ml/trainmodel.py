from sklearn.linear_model import LinearRegression
import pandas as pd
import pickle
import os

# Paths
csv_path = os.path.join(os.path.dirname(__file__), 'event_budget.csv')
model_path = os.path.join(os.path.dirname(__file__), 'budget_model.pkl')

# Load dataset
data = pd.read_csv(csv_path)

# Features and target
X = data[['guests', 'location', 'catering', 'decoration']]
y = data['budget']

# Train model
model = LinearRegression()
model.fit(X, y)

# Save model
pickle.dump(model, open(model_path, 'wb'))

print("Model trained and saved successfully at:", model_path)
