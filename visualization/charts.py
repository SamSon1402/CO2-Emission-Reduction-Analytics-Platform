"""
Chart generation functions for the CO2 Emission Reduction Analytics Platform
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Color schemes
COLOR_SCHEMES = {
    'emissions': 'Blues',
    'efficiency': 'RdYlGn_r',
    'savings': 'Greens',
    'comparison': 'RdBu_r'
}

def create_emissions_by_aircraft_chart(data):
    """
    Create bar chart showing emissions by aircraft type
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Plotly figure object
    """
    logger.info("Creating emissions by aircraft chart")
    
    # Group data by aircraft type
    aircraft_emissions = data.groupby('aircraft_type').agg({
        'co2_emissions_kg': 'sum',
        'distance_km': 'sum',
        'flight_id': 'count'
    }).reset_index()
    
    aircraft_emissions['emissions_per_km'] = aircraft_emissions['co2_emissions_kg'] / aircraft_emissions['distance_km']
    aircraft_emissions = aircraft_emissions.sort_values('emissions_per_km', ascending=False)
    
    fig = px.bar(
        aircraft_emissions,
        x='aircraft_type',
        y='emissions_per_km',
        color='emissions_per_km',
        color_continuous_scale=COLOR_SCHEMES['emissions'],
        labels={
            'aircraft_type': 'Aircraft Type',
            'emissions_per_km': 'CO2 Emissions (kg) per km'
        },
        text=aircraft_emissions['emissions_per_km'].round(2)
    )
    
    fig.update_layout(
        height=400,
        coloraxis_showscale=False,
        title_x=0.5,
        xaxis_title="",
        yaxis_title="kg CO2 per km",
    )
    
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    
    return fig

def create_emissions_by_distance_chart(data):
    """
    Create bar chart showing emissions by route distance category
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Plotly figure object
    """
    logger.info("Creating emissions by distance chart")
    
    # Create a copy to avoid modifying the original
    df = data.copy()
    
    # Create bins for route distances
    df['distance_bin'] = pd.cut(
        df['distance_km'], 
        bins=[0, 1000, 3000, 6000, 12000],
        labels=['Short (<1000km)', 'Medium (1000-3000km)', 'Long (3000-6000km)', 'Ultra-Long (>6000km)']
    )
    
    distance_emissions = df.groupby('distance_bin').agg({
        'co2_emissions_kg': 'sum',
        'distance_km': 'sum',
        'flight_id': 'count'
    }).reset_index()
    
    distance_emissions['emissions_per_flight'] = distance_emissions['co2_emissions_kg'] / distance_emissions['flight_id']
    
    fig = px.bar(
        distance_emissions,
        x='distance_bin',
        y='emissions_per_flight',
        color='emissions_per_flight',
        color_continuous_scale='Reds',
        labels={
            'distance_bin': 'Route Distance Category',
            'emissions_per_flight': 'Avg CO2 Emissions per Flight (kg)'
        },
        text=distance_emissions['emissions_per_flight'].round(0)
    )
    
    fig.update_layout(
        height=400,
        coloraxis_showscale=False,
        title_x=0.5,
        xaxis_title="",
        yaxis_title="kg CO2 per flight"
    )
    
    fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    
    return fig

def create_monthly_trend_chart(data):
    """
    Create line chart showing monthly emissions trend
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Plotly figure object
    """
    logger.info("Creating monthly trend chart")
    
    # Convert date string to datetime for grouping
    df = data.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%Y-%m')
    
    monthly_emissions = df.groupby('month').agg({
        'co2_emissions_kg': 'sum',
        'flight_id': 'count'
    }).reset_index()
    
    # Sort by month
    monthly_emissions = monthly_emissions.sort_values('month')
    
    fig = px.line(
        monthly_emissions, 
        x='month', 
        y='co2_emissions_kg',
        markers=True,
        labels={
            'month': 'Month',
            'co2_emissions_kg': 'Total CO2 Emissions (kg)'
        }
    )
    
    fig.update_layout(
        height=400,
        title_x=0.5,
        xaxis_title="",
        yaxis_title="kg CO2"
    )
    
    return fig

def create_potential_savings_chart(data):
    """
    Create bar chart showing potential savings from climb optimization
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Plotly figure object
    """
    logger.info("Creating potential savings chart")
    
    # Calculate potential savings from optimizing climb profiles
    non_optimal = data[~data['optimal_climb_used']]
    potential_savings = non_optimal.groupby('aircraft_type').agg({
        'potential_fuel_savings_kg': 'sum',
        'flight_id': 'count'
    }).reset_index()
    
    # Calculate CO2 savings (3.16 kg CO2 per kg fuel)
    potential_savings['co2_savings_kg'] = potential_savings['potential_fuel_savings_kg'] * 3.16
    
    # Sort by potential savings
    potential_savings = potential_savings.sort_values('co2_savings_kg', ascending=False)
    
    fig = px.bar(
        potential_savings,
        x='aircraft_type',
        y='co2_savings_kg',
        color='co2_savings_kg',
        color_continuous_scale=COLOR_SCHEMES['savings'],
        labels={
            'aircraft_type': 'Aircraft Type',
            'co2_savings_kg': 'Potential CO2 Savings (kg)'
        },
        text=potential_savings['co2_savings_kg'].round(0)
    )
    
    fig.update_layout(
        height=400,
        coloraxis_showscale=False,
        title_x=0.5,
        xaxis_title="",
        yaxis_title="kg CO2 Savings"
    )
    
    fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    
    return fig

def create_emissions_flight_level_chart(data):
    """
    Create scatter plot of emissions vs flight level
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Flight data
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Plotly figure object
    """
    logger.info("Creating emissions vs flight level chart")
    
    # Group by flight level
    fl_data = data.groupby('flight_level').agg({
        'co2_emissions_kg': 'mean',
        'distance_km': 'mean',
        'flight_id': 'count'
    }).reset_index()
    
    fl_data['emissions_per_km'] = fl_data['co2_emissions_kg'] / fl_data['distance_km']
    
    fig = px.scatter(
        fl_data,
        x='flight_level',
        y='emissions_per_km',
        size='flight_id',
        color='emissions_per_km',
        color_continuous_scale=COLOR_SCHEMES['emissions'],
        labels={
            'flight_level': 'Flight Level (ft)',
            'emissions_per_km': 'Avg CO2 per km (kg)',
            'flight_id': 'Number of Flights'
        }
    )
    
    fig.update_layout(
        height=400,
        title_x=0.5,
        xaxis_title="Flight Level (ft)",
        yaxis_title="kg CO2 per km"
    )
    
    return fig

def create_intervention_savings_chart(savings_by_intervention):
    """
    Create bar chart showing emission reduction by intervention
    
    Parameters:
    -----------
    savings_by_intervention : dict
        Dictionary of savings by intervention
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Plotly figure object
    """
    logger.info("Creating intervention savings chart")
    
    if not savings_by_intervention:
        return None
    
    # Prepare data for chart
    interventions_labels = {
        'optimize_climb': 'Optimize Climb Profiles',
        'weight_reduction': 'Aircraft Weight Reduction',
        'efficient_routing': 'Efficient Flight Routing',
        'engine_washing': 'Regular Engine Washing'
    }
    
    savings_data = pd.DataFrame({
        'intervention': [interventions_labels[i] for i in savings_by_intervention.keys()],
        'co2_reduction_kg': list(savings_by_intervention.values())
    })
    
    # Sort by impact
    savings_data = savings_data.sort_values('co2_reduction_kg', ascending=False)
    
    # Create chart
    fig = px.bar(
        savings_data,
        x='intervention',
        y='co2_reduction_kg',
        color='co2_reduction_kg',
        color_continuous_scale=COLOR_SCHEMES['savings'],
        labels={
            'intervention': 'Intervention',
            'co2_reduction_kg': 'CO2 Reduction (kg)'
        },
        text=savings_data['co2_reduction_kg'].round(0)
    )
    
    fig.update_layout(
        height=400,
        coloraxis_showscale=False,
        title_x=0.5,
        xaxis_title="",
        yaxis_title="kg CO2 Reduction"
    )
    
    fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    
    return fig