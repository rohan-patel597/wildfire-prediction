import plotly.express as px
import pandas as pd
import requests
import urllib.parse
import logging
import os 

log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Always log to console
    ]
)

# Add file handler after creating directory
logger = logging.getLogger(__name__)
try:
    file_handler = logging.FileHandler(os.path.join(log_dir, 'Logwildfire_map.log'))
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
except Exception as e:
    logger.warning(f"Could not set up file logging: {e}")

def create_map(city, county, community, risk_probabilities):
    try:
        logger.info("Starting map creation process.")
        # Geocode the location
        location = f"{city}, {county}, {community}, California, USA"
        logger.info(f"Geocoding location: {location}")
        encoded_location = urllib.parse.quote(location)
        
        headers = {
            'User-Agent': 'WildfirePredictionApp/1.0',
            'Accept': 'application/json'
        }
        
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_location}&format=jsonv2&limit=1"
        logger.info(f"Making request to: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Geocoding response: {data}")
        
        if data and len(data) > 0:
            lat = float(data[0].get('lat', 39.7233))
            lon = float(data[0].get('lon', -121.9026))
        else:
            lat, lon = 39.7233, -121.9026  # California Butte
            logger.warning("Fallback to default coordinates (Butte, California).")
            
        # Create a grid of points around the location for the heatmap
        radius = 50  # Approximately 5km radius
        points = []
        
        # Get the highest risk probability to determine intensity
        max_prob = max(risk_probabilities.values())
        logger.info(f"Max risk probability: {max_prob}")
        
        # Generate points in a grid pattern around the location
        for i in range(-5, 6):
            for j in range(-5, 6):
                points.append({
                    'lat': lat + (i * radius / 5),
                    'lon': lon + (j * radius / 5),
                    'intensity': max_prob * (1 - (abs(i) / 5 + abs(j) / 5) / 2)  # Decrease intensity with distance
                })
        
        df = pd.DataFrame(points)
        logger.info("Generated points for heatmap grid.")

        # Create the map with both scatter and density layers
        fig = px.density_mapbox(
            df,
            lat='lat',
            lon='lon',
            z='intensity',
            radius=200,
            center=dict(lat=lat, lon=lon),
            zoom=14,
            mapbox_style="open-street-map",
            opacity=0.8,
            color_continuous_scale=["green", "yellow", "red"]
        )
        
        # Add a marker for the exact location
        fig.add_scattermapbox(
            lat=[lat],
            lon=[lon],
            mode='markers',
            marker=dict(size=10, color='red'),
            name='Location'
        )
        
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            mapbox=dict(
                center=dict(lat=lat, lon=lon),
                zoom=14
            )
        )
        logger.info("Map successfully created.")
        return fig

    except requests.RequestException as e:
        logger.error(f"Error in geocoding request: {e}")
        # Fallback to California center coordinates
        lat, lon = 39.7233, -121.9026
        logger.info("Using fallback coordinates for map creation.")
        return None

    except ValueError as e:
        logger.error(f"ValueError during map creation: {e}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None
