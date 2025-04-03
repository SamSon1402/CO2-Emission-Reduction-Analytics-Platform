"""
Optimization models for the CO2 Emission Reduction Analytics Platform
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def optimize_flight_level(data, aircraft_type=None):
    """
    Find optimal flight levels for minimum emissions
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
    aircraft_type : str, optional
        Specific aircraft type to analyze
        
    Returns:
    --------
    dict
        Optimal flight levels by aircraft type
    """
    logger.info(f"Optimizing flight level for aircraft type: {aircraft_type}")
    
    # Filter by aircraft type if specified
    if aircraft_type:
        filtered_data = data[data['aircraft_type'] == aircraft_type].copy()
    else:
        filtered_data = data.copy()
    
    if len(filtered_data) == 0:
        logger.warning(f"No data found for aircraft type: {aircraft_type}")
        return {}
    
    # Group by aircraft type and flight level
    fl_data = filtered_data.groupby(['aircraft_type', 'flight_level']).agg({
        'co2_emissions_kg': 'mean',
        'distance_km': 'mean',
        'flight_id': 'count'
    }).reset_index()
    
    # Calculate emissions per km
    fl_data['emissions_per_km'] = fl_data['co2_emissions_kg'] / fl_data['distance_km']
    
    # Find optimal flight level for each aircraft type
    optimal_fls = {}
    
    for ac_type in fl_data['aircraft_type'].unique():
        ac_data = fl_data[fl_data['aircraft_type'] == ac_type]
        
        if len(ac_data) > 0:
            # Find flight level with minimum emissions per km
            min_idx = ac_data['emissions_per_km'].idxmin()
            optimal_fl = ac_data.loc[min_idx, 'flight_level']
            min_emissions = ac_data.loc[min_idx, 'emissions_per_km']
            
            # Find current average emissions
            avg_emissions = filtered_data[filtered_data['aircraft_type'] == ac_type]['co2_emissions_kg'].sum() / \
                            filtered_data[filtered_data['aircraft_type'] == ac_type]['distance_km'].sum()
            
            # Calculate potential savings
            potential_savings_pct = (avg_emissions - min_emissions) / avg_emissions * 100
            
            optimal_fls[ac_type] = {
                'optimal_flight_level': optimal_fl,
                'min_emissions_per_km': min_emissions,
                'avg_emissions_per_km': avg_emissions,
                'potential_savings_pct': potential_savings_pct
            }
    
    logger.info(f"Identified optimal flight levels for {len(optimal_fls)} aircraft types")
    return optimal_fls