import streamlit as st
import pandas as pd
import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the trained model
with open('linear_regression_model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

# Load the scaler
with open('scaler.pkl', 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

# App title
st.title('CredYukti AI')  # This sets the heading on the webpage

# Sidebar - Feature Input Section
st.sidebar.header('Input the features')
feature_values = []

# Assuming the model expects 10 features, create input fields
for i in range(1, 11):  # Adjust the range based on your model's feature count
    feature_values.append(st.sidebar.number_input(f"Feature {i}", min_value=0.0, value=0.0))

# Convert the input feature values to a NumPy array
input_data = np.array(feature_values).reshape(1, -1)

# Button to make predictions
if st.sidebar.button('Make Prediction'):
    if len(feature_values) == 10:  # Ensure the number of inputs matches the required feature count
        # Scale the input data using the loaded scaler
        scaled_data = scaler.transform(input_data)

        # Make predictions using the loaded model
        prediction = model.predict(scaled_data)

        # Display the result
        st.write(f"Predicted Value: {prediction[0]:.2f}")
    else:
        st.error("Please input all feature values.")
        
# Visualize model performance metrics
st.sidebar.subheader('Model Performance Metrics')
st.sidebar.write('R²: 0.9991')  # Replace with your actual R² score
st.sidebar.write('MAE: 0.1384')  # Replace with your MAE
st.sidebar.write('MSE: 0.019')   # Replace with your MSE
st.sidebar.write('RMSE: 0.138')  # Replace with your RMSE

# Add model explanation
st.sidebar.subheader("How the Model Works")
st.sidebar.write("""
    This model predicts the target variable based on features provided in the input.
    It uses Linear Regression, which assumes a linear relationship between the features and the target.
    The model was trained using a dataset with features X1, X2, ..., X10 (e.g., feature names).
    """)
