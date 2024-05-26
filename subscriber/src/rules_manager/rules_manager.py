import pandas as pd
import numpy as np
import sys
import tensorflow as tf
from tensorflow import keras
sys.path.append('/home/matheus/Documentos/GIT/FuzzyLogicExp/subscriber/src')

# Define pre-processing function (replace with your actual scaling method)
def scale_data(data):
    # Standardize features using min-max scaling or normalization
    return (data - data.min(axis=0)) / (data.max(axis=0) - data.min(axis=0))

data = pd.read_csv('./results.csv')

# Preprocess data
scaled_data = scale_data(data)
features = scaled_data[:, :-1]  # Separate features
# Separate target (assuming last column is membership function indicator)
targets = data[:, -1]

# Define the Model
model = keras.Sequential([
    keras.Input(shape=(features.shape[1],)),  # Input layer for 4 features
    # Hidden layer with 16 neurons and ReLU activation
    keras.layers.Dense(16, activation="relu"),
    # Another hidden layer with 32 neurons and ReLU activation
    keras.layers.Dense(32, activation="relu"),
    # Output layer with number of neurons equal to total membership functions (assuming 10)
    keras.layers.Dense(10, activation="sigmoid"),
])

# Compile the model (Categorical crossentropy loss for binary classification, Adam optimizer)
model.compile(loss="categorical_crossentropy",
              optimizer="adam", metrics=["accuracy"])

# Train the model (replace with your training parameters)
model.fit(features, targets, epochs=100, batch_size=32)

# Generate fuzzy rules for a new data point (replace with your new data)
new_data = ...  # Your new data point with 4 features
scaled_new_data = scale_data(np.array([new_data]))  # Scale the new data point

# Get model prediction
fuzzy_rule_antecedent = model.predict(scaled_new_data)[0]

# Threshold to convert probabilities to binary (replace 0.5 with your chosen threshold)
fuzzy_rule_antecedent = (fuzzy_rule_antecedent > 0.5).astype(int)

# Print the generated fuzzy rule antecedent (active membership functions)
print("Generated Fuzzy Rule Antecedent:", fuzzy_rule_antecedent)
