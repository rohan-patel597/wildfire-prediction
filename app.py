import streamlit as st
import pandas as pd
import numpy as np
import pickle
import requests
import streamlit as st
import plotly.express as px
from prediction import predict_risk

st.title("California Wildfire Housing Damage Risk Predictor")

# Input: CITY, COUNTY, COMMUNITY
with st.container():
    col1, col2, col3 = st.columns(3)
    col1.markdown("**City**")
    city = col1.text_input("City", placeholder="Enter the city name", label_visibility="collapsed")
    col2.markdown("**County**")
    county = col2.text_input("County", placeholder="Enter the county name", label_visibility="collapsed")
    col3.markdown("**Community**")
    community = col3.text_input("Community", placeholder="Enter the community name", label_visibility="collapsed")

# Input: Vegetation Clearance
st.markdown("**Vegetation Clearance (distance in feet)**")
veg_clearance = st.selectbox(
    "Vegetation Clearance",
    ["""0-30'""", """30-60'""", """60-100'""", """>100'""", "Unknown"],
    label_visibility="collapsed"
)

# Input: Structure Type, Roof Construction, Eaves
with st.container():
    col1, col2, col3 = st.columns(3)
    col1.markdown("**Structure Type**")
    structure_type = col1.selectbox(
        "Structure Type",
        ["Single Family Residence", "Mobile Home", "Non-habitable",
        "Outbuilding", "Commercial Building", "Multi Family Residence",
        "Public Building", "Mixed Use", "Other"],
        label_visibility="collapsed"
    )

    col2.markdown("**Roof Construction Type**")
    roof_construction = col2.selectbox(
        "Roof Construction Type",
        ["Asphalt", "Fire Resistant", "Metal", "Unknown",
        "Tile", "Combustible", "Wood", "Concrete", "Other"],
        label_visibility="collapsed"
    )

    col3.markdown("**Eaves Type**")
    eaves = col3.selectbox(
        "Eaves Type",
        ["Unknown", "Unenclosed", "Enclosed",
        "No Eaves", "Not Applicable"],
        label_visibility="collapsed"
    )

# Input: Vent Screen, Exterior Surface, Window Pane
with st.container():
    col1, col2, col3 = st.columns(3)
    col1.markdown("**Vent Screen Type**")
    vent_screen = col1.selectbox(
        "Vent Screen Type",
        ["Yes", "No", "Mesh Screen <= 1/8",
        "No Vents", "Unscreened", "Mesh Screen > 1/8", "Unknown"],
        label_visibility="collapsed"
    )

    col2.markdown("**Exterior Surface Type**")
    exterior_surface = col2.selectbox(
        "Exterior Surface Type",
        ["Combustible", "Ignition Resistant",
        "Fire Resistant", "Unknown"],
        label_visibility="collapsed"
    )

    col3.markdown("**Window Pane Type**")
    window_pane = col3.selectbox(
        "Window Pane Type",
        ["Single Pane", "No Windows", "Multi Pane", "Unknown"],
        label_visibility="collapsed"
    )

# Input: Topography and Year Built
with st.container():
    col1, col2 = st.columns(2)
    col1.markdown("**Topography**")
    topography = col1.selectbox(
        "Topography",
        ["Flat Ground", "Slope", "Ridge Top", "Saddle", "Chimney", "Unknown"],
        label_visibility="collapsed"
    )

    col2.markdown("**Year Built**")
    year_built = col2.number_input(
        "Year Built",
        min_value=1800,
        max_value=2025,
        step=1,
        label_visibility="collapsed"
    )

# Buttons: Place buttons side by side
col1, col2 = st.columns(2)
with col1:
    predict_button = st.button("Predict Risk")
with col2:
    reset_button = st.button("Reset")

# Button: Predict Risk
if predict_button:
    # Prepare user input
    user_input = {
        "CITY": city,
        "COUNTY": county,
        "COMMUNITY": community,
        "VEGCLERANCE": veg_clearance,
        "STRUCTURET_STANDARDIZED": structure_type,
        "ROOFCONSTRUCTR": roof_construction,
        "EAVES": eaves,
        "VENTSCREEN": vent_screen,
        "EXTERIORSI": exterior_surface,
        "WINDOWPANE": window_pane,
        "TOPOGRAPHY": topography,
        "YEARBUILT": year_built
    }

    # Make prediction
    result = predict_risk(user_input)

    # # Display results
    # st.subheader("Prediction Results")
    # st.write(f"Predicted Risk Class: **{result['predicted_risk']}**")

    # st.write("Prediction Probabilities:")
    # for label, prob in result["probabilities"].items():
    #     st.write(f"- {label}: {prob:.2%}")
        
    # Display Bar Plot using Plotly
    st.subheader("Prediction Probabilities Visualization")
    probabilities = result["probabilities"]
    labels = list(probabilities.keys())
    values = list(probabilities.values())

    # Create Plotly bar chart
    fig = px.bar(
        x=labels,
        y=values,
        labels={"x": "Risk Categories", "y": "Probability"},
        title="Prediction Probabilities",
        text=values
    )
    fig.update_traces(texttemplate='%{text:.1%}', textposition='outside')  # Show percentages on bars
    fig.update_layout(yaxis=dict(range=[0, 1]))  # Set y-axis range to [0, 1]

    # Display the plot in Streamlit
    st.plotly_chart(fig)