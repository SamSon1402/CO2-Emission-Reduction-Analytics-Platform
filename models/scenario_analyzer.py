"""
Scenario analysis models for the CO2 Emission Reduction Analytics Platform
"""

import pandas as pd
import numpy as np
import logging
from models.emissions_calculator import FUEL_TO_CO2_RATIO

logger = logging.getLogger(__name__)

def create_baseline_scenario(data):
    """
    Create baseline scenario from flight data
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
        
    Returns:
    --------
    dict
        Baseline scenario metrics
    """
    logger.info("Creating baseline scenario")
    
    total_flights = len(data)
    total_distance = data['distance_km'].sum()
    total_fuel = data['fuel_consumed_kg'].sum()
    total_emissions = data['co2_emissions_kg'].sum()
    
    avg_emission_per_km = total_emissions / total_distance
    avg_emission_per_flight = total_emissions / total_flights
    
    return {
        'total_flights': total_flights,
        'total_distance_km': total_distance,
        'total_fuel_kg': total_fuel,
        'total_emissions_kg': total_emissions,
        'avg_emission_per_km': avg_emission_per_km,
        'avg_emission_per_flight': avg_emission_per_flight
    }

def analyze_fleet_optimization(data, target_aircraft_replacement=None):
    """
    Analyze the impact of fleet optimization by replacing aircraft
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
    target_aircraft_replacement : dict, optional
        Dictionary mapping aircraft types to their replacements
        
    Returns:
    --------
    tuple
        (modified_data, emission_reduction)
    """
    logger.info("Analyzing fleet optimization scenario")
    
    if target_aircraft_replacement is None:
        # Default replacements with more efficient aircraft
        target_aircraft_replacement = {
            'B777': 'B787',  # Replace B777 with more efficient B787
            'A320': 'A220'   # Replace A320 with more efficient A220
        }
    
    # Copy the data to avoid modifying the original
    modified_data = data.copy()
    
    baseline = create_baseline_scenario(data)
    
    # Aircraft efficiency factors (relative to current models)
    efficiency_improvements = {
        'B787': 0.85,  # 15% more efficient than average
        'A220': 0.80   # 20% more efficient than average
    }
    
    # Apply replacements
    for old_aircraft, new_aircraft in target_aircraft_replacement.items():
        flights_to_replace = modified_data['aircraft_type'] == old_aircraft
        num_flights = flights_to_replace.sum()
        
        if num_flights > 0:
            logger.info(f"Replacing {num_flights} flights from {old_aircraft} to {new_aircraft}")
            
            # Update aircraft type
            modified_data.loc[flights_to_replace, 'aircraft_type'] = new_aircraft
            
            # Apply efficiency improvement
            if new_aircraft in efficiency_improvements:
                efficiency_factor = efficiency_improvements[new_aircraft]
                modified_data.loc[flights_to_replace, 'fuel_consumed_kg'] *= efficiency_factor
                modified_data.loc[flights_to_replace, 'co2_emissions_kg'] *= efficiency_factor
    
    # Calculate total savings
    new_scenario = create_baseline_scenario(modified_data)
    emission_reduction = baseline['total_emissions_kg'] - new_scenario['total_emissions_kg']
    
    logger.info(f"Fleet optimization could reduce emissions by {emission_reduction:.2f} kg CO2")
    
    return modified_data, emission_reduction

def analyze_route_optimization(data, route=None):
    """
    Analyze the impact of route optimization
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
    route : str, optional
        Specific route to analyze
        
    Returns:
    --------
    dict
        Route optimization analysis
    """
    logger.info(f"Analyzing route optimization for route: {route}")
    
    # Filter data for specific route if provided
    if route:
        origin, destination = route.split(' - ')
        route_data = data[(data['origin'] == origin) & (data['destination'] == destination)].copy()
    else:
        route_data = data.copy()
        
    if len(route_data) == 0:
        logger.warning(f"No data found for route: {route}")
        return {}
    
    # Group by route
    route_metrics = route_data.groupby(['origin', 'destination']).agg({
        'co2_emissions_kg': ['mean', 'min', 'max', 'std'],
        'distance_km': 'mean',
        'fuel_consumed_kg': ['mean', 'min'],
        'flight_id': 'count'
    }).reset_index()
    
    # Flatten the multi-index columns
    route_metrics.columns = ['_'.join(col).strip('_') for col in route_metrics.columns.values]
    
    # Calculate emissions per km
    route_metrics['emissions_per_km'] = route_metrics['co2_emissions_kg_mean'] / route_metrics['distance_km_mean']
    route_metrics['min_emissions_per_km'] = route_metrics['co2_emissions_kg_min'] / route_metrics['distance_km_mean']
    
    # Calculate potential savings
    route_metrics['potential_savings_kg'] = route_metrics['co2_emissions_kg_mean'] - route_metrics['co2_emissions_kg_min']
    route_metrics['savings_percentage'] = (route_metrics['potential_savings_kg'] / route_metrics['co2_emissions_kg_mean']) * 100
    
    # Add route column
    route_metrics['route'] = route_metrics['origin_'] + ' - ' + route_metrics['destination_']
    
    # Calculate total potential savings
    total_flights = route_metrics['flight_id_count'].sum()
    total_potential_savings = (route_metrics['potential_savings_kg'] * route_metrics['flight_id_count']).sum()
    
    result = {
        'route_metrics': route_metrics,
        'total_flights': total_flights,
        'total_potential_savings_kg': total_potential_savings,
        'average_savings_per_flight_kg': total_potential_savings / total_flights
    }
    
    logger.info(f"Route optimization could save {total_potential_savings:.2f} kg CO2 across {total_flights} flights")
    
    return result