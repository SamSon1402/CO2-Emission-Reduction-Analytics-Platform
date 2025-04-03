"""
CO2 emissions calculation models for the analytics platform
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Constants
FUEL_TO_CO2_RATIO = 3.16  # kg CO2 per kg fuel

def calculate_emissions(fuel_consumed):
    """
    Calculate CO2 emissions from fuel consumption
    
    Parameters:
    -----------
    fuel_consumed : float or array-like
        Fuel consumed in kg
        
    Returns:
    --------
    float or array-like
        CO2 emissions in kg
    """
    return fuel_consumed * FUEL_TO_CO2_RATIO

def calculate_fuel_consumption(
    distance_km, 
    aircraft_type, 
    takeoff_weight_kg,
    flight_level,
    headwind_kmh=0,
    temperature_deviation=0,
    optimal_climb=False
):
    """
    Calculate fuel consumption based on flight parameters
    
    Parameters:
    -----------
    distance_km : float
        Flight distance in km
    aircraft_type : str
        Type of aircraft
    takeoff_weight_kg : float
        Takeoff weight in kg
    flight_level : int
        Flight level (altitude)
    headwind_kmh : float
        Headwind in km/h (negative for tailwind)
    temperature_deviation : float
        Temperature deviation from ISA in Celsius
    optimal_climb : bool
        Whether optimal climb profile is used
        
    Returns:
    --------
    dict
        Dictionary containing fuel consumption and potential savings
    """
    # Base fuel consumption rates by aircraft type (kg/km)
    base_fuel_rates = {
        'A320': 3.0,
        'B737': 3.2,
        'A350': 7.5,
        'B777': 8.0,
        'A220': 2.5,
        'B787': 6.8
    }
    
    # Aircraft weight ranges
    aircraft_weights = {
        'A320': (65000, 78000),
        'B737': (62000, 82000),
        'A350': (185000, 220000),
        'B777': (190000, 247000),
        'A220': (45000, 60000),
        'B787': (150000, 180000)
    }
    
    # Check if we have data for this aircraft type
    if aircraft_type not in base_fuel_rates:
        logger.warning(f"Unknown aircraft type: {aircraft_type}, using A320 as default")
        aircraft_type = 'A320'
    
    # Get base fuel rate
    base_rate = base_fuel_rates[aircraft_type]
    
    # Weight factor calculation
    min_weight, max_weight = aircraft_weights[aircraft_type]
    normalized_weight = min(max(takeoff_weight_kg, min_weight), max_weight)
    weight_factor = 0.9 + ((normalized_weight - min_weight) / (max_weight - min_weight)) * 0.2
    
    # Altitude factor (simplified model)
    optimal_flight_level = {
        'A320': 360,
        'B737': 370,
        'A350': 400,
        'B777': 390,
        'B787': 400,
        'A220': 350
    }.get(aircraft_type, 370)
    
    flight_level_diff = abs(flight_level - optimal_flight_level * 100)
    altitude_factor = 1.0 + (flight_level_diff / 10000) * 0.05
    
    # Weather factors
    headwind_factor = 1.0 + (headwind_kmh / 500)
    temp_factor = 1.0 + (temperature_deviation / 100)
    
    # Calculate total fuel consumption
    fuel_consumption = base_rate * distance_km * weight_factor * altitude_factor * headwind_factor * temp_factor
    
    # Calculate potential savings from optimal climb
    potential_savings = 0
    if not optimal_climb:
        # If not using optimal climb, calculate potential savings (1-3% of fuel)
        saving_percentage = 0.02  # Average 2% savings
        potential_savings = fuel_consumption * saving_percentage
    
    return {
        'fuel_consumed_kg': fuel_consumption,
        'co2_emissions_kg': fuel_consumption * FUEL_TO_CO2_RATIO,
        'potential_fuel_savings_kg': potential_savings,
        'potential_co2_savings_kg': potential_savings * FUEL_TO_CO2_RATIO
    }

def calculate_emission_reductions(data, interventions):
    """
    Calculate the emission reduction based on selected interventions
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
    interventions : list
        List of interventions to apply
        
    Returns:
    --------
    tuple
        (modified_data, total_reduction, savings_by_intervention)
    """
    logger.info(f"Calculating emission reductions for interventions: {interventions}")
    
    total_emissions = data['co2_emissions_kg'].sum()
    total_fuel = data['fuel_consumed_kg'].sum()
    
    # Copy the data to avoid modifying the original
    modified_data = data.copy()
    savings = {}
    
    # Apply selected interventions
    if 'optimize_climb' in interventions:
        # Calculate savings for flights not using optimal climb
        non_optimal_flights = modified_data[~modified_data['optimal_climb_used']]
        climb_savings = non_optimal_flights['potential_fuel_savings_kg'].sum()
        modified_data.loc[~modified_data['optimal_climb_used'], 'fuel_consumed_kg'] -= modified_data.loc[~modified_data['optimal_climb_used'], 'potential_fuel_savings_kg']
        co2_reduction = climb_savings * FUEL_TO_CO2_RATIO
        savings['optimize_climb'] = co2_reduction
        logger.info(f"Optimize climb savings: {co2_reduction:.2f} kg CO2")
    
    if 'weight_reduction' in interventions:
        # Simulate 1% weight reduction = ~0.6% fuel savings
        weight_factor = 0.006
        weight_savings = modified_data['fuel_consumed_kg'] * weight_factor
        modified_data['fuel_consumed_kg'] -= weight_savings
        co2_reduction = weight_savings.sum() * FUEL_TO_CO2_RATIO
        savings['weight_reduction'] = co2_reduction
        logger.info(f"Weight reduction savings: {co2_reduction:.2f} kg CO2")
    
    if 'efficient_routing' in interventions:
        # Simulate more efficient routes (1-2% savings)
        route_factor = 0.015
        route_savings = modified_data['fuel_consumed_kg'] * route_factor
        modified_data['fuel_consumed_kg'] -= route_savings
        co2_reduction = route_savings.sum() * FUEL_TO_CO2_RATIO
        savings['efficient_routing'] = co2_reduction
        logger.info(f"Efficient routing savings: {co2_reduction:.2f} kg CO2")
    
    if 'engine_washing' in interventions:
        # Engine washing can save ~0.5-1% fuel
        engine_factor = 0.008
        engine_savings = modified_data['fuel_consumed_kg'] * engine_factor
        modified_data['fuel_consumed_kg'] -= engine_savings
        co2_reduction = engine_savings.sum() * FUEL_TO_CO2_RATIO
        savings['engine_washing'] = co2_reduction
        logger.info(f"Engine washing savings: {co2_reduction:.2f} kg CO2")
    
    # Recalculate CO2 emissions
    modified_data['co2_emissions_kg'] = modified_data['fuel_consumed_kg'] * FUEL_TO_CO2_RATIO
    
    # Calculate total savings
    new_total_emissions = modified_data['co2_emissions_kg'].sum()
    emission_reduction = total_emissions - new_total_emissions
    
    logger.info(f"Total emission reduction: {emission_reduction:.2f} kg CO2 ({emission_reduction/total_emissions*100:.2f}%)")
    
    return modified_data, emission_reduction, savings

def calculate_financial_impact(emission_reduction, carbon_price=80, fuel_price=800):
    """
    Calculate financial impact of emission reductions
    
    Parameters:
    -----------
    emission_reduction : float
        CO2 emission reduction in kg
    carbon_price : float
        Carbon credit price in EUR per tonne
    fuel_price : float
        Jet fuel price in EUR per tonne
        
    Returns:
    --------
    dict
        Dictionary with financial metrics
    """
    # Calculate fuel savings (CO2 / 3.16)
    fuel_savings = emission_reduction / FUEL_TO_CO2_RATIO
    
    # Calculate financial savings
    carbon_savings = (emission_reduction / 1000) * carbon_price  # Convert kg to tonnes
    fuel_cost_savings = (fuel_savings / 1000) * fuel_price  # Convert kg to tonnes
    total_savings = carbon_savings + fuel_cost_savings
    
    return {
        'fuel_savings_kg': fuel_savings,
        'fuel_savings_tonnes': fuel_savings / 1000,
        'carbon_savings_eur': carbon_savings,
        'fuel_cost_savings_eur': fuel_cost_savings,
        'total_savings_eur': total_savings
    }