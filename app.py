import streamlit as st
import joblib
import pandas as pd
import numpy as np
import os

st.title('Car Price Prediction App')

st.write('Enter the car features below to get a price prediction.')

# Add print statements for debugging file loading
# st.write(f"Current working directory: {os.getcwd()}")
# st.write(f"Files in current directory: {os.listdir()}")


# Load the saved model and selected features
try:
    # st.write("Attempting to load best_model.joblib...")
    best_model = joblib.load('best_model.joblib')
    # st.write("best_model.joblib loaded successfully.")

    # st.write("Attempting to load selected_features.joblib...")
    selected_features = joblib.load('selected_features.joblib')
    # st.write("selected_features.joblib loaded successfully.")
    # st.write(f"Selected features loaded: {selected_features}")

except FileNotFoundError as e:
    st.error(f"Error: Required file not found - {e}. Make sure best_model.joblib and selected_features.joblib are in the same directory as app.py")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred during file loading: {e}")
    st.stop()

# list of all possible models from training data
# For demonstration, List of all Models below:
all_possible_models = ['3','5','6','7','A4','A6','A8','Alto','Altroz','Alturas','Amaze','Aspire','Aura','Baleno','Bolero','C','Camry','Carnival','Cayenne','C-Class','Celerio','Ciaz','City','Civic','CLS','Compass','Continental','Cooper','CR','Creta','CR-V','D-Max','Duster','DzireLXI','DzireVXI','DzireZXI','E-Class','Ecosport','Eeco','Elantra','Endeavour','Ertiga','ES','Figo','Fortuner','F-PACE','Freestyle','Ghibli','Ghost','Glanza','GL-Class','GLS','GO','Grand','GTC4Lusso','Gurkha','Harrier','Hector','Hexa','i10','i20','Ignis','Innova','Jazz','Kicks','KUV','KUV100','KWID','Macan','Marazzo','MUX','Nexon','NX','Octavia','Panamera','Polo','Q7','Quattroporte','Rapid','RediGO','redi-GO','Rover','RX','S90','Safari','Santro','S-Class','Scorpio','Seltos','S-Presso','Superb','Swift','SwiftDzire','Thar','Tiago','Tigor','Triber','Tucson','Vento','Venue','Verna','Vitara','WagonR','Wrangler','WR-V','X1','X3','X4','X5','XC','XC60','XC90','XE','XF','XL6','X-Trail','XUV300','XUV500','Yaris','Z4'] # Replace with actual loaded list


# For now, using a simple mapping based on the order of all_possible_models
def encode_model(model_name, model_list):
    try:
        return model_list.index(model_name)
    except ValueError:
        return -1 # Handle unseen models, or use a more robust approach

# Create input widgets for each selected feature
input_data = {}
# Check if selected_features is loaded and is iterable before looping
if 'selected_features' in locals() and isinstance(selected_features, list):
    for feature in selected_features:
        if feature == 'model':
             # Add a selectbox for the 'model' feature
            selected_model_name = st.selectbox(f'Select {feature.replace("_", " ").title()}', all_possible_models)
            input_data[feature] = encode_model(selected_model_name, all_possible_models) # Encode the selected model
        elif feature in ['vehicle_age', 'km_driven', 'engine', 'seats']:
            input_data[feature] = st.number_input(f'Enter {feature.replace("_", " ").title()}', min_value=0, value=0, step=1)
        elif feature in ['mileage', 'max_power']:
             input_data[feature] = st.number_input(f'Enter {feature.replace("_", " ").title()}', min_value=0.0, value=0.0, step=0.1)
        elif feature.startswith('fuel_type_'):
            # Handle one-hot encoded fuel types
            fuel_type = feature.replace('fuel_type_', '')
            # Assuming False corresponds to the base category (e.g., not that fuel type) and True corresponds to the specific fuel type
            input_data[feature] = st.selectbox(f'Is the car {fuel_type} fueled?', [False, True])
        elif feature.startswith('transmission_type_'):
            # Handle one-hot encoded transmission types
            transmission_type = feature.replace('transmission_type_', '')
             # Assuming False corresponds to the base category (e.g., not that transmission type) and True corresponds to the specific transmission type
            input_data[feature] = st.selectbox(f'Is the car {transmission_type} transmission?', [False, True])
        # Add handling for other categorical features if they were included in selected_features
        # e.g., if 'brand' was selected and one-hot encoded
else:
    st.error("Selected features list is not loaded correctly. Cannot create input widgets.")
    st.stop()


if st.button('Predict Price'):
    # Create a DataFrame from the input data
    # Ensure all selected_features are present in input_data, even if not explicitly added via widgetr
    # Initialize input_data with all selected features set to a default (e.g., 0 for numerical, False for booleans)
    # Then update with user inputs

    # Create a dictionary with default values for all selected features
    default_input_data = {}
    for feature in selected_features:
        if feature in ['vehicle_age', 'km_driven', 'mileage', 'engine', 'max_power', 'seats', 'model']: # Assuming model is numeric after encoding
             default_input_data[feature] = 0
        elif feature.startswith('fuel_type_') or feature.startswith('transmission_type_'):
             default_input_data[feature] = False
        # Add default handling for other data types if necessary


    # Update default_input_data with values from the input widgets
    # This handles the case where a feature is selected but doesn't have a dedicated widget
    # For example, if 'brand' was in selected_features but no 'brand' widget exists,
    # input_data would be missing 'brand', causing a KeyError when creating the DataFrame from input_data directly.
    # By updating defaults, we ensure all selected_features are present in the intermediate dictionary.
    user_input_values = {}
    # Iterate through the features that actually had input widgets created and collect their values
    if 'selected_features' in locals() and isinstance(selected_features, list):
        for feature in selected_features:
             # Check if the feature was processed in the input widget creation loop and has a corresponding entry in input_data
             # A more robust approach would be to populate input_data directly with all selected features and their widget values.
            if feature in input_data: # Check if the feature from selected_features was processed by the widget loop
                user_input_values[feature] = input_data[feature] # Get the value from the widget

    # Now update the default_input_data with the user's inputs
    default_input_data.update(user_input_values)


    # Create a DataFrame from the prepared input data dictionary
    input_df = pd.DataFrame([default_input_data])


    input_df = input_df[selected_features]

    # Make prediction
    try:
        predicted_price = best_model.predict(input_df)
        st.success(f'The predicted selling price is: ₹{predicted_price[0]:,.2f}')
    except Exception as e:
        st.error(f"Error making prediction: {e}")

st.markdown("---")
st.write("Note: This is a basic prediction app. For a production deployment, consider more robust input validation and error handling. Model created by Mpho Malebana.....")
