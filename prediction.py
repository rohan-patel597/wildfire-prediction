import pickle
import pandas as pd
import numpy as np

# Loading the trained random forest model
with open('random_forest_model.pkl', 'rb') as model_file:
    random_forest_model = pickle.load(model_file)

print("Model loaded successfully!")

# Load the saved feature names
with open("all_feature_names.pkl", "rb") as file:
    all_feature_names = pickle.load(file)

# Load the saved mappings
class_names = np.load('label_mappings.npy', allow_pickle=True)
print("Loaded Label Mappings:", class_names)

def preprocess_input(user_input):
    """
    Preprocess the user input to match the model's expected feature set.
    """
    # Convert user input to a DataFrame
    input_df = pd.DataFrame([user_input])

    # Perform one-hot encoding
    processed_input = pd.get_dummies(input_df, columns=input_df.select_dtypes(include=['object']).columns[:])

    # Align with all features used in training
    aligned_input = processed_input.reindex(columns=all_feature_names, fill_value=0)

    return aligned_input.to_numpy()

def predict_risk(user_input):
    """
    Predict the wildfire risk category using the Random Forest model.

    Args:
        user_input (dict): Dictionary of user-provided input features.

    Returns:
        dict: Predicted risk category and probabilities for each category.
    """
    # Preprocess the input
    processed_input = preprocess_input(user_input)

    # Predict class
    predicted_class = random_forest_model.predict(processed_input)

    # Predict probabilities
    predicted_probabilities = random_forest_model.predict_proba(processed_input)

    # Map predicted class to risk label
    predicted_risk = class_names[int(predicted_class[0])]

    # Return results
    return {
        "predicted_risk": predicted_risk,
        "probabilities": {label: prob for label, prob in zip(class_names, predicted_probabilities[0])}
    }
