import plotly.express as px
import pandas as pd
import requests
import urllib.parse

def create_map(city, county, community):
    try:
        # Encode the location to handle special characters
        location = f"{city}, {county}, {community}, California, USA"
        encoded_location = urllib.parse.quote(location)
        
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'WildfirePredictionApp/1.0',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        
        # Construct the URL with explicit format parameter
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_location}&format=jsonv2&limit=1"
        
        # Send the request
        response = requests.get(url, headers=headers)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Try to parse JSON
        data = response.json()
        
        # Check if data is not empty
        if data and len(data) > 0:
            lat = float(data[0].get('lat', 39.7233))
            lon = float(data[0].get('lon', -121.9026))
        else:
            # Fallback to California center coordinates
            lat, lon = 39.7233, -121.9026
        
    except (requests.RequestException, ValueError) as e:
        print(f"Error in geocoding: {e}")
        # Fallback to California center coordinates
        lat, lon = 39.7233, -121.9026
    
    # Create a DataFrame for the location
    df = pd.DataFrame({'lat': [lat], 'lon': [lon], 'location': [location]})
    
    # Create the map
    fig = px.scatter_mapbox(df, lat='lat', lon='lon', hover_name='location',
                            zoom=10, height=400)
    fig.update_layout(mapbox_style="open-street-map")
    
    return fig
