import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime
import logging
import os

# Custom CSS for buttons
st.markdown("""
    <style>
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        padding: 8px 16px;
        font-size: 16px;
        border: none;
        border-radius: 4px;
        margin-right: 10px;
        cursor: pointer;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .stButton.stop > button {
        background-color: #f44336;
        color: white;
    }
    .stButton.stop > button:hover {
        background-color: #e53935;
    }
    </style>
""", unsafe_allow_html=True)

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/location_tracking_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Title
st.title("California Wildfire Housing Damage Risk Predictor")


# Initialize session state for tracking
if 'tracking' not in st.session_state:
    st.session_state.tracking = False  # Whether location tracking is enabled
if 'location' not in st.session_state:
    st.session_state.location = None  # Store the current location
if 'prev_location' not in st.session_state:
    st.session_state.prev_location = None  # Store the previous location


# Create columns for the location icon and "Stop Tracking" button
col1, col2 = st.columns(2)

if 'tracking' not in st.session_state:
    st.session_state.tracking = False

with col1:
    # Toggle for starting/stopping tracking
    st.session_state.tracking = st.checkbox("Track Location", value=st.session_state.tracking)
    
    if st.session_state.tracking:
        st.info("Please Click the icon to start sharing your location")
    
        location = streamlit_geolocation()
        if location and location.get('latitude') and location.get('longitude'):
            # st.warning("Fetching location...")
            st.session_state.location = location
            st.info("Location tracking in progress.")

with col2:
    if st.button("Stop Tracking", key="stop", help="Stop location updates", disabled=not st.session_state.tracking):
        st.session_state.tracking = False
        st.info("Location tracking stopped.")
        st.rerun()

# Update the map if location changes
if st.session_state.tracking:
    if location is not None and location.get('latitude') is not None and location.get('longitude') is not None:
        st.info("Location tracking started.")
        lat = st.session_state.location.get('latitude')
        lon = st.session_state.location.get('longitude')
        st.session_state.location = {'latitude': lat, 'longitude': lon}
        
        # Log location update if it's different from previous location    
        if st.session_state.prev_location != (lat, lon):
            logger.info(f"Location updated - Latitude: {lat:.6f}, Longitude: {lon:.6f}")
            st.session_state.prev_location = (lat, lon)

        # Display current location
        st.success(f"Current Location: Latitude: {lat:.6f}, Longitude: {lon:.6f}")
        st.text(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Display map
        try:
            location_map = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker([lat, lon], popup="Current Location", icon=folium.Icon(color='red', icon='info-sign')).add_to(location_map)
            st_folium(location_map, width=700, height=500)
        except Exception as e:
            logger.error(f"Error creating map: {str(e)}")
            st.error("Error creating map")
else:
    st.info("Click the location icon to share your real-time location or stop tracking to halt updates.")

# Retain the last known location if tracking is stopped
if not st.session_state.tracking and st.session_state.location:
    # lat, lon = st.session_state.location
    lat = st.session_state.location['latitude']
    lon = st.session_state.location['longitude']
    st.info(f"Tracking stopped. Last known location: Latitude: {lat:.6f}, Longitude: {lon:.6f}")
    try:
        # Display the last known location on the map
        location_map = folium.Map(location=[lat, lon], zoom_start=15)
        folium.Marker([lat, lon], popup="Last Known Location", icon=folium.Icon(color='blue', icon='info-sign')).add_to(location_map)
        st_folium(location_map, width=700, height=500)
    except Exception as e:
        logger.error(f"Error creating map: {str(e)}")
        st.error("Error creating map")

# Debug Information
if st.checkbox("Show Debug Info"):
    st.write("Session State:", st.session_state)