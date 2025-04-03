"""
Generate synthetic flight data for the CO2 Emission Reduction Analytics Platform
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)

def generate_flight_data(num_flights=1000, seed=42):
    """
    Generate synthetic flight data for demonstration purposes
    
    Parameters:
    -----------
    num_flights : int
        Number of flight records to generate
    seed : int
        Random seed for reproducibility
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing synthetic flight data
    """
    logger.info(f"Generating synthetic flight data with {num_flights} flights")
    np.random.seed(seed)
    
    # Create base dataframe
    today = datetime.now()
    
    # Aircraft types with different emissions profiles
    aircraft_types = ['A320', 'B737', 'A350', 'B777', 'A220', 'B787']
    aircraft_weights = {
        'A320': (65000, 78000),
        'B737': (62000, 82000),
        'A350': (185000, 220000),
        'B777': (190000, 247000),
        'A220': (45000, 60000),
        'B787': (150000, 180000)
    }
    
    routes = [
        ('Paris', 'London', 350),
        ('Paris', 'Madrid', 1050),
        ('Paris', 'Rome', 1100),
        ('Paris', 'Berlin', 880),
        ('Paris', 'Istanbul', 2200),
        ('Paris', 'Dubai', 5200),
        ('Paris', 'New York', 5800),
        ('Paris', 'Tokyo', 9700),
        ('Paris', 'Singapore', 10700)
    ]
    
    data = []
    flight_ids = [f"FL{i:04d}" for i in range(1, num_flights + 1)]
    
    for flight_id in flight_ids:
        # Select random route
        origin, destination, distance = routes[np.random.randint(0, len(routes))]
        
        # Select random aircraft
        aircraft = np.random.choice(aircraft_types)
        min_weight, max_weight = aircraft_weights[aircraft]
        takeoff_weight = np.random.randint(min_weight, max_weight)
        
        # Generate flight parameters
        flight_date = today - timedelta(days=np.random.randint(0, 90))
        flight_hour = np.random.randint(0, 24)
        flight_minute = np.random.choice([0, 15, 30, 45])
        departure_time = flight_date.replace(hour=flight_hour, minute=flight_minute)
        
        # Calculate flight parameters
        flight_level = np.random.randint(300, 410) * 100  # FL300-FL410
        avg_speed = np.random.randint(750, 900)  # km/h
        
        # Weather conditions (simplified)
        headwind = np.random.randint(-50, 80)  # negative for tailwind
        temperature_deviation = np.random.randint(-15, 15)  # from ISA
        
        # Calculate fuel and emissions
        base_fuel_per_km = {
            'A320': 3.0,
            'B737': 3.2,
            'A350': 7.5,
            'B777': 8.0,
            'A220': 2.5,
            'B787': 6.8
        }
        
        # Add some randomness to fuel consumption
        fuel_efficiency_factor = 0.85 + (np.random.rand() * 0.3)  # 0.85 to 1.15
        
        # Weather impact - headwind increases fuel consumption
        weather_factor = 1.0 + (headwind / 500)
        
        # Weight impact
        weight_factor = 0.9 + ((takeoff_weight - min_weight) / (max_weight - min_weight)) * 0.2
        
        # Calculate total fuel based on factors
        fuel_per_km = base_fuel_per_km[aircraft]
        total_fuel = fuel_per_km * distance * fuel_efficiency_factor * weather_factor * weight_factor
        
        # CO2 emissions: ~3.16 kg CO2 per kg of jet fuel
        co2_emissions = total_fuel * 3.16
        
        # Optimize climb calculation
        optimal_climb = np.random.choice([True, False], p=[0.4, 0.6])
        potential_savings = 0
        if not optimal_climb:
            # If not using optimal climb, calculate potential savings (1-3% of fuel)
            saving_percentage = 0.01 + (np.random.rand() * 0.02)
            potential_savings = total_fuel * saving_percentage
        
        # Add row to data
        data.append({
            'flight_id': flight_id,
            'date': flight_date.strftime('%Y-%m-%d'),
            'origin': origin,
            'destination': destination,
            'distance_km': distance,
            'aircraft_type': aircraft,
            'takeoff_weight_kg': takeoff_weight,
            'flight_level': flight_level,
            'avg_speed_kmh': avg_speed,
            'headwind_kmh': headwind,
            'temperature_deviation': temperature_deviation,
            'fuel_consumed_kg': total_fuel,
            'co2_emissions_kg': co2_emissions,
            'optimal_climb_used': optimal_climb,
            'potential_fuel_savings_kg': potential_savings,
            'departure_time': departure_time
        })
    
    df = pd.DataFrame(data)
    logger.info(f"Generated DataFrame with shape: {df.shape}")
    return df

def save_sample_data(num_flights=1000, filename="sample_flights.csv"):
    """
    Generate and save sample flight data to a CSV file
    
    Parameters:
    -----------
    num_flights : int
        Number of flight records to generate
    filename : str
        Output filename
    """
    data = generate_flight_data(num_flights)
    output_path = os.path.join("assets", "data", filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    data.to_csv(output_path, index=False)
    logger.info(f"Saved sample data to {output_path}")
    return data

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Generate and save sample data
    save_sample_data(1000)