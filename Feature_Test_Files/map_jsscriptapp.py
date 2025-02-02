import streamlit as st
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components
import logging
from datetime import datetime

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("=== Application Starting ===")
print(f"Initializing app at {datetime.now()}")

# Initialize session state
if 'coords' not in st.session_state:
    st.session_state.coords = None
if 'location_history' not in st.session_state:
    st.session_state.location_history = []

st.title("California Wildfire Housing Damage Risk Predictor")
print("Title rendered")

# JavaScript code remains same but add console.logs
geolocation_js = """
<script>
let watchId = null;

function success(position) {
    console.log('Starting location tracking...');
    const coords = {
        lat: position.coords.latitude,
        lon: position.coords.longitude,
        accuracy: position.coords.accuracy,
        timestamp: new Date().toISOString()
    };

    console.log('New position received:', coords);
    
    // Log the data being sent to Streamlit
    console.log('Sending coordinates to Streamlit:', coords);
    
    window.parent.postMessage({
        type: "streamlit:setCoords",
        coords: coords
    }, "*");
}

function error(err) {
    if(err.code === 1) {
        alert("Location access denied by user. Please allow access!!");
    } else {
        alert("Position unavailable for current User location - check GPS settings");
    }
}

function startLocationTracking() {
    if (!navigator.geolocation) {
        alert('No GeoLocation Available');
        return;
    }
    
    const options = {
        enableHighAccuracy: true,
        maximumAge: 0,
        timeout: 10000
    };
    
    watchId = navigator.geolocation.watchPosition(success, error, options);
}

function stopLocationTracking() {
    if (watchId) {
        console.log('Stopping location tracking...');
        navigator.geolocation.clearWatch(watchId);
        watchId = null;
        console.log('Location tracking stopped');
    }
}

</script>

<div style="margin: 10px 0;">
    <button onclick="startLocationTracking()" style="padding: 8px 16px; margin-right: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">
        Start Location Tracking
    </button>
    <button onclick="stopLocationTracking()" style="padding: 8px 16px; background-color: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer;">
        Stop Tracking
    </button>
</div>
"""

st.subheader("Real-time Location Tracking")
print("Subheader rendered")

# Add JavaScript component
components.html(geolocation_js, height=70)
print("JavaScript component added")

# Listen for messages from JavaScript
components.html(
    """
    <script>
    window.addEventListener("message", (event) => {
        if (event.data.type === "streamlit:setCoords") {
            const coords = event.data.coords;
            const markup = event.data.markup;
            window.parent.postMessage({
                type: "streamlit:updateCoords",
                coords: coords
            }, "*");
        }
    });
    </script>
    """,
    height=0
)
print('After javascript')
print(st.session_state.coords)

# # Handle the message from JavaScript
# def handle_message():
#     if 'coords' in st.session_state and st.session_state.coords is None:
#         st.session_state.location_history.append(st.session_state.coords)
        
# handle_message()

# Handle the message from JavaScript
def handle_message():
    if 'coords' in st.session_state:
        st.session_state.location_history.append(st.session_state.coords)

# Listen for updates from JavaScript
if 'coords' not in st.session_state:
    st.session_state.coords = None

# Update session state when coordinates are received
if st.session_state.coords is None:
    # Simulate receiving coordinates (for testing)
    # Replace this with actual logic to listen for JavaScript messages
    st.session_state.coords = {'lat': 37.7749, 'lon': -122.4194}  # Example coordinates

handle_message()

# print(st.s)
# Display the map if coordinates are available
if st.session_state.coords:
    lat = st.session_state.coords['lat']
    lon = st.session_state.coords['lon']
    print(f"Coordinates', ${lat} and ${lon}")
    
    logger.debug(f"Displaying coordinates - Latitude: {lat}, Longitude: {lon}")
    
    
    try:
        print('Inside Try')
        print(f"Creating map with coordinates: {lat}, {lon}")
        location_map = folium.Map(location=[lat, lon], zoom_start=15)
        print()
        
        # Add marker for current location
        folium.Marker([lat, lon], popup="Current Location", icon=folium.Icon(color='red', icon='info-sign')).add_to(location_map)
        
        # # Add location history path if available
        # if len(st.session_state.location_history) > 1:
        #     locations = [[pos['lat'], pos['lon']] for pos in st.session_state.location_history]
        #     folium.PolyLine(
        #         locations,
        #         weight=3,
        #         color='blue',
        #         opacity=0.8
        #     ).add_to(location_map)
        
        # Render the map
        st_folium(location_map, width=700, height=500)
        
        st.success(f"Current Location: Latitude: {lat:.6f}, Longitude: {lon:.6f}")
        st.text(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print('Inside Expcetion')
        
        st.error(f"Error creating map: {str(e)}")
else:
    st.info("Click 'Start Location Tracking' to begin tracking your location")

# Debug information
if st.checkbox("Show Debug Info"):
    st.write("Current Coordinates:", st.session_state.coords)
    st.write("Location History Count:", len(st.session_state.location_history))
    if st.session_state.location_history:
        st.write("Recent Location History:", st.session_state.location_history[-5:])

print("=== Application Rendered ===")