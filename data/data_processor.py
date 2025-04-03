"""
Data preprocessing utilities for the CO2 Emission Reduction Analytics Platform
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def preprocess_flight_data(data):
    """
    Preprocess flight data for analysis
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Raw flight data
        
    Returns:
    --------
    pandas.DataFrame
        Preprocessed flight data
    """
    logger.info("Preprocessing flight data")
    
    # Create a copy to avoid modifying the original
    df = data.copy()
    
    # Convert date string to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Extract month and year
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['month_name'] = df['date'].dt.strftime('%b')
    df['year_month'] = df['date'].dt.strftime('%Y-%m')
    
    # Create route column
    df['route'] = df['origin'] + ' - ' + df['destination']
    
    # Create distance categories
    df['distance_category'] = pd.cut(
        df['distance_km'], 
        bins=[0, 1000, 3000, 6000, 12000],
        labels=['Short', 'Medium', 'Long', 'Ultra-Long']
    )
    
    # Calculate emissions metrics
    df['emissions_per_km'] = df['co2_emissions_kg'] / df['distance_km']
    df['fuel_per_km'] = df['fuel_consumed_kg'] / df['distance_km']
    
    # Create headwind categories
    df['wind_category'] = pd.cut(
        df['headwind_kmh'], 
        bins=[-50, -20, 0, 20, 40, 80],
        labels=['Strong Tailwind', 'Light Tailwind', 'Neutral', 'Light Headwind', 'Strong Headwind']
    )
    
    logger.info(f"Preprocessing complete. Shape: {df.shape}")
    return df

def filter_data(data, aircraft_type=None, route=None, date_range=None):
    """
    Filter data based on criteria
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
    aircraft_type : str, optional
        Aircraft type to filter by
    route : str, optional
        Route to filter by
    date_range : tuple, optional
        (start_date, end_date) to filter by
        
    Returns:
    --------
    pandas.DataFrame
        Filtered data
    """
    logger.info(f"Filtering data: aircraft={aircraft_type}, route={route}, date_range={date_range}")
    
    # Create a copy to avoid modifying the original
    filtered_data = data.copy()
    
    # Apply filters
    if aircraft_type and aircraft_type != 'All':
        filtered_data = filtered_data[filtered_data['aircraft_type'] == aircraft_type]
    
    if route and route != 'All':
        origin, destination = route.split(' - ')
        filtered_data = filtered_data[(filtered_data['origin'] == origin) & 
                                     (filtered_data['destination'] == destination)]
    
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_data = filtered_data[(filtered_data['date'] >= start_date) & 
                                     (filtered_data['date'] <= end_date)]
    
    logger.info(f"Filtered data shape: {filtered_data.shape}")
    return filtered_data