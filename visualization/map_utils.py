"""
Map visualization utilities for the CO2 Emission Reduction Analytics Platform
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Airport coordinates (simplified version for demo)
AIRPORT_COORDS = {
    'Paris': (48.8566, 2.3522),
    'London': (51.5074, -0.1278),
    'Madrid': (40.4168, -3.7038),
    'Rome': (41.9028, 12.4964),
    'Berlin': (52.5200, 13.4050),
    'Istanbul': (41.0082, 28.9784),
    'Dubai': (25.2048, 55.2708),
    'New York': (40.7128, -74.0060),
    'Tokyo': (35.6762, 139.6503),
    'Singapore': (1.3521, 103.8198)
}

def create_route_map(data, selected_routes=None, color_by='emissions'):
    """
    Create a map visualization of routes
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
    selected_routes : list, optional
        List of routes to display
    color_by : str
        Metric to color routes by ('emissions', 'savings', 'frequency')
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Plotly figure object
    """
    logger.info(f"Creating route map colored by {color_by}")
    
    # Group by route
    route_data = data.groupby(['origin', 'destination']).agg({
        'co2_emissions_kg': 'mean',
        'distance_km': 'mean',
        'flight_id': 'count'
    }).reset_index()
    
    # Calculate emissions per km
    route_data['emissions_per_km'] = route_data['co2_emissions_kg'] / route_data['distance_km']
    
    # Filter by selected routes if provided
    if selected_routes:
        filtered_routes = []
        for route in selected_routes:
            origin, destination = route.split(' - ')
            filtered_routes.append((origin, destination))
        
        route_data = route_data[route_data.apply(lambda x: (x['origin'], x['destination']) in filtered_routes, axis=1)]
    
    # Add route name
    route_data['route'] = route_data['origin'] + ' - ' + route_data['destination']
    
    # Create map
    fig = go.Figure()
    
    # Color mapping
    if color_by == 'emissions':
        color_values = route_data['emissions_per_km']
        color_scale = 'Blues'
        color_label = 'CO2 per km (kg)'
    elif color_by == 'frequency':
        color_values = route_data['flight_id']
        color_scale = 'Viridis'
        color_label = 'Number of Flights'
    else:
        color_values = route_data['emissions_per_km']
        color_scale = 'Blues'
        color_label = 'CO2 per km (kg)'
    
    # Normalize colors for better visibility
    min_val = color_values.min()
    max_val = color_values.max()
    normalized_colors = (color_values - min_val) / (max_val - min_val)
    
    # Add flight routes
    for idx, row in route_data.iterrows():
        origin = row['origin']
        destination = row['destination']
        
        if origin in AIRPORT_COORDS and destination in AIRPORT_COORDS:
            orig_lat, orig_lon = AIRPORT_COORDS[origin]
            dest_lat, dest_lon = AIRPORT_COORDS[destination]
            
            # Create great circle path
            lons = np.linspace(orig_lon, dest_lon, 100)
            lats = np.linspace(orig_lat, dest_lat, 100)
            
            # Add path
            color_idx = normalized_colors.iloc[idx]
            
            fig.add_trace(go.Scattergeo(
                lon=lons,
                lat=lats,
                mode='lines',
                line=dict(width=2, color=f'rgba(0, 0, 255, {0.3 + 0.7 * color_idx})'),
                opacity=0.7,
                name=row['route'],
                hoverinfo='text',
                text=f"{row['route']}<br>Distance: {row['distance_km']:.0f} km<br>CO2: {row['co2_emissions_kg']:.0f} kg<br>Flights: {row['flight_id']}"
            ))
    
    # Add airport markers
    airports = set()
    for idx, row in route_data.iterrows():
        airports.add(row['origin'])
        airports.add(row['destination'])
    
    airport_lats = []
    airport_lons = []
    airport_names = []
    
    for airport in airports:
        if airport in AIRPORT_COORDS:
            lat, lon = AIRPORT_COORDS[airport]
            airport_lats.append(lat)
            airport_lons.append(lon)
            airport_names.append(airport)
    
    fig.add_trace(go.Scattergeo(
        lon=airport_lons,
        lat=airport_lats,
        text=airport_names,
        mode='markers',
        marker=dict(
            size=8,
            color='red',
            symbol='circle'
        ),
        name='Airports'
    ))
    
    # Update layout
    fig.update_layout(
        height=600,
        geo=dict(
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
            showocean=True,
            oceancolor='rgb(230, 230, 250)',
            showlakes=True,
            lakecolor='rgb(230, 230, 250)',
            showcountries=True,
            resolution=50
        ),
        showlegend=False
    )
    
    return fig